from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "your-super-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models import User
from . import schemas, utils, jwt

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.UserRead)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_data.email,
        hashed_password=utils.hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from auth.jwt import decode_token
from sqlalchemy.orm import Session
from models import User
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        user = db.query(User).get(int(user_id))
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {"user_id": user.id}
