import re
import date_parser2
from py2neo import Graph
import requests
#graph = Graph("bolt://localhost:7687", auth=("", ""))

months = ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', '-', 'May', 'June', 'Jun', 'July', 'Jul', 'August', 'Aug', 'September', 'Sept', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']


def addEvent(event):
		query="""
		MERGE (e:Event:ConfRef {eventId:$event.eventId})
		ON CREATE SET e = $event
		ON MATCH SET e += $event
		"""
		records=event
		params={"event":records}
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

acronym = "ICEIS"
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


if(dblpRecords is not None):
	for record in dblpRecords:
		if (record.get("acronym") is not None):
			record['acronym'] = normalizeAcronym(record.get("acronym"))
		if(record.get("title") is not None):
			results = date_parser2.dateParser(record.get("title"))
			if(results is not None):
				record['startDate'] = results['startDate']
				record['endDate'] = results['endDate']
		print(record)




if(crossrefRecords is not None):
	for record in crossrefRecords:
		if (record.get("startDate") is not None):
			record['startDate'] = normalizeDate(record.get("startDate"))
		if (record.get("endDate") is not None):
			record['endDate'] = normalizeDate(record.get("endDate"))
		if (record.get("acronym") is not None):
			record['acronym'] = normalizeAcronym(record.get("acronym"))


if(wikidataRecords is not None):
	for record in wikidataRecords:
		if (record.get("acronym") is not None):
			record['acronym'] = normalizeAcronym(record.get("acronym"))
		if(record.get("cityId") is not None):
			record['cityId'] = normalizeCityId(record.get("cityId"))
		if (record.get("startDate") is not None):
			record['startDate'] = normalizeDate(record.get("startDate"))
		if (record.get("endDate") is not None):
			record['endDate'] = normalizeDate(record.get("endDate"))

if(confrefRecords is not None):
	for record in confrefRecords:
		if (record.get("startDate") is not None):
			record['startDate'] = normalizeNumToDate(record.get("startDate"))
		if (record.get("endDate") is not None):
			record['endDate'] = normalizeNumToDate(record.get("endDate"))
#    addEvent(record)



