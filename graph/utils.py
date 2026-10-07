"""
The utilities and auxiliary functions used in the package, including:
- Exceptions: EdgeError
- Type hint templates: Comparable
- Data structures: FindUnionSet
"""

from typing import List, TypeVar, Protocol

class EdgeError(Exception):
    def __init__(self, pair: List[int], *args: object) -> None:
        self.pair = pair

    def __str__(self) -> str:
        return f'Each edge must have exactly two different ends, got {self.pair}'

class NodeError(Exception):
    def __init__(self, n1, n2, *args: object) -> None:
        self.t1, self.t2 = type(n1), type(n2)

    def __str__(self) -> str:
        return f"Two adjacent nodes must be of the same type, got {self.t1} and {self.t2}"

class Comparable(Protocol):
    def __lt__(self, other: 'Comparable') -> bool: ...
    def __gt__(self, other: 'Comparable') -> bool: ...
    def __le__(self, other: 'Comparable') -> bool: ...
    def __ge__(self, other: 'Comparable') -> bool: ...
    def __eq__(self, other: object) -> bool: ...

# The supported value types in a node, only integers and strings for now.
NodeValue = TypeVar('NodeValue', bound=int|str)