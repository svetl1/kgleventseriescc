import event
import re
import regex
import geograpy

class Parser:
    def __init__(self, signature):
        self.signature = signature
        self.split_signature = re.split(r'[., \-:]+', signature)
        self.event = event()

    def extract_acronym(self):
        acronym = re.search(r'\b[A-Z]{4,}\b', self.signature)

        if (acronym is not None):
            acronym = acronym.group()
            self.event.acronym = acronym
            while acronym in self.split_signature:
                self.split_signature.remove(acronym)

    def extract_ordinal(self):
        ordinal = re.search(r'\b[1-9]([0-9])?(st|nd|rd|th)\b', self.signature)

        if (ordinal is not None):
            ordinal = ordinal.group()
            self.event.ordinal = ordinal
            while ordinal in self.split_signature:
                self.split_signature.remove(ordinal)

    def extract_date(self):
        months = {
            'January': 1, 'Jan': 1,
            'February': 2, 'Feb': 2,
            'March': 3, 'Mar': 3,
            'April': 4, 'Apr': 4,
            'May': 5,
            'June': 6, 'Jun': 6,
            'July': 7, 'Jul': 7,
            'August': 8, 'Aug': 8,
            'September': 9, 'Sep': 9,
            'October': 10, 'Oct': 10,
            'November': 11, 'Nov': 11,
            'December': 12, 'Dec': 12
        }

        year = re.search(r'(19|20)[0-9]{2}', self.split_signature)

        if (year is not None):
            year = year.group()
            self.event.year = year.group()
            while year in self.split_signature:
                self.split_signature.remove(year)

        find_months = [m for m in self.split_signature if m in months.keys()]

        if (len(find_months) == 0):
            return
        
        day_after = True
        is_start_day = True
        i = self.split_signature.index(find_months[0])

        if (len(find_months) == 2):
            self.event.start_month = months[find_months[0]]
            self.event.start_month = months[find_months[1]]

            if (self.split_signature[i-1].isdigit()):
                day_after = False
            elif (not self.split_signature[i+1].isdigit()):
                return
            
            for m in find_months:
                if(day_after):
                    if (is_start_day):
                        self.event.start_day = self.split_signature[i+1]
                        is_start_day = not is_start_day
                    else:
                        self.event.end_day = self.split_signature[i+1]
                    i = self.split_signature.index(find_months[1])
                else:
                    if (is_start_day):
                        self.event.start_day = self.split_signature[i-1]
                        is_start_day = not is_start_day
                    else:
                        self.event.end_day = self.split_signature[i-1]
                    i = self.split_signature.index(find_months[1])
                    
        elif (len(find_months) == 1):
            self.event.start_month = months[find_months[0]]

            if (self.split_signature[i-1].isdigit() and len(self.split_signature[i-1]) < 3):
                self.event.start_day = self.split_signature[i-2]
                self.event.start_day = self.split_signature[i-1]
            else:
                self.event.start_day = self.split_signature[i+1]
                self.event.start_day = self.split_signature[i+2]

        for m in find_months:
            self.split_signature.remove(m)

    def extract_location(self):
        locator = geograpy.locator.LocationContext.fromCache()
        if (locator is not None):
            s1 = str(locator.locateLocation(self.signature, verbose=True)[0]).split(" ", 1)
            self.event.city = s1[0]
            s2 = re.findall(r'\(.*?\)', s1[1][1:-1])
            self.event.region = s2[0][1:-1]
            self.event.country = s2[1][1:-1]
            space_signature = ' '.join(self.split_signature)
            city = regex.search(r'(?:' + s1[0] + '){e<=3}', space_signature)
            i = space_signature.find(city)
            if (i != -1):
                space_signature = space_signature[:i-1]
                self.split_signature = space_signature.split(' ')

    def get_event(self):
        self.extract_acronym()
        self.extract_ordinal()
        self.extract_location()
        self.event.title = ' '.join(self.split_signature)
        return self.event