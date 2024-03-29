import re
from utils.encryption import user_password
from config.database import Session
from models.user import User
from fastapi import HTTPException,Depends
from middlewares.auth_middleware import JWTBearer

def is_valid_email(email: str) -> bool:
    email_regex = r'^[\w\.-]+@(gmail|hotmail)\.(com|org|net|gov|edu|info|biz|io|co|tv|[a-zA-Z]{2,3})$'
    return bool(re.match(email_regex, email))

def is_valid_password(password: str) -> bool:
    return len(password) >= 8

def is_valid_username(username: str) -> bool:
    return len(username) >= 3

def validate_identity(username: str, password: str) -> bool:
   db = Session()
   user = db.query(User).filter(User.username == username).first()
   db.close()
   
   if not user:
       return False
   
   if len(password) >= 60 :
       return user.password == password
   else:
       encrypted_password = user_password(password)
       return encrypted_password == user.password


    

async def get_current_user(user: User = Depends(JWTBearer())):
    return user

