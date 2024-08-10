from app.database import db


class Sources(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    web = db.Column(db.String)
    rss = db.Column(db.String)
    tags = db.Column(db.Text)
    name_alias = db.Column(db.String)
