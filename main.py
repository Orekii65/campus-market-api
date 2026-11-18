import sqlite3
import hashlib
from fastapi import FastAPI,HTTPException
from datetime import datetime,timezone
from pydantic import BaseModel,Field
DATABASE = "campus_market.db"

app = FastAPI(title="校园二手交易平台 API")

class UserCreate(BaseModel):
    username:str =Field(min_length=3,max_length=30)
    password:str=Field(min_length=6,max_length=50)

def hash_password(password:str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS items(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL ,
                description TEXT ,
                price REAL NOT NULL,
                owner_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'on_sale',
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        buyer_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'created',
        created_at TEXT NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(id),
        FOREIGN KEY (buyer_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.get("/health")
def health():
    return{
        "code":0,
        "message":"ok"
    }
@app.post("/register",status_code=201)
def register(user:UserCreate):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (user.username,)
    )
    existing_user=cursor.fetchone()

    if existing_user is not None:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )

    password_hash=hash_password(user.password)
    created_at=datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO users (username,password_hash,created_at)
        VALUES(?,?,?)
    """,
   (user.username,password_hash,created_at)  
    )

    conn.commit()
    user_id=cursor.lastrowid
    conn.close()

    return{
        "code":0,
        "message":"注册成功",
        "data":{
            "id":user_id,
            "username":user.username
        }
    }
