from typing import Optional, Literal
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: Optional[str]
    name: Optional[str]
    phoneNumber: Optional[str]
    role: Literal["admin", "staff", "factory-manager"]

    def to_payload(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "phoneNumber": self.phoneNumber,
            "role": self.role
        }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
