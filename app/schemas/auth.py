from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
