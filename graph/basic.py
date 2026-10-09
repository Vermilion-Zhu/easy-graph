import random
from pprint import pp
from typing import List, Dict, Tuple

from utils import EdgeError, EdgeType

DELIMITER = '-' * 10

class Graph:
    """
    The basic type of undirected graphs. 
    duplicate edges are allowed but not recommended.

    Set m = e(G) and n = v(G) when analyzing the time complexity of algorithms.
    """

    def __init__(self, vnum: int = 1, edges: List[EdgeType] = [], dedu: bool = True) -> None:
        self.vertices = list(range(vnum))
        self.adjacent: List[List[int]] = [[] for _ in range(vnum)] 

        for pair in edges:
            self._add_edge(pair, directed=False)
        
        # It is optional to remove the duplicate edges in the adjacent matrix,
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
            # This unnecessary step is the result of
            # giving in to the static type checker...
            l = random.sample(vertices, k=2)
            edges.append((l[0], l[1]))
        return cls(vnum, edges)

    @classmethod
    def complete(cls, n: int):
        """Generate a complete graph K_n"""
        edges = [(i,j) for i in range(n) for j in range(i+1,n)]
        return cls(n, edges, dedu=False)

    @classmethod
    def cycle(cls, n: int):
        """Generate a cycle C_n"""
        edges = [(i, (i+1) % n) for i in range(n)]
        return cls(n, edges, dedu=False)

    def display(self) -> None:
        print(f'v(G) = {self.v}, e(G) = {self.e}, connected components = {self.count_cc()}')
        print(DELIMITER)
        for i in self.vertices:
            print(f'{i}: {self.adjacent[i]}')
        print(DELIMITER)

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
    # then the derived classes cannot access it by super().__add_edge(...)
    # Otherwise it would raise an AttributeError that the base class
    # has no attribute '_DirectedGraph__add_edge'
    def _add_edge(self, pair: EdgeType, directed: bool = True) -> None:
        """Add a (directed) edge (u,v) to the graph"""
        if len(pair) != 2 or pair[0] == pair[1]:
            raise EdgeError(pair)
        u, v = pair
        self.adjacent[u].append(v)
        if not directed:
            self.adjacent[v].append(u)

    def _rm_edge(self, pair: EdgeType, directed: bool = True) -> None:
        """
        Remove an edge (u,v) from the graph. If directed == False, remove (v,u) by the way.
        Do nothing if the target does not exist.
        """
        def rm(u: int, v: int) -> None:
            try:
                self.adjacent[u].remove(v)
            except (ValueError, IndexError):
                pass

        if len(pair) != 2 or pair[0] == pair[1]:
            raise EdgeError(pair)
        u, v = pair
        rm(u,v)
        if not directed:
            rm(v,u)

    # The two methods below are the real interfaces exposed to the user
    def add_edge(self, pair: EdgeType) -> None:
        self._add_edge(pair, directed=False)

    def rm_edge(self, pair: EdgeType) -> None:
        self._rm_edge(pair, directed=False)

    def deduplicate(self) -> None:
        """Remove the duplicate edges"""
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

    def induce(self, H: List[int] = [0]):
        """
        Return the subgraph induced by the given vertex list H.
        The out-of-range or duplicate vertices will be ignored.
        """
        # pre-process
        vset = set(H)
        vlist = [v for v in vset if v < self.v] # pre-process
        posmap = {v: i for i, v in enumerate(vlist)}
        edges: List[EdgeType] = list()

        for u in self.vertices:
            if u in vset:
                for v in self.adjacent[u]:
                    if v in vset:
                        edges.append((posmap[u], posmap[v]))
        return Graph(len(vlist), edges)

    def SpanningTree(self):
        """
        Return a spanning tree of the graph if it is connected.
        Otherwise raise a ValueError
        - Every connected graph has a spanning tree.
        """
        if not self.connected:
            raise ValueError("The given graph is not connected.")
        
        edges: List[EdgeType] = list()
        seen = [False] * self.v
        q: List[int] = list()

        q.append(0)
        seen[0] = True
        while q:
            front = q.pop(0)
            for v in self.adjacent[front]:
                if not seen[v]:
                    edges.append((front, v))
                    q.append(v)
                    seen[v] = True
        res = Graph(self.v, edges)
        assert(res.isTree()) # for debugging
        return res

