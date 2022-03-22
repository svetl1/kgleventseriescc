from py2neo import Graph

from matching import matchAndExtract


class testGraph():
    graph = Graph("bolt://localhost:7687", auth=("", ""))
    myGraph = matchAndExtract.CCtoGraph(graph)
    myGraph.getAndAddAll("SAST")
