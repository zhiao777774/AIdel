import json
import requests
import pathlib
import logging
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_socketio import SocketIO
from flask_cors import CORS

from api.dodger import Maze, Dodger, PathNotFoundError


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form = request.form
        return render_template('index.html',
                               model_file_name=form['model_file_name'],
                               model_file_content=form['model_file_content'])
    else:
        return render_template('index.html')


@app.route('/fileUpload')
def fileUpload():
    return render_template('file_upload.html')


@app.route('/equipment3D')
def equipment3D():
    return render_template('equipment_3d.html')


@app.route('/calculatePath', methods=['POST'])
def calc_path():
    req_data = request.get_json()
    res = dict()

    maze = req_data['maze']
    maze.insert(0, ['*' for i in range(len(maze[0]))])
    maze.append(['*' for i in range(len(maze[0]))])
    for i in range(len(maze)):
        maze[i].append('*')
        maze[i].insert(0, '*')

    maze = Maze(maze)
    dodger = Dodger()
    print(maze)

    try:
        dirs = dodger.solve(maze)
        res['directions'] = dirs
        print(dirs)
    except (PathNotFoundError, IndexError):
        res['error'] = 'Path cannot founded, no solution (no start, end, or path).'

    return jsonify(res)


@app.route('/latlngQueryAddress', methods=['POST'])
def latlng_query_addr():
    req_data = request.get_json()

    service_url = 'https://addr.tgos.tw/addrws/v40/GeoQueryAddr.asmx/PointQueryAddr'
    params = {
        'oAPPId': 'yplbHN5BJuiEf7LgSExdqxgq7sWsC3ixOinIiChGRbQPLvpGMD+gJQ==',
        'oAPIKey': 'cGEErDNy5yN/1fQ0vyTOZrghjE+jIU6upB/qBs9aoOxKqAeB/zLieVBCYS2k8BuE+UTfAliTTUmvPT61TZIiQctLbnoWpQmk8Kv4M2DcPjcUNM7zNCrPglb3vGflAyMzHtGKvQW/aEsVPTs0tJubkV8qAYvr9w07TvNuV4hrT0fegvck5L12WfaVeDMjXBxu9fpErze+e/aYi5Sk+qeJwQrdYN6tBZ/n2m5jKGpEiX7Zk5sOLGsf1n8JEgOAtb/W9MVMxNsFUw6XzzxWrsuf+6x0iqdULd1pRnaBzBXeag4/WyYxiUSmulD9jxeGC8Ll7uttC6pgt57NJAsWt2VKn0+ypkNF9Cf+',
        'oPX': req_data['lng'],
        'oPY': req_data['lat'],
        'oBuffer': req_data['buffer'],
        'oSRS': 'EPSG:4326',
        'oResultDataType': 'JSON'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.get(service_url, params=params, headers=headers)
    address = ''
    if response.status_code == 200:
        res = response.json()
        total = res['Info']['Total']

        if total > 0:
            address = res['AddressList'][0]['FULL_ADDR']

    return jsonify({
        'result': address
    })


@app.route('/modelFileUpload', methods=['GET', 'POST'])
def model_file_upload():
    if request.method == 'POST':
        model_file = request.files['input-model-file']
    else:
        model_file = request.args.get('input-model-file')

    file_name = model_file.filename
    file_content = model_file.read()
    file_content = file_content.decode('UTF-8')

    content = {}
    for data in file_content.split('\r\n\r\n'):
        if not data:
            continue

        data = data.split('\r\n')
        n = str(data[0])
        content[n] = []
        for item in data[3:]:
            cls_name, x, y, angle, distance = item.split('   ')

            content[n].append({
                'class': str(cls_name),
                'x': str(x),
                'y': str(y),
                'angle': str(angle),
                'distance': str(distance)
            })

    return jsonify({
        'model_file_name': file_name,
        'model_file_content': json.dumps(content)
    })

    # return redirect(url_for('index',
    #                         model_file_name=file_name,
    #                         model_file_content=content), code=307)


@ socketio.on('receiveEnvironmentalModel')
def receive_environmental_model(model):
    print('Environmental model received.')
    socketio.emit('environmentalModel', model)


@ socketio.on('writeEnvironmentalModel')
def write_environmental_model(data):
    print('write Environmental model.')

    root_path = str(pathlib.PurePath(__file__).parent)
    path = root_path + '/data/environmentalModel.txt'
    # pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        for i, item in enumerate(data):
            f.write(f'T{i + 1}\n')
            f.write('-----------------------------------\n')
            f.write('class   x   y   angle   distance\n')

            for item_data in item:
                f.write(f'{item_data["clsName"]}   ')
                f.write(f'{item_data["x"]}   ')
                f.write(f'{item_data["y"]}   ')
                f.write(f'{item_data["angle"]}   ')
                f.write(f'{item_data["distance"]}\n')

            f.write('\n')


@ socketio.on('connect')
def socket_connect():
    print(f'socket connect id: {request.sid}')


@ socketio.on('disconnect')
def socket_disconnect():
    print(f'socket disconnect id: {request.sid}')


if __name__ == '__main__':
    host = '120.125.83.10'
    port = 8090

    print(f'api server running on {host}:{port}.')
    print('Simulator is start!')
    app.run(host=host, port=port)
