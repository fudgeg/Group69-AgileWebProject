from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MediaEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<{self.media_type}: {self.title}>"
