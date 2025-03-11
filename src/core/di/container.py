from utils.config import Config
from utils.logger import Logger
from utils.database import Database
from core.account_manager import AccountManager
from core.services.auth_service import AuthService
from core.services.invite_service import InviteService

class Container:
    """Контейнер зависимостей приложения"""
    
    def __init__(self, config: Config):
        self._config = config
        self._logger = None
        self._database = None
        self._account_manager = None
        self._auth_service = None
        self._invite_service = None
        
        # Инициализация базовых сервисов
        self.logger
        self.database
        
    @property
    def config(self) -> Config:
        return self._config
        
    @property
    def logger(self) -> Logger:
        if not self._logger:
            self._logger = Logger()
        return self._logger
        
    @property
    def database(self) -> Database:
        if not self._database:
            self._database = Database(self._config.db_path)
        return self._database
        
    @property
    def account_manager(self) -> AccountManager:
        if not self._account_manager:
            self._account_manager = AccountManager(
                self.database,
                self.logger
            )
        return self._account_manager
        
    @property
    def auth_service(self) -> AuthService:
        if not self._auth_service:
            self._auth_service = AuthService(
                self.account_manager,
                self.logger
            )
        return self._auth_service
        
    @property
    def invite_service(self) -> InviteService:
        if not self._invite_service:
            self._invite_service = InviteService(
                self.account_manager,
                self.logger
            )
        return self._invite_service 