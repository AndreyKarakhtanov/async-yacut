from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_id():
    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    try:
        url_map = URLMap.add(data['url'], data.get('custom_id', None))
    except Exception as e:
        raise InvalidAPIUsage(str(e))
    return jsonify(url_map.create_id()), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.get_by_short_id(short_id)
    if url_map is not None:
        return jsonify(url_map.get_url()), 200
    raise InvalidAPIUsage('Указанный id не найден', 404)