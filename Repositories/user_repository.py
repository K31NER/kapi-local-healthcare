from abc import ABC, abstractmethod
from Domain.user import User, CacheUser


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def get(self) -> User | None: ...

    @abstractmethod
    def update(self, user: User) -> User: ...

    @abstractmethod
    def delete(self) -> None: ...
    
    @abstractmethod
    def get_user_context(self) -> CacheUser | None: ...
