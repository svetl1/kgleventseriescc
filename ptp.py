import urllib
import requests
import re
from num2words import num2words
class Ptp:

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

#ptpObject = Ptp()
#res = (ptpObject.parseTitle("", "ICSR", "112"))
#print(res)