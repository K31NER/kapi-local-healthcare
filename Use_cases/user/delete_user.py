from Repositories.user_repository import UserRepository


class DeleteUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self) -> None:
        self.repo.delete()
