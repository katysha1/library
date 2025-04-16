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

    borrow_book = relationship("BorrowedBooks", back_populates="book")

    def __repr__(self):
        return f"<Books(id={self.id}, title={self.title}, author={self.author} published_year={self.published_year}, quantity={self.quantity})>"

class Readers(Base):
    __tablename__ = 'readers'

    id = Column(Integer, primary_key=True, comment = "Номер")
    name = Column(String(100), nullable=False, comment = "ФИО читателя")
    email = Column(String(100), nullable=False, unique=True, comment = "емейл")

    borrow_records = relationship("BorrowedBooks", back_populates="reader")

    def __repr__(self):
        return f"<Readers(id={self.id}, name={self.name}, email={self.email})>"

class BorrowedBooks(Base):
    __tablename__ = 'borrowedbooks'

    id = Column(Integer, primary_key=True, comment = "Номер")
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False, comment = "Номер книги в каталоге")
    reader_id = Column(Integer, ForeignKey('readers.id'), nullable=False, comment = "Код читателя")
    borrow_date = Column(TIMESTAMP, default=datetime.now, nullable=False, comment = "Дата выдачи книги")
    return_date = Column(TIMESTAMP, nullable=True, comment = "Дата возврата книги")

    book = relationship("Books", back_populates="borrow_book")
    reader = relationship("Readers", back_populates="borrow_records")

    def __repr__(self):
        return f"<Readers(id={self.id}, book_id={self.book_id}, reader_id={self.reader_id}, borrow_date={self.borrow_date}, return_date={self.return_date})>"


# Настройка подключения
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/postgres")
Session = sessionmaker(bind=engine)
session = Session()


def add_book(title: str, author: str, year: int, quantity: int = 1) -> str:
    existing = session.query(Books).filter_by(title=title, author=author).first()
    if existing:
        print(f"Книга '{title}' автора '{author}' уже существует")
        return

    new_book = Books(
        title=title,
        author=author,
        published_year=year,
        quantity=quantity
    )
    session.add(new_book)
    session.commit()
    print(f"Книга '{title}' автора '{author}' успешно добавлена")
    return


def add_reader(name: str, email: str):
    existing = session.query(Readers).filter_by(email=email).first()
    if existing:
        print(f"Такой email '{email}' уже зарегистрирован в базе")
        return

    new_reader = Readers(name=name, email=email)
    session.add(new_reader)
    session.commit()
    print(f"Читатель '{name}' успешно зарегистрирован")
    return


def borrow_book(book_id: int, reader_id: int) -> str:
    book = session.get(Books, book_id)
    if not book or book.quantity < 1:
        print("Книги нет в наличии")
        return

    reader = session.get(Readers, reader_id)
    if not reader:
        print("Читатель не найден")
        return

    book.quantity -= 1
    new_borrow = BorrowedBooks(
        book_id=book_id,
        reader_id=reader_id,
        borrow_date = datetime.now(),
        return_date = None
    )
    session.add(new_borrow)
    session.commit()
    print(f"Книга '{book.title}' выдана читателю {reader.name}")
    return


def return_book(reader_id: int, book_id: int) -> str:
    borrow = (
        session.query(BorrowedBooks)
        .filter_by(reader_id=reader_id, book_id=book_id, return_date=None)
        .first()
    )
    if not borrow:
        print("Нет такой выданной книги или книга уже возвращена.")
        return

    book = session.get(Books, book_id)
    if not book:
        print("Книга не найдена в библиотеке.")
        return

    try:
        book.quantity += 1
        borrow.return_date = datetime.now()
        session.commit()
        print(f"Книга '{book.title}' успешно возвращена.")
        return

    except Exception as e:
        session.rollback()
        return f"Ошибка при возврате: {str(e)}"



def sort_by_year() -> list:
    books = session.query(Books).order_by(Books.published_year).all()
    for b in books:
        print(
            f"Название книги: {b.title}, Автор: {b.author}, Год издания: {b.published_year}, Количество: {b.quantity}")
    return

