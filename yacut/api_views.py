
from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    if 'custom_id' not in data or data['custom_id'] == '':
        data['custom_id'] = get_unique_short_id()
    else:
        custom_id = data['custom_id']
        if (not (custom_id.isalnum()
                 and custom_id.isascii()) or len(custom_id) > 16):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        elif (custom_id == 'files'
              or URLMap.query.filter_by(short=custom_id).first()
              is not None):
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )

    url_map = URLMap()
    url_map.from_dict(
        {'original': data['url'], 'short': data['custom_id']}
    )
    db.session.add(url_map)
    db.session.commit()
    return jsonify(url_map.create_id()), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    print(url_map)
    if url_map is not None:
        return jsonify(url_map.get_url()), 200
    raise InvalidAPIUsage('Указанный id не найден', 404)