
from app import create_app
from app.models import db, User, Book, Movie, TVShow, Music
from datetime import date

# This script seeds the database with static test data for development and testing purposes.
app = create_app()

def create_user(name, email, password="test123"):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created user: {name} ({email})")
    return user

def add_friend(user_a, user_b):
    if user_b not in user_a.friends:
        user_a.friends.append(user_b)
        user_b.friends.append(user_a)
        db.session.commit()
        print(f"🤝 {user_a.name} and {user_b.name} are now friends")

def seed_static_media():
    db.drop_all()
    db.create_all()

    alice = create_user("Alice", "alice@example.com")
    bob = create_user("Bob", "bob@example.com")
    charlie = create_user("Charlie", "charlie@example.com")

    # Alice's entries
    db.session.add_all([
        Book(title="Dune", genre="Sci-Fi", author="Frank Herbert", date_started=date(2024, 1, 10), date_finished=date(2024, 2, 5), status="completed", media_type="book", user_id=alice.id),
        Movie(title="Interstellar", genre="Sci-Fi", watched_date=date(2024, 3, 15), media_type="movie", user_id=alice.id),
        TVShow(title="Stranger Things", genre="Sci-Fi", watched_date=date(2024, 4, 1), media_type="tv_show", user_id=alice.id),
        Music(title="Starlight", genre="Sci-Fi", artist="Muse", listened_date=date(2024, 5, 1), media_type="music", user_id=alice.id),
    ])

    # Bob's entries
    db.session.add_all([
        Book(title="Catch-22", genre="Satire", author="Joseph Heller", date_started=date(2024, 2, 1), date_finished=date(2024, 3, 1), status="completed", media_type="book", user_id=bob.id),
        Movie(title="The Truman Show", genre="Comedy", watched_date=date(2024, 4, 10), media_type="movie", user_id=bob.id),
        TVShow(title="Brooklyn Nine-Nine", genre="Comedy", watched_date=date(2024, 4, 20), media_type="tv_show", user_id=bob.id),
        Music(title="Happy", genre="Pop", artist="Pharrell Williams", listened_date=date(2024, 5, 5), media_type="music", user_id=bob.id),
    ])

    # Charlie's entries
    db.session.add_all([
        Book(title="Educated", genre="Memoir", author="Tara Westover", date_started=date(2024, 1, 15), date_finished=date(2024, 2, 20), status="completed", media_type="book", user_id=charlie.id),
        Movie(title="The Pursuit of Happyness", genre="Drama", watched_date=date(2024, 3, 25), media_type="movie", user_id=charlie.id),
        TVShow(title="This Is Us", genre="Drama", watched_date=date(2024, 4, 12), media_type="tv_show", user_id=charlie.id),
        Music(title="Fix You", genre="Alternative", artist="Coldplay", listened_date=date(2024, 5, 8), media_type="music", user_id=charlie.id),
    ])

    # Friendships
    add_friend(alice, bob)
    add_friend(alice, charlie)

    db.session.commit()
    print("✅ Static test data seeded successfully.")

if __name__ == "__main__":
    with app.app_context():
        seed_static_media()
