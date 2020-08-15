from flask import Flask, jsonify, request
from dodger import Dodger, Maze, PathNotFoundError


app = Flask(__name__)

@app.route('/')
def main():
    return f'api server running on {host}:{port}.'

@app.route('/calculatePath' , methods=['POST'])
def calc_path():
    req_data = request.get_json()
    res = dict()

    maze = Maze(req_data['maze'])
    dodger = Dodger()
    print(maze)

    try:
        dirs = dodger.solve(maze)
        res['directions'] = dirs
        print(dirs)
    except (PathNotFoundError, IndexError):
        res['error'] = 'Path cannot founded, no solution (no start, end, or path).'

    return jsonify(res)


if __name__ == '__main__':
    host = '120.125.83.10'
    port = 8091

    app.run(host = host, port = port)
    print(f'api server running on {host}:{port}.')