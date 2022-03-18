import urllib
import requests
import re
from num2words import num2words
class Ptp:

    def __init__(self):
        pass

    def parseTitle(self, text : str):
        title = urllib.parse.quote_plus(text)
        res = requests.get("https://ptp.bitplan.com/parse?titles=" + title + "&examples=example1&format=json&metadebug=on")
        lods = res.json()
        return lods

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

ptpObject = Ptp()
print(ptpObject.parseTitle("Proceedings of 3rd International Conference on Software Reuse, ICSR 1994, Rio De Janeiro, Brazil, November 1-4, 1994"))