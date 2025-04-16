from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DECIMAL, TIMESTAMP, CheckConstraint, create_engine
)

from sqlalchemy.orm import relationship, Session, foreign, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import warnings
from sqlalchemy.schema import CreateTable
from datetime import datetime


warnings.filterwarnings("ignore")
Base = declarative_base()

# Модель для таблицы категорий
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


# Настройка подключения
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/postgres")
Session = sessionmaker(bind=engine)
session = Session()


def add_book(title: str, author: str, year: int, quantity: int = 1) -> str:
    existing = session.query(Books).filter_by(title=title, author=author).first()
    if existing:
        return f"Книга '{title}' автора '{author}' уже существует"

    new_book = Books(
        title=title,
        author=author,
        published_year=year,
        quantity=quantity
    )
    session.add(new_book)
    session.commit()
    return f"Книга '{title}' успешно добавлена"


def add_reader(name: str, email: str):
    existing = session.query(Readers).filter_by(email=email).first()
    if existing:
        return f"Такой email '{email}' уже зарегистрирован в базе"

    new_reader = Readers(name=name, email=email)
    session.add(new_reader)
    session.commit()
    return f"Читатель '{name}' успешно зарегистрирован"

def borrow_book():
    pass


def borrow_book(book_id: int, reader_id: int) -> str:
    book = session.get(Books, book_id)
    if not book or book.quantity < 1:
        return "Книги нет в наличии"

    reader = session.get(Readers, reader_id)
    if not reader:
        return "Читатель не найден"

    book.quantity -= 1
    new_borrow = BorrowedBooks(
        book_id=book_id,
        reader_id=reader_id,
        borrowed_date = datetime.now()
    )
    session.add(new_borrow)
    session.commit()
    return f"Книга '{book.title}' выдана читателю {reader.name}"


def return_book(book_id: int, reader_id: str) -> str:
    borrow = session.get(BorrowedBooks, book_id, reader_id)
    if not borrow or borrow.return_date:
        return "Некорректная операция"

    book = session.get(Books, borrow.book_id)
    book.quantity += 1
    borrow.return_date = datetime.now()
    session.commit()
    return f"Книга '{book.title}' возвращена"


def sort_by_year() -> list:
    books = session.query(Books).order_by(Books.published_year).all()
    return [{
        "Название книги": b.title,
        "Автор": b.author,
        "Год издания": b.published_year,
        "Количество": b.quantity
    } for b in books]

def readers_list():

    readers_list = (
        session.query(Readers)
        .join(BorrowedBooks)
        .distinct()
        .all()
    )

    return [{
        "Номер": b.id,
        "ФИО читателя": b.name,
        "Адрес электронной почты": b.email
    } for b in readers_list]


def borrowed_books_list():

    borrows = session.query(BorrowedBooks).filter_by(return_date=None).all()
    result = []
    for b in borrows:
        result.append({
            "Книга": b.books.title,
            "Читатель": b.readers.name,
            "Дата выдачи": b.borrow_date.strftime("%Y-%m-%d %H:%M")
        })
    return result


def search_by_author(author: str):
    books = session.query(Books).filter(Books.author.ilike(f"%{author}%")).all()
    return [{
        "Номер": b.id,
        "Название книги": b.title,
        "Автор": b.author,
        "Год издания": b.published_year,
        "Количество": b.quantity
    } for b in books]

def search_by_name(name: str):
    books = session.query(Books).filter(Books.author.ilike(f"%{name}%")).all()
    return [{
        "Номер": b.id,
        "Название книги": b.title,
        "Автор": b.author,
        "Год издания": b.published_year,
        "Количество": b.quantity
    } for b in books]

def delete_book(id: int):
    book = session.query(Books).get(id)
    if not book:
        return f"Книга с ID {id} не найдена."

    active_borrows = session.query(BorrowedBooks).filter_by(book_id=id, return_date=None).count()
    if active_borrows > 0:
        return "Невозможно удалить книгу: она выдана читателям."

    session.delete(book)
    session.commit()
    return f"Книга '{book.title}' успешно удалена."


def delete_reader(name: int):

    reader = session.query(Readers).get(name)
    if not reader:
        return f"Читатель {name} не найден."


    active_borrows = session.query(BorrowedBooks).filter_by(name=name, return_date=None).count()
    if active_borrows > 0:
        return "Невозможно удалить читателя: у него есть невозвращённые книги."

    # Удаляем читателя
    session.delete(reader)
    session.commit()
    return f"Читатель '{reader.name}' успешно удалён."

def main():
    add_book()
    add_reader()
    borrow_book()
    # return_book()
    # sort_by_year()
    # readers_list()
    # borrowed_books_list()
    # search_by_author()
    # search_by_name()


if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/postgres")

    with engine.connect() as conn:

        conn.execute(CreateTable(Books.__table__))
        conn.execute(CreateTable(Readers.__table__))
        conn.execute(CreateTable(BorrowedBooks.__table__))


        add_book(
            "Фаербол на палочке", "Вадим Кленин", 2024, 1,
            "Волшебник Изумрудного города", "Александр Волков", 2013, 2,
            "Ходячий замок", "Диана Уинн Джонс", 2014, 1,
            "Приключения Незнайки и его друзей", "Николай Носов", 2000, 1,
            "Вафельное сердце", "Мария Парр", 1994, 2,
            "Приключения Тома Сойера", "Марк Твен", 1989, 1,
            "Собачка Соня на даче", "Андрей Усачев", 2000, 2,
            "Летом всякое бывает. Побег из Сколбора", "Сол Тай", 2011, 1,
            "Зверский детектив. Логово Волка", "Анна Старобинец", 2020, 1,
            "Все рассказы", "Николай Носов", 1998, 2,
            "Одиссея капитана Блада", "Рафаэль Сабатини", 2004, 1,
            "Часовой ключ", "Наталья Щерба", 2017, 1
        )

        add_reader(
            "Петров Иван Семенович", "petrov@mail.ru",
            "Кукушкина Инна Ивановна", "kukushka@gmai.com",
            "Стасин Вячеслав Владимирович", "Stas@yahoo.com",
            "Кулешов Андрей Петрович", "kuleshov@mail.ru",
            "Семенова Ольга Игоревна", "semenova@gmai.com"
        )
        conn.commit()
        # cur.close()
        conn.close()
        # print("Подключение закрыто")