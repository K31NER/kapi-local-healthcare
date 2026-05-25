from Domain.user import User
from Repositories.user_repository import UserRepository


class CreateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, user: User) -> User:
        return self.repo.save(user)
