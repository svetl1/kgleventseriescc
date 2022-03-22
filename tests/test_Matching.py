import unittest
from py2neo import Graph
import re
import date_parser2
import requests

import matchAndExtract
import parsingUtils
from matchAndExtract import CCtoGraph

class testGraph():
    graph = Graph("bolt://localhost:7687", auth=("", ""))
    myGraph = matchAndExtract.CCtoGraph(graph)
    myGraph.getAndAddAll("SAST")
