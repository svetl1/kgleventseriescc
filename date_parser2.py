import re
def dateParser(dateString):
        conf_split = re.split(r'[., \-:]+', dateString)
        year_match = re.search(r'(19|20)[0-9]{2}', dateString)
        year = year_match.group()

        months = ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', 'May', 'June', 'Jun', 'July',
                  'Jul', 'August', 'Aug', 'September', 'Sep', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']

        months_found = [m for m in conf_split if m in months]

        month_day = []
        results = {}
        day_after = True
        i = conf_split.index(months_found[0])

        if (len(months_found) == 2):
            if (conf_split[i - 1].isdigit() and len(conf_split[i - 1]) < 3):
                day_after = False
            elif(not(conf_split[i + 1].isdigit() and len(conf_split[i+1]) < 3)):
                return None
            for m in months_found:
                if (day_after):
                    month_day.append(m[0:3] + ' ' + conf_split[i + 1])
                    i = conf_split.index(months_found[1])
                else:
                    month_day.append(m[0:3] + ' ' + conf_split[i - 1])
                    i = conf_split.index(months_found[1])
        elif (len(months_found) == 1):

            if (conf_split[i - 1].isdigit() and len(conf_split[i - 1]) < 3):
                month_day.append(months_found[0][0:3] + ' ' + conf_split[i - 2])
                month_day.append(months_found[0][0:3] + ' ' + conf_split[i - 1])
            elif (not(conf_split[i + 1].isdigit() and len(conf_split[i + 1]) < 3)):
                return None
            else:
                month_day.append(months_found[0][0:3] + ' ' + conf_split[i + 1])
                month_day.append(months_found[0][0:3] + ' ' + conf_split[i + 2])

        results['startDate'] = month_day[0]
        results['endDate'] = month_day[1]
        results['year'] = year

        while year in conf_split:
            conf_split.remove(year)

        for month in months_found:
            conf_split.remove(month)

        for date in month_day:
            for day in re.findall(r'\b\d+\b', date):
                conf_split.remove(day)
        results['rest'] = conf_split
        return results