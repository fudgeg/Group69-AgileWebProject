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
            Book(
                title="The Hobbit",
                media_type="book",
                rating=5,
                comments="A timeless fantasy adventure.",
                consumed_date=date(2024, 3, 10),
                is_favorite=True,
                genre="Fantasy",
                author="J.R.R. Tolkien",
                date_started=date(2024, 3, 1),
                date_finished=date(2024, 3, 10),
                status="finished",
                user_id=user.id
            ),
            Book(
                title="Sapiens",
                media_type="book",
                rating=4,
                comments="Eye-opening take on human history.",
                consumed_date=date(2024, 4, 15),
                is_favorite=False,
                genre="Non-Fiction",
                author="Yuval Noah Harari",
                date_started=date(2024, 4, 1),
                date_finished=date(2024, 4, 15),
                status="finished",
                user_id=user.id
            ),

            Movie(
                title="Inception",
                media_type="movie",
                rating=5,
                comments="Mind-bending masterpiece.",
                consumed_date=date(2024, 5, 1),
                is_favorite=True,
                genre="Sci-Fi",
                watched_date=date(2024, 5, 1),
                user_id=user.id
            ),
            Movie(
                title="The Godfather",
                media_type="movie",
                rating=5,
                comments="A cinematic classic.",
                consumed_date=date(2024, 5, 2),
                is_favorite=True,
                genre="Drama",
                watched_date=date(2024, 5, 2),
                user_id=user.id
            ),

            TVShow(
                title="Breaking Bad",
                media_type="tv_show",
                rating=5,
                comments="Best character development ever.",
                consumed_date=date(2024, 4, 20),
                is_favorite=True,
                genre="Thriller",
                watched_date=date(2024, 4, 20),
                user_id=user.id
            ),
            TVShow(
                title="Friends",
                media_type="tv_show",
                rating=4,
                comments="Fun comfort show.",
                consumed_date=date(2024, 4, 18),
                is_favorite=False,
                genre="Comedy",
                watched_date=date(2024, 4, 18),
                user_id=user.id
            ),

            Music(
                title="Bohemian Rhapsody",
                media_type="music",
                rating=5,
                comments="A rock opera legend.",
                consumed_date=date(2024, 4, 5),
                is_favorite=True,
                genre="Rock",
                artist="Queen",
                listened_date=date(2024, 4, 5),
                user_id=user.id
            ),
            Music(
                title="Blinding Lights",
                media_type="music",
                rating=4,
                comments="80s synth vibe done right.",
                consumed_date=date(2024, 4, 7),
                is_favorite=False,
                genre="Pop",
                artist="The Weeknd",
                listened_date=date(2024, 4, 7),
                user_id=user.id
            ),
        ])
        db.session.commit()
        print("Test media entries added for admin@example.com")
