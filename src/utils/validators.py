import re
from typing import Optional, Tuple

class Validators:
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Проверка номера телефона"""
        # Удаляем все нецифровые символы
        cleaned_phone = re.sub(r'\D', '', phone)
        
        if not cleaned_phone:
            return False, "Номер телефона не может быть пустым"
        
        if not cleaned_phone.startswith(('7', '375', '380')):
            return False, "Поддерживаются только номера в формате +7, +375, +380"
        
        if len(cleaned_phone) not in [11, 12, 13]:
            return False, "Неверная длина номера телефона"
            
        return True, None

    @staticmethod
    def validate_api_id(api_id: str) -> Tuple[bool, Optional[str]]:
        """Проверка API ID"""
        if not api_id:
            return False, "API ID не может быть пустым"
        
        if not api_id.isdigit():
            return False, "API ID должен содержать только цифры"
            
        if len(api_id) < 6 or len(api_id) > 8:
            return False, "Неверная длина API ID"
            
        return True, None

    @staticmethod
    def validate_api_hash(api_hash: str) -> Tuple[bool, Optional[str]]:
        """Проверка API Hash"""
        if not api_hash:
            return False, "API Hash не может быть пустым"
        
        if not re.match(r'^[a-fA-F0-9]{32}$', api_hash):
            return False, "API Hash должен содержать 32 символа (0-9, a-f)"
            
        return True, None

    @staticmethod
    def validate_channel_username(username: str) -> Tuple[bool, Optional[str]]:
        """Проверка username канала"""
        if not username:
            return False, "Username канала не может быть пустым"
        
        # Убираем @ если есть
        username = username.lstrip('@')
        
        if not re.match(r'^[a-zA-Z]\w{3,30}[a-zA-Z0-9]$', username):
            return False, "Неверный формат username канала"
            
        return True, None

    @staticmethod
    def validate_user_list(users: list) -> Tuple[bool, Optional[str]]:
        """Проверка списка пользователей"""
        if not users:
            return False, "Список пользователей пуст"
        
        invalid_users = []
        for user in users:
            # Проверяем формат username или phone
            if not re.match(r'^@?[a-zA-Z]\w{3,30}[a-zA-Z0-9]$', user) and \
               not re.match(r'^\+?\d{10,15}$', user):
                invalid_users.append(user)
                
        if invalid_users:
            return False, f"Неверный формат для пользователей: {', '.join(invalid_users)}"
            
        return True, None