import urllib
import requests
class Ptp:

    def __init__(self):
        pass

    def parseTitle(self, text : str):
        title = urllib.parse.quote_plus(text)
        res = requests.get("https://ptp.bitplan.com/parse?titles=" + title + "&examples=example1&format=json&metadebug=on")
        lods = res.json()
        return lods

ptpObject = Ptp()
print(ptpObject.parseTitle("Proceedings of 3rd International Conference on Software Reuse, ICSR 1994, Rio De Janeiro, Brazil, November 1-4, 1994"))