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
			monthDay = months_found[0][0:3] + " " + dateList[i + 1]
		return monthDay

	def normalizeNumToDate(self, dateString):
		dateList = re.split(r'[-]', dateString)
		if (dateList[2][0] == "0"):  # remove leading zero
			dateList[2] = dateList[2][1:]
		monthDay = months[(int(dateList[1]) * 2) - 1] + " " + dateList[2]
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
				if (record.get("locality") is not None): # get location data from locality if city or country is None
					localityData = re.split(r",\s|/|/\s", record.get("locality")) # inside r"" are the regular expressions to look for split with | . \s stay for white space as expression
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

				record['ordinal'] = parser.guessOrdinal(record)
				if (record.get("title") is not None):
					results = date_parser2.dateParser(record.get("title"))
					if (results is not None):
						record['startDate'] = results['startDate']
						record['endDate'] = results['endDate']
					if(record.get("title").find("Workshop") == -1 and record.get("title").find("Workshops") == -1):
						idList = re.split(r'[-]', record.get("eventId"))
						record['title'] = parser.parseTitle(record.get("title"), record.get("acronym"),
															str(record.get("year")))


						if(len(idList) > 1 and idList[1].isnumeric()):
							if(int(idList[1]) < 2):
								self.addEvent(record, "DBLP")
								#print(record.get("title"))
						else:
							self.addEvent(record, "DBLP")
							#print(record.get("title"))



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
		query = f'''MATCH(n: Event) WHERE NOT exists((n)-[]-(:Acronym)) AND NOT n.acronym = "{self.acronym}" OR n.acronym IS NULL DETACH DELETE n'''
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
		query = f'''MATCH (n:Event) WHERE NOT exists((n)-[]-(:Acronym)) 
					AND exists((n)-[]-(:Event))
					AND NOT exists ((n)-[:SAME]-()) 
					DETACH DELETE n'''
		self.graph.run(query)

	def bindToAcronym(self):
		query = f'''CREATE (a:Acronym {{Id: "{self.acronym}"}})'''
		self.graph.run(query)

		query = f'''MATCH (n:Acronym{{Id : "{self.acronym}"}}) MATCH (m:Event) 
		WHERE NOT exists((m)-[]-(:Acronym)) MERGE (m)-[:acronym]-(n)'''
		self.graph.run(query)

	def setForExtraction(self):
		query = f'''MATCH (n:Event) WHERE n.acronym = "{self.acronym}"
			Set n.ordinalRel = size((n)-[:same_ordinal]-()) + (CASE WHEN n.ordinal is Null then 0 else 1 END) , 
			n.locationRel = size((n)-[:same_location]-()) + (CASE WHEN n.city is NULL and n.country is NULL then 0 else 1 END), 
			n.dayMonthRel = size((n)-[:same_dayMonth]-()) + (CASE WHEN n.startDate is Null and n.endDate is Null then 0 else 1 END)'''
		graph.run(query)

	def extractLocation(self, year, acronym):
		query = f'''MATCH (n:Event{{year:{year}}}) WHERE n.acronym = "{acronym}"
				RETURN n.city, n.country order by n.locationRel descending Limit 1'''
		res = graph.run(query).data()
		if(len(res) < 1):
			return None
		else:
			return res[0]

	def extractOrdinal(self, year, acronym):
		query = f'''MATCH (n:Event{{year:{year}}}) WHERE n.acronym = "{acronym}"
						RETURN n.ordinal order by n.ordinalRel descending Limit 1'''
		res = graph.run(query).data()
		if(len(res) < 1):
			return None
		else:
			return res[0]


	def extractMonthDay(self, year, acronym):
		query = f'''MATCH (n:Event{{year:{year}}}) WHERE n.acronym = "{acronym}"
							RETURN n.startDate, n.endDate order by n.monthDayRel descending Limit 1'''
		res = graph.run(query).data()
		if(len(res) < 1):
			return None
		else:
			return res[0]

	def extractTitle(self, year, acronym):
		query = f'''MATCH (n:Event{{year:{year}}}) WHERE n.acronym = "{acronym}"
						AND n.source = "confref"
						RETURN n.title order by n.numOfRel descending Limit 1'''
		res = graph.run(query).data()
		if (len(res) > 0 and res[0].get("n.title") is not None):
			res = res[0]
			title = re.sub('\(|\)', '', res.get("n.title"))
			res['n.title'] = re.sub(acronym, '', title)
			return res
		else:
			query = f'''MATCH (n:Event{{year:{year}}}) WHERE n.acronym = "{acronym}"
							AND n.source = "dblp"
							RETURN n.title order by n.numOfRel descending Limit 1'''
			res = graph.run(query).data()
			if (len(res) > 0 and res[0].get("n.title") is not None):
				res = res[0]
				return res
			else:
				return None


	def extractProperties(self, acronym: str):
		query = f'''MATCH (n:Event) WHERE n.acronym = "{acronym}"
		RETURN distinct n.year Order by n.year'''
		res = self.graph.run(query)
		years = res.data()
		for yearElement in years:
			year = yearElement.get("n.year")
			if(year is not None):
				location = self.extractLocation(year, acronym)
				ordinal = self.extractOrdinal(year, acronym)
				monthDay = self.extractMonthDay(year, acronym)
				title = self.extractTitle(year, acronym)
				print(title or '-')
				print(location or '-')
				print(ordinal or '-')
				print(monthDay or '-')

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
		self.dayMonthRelation()
		self.locationRelation()
		self.ordinalRelation()
		self.yearRelation()
		self.filterYear()
		self.firstElimination()
		self.match(4)
		self.match(3)
		self.match(2)
		self.match(1)
		self.eliminateNonMatch()
		self.setForExtraction()
		self.bindToAcronym()


	def startExtracting(self, acronym):

		self.extractProperties(acronym)


myGraph = CCtoGraph(graph)
myGraph.resetGraph()
#myGraph.startMatching("RTA")
#myGraph.startMatching("ISCAS")
#myGraph.startMatching("DEXA")
myGraph.startMatching("ISCA")
#myGraph.startMatching("ISCAS")
#myGraph.startMatching("AAAI")


myGraph.startExtracting("ISCA")




