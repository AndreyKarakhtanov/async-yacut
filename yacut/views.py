import string
from random import choice

from flask import flash, redirect, render_template, request

from . import app, db
from .disk import get_download_file_url, upload_files_and_get_url
from .forms import FilesForm, URLMapForm
from .models import URLMap


def get_unique_short_id():
    flag = True
    while flag:
        short = ''.join(
            [choice(string.ascii_letters + string.digits)
             for _ in range(6)]
        )
        if short == 'files':
            continue
        elif URLMap.query.filter_by(short=short).first() is not None:
            continue
        return short


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        original_link = form.original_link.data
        short_id = form.custom_id.data
        if not short_id:
            short_id = get_unique_short_id()
        elif not short_id.isalnum():
            flash('Указано недопустимое имя для короткой ссылки')
            return render_template('index.html', form=form)
        query = URLMap.query.filter_by(short=short_id).first()
        if query is not None or short_id == 'files':
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)
        url_map = URLMap(
            original=original_link,
            short=short_id
        )
        db.session.add(url_map)
        db.session.commit()
        short = request.url + short_id
        return render_template('index.html', form=form, short=short)
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    if form.validate_on_submit():
        files = form.files.data
        paths = await upload_files_and_get_url(files)
        files_names = [file.filename for file in files]
        urls = []
        for path in paths:
            original_link = await get_download_file_url(path)
            short_id = get_unique_short_id()
            url_map = URLMap(
                original=original_link,
                short=short_id
            )
            db.session.add(url_map)
            db.session.commit()
            urls.append(request.scheme + '://' + request.host + '/' + short_id)
        return render_template('disk.html', form=form,
                               files=files_names, urls=urls)
    return render_template('disk.html', form=form)


@app.route('/<string:short_id>')
def opinion_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)