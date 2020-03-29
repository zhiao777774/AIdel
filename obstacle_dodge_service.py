class Dodger:
    _weight = {}
    _weight["distance"] = 0.4
    _weight["proportion"] = 1 - _weight["distance"]

    _max = 100
    _min = 0
    _med = (_max - _min) / 2

    @classmethod
    def calc(cls, bbox):
        dop = 0
        dis = cls._weight["distance"]
        prop = cls._weight["proportion"]

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


if __name__ == "__main__":
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