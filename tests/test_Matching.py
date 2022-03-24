import unittest
from py2neo import Graph
import matchAndExtract


class TestGraph(unittest.TestCase):
    def test_Adding(self):
        graph = Graph("bolt://localhost:7687", auth=("", ""))
        myGraph = matchAndExtract.CCtoGraph(graph)
        myGraph.resetGraph()
        myGraph.getAndAddAll("SAST")
        qres = '''MATCH (n) return count(n) as count'''
        count = graph.run(qres).data()[0].get("count")
        self.assertEqual(count, 26, "the event-nodes should equals 26")

if __name__ == '__main__':
    unittest.main()
