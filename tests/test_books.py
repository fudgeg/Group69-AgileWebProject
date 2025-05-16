
from app.models import Book

# Test the Book model
def test_book_repr():
    book = Book(title="1984", author="George Orwell")
    assert "1984" in repr(book)
    assert "George Orwell" in repr(book)
