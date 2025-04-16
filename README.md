# library
### Домашнее задание по теме Работа с postgresql, ч.3

Необходимо разработать систему учета книг в библиотеке, которая позволяет добавлять новые книги, 
регистрировать читателей и отслеживать выдачу книг. В системе должны быть реализованы следующие функции:

- Создание базы данных и таблиц:
- Таблица для хранения книг (Books):
- id (INTEGER, PRIMARY KEY)
- title (VARCHAR(100), NOT NULL)
- author (VARCHAR(50), NOT NULL)
- published_year (INTEGER)
- quantity (INTEGER, NOT NULL, CHECK (quantity >= 0))
![img_5.png](img_5.png)

- Таблица для хранения читателей (Readers):
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR(100), NOT NULL)
- email (VARCHAR(100), UNIQUE)
![img_7.png](img_7.png)

Таблица для регистрации выдачи книг (BorrowedBooks):
- id (INTEGER, PRIMARY KEY)
- book_id (INTEGER, FOREIGN KEY ссылается на Books.id)
- reader_id (INTEGER, FOREIGN KEY ссылается на Readers.id)
- borrow_date (TIMESTAMP, дата выдачи книги)
- return_date (TIMESTAMP, дата возврата книги, может быть NULL)

![img_6.png](img_6.png)

## Код на создание таблиц и подключения к базе данных с помощью engine в файле tables
"""
    from sqlalchemy import (
        Column, Integer, String, Text, ForeignKey, DECIMAL, TIMESTAMP, CheckConstraint, create_engine
    )
    
    from sqlalchemy.orm import relationship, Session, foreign
    from sqlalchemy.ext.declarative import declarative_base
    import warnings
    from sqlalchemy.schema import CreateTable
    from datetime import datetime
    
    warnings.filterwarnings("ignore")
    Base = declarative_base()
    class Books(Base):
        __tablename__ = 'books'

        id = Column(Integer, primary_key=True, comment = "Номер")
        title = Column(String(100), nullable=False, comment = "Название книги")
        author = Column(String(50), nullable=False, comment = "Автор")
        published_year = Column(Integer, nullable=False, comment = "Год издания")
        quantity = Column(Integer, comment="Количество книг в наличии")
    
        borrow_book = relationship("BorrowedBook", back_populates="book")

        def __repr__(self):
            return f"<Books(id={self.id}, title={self.title}, author={self.author} published_year={self.published_year}, quantity={self.quantity})>"

    class Readers(Base):
        __tablename__ = 'readers'

        id = Column(Integer, primary_key=True, comment = "Номер")
        name = Column(String(100), nullable=False, comment = "ФИО читателя")
        email = Column(String(100), nullable=False, unique=True, comment = "емейл")
    
        borrow_records = relationship("BorrowedBook", back_populates="reader")
    
        def __repr__(self):
            return f"<Readers(id={self.id}, name={self.name}, email={self.email})>"

    class BorrowedBooks(Base):
        __tablename__ = 'borrowedbooks'

        id = Column(Integer, primary_key=True, comment = "Номер")
        book_id = Column(Integer, ForeignKey('books.id'), nullable=False, comment = "Номер книги в каталоге")
        reader_id = Column(Integer, ForeignKey('readers.id'), nullable=False, comment = "Код читателя")
        borrow_date = Column(TIMESTAMP, default=datetime.now, nullable=False, comment = "Дата выдачи книги")
        return_date = Column(TIMESTAMP, default=datetime.now, nullable=True, comment = "Дата возврата книги")
    
        book = relationship("Book", back_populates="borrow_book")
        reader = relationship("Reader", back_populates="borrow_records")
    
        def __repr__(self):
            return f"<Readers(id={self.id}, book_id={self.book_id}, reader_id={self.reader_id}, borrow_date={self.borrow_date}, return_date={self.return_date})>"

    if __name__ == "__main__":
        engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/postgres")

    with engine.connect() as conn:
        print("connected")
        conn.execute(CreateTable(Books.__table__))
        conn.execute(CreateTable(Readers.__table__))
        conn.execute(CreateTable(BorrowedBooks.__table__))

        conn.commit()
"""

Использование Alembic для создания миграций(необязательно):
![img_3.png](img_3.png)
![img_4.png](img_4.png)

Создайте миграции для создания таблиц Books, Readers и BorrowedBooks.
Примените миграции к базе данных.

## Реализация основных функций в Python:

Добавление новой книги в базу данных. Должны проверяться уникальность заголовка и автора.
![img.png](img.png)
![img_2.png](img_2.png)

Регистрация нового читателя. Должна проверяться уникальность email.
![img_1.png](img_1.png)
![img_8.png](img_8.png)

Выдача книги. Проверяйте, что книга доступна (количество больше нуля) и обновляйте количество при выдаче.
![img_9.png](img_9.png)
![img_10.png](img_10.png)
![img_13.png](img_13.png)

Возврат книги. Обновляйте количество книг при возврате и устанавливайте дату возврата.
![img_17.png](img_17.png)
![img_18.png](img_18.png)
PS У меня так и не получилось понять почему не находятся книги из списка выданных, если делаю запрос списка выданных книг, там они есть, но почему-то обратно не возвращаются


Запрос списка всех книг, отсортированных по году выпуска.
![img_11.png](img_11.png)

Запрос всех читателей, которые брали хотя бы одну книгу.
![img_12.png](img_12.png)
![img_14.png](img_14.png)


Запрос списка книг, которые сейчас находятся у читателей (еще не возвращены).
![img_15.png](img_15.png)
![img_16.png](img_16.png)


## Дополнительные задачи:

Добавьте возможность поиска книг по автору или названию.
![img_19.png](img_19.png)
![img_20.png](img_20.png)

поиск книги по автору, которой нет в базе данных
![img_21.png](img_21.png)
![img_22.png](img_22.png)

поиск книги по названию
![img_23.png](img_23.png)
поиск книга по названию, отсутствующей в базе
![img_24.png](img_24.png)
Реализуйте функции для удаления книг и читателей из базы данных (при этом удаление книги должно быть возможно только, если она не выдана читателям).
-удаление книги
![img_25.png](img_25.png)
список книг до удаления
![img_26.png](img_26.png)
список книг после удаления
![img_27.png](img_27.png)
попытка удалить книгу, которая выдана читателю
![img_28.png](img_28.png)

-удаление читателя
с выданными книгами ![img_29.png](img_29.png) ![img_30.png](img_30.png)
без выданных книг ![img_31.png](img_31.png) 
до удаления ![img_32.png](img_32.png)
после удаления ![img_33.png](img_33.png)

### Создайте тесты для проверки правильности работы всех функций.
-В программе курса не было тем как делать тесты проверки функций. На одной из консультаций Руслан показывал тесты, но я все равно не поняла как их делать.

