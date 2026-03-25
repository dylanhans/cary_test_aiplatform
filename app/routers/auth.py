# app/routers/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Test accounts — in production these come from Azure AD
TEST_ACCOUNTS = {
    "nicole@carycompany.com": {
        "password": "test1234",
        "name": "Nicole Cosentino",
        "department": "HR",
        "role": "Recruiting Coordinator"
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    name: str
    department: str
    role: str
    email: str

@router.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    account = TEST_ACCOUNTS.get(request.email.lower())
    
    if not account or account["password"] != request.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    return LoginResponse(
        success=True,
        name=account["name"],
        department=account["department"],
        role=account["role"],
        email=request.email
    )