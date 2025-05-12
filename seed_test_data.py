from app import create_app
from app.models import db, User, Book, Movie, TVShow, Music
from datetime import date

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='admin@example.com').first()

    if not user:
        print("Admin user not found.")
    else:
        db.session.add_all([
            Book(title="The Hobbit", genre="Fantasy", author="J.R.R. Tolkien", media_type="book", user_id=user.id),
            Book(title="Sapiens", genre="Non-Fiction", author="Yuval Noah Harari", media_type="book", user_id=user.id),

            Movie(title="Inception", genre="Sci-Fi", media_type="movie", consumed_date=date(2024, 5, 1), user_id=user.id),
            Movie(title="The Godfather", genre="Drama", media_type="movie", consumed_date=date(2024, 5, 2), user_id=user.id),

            TVShow(title="Breaking Bad", genre="Thriller", media_type="tv_show", consumed_date=date(2024, 4, 20), user_id=user.id),
            TVShow(title="Friends", genre="Comedy", media_type="tv_show", consumed_date=date(2024, 4, 18), user_id=user.id),

            Music(title="Bohemian Rhapsody", genre="Rock", artist="Queen", media_type="music", user_id=user.id),
            Music(title="Blinding Lights", genre="Pop", artist="The Weeknd", media_type="music", user_id=user.id),
        ])
        db.session.commit()
        print("Test media entries added for admin@example.com")
