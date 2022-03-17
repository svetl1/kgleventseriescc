import re
import date_parser2
from py2neo import Graph
import requests
import ptp

graph = Graph("bolt://localhost:7687", auth=("", ""))

months = ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', '-', 'May', 'June', 'Jun', 'July', 'Jul', 'August', 'Aug', 'September', 'Sep', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']
parser = ptp.Ptp()

class CCtoGraph:
	def __init__(self, graph: Graph):
		self.graph = graph
		self.acronyms = []

	def addEvent(self, event: dict, source):
		event['matches'] = "empty"
		event['numOfRel'] = 0
		query = f"""
		MERGE (e:Event:{source} {{eventId:$event.eventId}})
		ON CREATE SET e = $event
		ON MATCH SET e += $event
		"""
		params = {"event": event}
		qres = self.graph.run(query, params)
		return qres

	def normalizeAcronym(self, acronymString):
		listForAcronym = re.split(r'[., \-:]+', acronymString)
		for element in listForAcronym:
			if (element.isupper()):
				return element

	def normalizeCityId(self, cityIdString):
		return cityIdString.replace('http://www.wikidata.org/entity/', '')

	def normalizeDate(self, dateString):
		dateList = re.split(r'[., \-]+', dateString)
		months_found = [m for m in dateList if m in months]
		i = dateList.index(months_found[0])
		if (dateList[i - 1].isdigit() and len(dateList[i - 1]) < 3):
			if(dateList[i-1][0] == "0"): #remove leading zero
				dateList[i-1] = dateList[i-1][1:]
			monthDay = months_found[0][0:3] + " " + dateList[i - 1]
		else:
			if (dateList[i + 1][0] == "0"):  # remove leading zero
				dateList[i + 1] = dateList[i+1][1:]
			monthDay = months_found[0][0:3] + " " + dateList[i + 1].lstrip('0')
		print(monthDay)
		return monthDay

	def normalizeNumToDate(self, dateString):
		dateList = re.split(r'[-]', dateString)
		monthDay = months[(int(dateList[1]) * 2) - 1] + " " + dateList[2].lstrip('0')
		return monthDay

	def addAll(self):
		if (self.wikicfpRecords is not None):
			for record in self.wikicfpRecords:
				record['ordinal'] = parser.guessOrdinal(record)
				if (record.get("startDate") is not None):
					record['startDate'] = self.normalizeDate(record.get("startDate"))
				if (record.get("endDate") is not None):
					record['endDate'] = self.normalizeDate(record.get("endDate"))
				if (record.get("acronym") is not None):
					record['acronym'] = self.normalizeAcronym(record.get("acronym"))
				if (record.get("locality") is not None):
					localityData = re.split(r",\s|/|/\s", record.get("locality"))
					if (record.get("city") is None):
						record['city'] = localityData[0]
					if (record.get("country") is None):
						record['country'] = localityData[len(localityData) - 1]
				# print(str(record['locality'] or '-') + "  city: " + str(record['city'] or '-') + " country: " + str(record['country'] or '-'))
				self.addEvent(record, "wikiCFP")

		if (self.dblpRecords is not None):
			for record in self.dblpRecords:
				if (record.get("acronym") is not None):
					record['acronym'] = self.normalizeAcronym(record.get("acronym"))

				record['ordinal'] = (parser.guessOrdinal(record))

				if (record.get("title") is not None):
					results = date_parser2.dateParser(record.get("title"))
					if (results is not None):
						record['startDate'] = results['startDate']
						record['endDate'] = results['endDate']
					if(record.get("title").find("Workshop") == -1 and record.get("title").find("Workshops") == -1):
						idList = re.split(r'[-]', record.get("eventId"))
						if(len(idList) > 1 and idList[1].isnumeric()):
							if(int(idList[1]) < 2):
								self.addEvent(record, "DBLP")
						else:
							self.addEvent(record, "DBLP")


		if (self.crossrefRecords is not None):
			for record in self.crossrefRecords:
				if(record.get("number") is None):
					record["ordinal"] = parser.guessOrdinal(record)
				else:
					record["ordinal"] = record['number']
				if (record.get("startDate") is not None):
					record['startDate'] = self.normalizeDate(record.get("startDate"))
				if (record.get("endDate") is not None):
					record['endDate'] = self.normalizeDate(record.get("endDate"))
				if (record.get("acronym") is not None):
					record['acronym'] = self.normalizeAcronym(record.get("acronym"))
				if (record.get("location") is not None and not record.get("location") == "Not Known"):
					locationData = re.split(r",\s|/|/\s", record.get("location"))
					if (record.get("city") is None):
						record['city'] = locationData[0]
					if (record.get("country") is None):
						record['country'] = locationData[len(locationData) - 1]
				'''if (record.get("title") is None or (
						record.get("title").find("Proceedings") == -1 and record.get("title").find(
						"Proceeding") == -1)):'''
				self.addEvent(record, "crossref")
			# print(str(record['location'] or '-') + "  city: " + str(record['city'] or '-') + " country: " + str(
			# record['country'] or '-') + "TITLE: " + record['title'])

		if (self.wikidataRecords is not None):
			for record in self.wikidataRecords:
				if (record.get("acronym") is not None):
					record['acronym'] = self.normalizeAcronym(record.get("acronym"))
				if (record.get("cityId") is not None):
					record['cityWikidataid'] = self.normalizeCityId(record.get("cityId"))
				if (record.get("startDate") is not None):
					record['startDate'] = self.normalizeDate(record.get("startDate"))
				if (record.get("endDate") is not None):
					record['endDate'] = self.normalizeDate(record.get("endDate"))
				if (record.get("city") is None):
					if (record.get("location") is not None):
						record['city'] = record.get("location")
				self.addEvent(record, "wikiData")

		if (self.confrefRecords is not None):
			for record in self.confrefRecords:
				if (record.get("startDate") is not None):
					record['startDate'] = self.normalizeNumToDate(record.get("startDate"))
				if (record.get("endDate") is not None):
					record['endDate'] = self.normalizeNumToDate(record.get("endDate"))
				self.addEvent(record, "confref")
		# print(str(record['location'] or '-') + "  city: " + str(record['city'] or '-') + " country: " + str(
		# record['country'] or '-') + "TITLE: " + record['title'])

	queryCondition = "NOT exists((n)-[]-(:Acronym)) AND NOT exists((m)-[]-(:Acronym))"

	def filterAcronym(self):
		query = f'''MATCH(n: Event) WHERE NOT exists((n)-[]-(:Acronym)) AND (NOT n.acronym = "{self.acronym}" OR n.acronym IS NULL) DETACH DELETE n'''
		self.graph.run(query)

	def locationRelation(self):
		query = f'''MATCH(n: Event) MATCH(m: Event) 
		WHERE {self.queryCondition}
		AND n.country = m.country 
		AND n.city = m.city
		AND NOT m.source = n.source
		MERGE(n) - [r: same_location]-(m)
		ON CREATE SET n.numOfRel = n.numOfRel +1, m.numOfRel = m.numOfRel +1
		RETURN *'''
		self.graph.run(query)

	def dayMonthRelation(self):
		query = f'''MATCH(n:Event)
		MATCH(m:Event) 
		WHERE {self.queryCondition}
		AND n.startDate = m.startDate 
		AND n.endDate = m.endDate
		AND NOT n.source = m.source
		MERGE(n)-[r:same_dayMonth]-(m)
		ON CREATE SET n.numOfRel = n.numOfRel +1, m.numOfRel = m.numOfRel +1
		RETURN *'''
		self.graph.run(query)

	def ordinalRelation(self):
		query = f'''MATCH(n:Event)
		MATCH(m:Event) 
		WHERE {self.queryCondition}
		AND n.ordinal = m.ordinal
		AND NOT n.source = m.source
		MERGE(n)-[r:same_ordinal]-(m)
		ON CREATE SET n.numOfRel = n.numOfRel +1, m.numOfRel = m.numOfRel +1
		RETURN *'''
		self.graph.run(query)

	def yearRelation(self):
		query = f'''MATCH(n:Event)
		MATCH(m:Event) 
		WHERE {self.queryCondition}
		AND n.year = m.year
		AND NOT n.source = m.source
		MERGE(n)-[r:same_year]-(m)
		ON CREATE SET n.numOfRel = n.numOfRel +1, m.numOfRel = m.numOfRel +1
		RETURN *'''
		self.graph.run(query)

	def filterYear(self):
		query = f'''MATCH (n:Event)-[r]-(m:Event)
		WHERE {self.queryCondition}
		AND NOT (n) =(m) 
		AND NOT (n)-[:same_year]-(m)
		AND n.year > m.year
		SET n.numOfRel = n.numOfRel -1, m.numOfRel = m.numOfRel -1
		DELETE r'''
		self.graph.run(query)

	def firstElimination(self):
		query = f'''MATCH (n:Event)-[]-()-[]-(m:Event {{source:n.source}})
		WHERE {self.queryCondition}
		AND NOT (n) = (m)
		AND n.numOfRel < m.numOfRel
		WITH distinct(n) as d
		DETACH DELETE d'''
		self.graph.run(query)

	def resetGraph(self):
		query = '''match ()-[r]-() delete r'''
		self.graph.run(query)
		query = '''match (n) DELETE n'''
		self.graph.run(query)

	def match(self, numberOfRelations):
		query = f'''MATCH (n:Event) MATCH (m:Event) 
		WHERE {self.queryCondition}
		AND size((n)-[]-(m)) = {numberOfRelations} 
		AND NOT n.matches contains m.source 
		AND NOT m.matches contains n.source 
		MERGE (n)-[:SAME]-(m) ON CREATE SET n.matches = n.matches + m.source, m.matches = m.matches + n.source'''
		self.graph.run(query)

	def eliminateNonMatch(self):
		query = '''MATCH (n:Event) WHERE exists((n)-[]-(:Event)) 
					AND NOT exists ((n)-[:SAME]-()) 
					DETACH DELETE n'''
		self.graph.run(query)

	def bindToAcronym(self):
		query = f'''CREATE (a:Acronym {{Id: "{self.acronym}"}})'''
		self.graph.run(query)

		query = f'''MATCH (n:Acronym{{Id : "{self.acronym}"}}) MATCH (m:Event) 
		WHERE NOT exists((m)-[]-(:Acronym)) MERGE (m)-[:acronym]-(n)'''
		self.graph.run(query)

	def startMatching(self, acronym):
		if(not acronym in self.acronyms):
			self.acronyms.append(acronym)
		else:
			print(acronym + " already in graph")
			return
		self.acronym = acronym
		res = requests.get("https://conferencecorpus.bitplan.com/eventseries/" + acronym)
		lods = res.json()
		self.wikidataRecords = lods.get("wikidata")
		self.wikicfpRecords = lods.get("wikicfp")
		self.dblpRecords = lods.get("dblp")
		self.confrefRecords = lods.get("confref")
		self.crossrefRecords = lods.get("crossref")
		self.addAll()
		self.filterAcronym()
		self.locationRelation()
		self.dayMonthRelation()
		self.ordinalRelation()
		self.yearRelation()
		self.filterYear()
		self.firstElimination()
		self.match(4)
		self.match(3)
		self.match(2)
		self.match(1)
		self.eliminateNonMatch()
		#self.bindToAcronym()

myGraph = CCtoGraph(graph)
myGraph.resetGraph()
myGraph.startMatching("DEXA")




