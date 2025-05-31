from flask import flash, redirect, render_template, url_for

from . import app
from .disk import get_download_file_url, upload_files_and_get_url
from .exceptions import ValidationError
from .forms import FilesForm, URLMapForm
from .models import URLMap


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    original_link = form.original_link.data
    short_id = form.custom_id.data
    try:
        url_map = URLMap.add(original_link, short_id)
    except ValidationError as e:
        flash(str(e))
        return render_template('index.html', form=form)
    short = url_for('index_view', _external=True) + url_map.short
    return render_template('index.html', form=form, short=short)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    if form.validate_on_submit():
        files = form.files.data
        paths = await upload_files_and_get_url(files)
        file_link = []
        for path in paths:
            original_link = await get_download_file_url(path)
            try:
                url_map = URLMap.add(original_link)
            except ValidationError as e:
                flash(str(e))
                return render_template('disk.html', form=form)
            file_link.append(
                {'name': path.split('/')[-1],
                 'link': url_for('index_view', _external=True) + url_map.short}
            )
        return render_template('disk.html', form=form,
                               file_link=file_link)
    return render_template('disk.html', form=form)


@app.route('/<string:short_id>')
def opinion_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)