from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    fullName: str
    provider: str

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    refreshToken: str

class RefreshTokenRequest(BaseModel):
    refreshToken: str