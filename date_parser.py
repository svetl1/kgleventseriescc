import re

# Original signature
conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, January 8-9, 2018'
print('Input:\n' + conf)

# Tests for different date formats (DO NOT FORGET TO COMMENT THE LINE ABOVE BEFORE TESTING!):
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 8-9 January, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, December 31 - January 3, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 31 December - 3 January, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, Jan 8-9, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 8-9 Jan, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, Dec 31 - Jan 3, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 31 Dec - 3 Jan, 2018'

conf_split = re.split(r'[., \-:]+', conf)
print('Split input:')
print(conf_split)

year_match = re.search(r'(19|20)[0-9]{2}', conf)
year = year_match.group()

months =  ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', 'May', 'June', 'Jun', 'July', 'Jul', 'August', 'Aug', 'September', 'Sept', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']

months_found = [m for m in conf_split if m in months]

month_day = []

day_after = True

if(len(months_found) == 2):
    i = conf_split.index(months_found[0])
    if(conf_split[i-1].isdigit()):
        day_after = False
    for m in months_found:
        if(day_after):
            month_day.append(m + ' ' + conf_split[i+1])
            i = conf_split.index(months_found[1])
        else:
            month_day.append(m + ' ' + conf_split[i-1])
            i = conf_split.index(months_found[1])
elif(len(months_found) == 1):
    i = conf_split.index(months_found[0])
    if(conf_split[i-1].isdigit()):
        month_day.append(months_found[0] + ' ' + conf_split[i-2])
        month_day.append(months_found[0] + ' ' + conf_split[i-1])
    else:
        month_day.append(months_found[0] + ' ' + conf_split[i+1])
        month_day.append(months_found[0] + ' ' + conf_split[i+2])

start_date = month_day[0]
end_date = month_day[1]

print('Extracted data:')
print('- Year: ' + year)
print('- Start date: ' + start_date)
print('- End date: ' + end_date)

conf_split.remove(year)

for month in months_found:
    conf_split.remove(month)

for date in month_day:
    for day in re.findall(r'\b\d+\b', date):
        conf_split.remove(day)

print('Split input after removing extracted data:')
print(conf_split)