from enum import Enum
from typing import Any, Optional, TypeVar, Generic

# For storing Agent objects - forward declaration for type hinting
# Actual Agent objects will be passed in.
# from agent import Agent # Avoid direct import if Agent also imports parts of this, handle with TypeVar or 'Agent' string hint

# Define a type variable for the values stored in the tree (Agent objects)
V = TypeVar('V') 
K = TypeVar('K') # Type for keys (agent_id)

class Color(Enum):
    RED = 0
    BLACK = 1

class RBNode(Generic[K, V]):
    def __init__(self, key: K, value: V, color: Color = Color.RED, 
                 parent: Optional['RBNode[K, V]'] = None, 
                 left: Optional['RBNode[K, V]'] = None, 
                 right: Optional['RBNode[K, V]'] = None):
        self.key: K = key  # Agent ID
        self.value: V = value # Agent object (or could include description here too)
        # self.agent_description: str = description # Or store description alongside agent in `value` if V is complex
        self.color: Color = color
        self.parent: Optional['RBNode[K, V]'] = parent
        self.left: Optional['RBNode[K, V]'] = left
        self.right: Optional['RBNode[K, V]'] = right

class RedBlackTree(Generic[K, V]):
    def __init__(self):
        self.TNULL: RBNode[K, V] = RBNode(None, None, Color.BLACK) # Sentinel NIL node
        self.root: RBNode[K, V] = self.TNULL

    def _left_rotate(self, x: RBNode[K, V]):
        y = x.right
        x.right = y.left
        if y.left != self.TNULL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None: # x was root
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, x: RBNode[K, V]):
        y = x.left
        x.left = y.right
        if y.right != self.TNULL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None: # x was root
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def insert(self, key: K, value: V):
        # Ordinary Binary Search Tree insert
        node = RBNode(key, value)
        node.parent = None
        node.left = self.TNULL
        node.right = self.TNULL
        node.color = Color.RED # New nodes are red

        y = None
        x = self.root

        while x != self.TNULL:
            y = x
            if node.key < x.key:
                x = x.left
            elif node.key > x.key: # Allow overwrite or handle duplicate keys? For now, assume keys are unique or overwrite.
                x = x.right
            else: # Key already exists, update value (or raise error)
                x.value = value 
                return # Or some other handling for duplicates

        node.parent = y
        if y is None: # Tree was empty
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node

        # If new node is root, color it black (handled by fixup if parent is None)
        if node.parent is None:
            node.color = Color.BLACK
            return

        # If parent is None (already root), or parent of parent is None (parent is root)
        if node.parent.parent is None:
            return 

        # Fix Red-Black Tree properties
        self._insert_fixup(node)

    def _insert_fixup(self, k: RBNode[K, V]):
        while k.parent is not None and k.parent.color == Color.RED:
            if k.parent == k.parent.parent.right: # Parent is right child
                u = k.parent.parent.left # Uncle
                if u.color == Color.RED: # Case 1: Uncle is red
                    u.color = Color.BLACK
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    k = k.parent.parent # Move k up
                else: # Case 2: Uncle is black
                    if k == k.parent.left: # K is left child (triangle)
                        k = k.parent
                        self._right_rotate(k)
                    # Case 3: K is right child (line)
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    self._left_rotate(k.parent.parent)
            else: # Parent is left child (symmetric to above)
                u = k.parent.parent.right # Uncle
                if u.color == Color.RED: # Case 1
                    u.color = Color.BLACK
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    k = k.parent.parent
                else: # Case 2
                    if k == k.parent.right: # K is right child (triangle)
                        k = k.parent
                        self._left_rotate(k)
                    # Case 3
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    self._right_rotate(k.parent.parent)
            if k == self.root:
                break
        self.root.color = Color.BLACK


    def search(self, key: K) -> Optional[V]:
        node = self._search_tree_helper(self.root, key)
        return node.value if node != self.TNULL else None

    def _search_tree_helper(self, node: RBNode[K, V], key: K) -> RBNode[K, V]:
        if node == self.TNULL or key == node.key:
            return node
        if key < node.key:
            return self._search_tree_helper(node.left, key)
        return self._search_tree_helper(node.right, key)

    # Transplant helper for delete
    def _rb_transplant(self, u: RBNode[K, V], v: RBNode[K, V]):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent
        
    def _minimum(self, node: RBNode[K,V]) -> RBNode[K,V]:
        while node.left != self.TNULL:
            node = node.left
        return node

    def delete(self, key: K):
        z = self._search_tree_helper(self.root, key)
        if z == self.TNULL:
            # print(f"Key {key} not found in tree.")
            return # Key not found

        y = z
        y_original_color = y.color
        if z.left == self.TNULL:
            x = z.right
            self._rb_transplant(z, z.right)
        elif z.right == self.TNULL:
            x = z.left
            self._rb_transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y # x might be TNULL, its parent needs to be y if y is z's direct child
            else:
                self._rb_transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            
            self._rb_transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        
        if y_original_color == Color.BLACK:
            self._delete_fixup(x)

    def _delete_fixup(self, x: RBNode[K, V]):
        while x != self.root and x.color == Color.BLACK:
            if x == x.parent.left: # x is left child
                s = x.parent.right # sibling
                if s.color == Color.RED: # Case 1: sibling is red
                    s.color = Color.BLACK
                    x.parent.color = Color.RED
                    self._left_rotate(x.parent)
                    s = x.parent.right 
                # Now sibling s is black
                if s.left.color == Color.BLACK and s.right.color == Color.BLACK: # Case 2: sibling's children are black
                    s.color = Color.RED
                    x = x.parent # Move up
                else: 
                    if s.right.color == Color.BLACK: # Case 3: sibling's right child is black (left is red)
                        s.left.color = Color.BLACK
                        s.color = Color.RED
                        self._right_rotate(s)
                        s = x.parent.right
                    # Case 4: sibling's right child is red
                    s.color = x.parent.color
                    x.parent.color = Color.BLACK
                    s.right.color = Color.BLACK
                    self._left_rotate(x.parent)
                    x = self.root # Exit loop
            else: # x is right child (symmetric)
                s = x.parent.left # sibling
                if s.color == Color.RED: # Case 1
                    s.color = Color.BLACK
                    x.parent.color = Color.RED
                    self._right_rotate(x.parent)
                    s = x.parent.left
                
                if s.right.color == Color.BLACK and s.left.color == Color.BLACK: # Case 2
                    s.color = Color.RED
                    x = x.parent
                else:
                    if s.left.color == Color.BLACK: # Case 3 (right is red)
                        s.right.color = Color.BLACK
                        s.color = Color.RED
                        self._left_rotate(s)
                        s = x.parent.left
                    # Case 4
                    s.color = x.parent.color
                    x.parent.color = Color.BLACK
                    s.left.color = Color.BLACK
                    self._right_rotate(x.parent)
                    x = self.root
        x.color = Color.BLACK

    # Helper for pretty printing (optional)
    def print_tree(self):
        self._print_helper(self.root, "", True)

    def _print_helper(self, node, indent, last):
        if node != self.TNULL:
            print(indent, end="")
            if last:
                print("R----", end="")
                indent += "     "
            else:
                print("L----", end="")
                indent += "|    "
            
            color_str = "R" if node.color == Color.RED else "B"
            print(f"{node.key}({color_str})") # Assuming key is printable
            self._print_helper(node.left, indent, False)
            self._print_helper(node.right, indent, True)
