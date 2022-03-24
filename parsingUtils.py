import urllib
import requests
import re
from num2words import num2words
import geograpy

months = ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', '-', 'May', 'June', 'Jun', 'July', 'Jul', 'August', 'Aug', 'September', 'Sep', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']

class Normalizer:

    def __init__(self):
        pass

    def parseTitle(self, text : str, acronym : str, year : str):
        title = urllib.parse.quote_plus(text)
        res = requests.get("https://ptp.bitplan.com/parse?titles=" + title + "&examples=example1&format=json&metadebug=on")
        lods = res.json()
        if(len(lods.get("events")) == 0):
            return None
        if(lods.get("events")[0].get("title") == None):
            return None

        title = (lods.get("events")[0].get("title"))
        title = re.sub(acronym, '', title)
        title = re.sub('\(|\)|\:', '', title)
        title = re.sub(year, '', title).replace('   ', ' ')

        return title

    def guessOrdinal(self, record: dict):
        """
        tries to guess the ordinal of the given record by returning a set of potential ordinals
        Assumption:
            - given record must have the property 'title'
        Args:
            record: event record
        Returns:
            list of potential ordinals
        """
        title = record.get('title', None)
        if title is None:
            return []
        ord_regex = r"(?P<ordinal>[0-9]+)(?: ?st|nd|rd|th)"
        potentialOrdinal = []
        match = re.findall(pattern=ord_regex, string=title)
        potentialOrdinal.extend([int(ord) for ord in match])
        # search for ordninals in textform
        for lang in ['en']:
            for ord in range(1, 100):
                ordWord = num2words(ord, lang=lang, to='ordinal')
                if ordWord in title.lower() or ordWord.replace("-", " ") in title.lower():
                    potentialOrdinal.append(ord)
        results = list(set(potentialOrdinal))
        if(len(results) == 1):
            return results[0]
        else:
            return None

    def normalizeAcronym(self, acronymString):
        acronym = re.search(r'\b[A-Z]{4,}\b', acronymString)
        if (acronym is None):
            return None
        acronym = acronym.group()
        return acronym

    def normalizeCityId(self, cityIdString):
        return cityIdString.replace('http://www.wikidata.org/entity/', '')

    def normalizeDate(self, dateString):
        dateList = re.split(r'[., \-]+', dateString)
        months_found = [m for m in dateList if m in months]
        i = dateList.index(months_found[0])
        if (dateList[i - 1].isdigit() and len(dateList[i - 1]) < 3):
            if (dateList[i - 1][0] == "0"):  # remove leading zero
                dateList[i - 1] = dateList[i - 1][1:]
            monthDay = months_found[0][0:3] + " " + dateList[i - 1]
        else:
            if (dateList[i + 1][0] == "0"):  # remove leading zero
                dateList[i + 1] = dateList[i + 1][1:]
            monthDay = months_found[0][0:3] + " " + dateList[i + 1]
        return monthDay

    def normalizeNumToDate(self, dateString):
        dateList = re.split(r'[-]', dateString)
        if (dateList[2][0] == "0"):  # remove leading zero
            dateList[2] = dateList[2][1:]
        monthDay = months[(int(dateList[1]) * 2) - 1] + " " + dateList[2]
        return monthDay

    def extract_location(self, title):
        locator = geograpy.locator.LocationContext.fromCache()
        list = {}
        if (locator is not None):
            if(len(locator.locateLocation(title, verbose=True)) < 1):
                return list
            s1 = str(locator.locateLocation(title, verbose=True)[0]).split(" ", 1)
            city = s1[0]
            s2 = re.findall(r'\(.*?\)', s1[1][1:-1])
            #region = s2[0][1:-1]
            country = s2[1][1:-1]

            list['city'] = city
            list['country'] = country
            return list