class DirectedGraph(Graph):
    """
    The directed graph class, with unweighted edges
    """

    def __init__(self, vnum: int = 1, edges: List[EdgeType] = [], dedu: bool = True) -> None:
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

        print(DELIMITER)
        for i in self.vertices:
            print(f'{i}: {self.adjacent[i]}')
        print(DELIMITER)

    @property
    def v(self) -> int:
        return super().v
    @property
    def e(self) -> int:
        """The number of directed edges in the graph"""
        return sum(len(self.adjacent[i]) for i in self.vertices)

    def add_edge(self, pair: EdgeType) -> None:
        """Add a directed edge."""
        return super()._add_edge(pair)

    def rm_edge(self, pair: EdgeType) -> None:
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
        - Consider any pair of vertices (u,v) and the paths between them.
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

        The time complexity has been reduced to O(m+n) after optimization.
        """
        indegree = self.getindeg()
        
        for v in self.topo():
            if indegree[v] > 0:
                return False
            for u in self.adjacent[v]:
                indegree[u] -= 1
        return True

class WeightedGraph(Graph):
    """
    Undirected weighted graph class.
    duplicate edges are NOT recommended since the weights are saved a in dictionary that
    uses the tuple of the ends of each edge as its key.
    """

    def __init__(self, vnum: int = 1, edges: List[EdgeType] = [], dedu: bool = True,
                 weights: List[int] = []) -> None:
        """
        Return a graph with given weights. Note that default value 1 will be used
        when there are not enough weights for the edges. On the other hand, 
        the overlong part may be truncated.
        """
        self.vertices = list(range(vnum))
        self.adjacent: List[List[int]] = [[] for _ in range(vnum)] 
        self.weights: Dict[EdgeType, int] = dict()

        for i, pair in enumerate(edges):
            w = weights[i] if i < len(weights) else 1
            self.add_edge(pair, weight=w)
        if dedu:
            self.deduplicate()

    @classmethod
    def fromrandom(cls, vnum: int = 7, elimit: int = 10, seed: int = -1, a: int = 1, b: int = 10):
        """
        Generate a graph with random edges and weights.
        - Weights are sampled in the close interval [a,b].
        """
        res = super().fromrandom(vnum, elimit, seed)
        for i in res.vertices:
            for j in res.adjacent[i]:
                n = random.randint(a,b)
                res.weights[(i,j)] = n
                res.weights[(j,i)] = n
        return res # Remember to return the result after reloading a method from the base class

    @classmethod
    def fromUnweighted(cls, g: Graph):
        """Assign weight 1 to the edges of an unweighted graph `g`"""
        vnum = g.v
        edges: List[EdgeType] = list()

        for i in g.vertices:
            for j in g.adjacent[i]:
                edges.append((i,j))
        return cls(vnum, edges)
    
    # These two private methods are reserved for the upcoming DirectedWeightedGraph class.
    def _add_edge(self, pair: EdgeType, directed: bool = True, weight: int = 1) -> None:
        super()._add_edge(pair, directed=False)
        self.weights[pair] = self.weights.get(pair,0) + weight
        rev = (pair[1],pair[0])
        if not directed:
            self.weights[rev] = self.weights.get(rev,0) + weight

    def _rm_edge(self, pair: EdgeType, directed: bool = True) -> None:
        super()._rm_edge(pair, directed=False)
        if pair in self.weights:
            del self.weights[pair]

        if not directed and (rev := (pair[1],pair[0])) in self.weights:
            del self.weights[rev]

    def add_edge(self, pair: EdgeType, weight: int = 1) -> None:
        """Add an undirected weighted edge."""
        return self._add_edge(pair, directed=False, weight=weight)
    def rm_edge(self, pair: EdgeType) -> None:
        """Remove an undirected weighted edge."""
        return self._rm_edge(pair, directed=False)

    def display(self) -> None:
        super().display()
        pp(self.weights)
        print(DELIMITER)

def complement(g: Graph) -> Graph:
    """
    Return the complement graph of g
    - There is at least one connected graph among g and g^c
    """
    vnum = g.v
    res = Graph.complete(vnum)
    for i in range(vnum):
        for j in g.adjacent[i]:
            res.rm_edge((i,j))
    return res

def inverse(dg: DirectedGraph) -> DirectedGraph:
    vnum = dg.v
    res = DirectedGraph(vnum)
    for i in range(vnum):
        for j in dg.adjacent[i]:
            res.add_edge((j,i))
    return res

if __name__ == "__main__":
    g = Graph.fromrandom(12,100,23938)
    g.display()
    # gc = complement(g)
    # gc.display()
    # ug = WeightedGraph.fromUnweighted(g)
    # ug.display()
    # ug.add_edge((1,2),10)
    # ug.display()

    # rug = WeightedGraph.fromrandom(12,10,23938)
    # rug.display()
    # rug.add_edge((1,2),50)
    # rug.rm_edge((9,10))
    # rug.display()

    # invalid = Graph(7, [(1,1)])
    # k = Graph.complete(10)
    # k.display()

    # c = Graph.cycle(4)
    # c.display()
    # print(c.NoOddCycle())
    # c.add_edge((0,2))
    # print(c.NoOddCycle())

    # dg = DirectedGraph.fromrandom(12,30,23938)
    # dg.display()
    # inv = inverse(dg)
    # inv.display()

    # t = DirectedGraph(5,[(0,1),(1,2),(3,4),(4,2)])
    # print(t.topo(), t.isDAG())
    # t.add_edge((2,0))
    # print(t.topo(), t.isDAG())
    gid = g.induce(list(range(0,12,2)))
    gid.display()
    gt = g.SpanningTree()
    gt.display()
    assert(gt.isTree())