
from app.models import Book

# This test function checks if the Book model is created correctly.
def test_book_repr():
    book = Book(title="1984", author="George Orwell")
    assert "1984" in repr(book)
    assert "George Orwell" in repr(book)
