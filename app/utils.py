# This file contains the utility functions for the application.
# It includes functions for user media identity, monthly media breakdown, and book metrics calculation.

from datetime import timedelta
from app.models import Book, MediaEntry, Movie, Music, TVShow
from app import db
from sqlalchemy import func
from collections import defaultdict

# This function retrieves the media type breakdown for a given user.
def get_media_type_breakdown(user_id):
    counts = (
        db.session.query(MediaEntry.media_type, func.count(MediaEntry.id))
        .filter_by(user_id=user_id)
        .group_by(MediaEntry.media_type)
        .all()
    )
    return {media_type: count for media_type, count in counts}

# This function determines the user's media identity based on their media type breakdown.
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
    
# This function retrieves the monthly media breakdown by type for a given user.
def get_monthly_media_by_type(user_id):
    def get_month_key(date):
        return date.strftime('%Y-%m')

    def parse_dates(entries, field):
        return [getattr(e, field) for e in entries if getattr(e, field)]

    counts = defaultdict(lambda: defaultdict(int))

    # Fetch all media entries
    movies = Movie.query.filter_by(user_id=user_id).all()
    tv = TVShow.query.filter_by(user_id=user_id).all()
    music = Music.query.filter_by(user_id=user_id).all()
    books = Book.query.filter_by(user_id=user_id).all()

    # Get all date fields that matter
    all_dates = []
    for model, field in [
        (Book, 'date_finished'),
        (Movie, 'watched_date'),
        (TVShow, 'watched_date'),
        (Music, 'listened_date')
    ]:
        all_dates += [
            getattr(entry, field)
            for entry in model.query.filter_by(user_id=user_id).all()
            if getattr(entry, field)
        ]

    # If no dates, return empty
    if not all_dates:
        return {}

    # Determine min and max months
    min_date = min(all_dates).replace(day=1)
    max_date = max(all_dates).replace(day=1)

    # Pad the full month range (step forward by 1 month)
    current = min_date
    while current <= max_date:
        month_key = current.strftime('%Y-%m')
        counts[month_key]  # ensures the key is present even if empty
        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

    # Tally real entries
    for m in movies:
        if m.watched_date:
            counts[get_month_key(m.watched_date)]['movie'] += 1
    for t in tv:
        if t.watched_date:
            counts[get_month_key(t.watched_date)]['tv_show'] += 1
    for s in music:
        if s.listened_date:
            counts[get_month_key(s.listened_date)]['music'] += 1
    for b in books:
        if b.date_finished:
            counts[get_month_key(b.date_finished)]['book'] += 1

    return dict(counts)

# This function calculates the completion rate and average reading duration for books.
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