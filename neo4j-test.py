import re
import date_parser2
from py2neo import Graph
import requests
graph = Graph("bolt://localhost:7687", auth=("", ""))

months = ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', '-', 'May', 'June', 'Jun', 'July', 'Jul', 'August', 'Aug', 'September', 'Sep', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']


def addEvent(event: dict, source):
		event['matches'] = "empty"
		query=f"""
		MERGE (e:Event:{source} {{eventId:$event.eventId}})
		ON CREATE SET e = $event
		ON MATCH SET e += $event
		"""
		params = {"event": event}
		qres = graph.run(query, params)
		return qres

def normalizeAcronym(acronymString):
	listForAcronym= re.split(r'[., \-:]+', acronymString)
	for element in listForAcronym:
		if(element.isupper()):
			return element

def normalizeCityId(cityIdString):
	return cityIdString.replace('http://www.wikidata.org/entity/', '')

def normalizeDate(dateString):
	dateList = re.split(r'[., \-]+', dateString)
	months_found = [m for m in dateList if m in months]
	i = dateList.index(months_found[0])
	if(dateList[i-1].isdigit() and len(dateList[i-1]) < 3):
		monthDay = months_found[0][0:3] + " " + dateList[i-1].lstrip('0')
	else:
		monthDay = months_found[0][0:3] + " " + dateList[i+1].lstrip('0')
	return monthDay

def normalizeNumToDate(dateString):
	dateList = re.split(r'[-]', dateString)
	monthDay = months[(int(dateList[1])*2) - 1] + " " + dateList[2].lstrip('0')
	return monthDay

acronym = "ISCA"
res = requests.get("https://conferencecorpus.bitplan.com/eventseries/" + acronym)
lods = res.json()
wikidataRecords = lods.get("wikidata")
wikicfpRecords = lods.get("wikicfp")
dblpRecords = lods.get("dblp")
confrefRecords = lods.get("confref")
crossrefRecords = lods.get("crossref")


if(wikicfpRecords is not None):
	for record in wikicfpRecords:
		if (record.get("startDate") is not None):
			record['startDate'] = normalizeDate(record.get("startDate"))
		if (record.get("endDate") is not None):
			record['endDate'] = normalizeDate(record.get("endDate"))
		if (record.get("acronym") is not None):
			record['acronym'] = normalizeAcronym(record.get("acronym"))
		if(record.get("locality") is not None):
			localityData = re.split(r",\s|/|/\s", record.get("locality"))
			if(record.get("city") is None):
				record['city'] = localityData[0]
			if(record.get("country") is None):
				record['country'] =localityData[len(localityData) - 1]
		#print(str(record['locality'] or '-') + "  city: " + str(record['city'] or '-') + " country: " + str(record['country'] or '-'))
		addEvent(record, "wikiCFP")


if(dblpRecords is not None):
	for record in dblpRecords:
		if (record.get("acronym") is not None):
			record['acronym'] = normalizeAcronym(record.get("acronym"))
		if(record.get("title") is not None):
			results = date_parser2.dateParser(record.get("title"))
			if(results is not None):
				record['startDate'] = results['startDate']
				record['endDate'] = results['endDate']
		if(record.get("title") is None or (record.get("title").find("Proceedings") == -1 and record.get("title").find("Proceeding") == -1) ):
			addEvent(record, "DBLP")

if(crossrefRecords is not None):
	for record in crossrefRecords:
		if (record.get("startDate") is not None):
			record['startDate'] = normalizeDate(record.get("startDate"))
		if (record.get("endDate") is not None):
			record['endDate'] = normalizeDate(record.get("endDate"))
		if (record.get("acronym") is not None):
			record['acronym'] = normalizeAcronym(record.get("acronym"))
		if (record.get("location") is not None and not record.get("location") == "Not Known"):
			locationData = re.split(r",\s|/|/\s", record.get("location"))
			if (record.get("city") is None):
				record['city'] = locationData[0]
			if (record.get("country") is None):
				record['country'] = locationData[len(locationData) - 1]
		if(record.get("title") is None or (record.get("title").find("Proceedings") == -1 and record.get("title").find("Proceeding") == -1) ):
			addEvent(record, "crossref")
			#print(str(record['location'] or '-') + "  city: " + str(record['city'] or '-') + " country: " + str(
			#record['country'] or '-') + "TITLE: " + record['title'])


