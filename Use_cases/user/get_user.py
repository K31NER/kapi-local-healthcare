from Domain.user import User
from Repositories.user_repository import UserRepository


class GetUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self) -> User | None:
        return self.repo.get()
