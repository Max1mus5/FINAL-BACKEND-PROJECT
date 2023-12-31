import string
import random
import time
from typing import List
from fastapi import HTTPException
from config.database import Session
from utils.encryption import encrypt_password, decrypt_password
from models.password import Password
from models.user import User
from sqlalchemy import update

class PasswordService:
    def create_password(self, user_id: int, username: str, title: str, URL: str, length: int, min_uppercase: int, min_lowercase: int, min_numbers: int, min_special_chars: int) -> dict:
        passwordSoli = self.generate_password(
            length,
            min_uppercase,
            min_lowercase,
            min_numbers,
            min_special_chars
        )
        hidepass= encrypt_password(passwordSoli)
        db = Session()
        try:
            new_password = Password(username=username, title=title, URL=URL, password=hidepass['encrypted_password'], unlock=hidepass['clave'], user_id=user_id)
            db.add(new_password)
            db.commit()
            db.refresh(new_password)
            db.close()
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
        return {"password": hidepass}, {"message": "Password successfully saved in the database."}
    
    

    def update_password(self, password_id: int, user_id: int, url: str, title: str, length: int, min_uppercase: int, min_lowercase: int, min_numbers: int, min_special_chars: int) -> dict:
        db = Session()
        try:
            password = db.query(Password).filter(Password.id == password_id, Password.user_id == user_id).first()
            user = db.query(User).filter(User.id == user_id).first()

            if password is None:
                raise HTTPException(status_code=404, detail="Password not found")

            if password.user_id != user_id:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            passwordSoli = self.generate_password(
            length,
            min_uppercase,
            min_lowercase,
            min_numbers,
            min_special_chars
                            )
            hidepass= encrypt_password(passwordSoli)

            # Actualiza la contraseña existente
            stmt = (
                update(Password)
                .where(Password.id == password_id)
                .values(title=title, username=user.username, URL=url, password=hidepass['encrypted_password'], unlock=hidepass['clave'])
            )
            db.execute(stmt)
            db.commit()
            db.close()

            return {"password": hidepass}, {"message": "Password successfully updated in the database."}

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        


    def generate_password(self, length: int, min_uppercase: int, min_lowercase: int, min_numbers: int, min_special_chars: int) -> str:
        caracteres = string.ascii_letters + string.digits + string.punctuation
        random.seed(time.time())

        while True:
            password = ''.join(random.choice(caracteres) for _ in range(length))

            if (sum(c.islower() for c in password) >= min_lowercase
                    and sum(c.isupper() for c in password) >= min_uppercase
                    and sum(c.isdigit() for c in password) >= min_numbers
                    and sum(c in string.punctuation for c in password) >= min_special_chars):
                return password
            


    def get_passwords(self, user_id: int) -> List[dict]:
        db = Session()
        try:
            passwords = (db.query(Password).filter(Password.user_id == user_id).all())

            decrypted_passwords = []
            for password in passwords:
                decrypted_password = {
                    "id": password.id,
                    "username": password.username,
                    "title": password.title,
                    "URL": password.URL,
                    "password": decrypt_password(password.password, password.unlock),
                    "user_id": password.user_id,
                }
                decrypted_passwords.append(decrypted_password)

            db.close()
            return decrypted_passwords
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete_password(self, user_id:int, password_id:int):
        db = Session()
        try:
            password = db.query(Password).filter(Password.id == password_id, Password.user_id == user_id).first()
            user = db.query(User).filter(User.id == user_id).first()
            if password is None:
                raise HTTPException(status_code=404, detail="Password not found")
            
            db.delete(password)
            db.commit()
            db.close()

            return {"message": f"Password {password_id} successfully deleted from the {user.username} database."}

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

