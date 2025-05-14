from app.models import MediaEntry
from app import db
from sqlalchemy import func

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