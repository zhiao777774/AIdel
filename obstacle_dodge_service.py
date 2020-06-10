import queue
import math
from enum import Enum

class MazeSymbol(str, Enum):
    START = 'O'
    END = 'X'
    OBSTACLE = '#'
    ROAD = ' '
    PATH = '+ '

    def __str__(self):
        return self.value
            
    def __repr__(self):
        return self.value

class Dodger:
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
                    print(MazeSymbol.PATH, end = '')
                else:
                    print(col + ' ', end = '')
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

def generate_maze(data, width, height, resolution, benchmark = 0):
    if width % resolution != 0 or height % resolution != 0:
        raise ArithmeticError('resolution should be divisible by width and height.')

    #sorting the data by distance (Ascending)
    data.sort(key = lambda bbox: bbox.distance)

    maze = []
    row_len = int(height / resolution) + 1
    row_len += 1 #adding default row (for end)
    row_len += 1 #adding default row (for user)
    col_len = int(width / resolution) + 1

    if col_len % 2 != 0: col_len -= 1

    #generating empty maze
    for i in range(row_len):
        maze.append([])
        for j in range(col_len):
            maze[i].append(MazeSymbol.ROAD)

    #setting start
    maze[row_len - 1][int((col_len - 1) / 2)] = MazeSymbol.START

    #setting end
    maze[0][int((col_len - 1) / 2)] = MazeSymbol.END

    #setting obstacles
    for bbox in data:
        lb = bbox.coordinates.lb
        rb = bbox.coordinates.rb

        y = math.ceil((lb.y - benchmark + resolution) / resolution)
        for x in range(lb.x, rb.x + resolution, resolution):
            x = math.ceil(x / resolution)
            if x >= col_len: x -= 1

            maze[y][x] = MazeSymbol.OBSTACLE

    return maze

'''
class Dodger:
    _weight = {}
    _weight['distance'] = 0.4
    _weight['proportion'] = 1 - _weight['distance']

    _max = 100
    _min = 0
    _med = (_max - _min) / 2

    @classmethod
    def calc(cls, bbox):
        dop = 0
        dis = cls._weight['distance']
        prop = cls._weight['proportion']

        return dop

    @classmethod
    def get_DOP(cls, node_vals = [], root_val = None):
        root_val = root_val if root_val else cls._med

        root = BinaryTreeNode(root_val)
        tree = BinarySearchTree(root)
        
        for val in node_vals:
            tree.insert_node(val)
        
        return tree

class BinarySearchTree:
    def __init__(self, root = None):
        self._root = root
        self._size = 1 if root != None else 0
  
    def is_empty(self):
        return self.size == 0
    
    def insert_node(self, data):
        self._root = self._insert(self.root, data)
        return self
    
    def _insert(self, node, data):
        if node is None:
            return BinaryTreeNode(data)
        
        if data < node.data:
            node.left_child = self._insert(node.left_child, data)
        else:
            node.right_child = self._insert(node.right_child, data)
            
        return node
    
    def search(self, node, i):
        while node is not None:
            if i == node.data:
                return node
        
            if i < node.data:
                node = node.left_child
            else:
                node = node.right_child
        return None
    
    def inorder_traversal(self):
        results = []
        if self.root is not None:
            def _inorder(node):
                if node is not None:
                    _inorder(node.left_child)
                    results.append(node.data)
                    _inorder(node.right_child)
            _inorder(self.root)
        return results

    @property
    def root(self):
        return self._root
    
    @property
    def size(self):
        return self._size

class BinaryTreeNode:
    def __init__(self, data, left_child = None, right_child = None):
        self._data = data
        self.left_child = left_child
        self.right_child = right_child
        
    def has_children(self):
        return (self.left_child is not None) or (self.right_child is not None)
        
    @property
    def data(self):
        return self._data
'''

if __name__ == '__main__':
    '''
    node5 = BinaryTreeNode(10)
    node4 = BinaryTreeNode(7)
    node3 = BinaryTreeNode(1)
    node2 = BinaryTreeNode(8, node4, node5)
    node1 = BinaryTreeNode(2, node3)
    root = BinaryTreeNode(5, node1, node2)

    tree = BinarySearchTree(root)
    print(tree.inorder_traversal()) #print result of inorder traversal 

    root_val = 5
    node_vals = [1,2,3,4,6,7,8]
    print(Dodger.get_DOP(node_vals, root_val).inorder_traversal())
    '''

    import time

    maze = []
    maze.append([' ', 'X', ' ', ' ', ' ', ' ', ' ', ' ', ' '])
    maze.append([' ', ' ', '#', '#', ' ', ' ', ' ', ' ', ' '])
    maze.append([' ', ' ', ' ', '#', ' ', ' ', '#', ' ', ' '])
    maze.append([' ', ' ', ' ', ' ', ' ', '#', '#', ' ', ' '])
    maze.append([' ', ' ', '#', ' ', ' ', '#', ' ', ' ', ' '])
    maze.append([' ', ' ', '#', ' ', ' ', ' ', '#', ' ', ' '])
    maze.append(['#', ' ', '#', ' ', '#', ' ', '#', '#', '#'])
    maze.append([' ', ' ', ' ', '#', ' ', ' ', '#', ' ', ' '])
    maze.append(['#', ' ', '#', 'O', ' ', '#', '#', ' ', '#'])

    dodger = Dodger(maze)
    start = time.time()
    dodger.calculate()
    dodger.print_maze()
    end = time.time()
    print('花費時間: {}s'.format(round(end - start, 2)))