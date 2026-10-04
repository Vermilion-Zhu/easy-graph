import argparse
from graph.basic import Graph

def testparser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(description='The parser for basic graph test')
    parser.add_argument('--vnum', '-v', type=int, default=10, help='the number of vertices')
    parser.add_argument('--seed', '-s', type=int, default=42, help='the seed to initialize a random graph')
    parser.add_argument('--limit', '-l', type=int, default=10, help='the maximum number of edges')

    return parser

args = testparser().parse_args()

g = Graph.fromrandom(vnum=args.vnum, elimit=args.limit, seed=args.seed)
g.display()