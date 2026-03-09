import psycopg2
from time import sleep

def init_db():
    while True:
        try:
            conn = psycopg2.connect(
                host='db',
                database='pendapatan-daerah',
                user='miko',
                password='miko123',
                port='5432'
            )
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