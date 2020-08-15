from flask import Flask, jsonify, request
from flask_cors import CORS
from dodger import Dodger, Maze, PathNotFoundError


app = Flask(__name__)
CORS(app)

@app.route('/')
def main():
    return f'api server running on {host}:{port}.'

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


if __name__ == '__main__':
    host = '120.125.83.10'
    port = 8091

    app.run(host = host, port = port)
    print(f'api server running on {host}:{port}.')