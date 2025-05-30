from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from .constants import (CUSTOM_ID_REG_EXP_PATTERN, MAX_CUSTOM_ID_LENGTH,
                        MAX_ORIGINAL_LINK_LENGTH, MIN_CUSTOM_ID_LENGTH,
                        MIN_ORIGINAL_LINK_LENGTH)


class URLMapForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='\"url\" является обязательным полем!'),
            URL(message='Указано недопустимый адрес ссылки'),
            Length(MIN_ORIGINAL_LINK_LENGTH, MAX_ORIGINAL_LINK_LENGTH)
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Regexp(
                CUSTOM_ID_REG_EXP_PATTERN,
                message='Указано недопустимое имя для короткой ссылки'
            ),
            Length(
                MIN_CUSTOM_ID_LENGTH,
                MAX_CUSTOM_ID_LENGTH,
                message='Указано недопустимое имя для короткой ссылки'
            )
        ]
    )
    submit = SubmitField('Создать')


class FilesForm(FlaskForm):
    files = MultipleFileField(
        validators=[FileRequired()]
    )
    submit = SubmitField('Загрузить')
