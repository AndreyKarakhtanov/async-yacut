import re
import string
from datetime import datetime
from random import choice

from flask import url_for

from .constants import (CUSTOM_ID_REG_EXP_PATTERN, GENERATOR_LENGTH_VALUE,
                        MAX_CUSTOM_ID_LENGTH, MAX_ORIGINAL_LINK_LENGTH)
from .exceptions import ValidationError
from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_ORIGINAL_LINK_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_CUSTOM_ID_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_url(self):
        return dict(
            url=self.original
        )

    def create_id(self):
        return dict(
            url=self.original,
            short_link=(
                url_for('index_view', _external=True) + self.short
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

    def validate_short(self):
        if (
            not re.match(CUSTOM_ID_REG_EXP_PATTERN, self.short)
            or len(self.short) > MAX_CUSTOM_ID_LENGTH
        ):
            raise ValidationError(
                'Указано недопустимое имя для короткой ссылки'
            )

        elif (
            self.short == 'files'
            or self.get_by_short_id(self.short) is not None
        ):
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.'
            )

    @classmethod
    def get_by_short_id(cls, short_id):
        return cls.query.filter_by(short=short_id).first()

    @staticmethod
    def get_unique_short_id():
        flag = True
        while flag:
            short = ''.join(
                [choice(string.ascii_letters + string.digits)
                 for _ in range(GENERATOR_LENGTH_VALUE)]
            )
            if (
                short == 'files'
                or URLMap.get_by_short_id(short) is not None
            ):
                continue
            return short

    @staticmethod
    def add(original_link, short_id=None):
        if not short_id:
            short_id = URLMap.get_unique_short_id()
        url_map = URLMap(
            original=original_link,
            short=short_id
        )
        url_map.validate_short()
        db.session.add(url_map)
        db.session.commit()
        return url_map
