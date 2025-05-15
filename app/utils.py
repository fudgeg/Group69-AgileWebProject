from app.models import Book, MediaEntry, Movie, Music, TVShow
from app import db
from sqlalchemy import func
from collections import defaultdict

def get_media_type_breakdown(user_id):
    counts = (
        db.session.query(MediaEntry.media_type, func.count(MediaEntry.id))
        .filter_by(user_id=user_id)
        .group_by(MediaEntry.media_type)
        .all()
    )
    return {media_type: count for media_type, count in counts}
def get_user_media_identity(counts_dict):
    if not counts_dict:
        return "You are a Media Explorer"

    max_count = max(counts_dict.values())
    top_types = [k for k, v in counts_dict.items() if v == max_count]

    if len(top_types) > 1:
        return "You are a Media Explorer"

    return {
        'book': "You are a Reader",
        'movie': "You are a Cinephile",
        'music': "You are a Music Lover",
        'tv_show': "You are a Binge-Watcher"
    }.get(top_types[0], "You are a Media Explorer")
    
def get_monthly_media_by_type(user_id):
    def get_month_key(date):
        return date.strftime('%Y-%m')
    
    counts = defaultdict(lambda: defaultdict(int))

    movies = Movie.query.filter_by(user_id=user_id).all()
    for m in movies:
        if m.watched_date:
            counts[get_month_key(m.watched_date)]['movie'] += 1

    tv = TVShow.query.filter_by(user_id=user_id).all()
    for t in tv:
        if t.watched_date:
            counts[get_month_key(t.watched_date)]['tv_show'] += 1

    music = Music.query.filter_by(user_id=user_id).all()
    for s in music:
        if s.listened_date:
            counts[get_month_key(s.listened_date)]['music'] += 1

    books = Book.query.filter_by(user_id=user_id).all()
    for b in books:
        if b.date_finished:
            counts[get_month_key(b.date_finished)]['book'] += 1

    return dict(counts)

def calculate_book_metrics(books):
    total = len(books)
    completed = [b for b in books if b.status and b.status.lower() == "finished"]
    completed_count = len(completed)

    completion_rate = round((completed_count / total) * 100, 1) if total else 0

    durations = []
    for b in completed:
        if b.date_started and b.date_finished:
            delta = (b.date_finished - b.date_started).days
            if delta > 0:
                durations.append(delta)

    avg_days = round(sum(durations) / len(durations), 1) if durations else 0

    return completion_rate, avg_days