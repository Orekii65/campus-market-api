import sqlite3

from fastapi import FastAPI


DATABASE = "campus_market.db"

app = FastAPI(title="校园二手交易平台 API")


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
                owner_id INGEGER NOT NULL,
                status TEXT NOT NULL DEFAULT "on_sale",
                created_at TEXT NOT NULL,
                FOREIGN KEY (owner_id)REFERENCES users(id)
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