if(wikidataRecords is not None):
	for record in wikidataRecords:
		if (record.get("acronym") is not None):
			record['acronym'] = normalizeAcronym(record.get("acronym"))
		if(record.get("cityId") is not None):
			record['cityWikidataid'] = normalizeCityId(record.get("cityId"))
		if (record.get("startDate") is not None):
			record['startDate'] = normalizeDate(record.get("startDate"))
		if (record.get("endDate") is not None):
			record['endDate'] = normalizeDate(record.get("endDate"))
		if (record.get("city") is None):
			if (record.get("location") is not None):
				record['city'] = record.get("location")
		addEvent(record, "wikiData")

if(confrefRecords is not None):
	for record in confrefRecords:
		if (record.get("startDate") is not None):
			record['startDate'] = normalizeNumToDate(record.get("startDate"))
		if (record.get("endDate") is not None):
			record['endDate'] = normalizeNumToDate(record.get("endDate"))
		addEvent(record, "confref")
		#print(str(record['location'] or '-') + "  city: " + str(record['city'] or '-') + " country: " + str(
		#record['country'] or '-') + "TITLE: " + record['title'])

queryCondition = "NOT exists((n)-[]-(:Acronym)) AND NOT exists((m)-[]-(:Acronym))"

def filterAcronym():
	query =f'''MATCH(n: Event) WHERE NOT exists((n)-[]-(:Acronym)) AND (NOT n.acronym = "{acronym}" OR n.acronym IS NULL) DETACH DELETE n'''
	graph.run(query)


def locationRelation():
	query = f'''MATCH(n: Event) MATCH(m: Event) 
	WHERE {queryCondition}
	AND n.country = m.country 
	AND n.city = m.city
	AND NOT m.source = n.source
	MERGE(n) - [r: SAME_location]-(m)
	RETURN *'''
	graph.run(query)


def dayMonthRelation():
	query = f'''MATCH(n:Event)
	MATCH(m:Event) 
	WHERE {queryCondition}
	AND n.startDate = m.startDate 
	AND n.endDate = m.endDate
	AND NOT n.source = m.source
	MERGE(n)-[r:SAME_dayMonth]-(m)
	RETURN *'''
	graph.run(query)

def yearRelation():
	query = f'''MATCH(n:Event)
	MATCH(m:Event) 
	WHERE {queryCondition}
	AND n.year = m.year
	AND NOT n.source = m.source
	MERGE(n)-[r:SAME_year]-(m)
	RETURN *'''
	graph.run(query)


def filterYear():
	query = f'''MATCH (n:Event)-[r]-(m:Event)
	WHERE {queryCondition}
	AND NOT (n) =(m) 
	AND NOT (n)-[:SAME_year]-(m) 
	DELETE r'''
	graph.run(query)

def resetGraph():
	query = '''match ()-[r]-() delete r'''
	graph.run(query)
	query = '''match (n) DELETE n'''
	graph.run(query)

def match(numberOfRelations):
	query = f'''MATCH (n:Event) MATCH (m:Event) 
	WHERE {queryCondition}
	AND size((n)-[]-(m)) = {numberOfRelations} 
	AND NOT n.matches contains m.source 
	AND NOT m.matches contains n.source 
	MERGE (n)-[:SAME]-(m) ON CREATE SET n.matches = n.matches + m.source, m.matches = m.matches + n.source'''
	graph.run(query)

def bindToAcronym():
	query = f'''CREATE (a:Acronym {{Id: "{acronym}"}})'''
	graph.run(query)

	query = '''MATCH (n:Event) WHERE exists((n)-[]-(:Event)) 
	AND NOT exists ((n)-[:SAME]-()) 
	DETACH DELETE n'''
	graph.run(query)

	query = f'''MATCH (n:Acronym{{Id : "{acronym}"}}) MATCH (m:Event) 
	WHERE NOT exists((m)-[]-(:Acronym)) MERGE (m)-[:acronym]-(n)'''
	graph.run(query)


filterAcronym()
locationRelation()
dayMonthRelation()
yearRelation()
filterYear()
match(3)
match(2)
match(1)
bindToAcronym()