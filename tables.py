from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DECIMAL, TIMESTAMP, CheckConstraint, create_engine
)

from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
import warnings
from sqlalchemy.schema import CreateTable


warnings.filterwarnings("ignore")
Base = declarative_base()

# # Модель для таблицы категорий
class Books(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, comment = "Номер")
    title = Column(String(100), nullable=False, unique=True, comment = "Название книги")
    author = Column(String(50), nullable=False, unique=True, comment = "Автор")
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
    book_id = Column(Integer, primary_key=True, comment = "Номер")
    name = Column(String(100), nullable=False, comment = "ФИО читателя")
    email = Column(String(100), nullable=False, unique=True, comment = "емейл")

    book = relationship("Book", back_populates="borrow_book")
    reader = relationship("Reader", back_populates="borrow_records")

    def __repr__(self):
        return f"<Readers(id={self.id}, name={self.name}, email={self.email})>"

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/postgres")

    with engine.connect() as conn:
        print("connected")
        conn.execute(CreateTable(Books.__table__))
        conn.execute(CreateTable(Readers.__table__))
        conn.execute(CreateTable(BorrowedBooks.__table__))

        conn.commit()