from fastapi import Request

class NotAuthenticated(Exception):
    pass

def require_session(request: Request) -> None:
    if not request.session.get("authenticated"):
        raise NotAuthenticated()
