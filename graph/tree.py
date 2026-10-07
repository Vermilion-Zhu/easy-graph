from typing import Optional, List, Sequence, Tuple

# from utils import NodeError # Haven't find its use till now...

class bNode:
    """
    The node class for BinaryTree
    """
    # Good news comes that I can extend the supported types of the value of a bNode
    # by slightly modify the __init__(...) function
    def __init__(self, value: int | float | str | Tuple[int,int], left = None, right = None) -> None:
        self.value = value
        self.left = left
        self.right = right

        self.father = None

    # Interestingly, even though I didn't write any type hint here,
    # mypy does not report any error.
    def add_left(self, other) -> None:
        self.left = other
        other.father = self
    def add_right(self, other) -> None:
        self.right = other
        other.father = self

    def __repr__(self) -> str:
        return str(self.value)

    @property
    def degree(self) -> int:
        return int((self.left != None) + (self.right != None) + (self.father != None))

    def isLeaf(self) -> bool:
        return self.degree == 1

class BinaryTree:
    """
    The basic type of binary tree
    """

    def __init__(self, seq: Sequence[Optional[bNode]] = []) -> None:
        """
        Generate a binary tree from a sequence of bNodes.
        The mismatch part where nodes have no valid father will be truncated.
        """
        # Guarantee a valid root
        if not seq or seq[0] == None:
            self.root = bNode(0)
            return
        
        self.root = seq[0]
        q: List[bNode] = list()
        q.append(self.root) 
        pos = 0

        while q:
            front = q.pop(0)
            if pos + 1 < len(seq):
                pos += 1
                if (next := seq[pos]) != None:
                    front.add_left(next)
                    q.append(next)
            else:
                break
            if pos + 1 < len(seq):
                pos += 1
                if (nnext := seq[pos]) != None:
                    front.add_right(nnext)
                    q.append(nnext)
            else:
                break

    @classmethod
    def fromvalue(cls, values: Sequence[Optional[int | float | str]]):
        """
        Generate a binary tree from the values of its nodes.
        Use None as placeholders.
        """
        nodeSeq: List[Optional[bNode]] = list()
        for v in values:
            if v == None:
                nodeSeq.append(v)
            else:
                nodeSeq.append(bNode(v))
        return cls(nodeSeq)

    @classmethod
    def complete(cls, values: Sequence[int | float | str]):
        """
        Return a complete binary tree, whose leaves appear at
        the same level and align to the left.
        """
        return cls(list(map(bNode, values)))

    @property
    def rank(self) -> int:
        """The rank, or 'height', of the tree."""
        def height(n: bNode) -> int:
            if n.left == None:
                if n.right == None:
                    return 1
                else:
                    return height(n.right) + 1
            else:
                if n.right == None:
                    return height(n.left) + 1
                else:
                    return max(height(n.left), height(n.right)) + 1
        return height(self.root)

    def display(self) -> None:
        layers: List[List[bNode]] = [[] for _ in range(self.rank)]

        q: List[bNode] = list()
        levels: List[int] = list()
        q.append(self.root)
        levels.append(0)

        while q:
            front = q.pop(0)
            curlev = levels.pop(0)
            layers[curlev].append(front)
            if front.left != None:
                q.append(front.left)
                levels.append(curlev+1)
            if front.right != None:
                q.append(front.right)
                levels.append(curlev+1)

        print('-' * 10)
        for i in range(len(layers)):
            print(f"Level {i+1}: ", layers[i])
        print('-' * 10)

    def preOrder(self) -> List[bNode]:
        """Traverse the tree in pre-order (root-left-right), which determines a unique binary tree"""
        # Implemented by using a stack
        stk: List[bNode] = list()
        res: List[bNode] = list()

        stk.append(self.root)
        while stk:
            top = stk.pop()
            res.append(top)
            if top.right != None:
                stk.append(top.right)
            if top.left != None:
                stk.append(top.left)
        return res

    def midOrder(self) -> List[bNode]:
        """Traverse the tree in mid-order (left-root-right), which is implemented by recursion."""
        res: List[bNode] = list()

        def mid(n: bNode) -> None:
            nonlocal res
            if n.left != None:
                mid(n.left)
            res.append(n)
            if n.right != None:
                mid(n.right)

        mid(self.root)
        return res

    def postOrder(self) -> List[bNode]:
        """Traverse the tree in post-order (left-right-root), which is implemented by recursion."""
        res: List[bNode] = list()

        def post(n: bNode) -> None:
            nonlocal res
            if n.left != None:
                post(n.left)
            if n.right != None:
                post(n.right)
            res.append(n)

        post(self.root)
        return res

    def levelTraverse(self) -> List[bNode]:
        """Traverse the tree level by level."""
        res: List[bNode] = list()
        q: List[bNode] = list()

        q.append(self.root)
        while q:
            front = q.pop(0)
            res.append(front)
            if front.left != None:
                q.append(front.left)
            if front.right != None:
                q.append(front.right)
        return res

if __name__ == "__main__":
    seq = [1,2,3,4,None,5,6,None,None,7,None,None,8]
    bt = BinaryTree.fromvalue(seq)
    bt.display()
    print(bt.preOrder())
    print(bt.midOrder())
    print(bt.levelTraverse())

    bc = BinaryTree.complete(list(range(1,16)))
    bc.display()
    print(bc.preOrder())