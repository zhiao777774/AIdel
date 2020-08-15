import time
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
            return solution[last_start_idx + 1:-1]
        else:
            raise PathNotFoundError('No solution (no start, end, or path)')