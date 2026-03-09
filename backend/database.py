import os

import psycopg2
from time import sleep

host='db'
database=os.getenv("DB_NAME")
user=os.getenv("DB_USER")
password=os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{database}"

def init_db():
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur= conn.cursor()
            cur.execute("""
                create table if not exists users (
                    id serial primary key,
                    username varchar(50) unique not null,
                    password varchar(50) not null
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("Success initialize table")
            break
        except Exception as e:
            print(f"Failed creating database, try to create again... {e}")
            sleep(2)