import random
import pprint as pp
from typing import List, Optional

from utils import EdgeError

class Graph:

    """
    The basic type of undirected graphs. 
    Duplicated edges are allowed but not recommended.

    Set m = e(G) and n = v(G) when analyzing the time complexity of algorithms.
    """

    def __init__(self, vnum: int = 1, edges: List[List[int]] = [], dedu: bool = True) -> None:
        self.vertices = list(range(vnum))
        self.adjacent: List[List[int]] = [[] for _ in range(vnum)] 

        for pair in edges:
            self._add_edge(pair, directed=False)
        
        # It is optional to remove the duplicated edges in the adjacent matrix,
        # which may improve the efficiency in certain cases.
        if dedu:
            self.deduplicate()

    @classmethod
    def fromrandom(cls, vnum: int = 7, elimit: int = 10, seed: int = -1):
        """
        Generate a random graph
        
        :param vnum: The number of vertices
        :type vnum: int
        :param elimit: The limit for the number of edges
        :type elimit: int
        :param seed: The seed for initialization. Use default seed if the given value is negative
        :type seed: int
        """
        if seed >= 0:
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
        return sum(len(self.adjacent[i]) for i in self.vertices) >> 1
    
    @property
    def connected(self) -> bool:
        return self.count_cc() == 1

    # It is annoying that if I write __add_edge here (i.e. set it to be a private method)
    # then the derived classes cannot access it by super.__add_edge(...)
    # Otherwise it would raise an AttributeError that the base class
    # has no attribute '_DirectedGraph__add_edge'
    def _add_edge(self, pair: List[int], directed: bool = True) -> None:
        """Add a (directed) edge (u,v) to the graph"""
        if len(pair) != 2 or pair[0] == pair[1]:
            raise EdgeError(pair)
        u, v = pair
        self.adjacent[u].append(v)
        if not directed:
            self.adjacent[v].append(u)

    def _rm_edge(self, pair: List[int], directed: bool = True) -> None:
        """
        Remove an edge (u,v) from the graph. If directed == False, remove (v,u) by the way.
        Do nothing if the target does not exist.
        """
        def rm(u: int, v: int) -> None:
            try:
                self.adjacent[u].remove(v)
            except ValueError:
                pass

        if len(pair) != 2 or pair[0] == pair[1]:
            raise EdgeError(pair)
        u, v = pair
        rm(u,v)
        if not directed:
            rm(v,u)

    # The two methods below are the real interfaces exposed to the user
    def add_edge(self, pair: List[int]) -> None:
        self._add_edge(pair, directed=False)

    def rm_edge(self, pair: List[int]) -> None:
        self._rm_edge(pair, directed=False)

    def deduplicate(self) -> None:
        """Remove the duplicated edges"""
        for i in self.vertices:
            self.adjacent[i] = list(set(self.adjacent[i]))

    def count_cc(self) -> int:
        """
        Count the number of the connected components by DFS. T(m,n) = O(m+n)
        """
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

    def getindeg(self) -> List[int]:
        """
        Get the in-degree of each vertex in V(G)
        """
        indegree = [0] * self.v
        for v in self.vertices:
            for u in self.adjacent[v]:
                indegree[u] += 1
        return indegree

    def NoOddCycle(self) -> bool:
        """
        Decide whether it contains no odd cycle.
        Return True if and only if the graph is bipartite, i.e. 2-colorable.
        """
        # Color the vertices greedily
        colored = [0] * self.v
        colored[0] = 1
        q = list()
        q.append(0)

        while q:
            v = q.pop(0)
            c = colored[v]
            for u in self.adjacent[v]:
                if colored[u] == 0:
                    colored[u] = - c
                    q.append(u)
                elif colored[u] == c:
                    return False
        return True

    def isTree(self) -> bool:
        """
        As for deciding whether the graph G is a tree, the following are equal:
        - G is a connected acyclic graph (definition)
        - G is a minimal connected graph
        - G is a maximal acyclic graph
        - e(G) = n - 1 and it is connected (implementation)
        - e(G) = n - 1 and it is acyclic
        """
        return self.e == self.v - 1 and self.connected

class DirectedGraph(Graph):

    """
    The directed graph class, with unweighted edges
    """

    def __init__(self, vnum: int = 1, edges: List[List[int]] = [], dedu: bool = True) -> None:
        self.vertices = list(range(vnum))
        self.adjacent: List[List[int]] = [[] for _ in range(vnum)] 

        for pair in edges:
            self.add_edge(pair)

        if dedu:
            self.deduplicate()

    @classmethod
    def fromrandom(cls, vnum: int = 7, elimit: int = 10, seed: int = 42):
        # This works because the cls argument in super().fromrandom(...) 
        # takes DirectedGraph rather than Graph
        return super().fromrandom(vnum, elimit, seed)

    def display(self) -> None:
        wcc = self.count_cc()
        print(f'v(G) = {self.v}, e(G) = {self.e}, weak connected components = {wcc}')
        if wcc == 1 and self.StronglyConnected():
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
        """The number of directed edges in the graph"""
        return sum(len(self.adjacent[i]) for i in self.vertices)

    def add_edge(self, pair: List[int]) -> None:
        """Add a directed edge."""
        return super()._add_edge(pair)

    def rm_edge(self, pair: List[int]) -> None:
        """Remove a directed edge (u,v) from the graph."""
        return super()._rm_edge(pair)

    def count_cc(self) -> int:
        """Count the number of weak connected components"""
        return super().count_cc()

    def getindeg(self) -> List[int]:
        # Another approach to calculate the in-degrees is using
        # the inverse graph, which may consume extra memory.
        return super().getindeg()

    def StronglyConnected(self) -> bool:
        '''
        The graph is strongly connected if and only if 
        both it and its inverse are weakly connected.
        Consider any pair of vertices (u,v) and the paths between them.
        '''
        if self.count_cc() > 1 or inverse(self).count_cc() > 1:
            return False
        return True

    def topo(self) -> List[int]:
        """
        Find the possible topological order of the vertices by DFS. T(m,n) = O(m+n)
        """
        visited = [False] * self.v
        res: List[int] = list()

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
        Decide whether it is a directed acyclic graph.
        Return True if and only if the topological order is valid.
        - If there is a cycle, then the vertices in it cannot fit into the topo order.
        - Conversely, if it is a DAG, take a maximal path inside and we assert that 
        the in-degree of the start vertex must be zero because it has no neighbor in 
        or out of the path. After removing it, we can apply induction on v(G).

        The time complexity is reduced to O(m+n) after optimization.
        """
        indegree = self.getindeg()
        
        for v in self.topo():
            if indegree[v] > 0:
                return False
            for u in self.adjacent[v]:
                indegree[u] -= 1
        return True

def complement(g: Graph) -> Graph:
    """
    Return the complement graph of g
    - There is at least one connected graph among g and g^c
    """
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

    c = Graph.cycle(4)
    c.display()
    print(c.NoOddCycle())
    c.add_edge([0,2])
    print(c.NoOddCycle())

    dg = DirectedGraph.fromrandom(12,30,23938)
    dg.display()
    inv = inverse(dg)
    inv.display()

    # t = DirectedGraph(5,[[0,1],[1,2],[3,4],[4,2]])
    # print(t.topo(), t.isDAG())
    # t.add_edge([2,0])
    # print(t.topo(), t.isDAG())