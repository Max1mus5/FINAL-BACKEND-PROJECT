from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class userS(BaseModel):
  username: str
  email: str
  password:str
