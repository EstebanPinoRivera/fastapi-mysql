#uvicorn app:app --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pymysql.cursors
import bcrypt

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='mypassword',
    database='user_db',
    cursorclass=pymysql.cursors.DictCursor
)

class User(BaseModel):
    name: str
    email: str
    password: str


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

app = FastAPI()

#create
@app.post("/users/")
async def create_user(user: User):
    hashed_password = hash_password(user.password)
    with connection.cursor() as cursor:
        sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user.name, user.email, hashed_password))
        connection.commit()
        return {"message": "User created successfully"}

#get all
@app.get("/users/")
async def get_users():
    with connection.cursor() as cursor:
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        users = cursor.fetchall()
        return users

#get
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()
        if user:
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")

#update
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    with connection.cursor() as cursor:
        sql = "UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s"
        cursor.execute(sql, (user.name, user.email, user.password, user_id))
        connection.commit()
        return {"message": "User updated successfully"}

#delete
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    with connection.cursor() as cursor:
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        connection.commit()
        return {"message": "User deleted successfully"}
