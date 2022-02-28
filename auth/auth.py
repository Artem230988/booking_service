from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth import schemas
from .service import AuthService, get_current_user
from .schemas import BaseUser
router = APIRouter(prefix='/auth',)


@router.post('/create_manager', response_model=schemas.Token)
async def sign_up(user_data: schemas.UserCreate,
                  service: AuthService = Depends(),
                  user: BaseUser = Depends(get_current_user)):
    return await service.register_new_user(user_data, user)


@router.post('/sign-in', response_model=schemas.Token)
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends()):
    return await service.authenticate_user(
        form_data.username,
        form_data.password,
    )


@router.get('/user', response_model=schemas.User)
async def get_user(user: schemas.User = Depends(get_current_user)):
    return user
