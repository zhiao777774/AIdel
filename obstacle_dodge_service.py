import time
import queue
import math
import operator
from enum import Enum


class MazeSymbol(str, Enum):
    START = 'S'
    END = 'E'
    OBSTACLE = '#'
    ROAD = ' '
    PATH = '+ '
    BACK_TRACK = '.'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Maze:
    def __init__(self, data):
        if type(data) is str:
            self.read_file(data)
        elif type(data) is list:
            self._data = data
        else:
            raise AttributeError(
                'data type must be file path(str) or maze(list).')

    def __str__(self):
        return '\n'.join(''.join(r) for r in self.data)

    def read_file(self, path):
        """Read a maze text file and split out each character. Return
           a 2-dimensional list where the first dimension is rows and
           the second is columns."""
        maze = []
        with open(path) as f:
            for line in f.read().splitlines():
                maze.append(list(line))
        self._data = maze

    def write_file(self, path):
        """Write the specified 2-dimensional maze to the specified
           file, writing one line per row and with columns
           side-by-side."""
        with open(path, 'w') as f:
            for r, line in enumerate(self.data):
                f.write('%s\n' % ''.join(line))

    def find(self, symbol):
        """Find the first instance of the specified symbol in the
           maze, and return the row-index and column-index of the
           matching cell. Return None if no such cell is found."""
        for r, line in enumerate(self.data):
            try:
                return r, line.index(MazeSymbol.START)
            except ValueError:
                pass

    def get(self, where):
        """Return the symbol stored in the specified cell."""
        r, c = where
        return self._data[r][c]

    def set(self, where, symbol):
        """Store the specified symbol in the specified cell."""
        r, c = where
        self._data[r][c] = symbol

    @property
    def data(self):
        return self._data


class PathNotFoundError(Exception):
    pass


class BfsDodger:
    def __init__(self, maze):
        self._seq = queue.Queue()
        self._seq.put('')
        self._maze = maze
        self._directions = ''

    def calculate(self):
        s = ''
        while not self._end(s):
            s = self.seq.get()
            for direction in ('L', 'R', 'U', 'D'):
                data = s + direction
                if self._validate(data):
                    self.seq.put(data)

    def _end(self, directions):
        maze = self.maze
        start = 0

        for i, symbol in enumerate(maze[-1]):
            if symbol == MazeSymbol.START:
                start = i
                break

        x = start
        y = len(maze) - 1
        for direction in directions:
            if direction == 'L':
                x -= 1
            elif direction == 'R':
                x += 1
            elif direction == 'U':
                y -= 1
            elif direction == 'D':
                y += 1

        if maze[y][x] == MazeSymbol.END:
            print('Found: ' + directions)
            self._directions = directions
            return True
        return False

    def _validate(self, directions):
        maze = self.maze
        start = 0

        for i, symbol in enumerate(maze[-1]):
            if symbol == MazeSymbol.START:
                start = i
                break

        x = start
        y = len(maze) - 1
        for direction in directions:
            if direction == 'L':
                x -= 1
            elif direction == 'R':
                x += 1
            elif direction == 'U':
                y -= 1
            elif direction == 'D':
                y += 1

            if not (0 <= x < len(maze[0]) and 0 <= y < len(maze)):
                return False
            elif maze[y][x] == MazeSymbol.OBSTACLE:
                return False

        return True

    def print_maze(self):
        maze = self.maze
        start = 0

        for i, symbol in enumerate(maze[-1]):
            if symbol == MazeSymbol.START:
                start = i
                break

        x = start
        y = len(maze) - 1
        sequence = set()
        for direction in self.directions:
            if direction == 'L':
                x -= 1
            elif direction == 'R':
                x += 1
            elif direction == 'U':
                y -= 1
            elif direction == 'D':
                y += 1
            sequence.add((y, x))

        for y, row in enumerate(maze):
            for x, col in enumerate(row):
                if (y, x) in sequence:
                    print(MazeSymbol.PATH, end='')
                else:
                    print(col + ' ', end='')
            print()

    @property
    def seq(self):
        return self._seq

    @property
    def maze(self):
        return self._maze

    @property
    def directions(self):
        return self._directions


