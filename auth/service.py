from datetime import (
    datetime,
    timedelta,
)
from sqlalchemy.future import select
from jose import jwt, JWTError
from passlib.hash import bcrypt
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from auth import schemas, models
from db import get_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign-in')


def get_current_user(token: str = Depends(oauth2_scheme)) -> schemas.User:
    return AuthService.validate_token(token)


class AuthService:
    SECRET_KEY = 'secret'

    @classmethod
    def verify_password(cls, plain_password, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def validate_token(cls, token: str) -> str:
        exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='COULD not validate credentials',
            headers={
                'WWW-Authenticate': 'Bearer'
            },
        )
        try:
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=['HS256',]
            )
        except JWTError:
            raise exception from None

        user_data = payload.get('user')
        try:
            user = schemas.User.parse_obj(user_data)
        except ValidationError:
            raise exception from None

        return user

    @classmethod
    async def create_token(cls, user: models.User) -> schemas.Token:
        user_data = schemas.User.from_orm(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=3600),
            'sub': str(user_data.id),
            'user': user_data.dict(),
        }
        token = jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm='HS256'
        )
        return schemas.Token(access_token=token)

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def register_new_user(self, user_data: schemas.UserCreate, auth_user: schemas.BaseUser) -> schemas.Token:
        exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='This feature is only available to administrators',
            headers={
                'WWW-Authenticate': 'Bearer'
            },
        )
        query = select(models.User).where(models.User.username == auth_user.username)
        result = await self.session.execute(query)
        auth_user_in_table = result.scalars().first()
        if auth_user_in_table and auth_user_in_table.role != models.Roles.administrator:
            raise exception
        user = models.User(
            email=user_data.email,
            username=user_data.username,
            password_hash=self.hash_password(user_data.password),
        )

        self.session.add(user)
        await self.session.commit()
        return await self.create_token(user)

    async def authenticate_user(self, username: str, password: str) -> schemas.Token:
        exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Incorrect username or password',
            headers={
                'WWW-Authenticate': 'Bearer'
            },
        )
        query = select(models.User).where(models.User.username == username)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if not user:
            raise exception
        if not self.verify_password(password, user.password_hash):
            raise exception
        return await self.create_token(user)
