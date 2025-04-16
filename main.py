import psycopg2
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    print("Подключение к Базе данных успешно выполнено")
    cur = conn.cursor()

except Exception as e:
    print("Ошибка при подключении к базе данных")

def add_book():
    # try:
    #     cur.execute(
    #         """
    #         INSERT INTO categories (name)
    #         VALUES (%s)
    #         """,
    #         (name,)
    #     )
    #     conn.commit()
    #     print(f"Категория '{name}' успешно добавлена.")
    # except Exception as e:
    #     conn.rollback()
    #     print(f"Ошибка при добавлении категории: {e}")
    
    pass



def add_reader():
    pass

def give_book():
    pass

def return_book():
    pass

def list_of_books():
    pass

def list_of_readers():
    pass

def list_of_books_away():
    pass

def sort_by_year():
    pass

def search_by_author():
    pass

def search_by_name():
    pass

def main():
    add_book()
    add_reader()
    give_book()
    return_book()
    list_of_books()
    list_of_readers()
    list_of_books_away()
    search_by_author()
    search_by_name()


if __name__ == "__main__":
    main()

cur.close()
conn.close()
print("Подключение закрыто")

