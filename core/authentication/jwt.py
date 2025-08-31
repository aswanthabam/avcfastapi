# core/auth.py

from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable, Protocol, TypeVar, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt

from ..settings import settings
from ..exception.authentication import ForbiddenException


T = TypeVar("T")


class JWTProvider(Protocol[T]):
    async def validate_token_data(self, token_data: dict) -> T:
        """
        Validates the token payload and maps it to a user model or data structure.
        This is where you would fetch the user from the database.
        """
        ...


class _JWTAuthentication:
    """
    The internal authentication class. It is not meant to be instantiated directly
    from other parts of the application. Note the leading underscore.
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.optional_oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl="token", auto_error=False
        )
        self.provider: Optional[JWTProvider[T]] = None

    def register_provider(self, provider: JWTProvider[T]):
        """Registers the provider that validates token data (e.g., fetches a user)."""
        if self.provider is not None:
            print("Warning: JWTProvider is already registered. Overwriting.")
        self.provider = provider

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def verify_access_token(self, token: str) -> T:
        if self.provider is None:
            raise RuntimeError(
                "A JWTProvider has not been registered. "
                "Call 'register_provider' during application startup."
            )

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.InvalidTokenError as e:
            raise ForbiddenException(detail="Invalid or expired token") from e

        return await self.provider.validate_token_data(payload)

    def get_auth_dependency(
        self, required: bool = True
    ) -> Callable[..., Awaitable[Optional[T]]]:
        """
        Returns a FastAPI dependency that enforces authentication.
        - If required=True, it will raise an exception for invalid/missing tokens.
        - If required=False, it will return None for invalid/missing tokens.
        """
        scheme = self.oauth2_scheme if required else self.optional_oauth2_scheme

        async def dependency(token: Optional[str] = Depends(scheme)) -> Optional[T]:
            if token is None:
                # This branch is mainly for the optional case, as the required
                # scheme would have already raised an error.
                return None

            try:
                return await self.verify_access_token(token)
            except ForbiddenException as e:
                if required:
                    raise e
                return None

        return dependency


# --- FACTORY CREATION ---
_jwt_auth_instance = _JWTAuthentication()


def register_provider(provider: JWTProvider[Any]) -> None:
    """Call this function once at application startup to set the user provider."""
    _jwt_auth_instance.register_provider(provider)


create_access_token = _jwt_auth_instance.create_access_token
get_password_hash = _jwt_auth_instance.get_password_hash
verify_password = _jwt_auth_instance.verify_password

require_auth: Callable[..., Awaitable[Any]] = _jwt_auth_instance.get_auth_dependency(
    required=True
)
optional_auth: Callable[..., Awaitable[Optional[Any]]] = (
    _jwt_auth_instance.get_auth_dependency(required=False)
)
