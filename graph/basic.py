import random
import pprint as pp
from typing import List, Optional

class EdgeError(Exception):
    def __init__(self, pair: List[int], *args: object) -> None:
        super().__init__(*args)
        self.pair = pair

    def __str__(self) -> str:
        return f'Each edge must have exact 2 ends, got {self.pair}'

class Edge:

    """
    The basic type of unweighted edges
    """

    def __init__(self, pair: List[int]) -> None:
        if len(pair) != 2:
            raise EdgeError(pair)
        self.src, self.dst = pair

class Graph:

    """
    The basic type of undirected graphs
    """

    def __init__(self, vnum: int = 1, edges: List[List[int]] = [], dedu: bool = True, directed: bool = False) -> None:
        self.vertices = list(range(vnum))
        self.adjacent: List[List[int]] = [[] for _ in range(vnum)] 

        for pair in edges:
            self.add_edge(pair, directed=directed)
        
        # It is optional to remove the duplicated edges in the adjacent matrix,
        # which may improve the efficiency in certain cases.
        if dedu:
            self.deduplicate()

    @classmethod
    def fromrandom(cls, vnum: int = 7, elimit: int = 10, seed: int = 42):
        """
        Generate a random graph
        
        :param vnum: the number of vertices
        :type vnum: int
        :param elimit: the limit for the number of edges
        :type elimit: int
        :param seed: the seed for initialization
        :type seed: int
        """
        random.seed(seed)
        elimit = min(elimit, random.randint(0, vnum * (vnum - 1) // 2))
        vertices = range(vnum)
        edges = list()
        for i in range(elimit):
            edges.append(random.sample(vertices, k=2))
        return cls(vnum, edges)

    @classmethod
    def complete(cls, n: int):
        """
        Generate a complete graph K_n
        """
        edges = [[i,j] for i in range(n) for j in range(i+1,n)]
        return cls(n, edges, dedu=False)

    @classmethod
    def cycle(cls, n: int):
        """
        Generate a cycle C_n
        """
        edges = [[i, (i+1) % n] for i in range(n)]
        return cls(n, edges, dedu=False)

    def display(self) -> None:
        print(f'v(G) = {self.v}, e(G) = {self.e}, connected components = {self.count_cc()}')
        print('-' * 10)
        for i in self.vertices:
            print(f'{i}: {self.adjacent[i]}')
        print('-' * 10)

    @property
    def v(self) -> int:
        """The number of vertices v(G)"""
        return len(self.vertices)
    
    @property
    def e(self) -> int:
        """The number of undirected edges e(G)"""
        return sum(len(self.adjacent[i]) for i in self.vertices) // 2
    
    @property
    def connected(self) -> bool:
        return self.count_cc() == 1

    def add_edge(self, pair: List[int], directed: bool = True) -> None:
        if len(pair) != 2:
            raise EdgeError(pair)
        u, v = pair
        self.adjacent[u].append(v)
        if not directed:
            self.adjacent[v].append(u)

    def rm_edge(self, pair: List[int], directed: bool = True) -> None:
        """
        Remove an edge (u,v) from the graph. If directed == False, remove (v,u) by the way
        """
        if len(pair) != 2:
            raise EdgeError(pair)
        u, v = pair
        try:
            self.adjacent[u].remove(v)
        except ValueError:
            pass
        if not directed:
            self.rm_edge(pair[::-1])

    
    def deduplicate(self) -> None:
        for i in self.vertices:
            self.adjacent[i] = list(set(self.adjacent[i]))

    def count_cc(self) -> int:
        visited = [False] * self.v
        cnt = 0

        def explore(v) -> None:
            nonlocal visited
            visited[v] = True
            for u in self.adjacent[v]:
                if not visited[u]:
                    explore(u)

        for i in self.vertices:
            if visited[i]:
                continue
            explore(i)
            cnt += 1

        return cnt


class DirectedGraph(Graph):

    """
    The directed graph class, with unweighted edges
    """

    def __init__(self, vnum: int = 1, edges: List[List[int]] = []) -> None:
        super().__init__(vnum, edges, directed=True)

    @classmethod
    def fromrandom(cls, vnum: int = 7, elimit: int = 10, seed: int = 42):
        # This works because the cls parameter in super().fromrandom(...) 
        # takes DirectedGraph rather than Graph
        return super().fromrandom(vnum, elimit, seed)

    def display(self) -> None:
        inv = inverse(self)
        print(f'v(G) = {self.v}, e(G) = {self.e}, weak connected components = {self.count_cc()}')
        if 1 == self.count_cc() == inv.count_cc():
            print('strongly connected = True')
        else:
            print('strongly connected = False')

        print('-' * 10)
        for i in self.vertices:
            print(f'{i}: {self.adjacent[i]}')
        print('-' * 10)

    @property
    def v(self) -> int:
        return super().v
    @property
    def e(self) -> int:
        return sum(len(self.adjacent[i]) for i in self.vertices)

    def add_edge(self, pair: List[int], **args) -> None:
        return super().add_edge(pair)

    def rm_edge(self, pair: List[int], **args) -> None:
        return super().rm_edge(pair)

    def count_cc(self) -> int:
        return super().count_cc()

    def topo(self) -> List[int]:
        """
        Find the possible topological order of the vertices by DFS
        """
        visited = [False] * self.v
        res = list()

        def explore(v: int) -> None:
            nonlocal visited, res
            visited[v] = True
            for u in self.adjacent[v]:
                if not visited[u]:
                    explore(u)
            res.insert(0, v)

        for i in self.vertices:
            if visited[i]:
                continue
            else:
                explore(i)
        return res

    def isDAG(self) -> bool:
        """
        Decide whether it is a directed acyclic graph
        """
        t = self.topo()
        visited = [False] * self.v
        for v in t:
            for u in self.vertices:
                if not visited[u] and v in self.adjacent[u]:
                    return False
            visited[v] = True
        return True

def complement(g: Graph) -> Graph:
    vnum = g.v
    res = Graph.complete(vnum)
    for i in range(vnum):
        for j in g.adjacent[i]:
            res.rm_edge([i,j])
    return res

def inverse(dg: DirectedGraph) -> DirectedGraph:
    vnum = dg.v
    res = DirectedGraph(vnum)
    for i in range(vnum):
        for j in dg.adjacent[i]:
            res.add_edge([j,i])
    return res

if __name__ == "__main__":
    # g = Graph.fromrandom(12,100,23938)
    # g.display()
    # gc = complement(g)
    # gc.display()

    # invalid = Graph(7, [[1,2,3]])
    # k = Graph.complete(10)
    # k.display()

    # c = Graph.cycle(7)
    # c.display()

    dg = DirectedGraph.fromrandom(12,30,23938)
    dg.display()
    inv = inverse(dg)
    inv.display()

    t = DirectedGraph(5,[[0,1],[1,2],[3,4],[4,2]])
    print(t.topo(), t.isDAG())
    t.add_edge([2,0])
    print(t.topo(), t.isDAG())