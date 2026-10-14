from pathlib import Path

import libsql
import pytest

from constants import (
    AUTHOR_BOOKS_TABLE_NAME,
    AUTHOR_TABLE_NAME,
    BOOK_DATE_READ_COLUMN_NAME,
    BOOK_ID_COLUMN_NAME,
    BOOK_REVIEW_COLUMN_NAME,
    BOOK_TABLE_NAME,
)
from sql_files.sql_commands import (
    add_book_manually,
    add_column_to_table,
    add_read_date_to_book,
    filter_data_by_book_name_and_author,
    remove_book_data_from_table,
    update_data_in_table,
)
from sql_files.write_to_sql import (
    push_author_data,
    push_authors_books_data,
    push_book_data,
)

SCHEMA_PATH = Path(__file__).parent.parent / "schema.sql"


@pytest.fixture
def db_connection():
    connection = libsql.connect(":memory:")
    schema_sql = SCHEMA_PATH.read_text()
    connection.executescript(schema_sql)
    yield connection
    connection.close()


def test_add_book_manually(db_connection, monkeypatch):
    data_books = [
        (1, "Patriot Games", "9780425134351", "1992-05-01", "BOOK", "NULL", "Fiction", "Write a review")
    ]
    data_authors = [(1, "Tom Clancy")]
    data_authors_books = [(1, 1)]

    inputs = iter([
        "Patriot Games",
        "Tom Clancy",
        "9780425134351",
        "1992-05-01",
        "BOOK",
        "NULL",
        "Fiction",
        "Write a review"
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    cursor = db_connection.cursor()
    add_book_manually(db_connection)
    cursor.execute(f"SELECT * FROM {BOOK_TABLE_NAME}")
    book_result = cursor.fetchall()
    cursor.execute(f"SELECT * FROM {AUTHOR_TABLE_NAME}")
    author_result = cursor.fetchall()
    cursor.execute(f"SELECT * FROM {AUTHOR_BOOKS_TABLE_NAME}")
    author_books_result = cursor.fetchall()
    assert book_result == data_books
    assert author_result == data_authors
    assert author_books_result == data_authors_books


def test_add_book_manually_multiple_authors(db_connection, monkeypatch):
    data_books = [
        (1, "Patriot Games", "9780425134351", "1992-05-01", "BOOK", "NULL", "Fiction", "Write a review")
    ]
    data_authors = [(1, "Tom Clancy"), (2, "Sam Fisher")]
    data_authors_books = [(1, 1), (2, 1)]

    inputs = iter([
            "Patriot Games",
            "Tom Clancy, Sam Fisher",
            "9780425134351",
            "1992-05-01",
            "BOOK",
            "NULL",
            "Fiction",
            "Write a review"
        ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    cursor = db_connection.cursor()
    add_book_manually(db_connection)
    cursor.execute(f"SELECT * FROM {BOOK_TABLE_NAME}")
    book_result = cursor.fetchall()
    cursor.execute(f"SELECT * FROM {AUTHOR_TABLE_NAME}")
    author_result = cursor.fetchall()
    cursor.execute(f"SELECT * FROM {AUTHOR_BOOKS_TABLE_NAME}")
    author_books_result = cursor.fetchall()
    assert book_result == data_books
    assert author_result == data_authors
    assert author_books_result == data_authors_books


def test_add_read_date_to_book(db_connection, monkeypatch):
    data = ["2002-05-01"]
    add_book_data_helper(db_connection)
    cursor = db_connection.cursor()

    inputs = iter(["2002-05-01", "I", "9780552150736"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    add_read_date_to_book(db_connection)
    cursor.execute(f"SELECT {BOOK_DATE_READ_COLUMN_NAME} FROM {BOOK_TABLE_NAME}")
    result = cursor.fetchone()
    assert result[0] == data[0]


def test_add_column_to_table(db_connection):
    add_book_data_helper(db_connection)
    cursor = db_connection.cursor()
    new_table = ["Rating"]
    add_column_to_table(new_table[0], db_connection)
    cursor.execute("SELECT name FROM pragma_table_info('books') WHERE name = 'Rating'")
    result = cursor.fetchone()
    assert result[0] == new_table[0]


def test_update_data_in_table(db_connection):
    add_book_data_helper(db_connection)
    cursor = db_connection.cursor()
    new_data = "Loved this book!"
    book_id = 1
    update_data_in_table(
        BOOK_TABLE_NAME,
        BOOK_REVIEW_COLUMN_NAME,
        new_data,
        BOOK_ID_COLUMN_NAME,
        book_id,
        db_connection,
    )
    sql = f"""SELECT {BOOK_REVIEW_COLUMN_NAME} FROM {BOOK_TABLE_NAME} WHERE {BOOK_ID_COLUMN_NAME} = ?
    """
    cursor.execute(sql, (1,))
    result = cursor.fetchone()
    print(result)
    assert result[0] == new_data


def test_remove_data_from_table(db_connection, monkeypatch):
    add_book_data_helper(db_connection)
    cursor = db_connection.cursor()
    data_to_remove = ["Angels and Demons"]

    monkeypatch.setattr("builtins.input", lambda _: "Y")

    remove_book_data_from_table(
        data_to_remove[0], db_connection
    )
    result = cursor.fetchone()
    assert result == None


def test_filter_data(db_connection):
    add_book_data_helper(db_connection)
    data = ("Angels and Demons", "Dan Brown")
    filtered_data = filter_data_by_book_name_and_author(db_connection)
    assert filtered_data[0] == data


def add_book_data_helper(db_connection):
    book_name, author, publication_year, format, categories = "Angels and Demons", ["Dan Brown"], "2001", "BOOK", "Fiction"
    push_author_data(author, db_connection)
    push_book_data(
        book_name,
        "9780552150736",
        publication_year,
        format,
        "NULL",
        categories,
        "Write a review",
        db_connection,
    )
    push_authors_books_data(author, "9780552150736", db_connection)
