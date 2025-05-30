from datetime import datetime

from flask import request

from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_url(self):
        return dict(
            url=self.original
        )

    def create_id(self):
        return dict(
            url=self.original,
            short_link=(
                request.scheme + '://' + request.host + '/' + self.short
            )
        )

    def create_id_rec(self):
        return dict(
            url=self.original,
            custom_id=self.short
        )

    def from_dict(self, data):
        for field in ['original', 'short']:
            if field in data:
                setattr(self, field, data[field])
