from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from utils.database import Account
import os

class AuthService:
    def __init__(self, account_manager, logger):
        self.account_manager = account_manager
        self.logger = logger
        self.current_client = None
        self.current_phone = None
        self.current_api_id = None
        self.current_api_hash = None
        
        # Создаем директорию для сессий если её нет
        if not os.path.exists('sessions'):
            os.makedirs('sessions')

    async def start_auth(self, phone: str, api_id: str, api_hash: str) -> dict:
        """Начало процесса авторизации"""
        try:
            # Очищаем предыдущую сессию если есть
            await self.reset_auth()
            
            self.current_phone = phone
            self.current_api_id = api_id
            self.current_api_hash = api_hash

            # Создаем клиент
            session_file = f'sessions/{phone}.session'
            self.current_client = TelegramClient(session_file, int(api_id), api_hash)

            await self.current_client.connect()
            self.logger.info(f"Подключение установлено для {phone}")

            if await self.current_client.is_user_authorized():
                self.logger.info(f"Пользователь {phone} уже авторизован")
                return await self.finish_auth()

            # Отправляем код
            await self.current_client.send_code_request(phone)
            self.logger.info(f"Код отправлен на номер {phone}")
            return {'need_code': True}

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Ошибка при начале авторизации: {error_msg}")
            await self.reset_auth()
            return {'error': error_msg}

    async def verify_code(self, code: str) -> dict:
        """Проверка кода подтверждения"""
        try:
            if not self.current_client:
                return {'error': 'Сначала начните процесс авторизации'}

            try:
                await self.current_client.sign_in(self.current_phone, code)
                self.logger.info(f"Код успешно проверен для {self.current_phone}")
                
                if await self.current_client.is_user_authorized():
                    return await self.finish_auth()
                
            except SessionPasswordNeededError:
                self.logger.info(f"Требуется 2FA для {self.current_phone}")
                return {'need_2fa': True}
            except PhoneCodeInvalidError:
                return {'error': 'Неверный код подтверждения'}
            except Exception as e:
                return {'error': str(e)}

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Ошибка при проверке кода: {error_msg}")
            await self.reset_auth()
            return {'error': error_msg}

    async def verify_2fa(self, password: str) -> dict:
        """Проверка пароля 2FA"""
        try:
            if not self.current_client:
                return {'error': 'Сначала начните процесс авторизации'}

            try:
                await self.current_client.sign_in(password=password)
                self.logger.info(f"2FA успешно пройдена для {self.current_phone}")
                
                if await self.current_client.is_user_authorized():
                    return await self.finish_auth()
                else:
                    return {'error': 'Не удалось авторизоваться после 2FA'}
                
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Ошибка при проверке 2FA: {error_msg}")
                return {'error': error_msg}

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Критическая ошибка при 2FA: {error_msg}")
            await self.reset_auth()
            return {'error': error_msg}

    async def finish_auth(self) -> dict:
        """Завершение процесса авторизации"""
        try:
            if not self.current_client or not self.current_phone:
                return {'error': 'Отсутствуют данные для авторизации'}

            if not await self.current_client.is_user_authorized():
                return {'error': 'Клиент не авторизован'}

            try:
                # Получаем информацию о пользователе
                me = await self.current_client.get_me()
                if not me:
                    return {'error': 'Не удалось получить информацию о пользователе'}

                # Получаем строку сессии
                session_string = await self.current_client.export_session_string()
                
                # Создаем объект Account
                account = Account(
                    id=None,
                    phone=self.current_phone,
                    api_id=self.current_api_id,
                    api_hash=self.current_api_hash,
                    session_string=session_string,
                    is_active=True,
                    restrictions=None
                )
                
                # Добавляем аккаунт в базу данных
                account_id = self.account_manager.db.add_account(account)
                if not account_id:
                    return {'error': 'Не удалось сохранить аккаунт в базе данных'}

                self.logger.info(f"Аккаунт {self.current_phone} успешно добавлен")
                return {'success': True}

            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Ошибка при завершении авторизации: {error_msg}")
                return {'error': error_msg}

        finally:
            await self.reset_auth()

    async def reset_auth(self):
        """Сброс состояния авторизации"""
        if self.current_client:
            try:
                await self.current_client.disconnect()
            except:
                pass
        self.current_client = None
        self.current_phone = None
        self.current_api_id = None
        self.current_api_hash = None 