def readers_list():

    reader_list = (
        session.query(Readers)
        .join(BorrowedBooks)
        .distinct()
        .all()
    )

    for b in reader_list:
        print(f"Номер: {b.id}, ФИО читателя: {b.name}, Адрес электронной почты: {b.email}")
    return

def borrowed_books_list():

    borrows =(
        session.query(BorrowedBooks)
        .join(BorrowedBooks.book)
        .join(BorrowedBooks.reader)
        .all()
    )

    for b in borrows:
        print(f"Книга:{b.book.id}-{b.book.title},Читатель: {b.reader.id}-{b.reader.name}, Дата выдачи: {b.borrow_date}")

    return


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
        print(f"Книга с ID {id} не найдена")
        return

    active_borrows = session.query(BorrowedBooks).filter_by(book_id=id, return_date=None).count()
    if active_borrows > 0:
        print("Невозможно удалить книгу: она выдана читателям.")
        return

    session.delete(book)
    session.commit()
    print(f"Книга '{book.title}' успешно удалена.")
    return


def delete_reader(name: int):

    reader = session.query(Readers).get(name)
    if not reader:
        print(f"Читатель {name} не найден.")
        return


    active_borrows = session.query(BorrowedBooks).filter_by(name=name, return_date=None).count()
    if active_borrows > 0:
        print(f"Невозможно удалить читателя: у него есть невозвращённые книги.")
        return

    # Удаляем читателя
    session.delete(reader)
    session.commit()
    print(f"Читатель '{reader.name}' успешно удалён.")
    return

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/postgres")

    with engine.connect() as conn:

        # conn.execute(CreateTable(Books.__table__))
        # conn.execute(CreateTable(Readers.__table__))
        # conn.execute(CreateTable(BorrowedBooks.__table__))


        # add_book("Фаербол на палочке", "Вадим Кленин", 2024, 1)
        # add_book("Волшебник Изумрудного города", "Александр Волков", 2013, 2)
        # add_book("Ходячий замок", "Диана Уинн Джонс", 2014, 2)
        # add_book("Приключения Незнайки и его друзей", "Николай Носов", 2000, 1)
        # add_book("Вафельное сердце", "Мария Парр", 1994, 1)
        # add_book("Приключения Тома Сойера", "Марк Твен", 1989, 1)
        # add_book("Собачка Соня на даче", "Андрей Усачев", 2000, 1)
        # add_book("Летом всякое бывает. Побег из Сколбора", "Сол Тай", 2011, 2)
        # add_book("Зверский детектив. Логово Волка", "Анна Старобинец", 2020, 1)
        # add_book("Все рассказы", "Николай Носов", 1998, 1)
        # add_book("Одиссея капитана Блада", "Рафаэль Сабатини", 2004, 3)
        # add_book("Часовой ключ", "Наталья Щерба", 2017, 1)

        # add_reader("Петров Иван Семенович", "petrov@mail.ru")
        # add_reader("Кукушкина Инна Ивановна", "kukushka@gmai.com")
        # add_reader("Стасин Вячеслав Владимирович", "stas@yahoo.com")
        # add_reader("Кулешов Андрей Петрович", "kuleshov@mail.ru")
        # add_reader("Семенова Ольга Игоревна", "semenova@gmai.com")

        # add_book("Летом всякое бывает. Побег из Сколбора", "Сол Тай", 2011, 2)
        # add_reader("Петрова Наталья Ивановна", "petrov@mail.ru")
        # borrow_book(4, 3)
        # borrow_book(8, 2)
        # borrow_book(11, 2)
        # borrow_book(2, 5)
        # borrow_book(12, 4)
        # borrow_book(10, 4)

        # sort_by_year()
        # readers_list()

        # borrowed_books_list()

        # return_book(12, 4)
        return_book(8, 2)
        # return_book(2, 5)

        conn.commit()
        # cur.close()
        conn.close()
        print("Подключение закрыто")
