from fastapi import APIRouter, Depends, HTTPException
from Domain.user import User
from API.schemas.user import UserCreate, UserRead, UserUpdate
from API.depends import get_create_user, get_get_user, get_update_user, get_delete_user
from Use_cases.user.create_user import CreateUser
from Use_cases.user.get_user import GetUser
from Use_cases.user.update_user import UpdateUser
from Use_cases.user.delete_user import DeleteUser

router = APIRouter(prefix="/user", tags=["user"])


def _to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        full_name=user.full_name,
        birth_date=user.birth_date,
        gender=user.gender,
        blood_type=user.blood_type,
        allergies=user.allergies,
        chronic_conditions=user.chronic_conditions,
        emergency_contact_name=user.emergency_contact_name,
        emergency_contact_phone=user.emergency_contact_phone,
    )


@router.post("", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, uc: CreateUser = Depends(get_create_user)):
    try:
        result = uc.execute(User(
            full_name=data.full_name,
            birth_date=data.birth_date,
            gender=data.gender,
            blood_type=data.blood_type,
            allergies=data.allergies,
            chronic_conditions=data.chronic_conditions,
            emergency_contact_name=data.emergency_contact_name,
            emergency_contact_phone=data.emergency_contact_phone,
        ))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return _to_read(result)


@router.get("", response_model=UserRead)
def get_user(uc: GetUser = Depends(get_get_user)):
    result = uc.execute()
    if not result:
        raise HTTPException(status_code=404, detail="No hay perfil de usuario registrado")
    return _to_read(result)


@router.put("", response_model=UserRead)
def update_user(
    data: UserUpdate,
    get_uc: GetUser = Depends(get_get_user),
    update_uc: UpdateUser = Depends(get_update_user),
):
    existing = get_uc.execute()
    if not existing:
        raise HTTPException(status_code=404, detail="No hay perfil de usuario registrado")
    changes = data.model_dump(exclude_none=True)
    for key, value in changes.items():
        setattr(existing, key, value)
    result = update_uc.execute(existing)
    return _to_read(result)


@router.delete("", status_code=204)
def delete_user(uc: DeleteUser = Depends(get_delete_user)):
    uc.execute()