class Dodger:
    def _inner_solve(self, maze, where=None, direction=None):
        """Finds a path through the specified maze beginning at where (or
           a cell marked 'S' if where is not provided), and a cell marked
           'E'. At each cell the four directions are tried in the order
           UP, RIGHT, LEFT, DOWN. When a cell is left, a marker symbol
           (one of '^', '>', '<', 'v') is written indicating the new
           direction, and if backtracking is necessary, a symbol ('.') is
           also written. The return value is None if no solution was
           found, and a (row_index, column_index) tuple when a solution
           is found."""

        start_symbol = MazeSymbol.START
        end_symbol = MazeSymbol.END
        vacant_symbol = MazeSymbol.ROAD
        backtrack_symbol = MazeSymbol.BACK_TRACK
        directions = (-1, 0), (0, 1), (0, -1), (1, 0)
        direction_marks = '^', '>', '<', 'v'

        where = where or maze.find(start_symbol)

        if(type(where) is map):
            where = list(where)

        if not where:
            # no start cell found
            return []
        if maze.get(where) == end_symbol:
            # standing on the end cell
            return [end_symbol]
        if maze.get(where) not in (vacant_symbol, start_symbol):
            # somebody has been here
            return []

        for direction in directions:
            next_cell = list(map(operator.add, where, direction))

            # spray-painting direction
            marker = direction_marks[directions.index(direction)]
            if maze.get(where) != start_symbol:
                maze.set(where, marker)

            sub_solve = self._inner_solve(maze, next_cell, direction)
            if sub_solve:
                # found solution in this direction
                is_first_step = maze.get(where) == start_symbol
                # make this line simply `[marker]` to include the initial step
                return ([start_symbol] if is_first_step else []) +\
                    [marker] + sub_solve

        # no directions worked from here - have to backtrack
        maze.set(where, backtrack_symbol)
        return []

    def solve(self, maze):
        start = time.time()
        solution = self._inner_solve(maze)
        if solution:
            end = time.time()
            print(f'Spend time: {round(end - start, 2)}s')
            print(f'Found path through maze {solution}')

            last_start_idx = (len(solution) - 1) - (solution[::-1].index('S'))
            return ''.join(solution[last_start_idx + 1:-1])
        else:
            raise PathNotFoundError('No solution (no start, end, or path)')


def generate_maze(data, width, height, resolution, benchmark=0):
    if width % resolution != 0 or height % resolution != 0:
        raise ArithmeticError(
            'resolution should be divisible by width and height.')

    # sorting the data by distance (Ascending)
    data.sort(key=lambda bbox: bbox.distance)

    maze = []
    row_len = int(height / resolution) + 1
    row_len += 1  # adding default row (for end)
    row_len += 1  # adding default row (for user)
    row_len += 1  # adding default row (for wall)
    col_len = int(width / resolution) + 1
    col_len += 1  # adding default column (for wall)

    if col_len % 2 != 0:
        col_len -= 1

    # generating empty maze
    for i in range(row_len):
        maze.append([])
        for j in range(col_len):
            if i == 0 or j == col_len - 1:
                maze[i].append(MazeSymbol.OBSTACLE)
            else:
                maze[i].append(MazeSymbol.ROAD)

    # setting start
    maze[row_len - 1][int((col_len - 1) / 2)] = MazeSymbol.START

    # setting end
    maze[1][int((col_len - 1) / 2)] = MazeSymbol.END

    # setting obstacles
    for bbox in data:
        lb = bbox.coordinates.lb
        rb = bbox.coordinates.rb

        y = math.ceil((lb.y - benchmark + resolution) / resolution)
        for x in range(lb.x, rb.x + resolution, resolution):
            x = math.ceil(x / resolution)
            if x >= col_len:
                x -= 1

            maze[y][x] = MazeSymbol.OBSTACLE

    return maze


if __name__ == '__main__':
    maze = []
    maze.append([' ', ' ', ' ', ' ', 'E', ' ', ' ', ' ', ' '])
    maze.append([' ', ' ', '#', '#', ' ', ' ', ' ', ' ', ' '])
    maze.append([' ', '#', ' ', '#', ' ', ' ', '#', ' ', ' '])
    maze.append([' ', ' ', ' ', '#', ' ', '#', '#', ' ', ' '])
    maze.append(['#', ' ', '#', ' ', 'S', '#', '#', ' ', '#'])

    '''
    dodger = BfsDodger(maze)
    start = time.time()
    dodger.calculate()
    dodger.print_maze()
    end = time.time()
    print('花費時間: {}s'.format(round(end - start, 2)))
    '''

    maze = Maze(maze)
    dodger = Dodger()
    dirs = dodger.solve(maze)
    print(maze)
    print(dirs)