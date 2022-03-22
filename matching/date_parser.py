import re

# Original signature
conf = '24th International Workshop on Database and Expert Systems Applications, DEXA 2013, Prague, Czech Republic,  30 November - 3 December, 2013'

# Tests for different date formats (DO NOT FORGET TO COMMENT THE LINE ABOVE BEFORE TESTING!):
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 8-11 January, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, November 30 - December 3, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 30 November - 3 December, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, Jan 8-11, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 8-11 Jan, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, Nov 30 - Dec 3, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 30 Nov - 3 Dec, 2018'

print('Input:\n' + conf)

conf_split = re.split(r'[., \-:]+', conf)
print('Split input:')
print(conf_split)

year_match = re.search(r'(19|20)[0-9]{2}', conf)
year = year_match.group()

months =  ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', 'May', 'June', 'Jun', 'July', 'Jul', 'August', 'Aug', 'September', 'Sep', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']

months_found = [m for m in conf_split if m in months]

month_day = []
resultMonth = []

day_after = True
i = conf_split.index(months_found[0])

if(len(months_found) == 2):
    if(conf_split[i-1].isdigit()):
        day_after = False
    for m in months_found:
        if(day_after):
            month_day.append(m[0:3] + ' ' + conf_split[i+1])
            i = conf_split.index(months_found[1])
        else:
            month_day.append(m[0:3] + ' ' + conf_split[i-1])
            i = conf_split.index(months_found[1])
elif(len(months_found) == 1):

    if(conf_split[i-1].isdigit()):
        month_day.append(months_found[0][0:3] + ' ' + conf_split[i-2])
        month_day.append(months_found[0][0:3] + ' ' + conf_split[i-1])
    else:
        month_day.append(months_found[0][0:3] + ' ' + conf_split[i+1])
        month_day.append(months_found[0][0:3] + ' ' + conf_split[i+2])

start_date = month_day[0]
end_date = month_day[1]

print('Extracted data:')
print('- Year: ' + year)
print('- Start date: ' + start_date)
print('- End date: ' + end_date)

while year in conf_split:
    conf_split.remove(year)

for month in months_found:
    conf_split.remove(month)

for date in month_day:
    for day in re.findall(r'\b\d+\b', date):
        conf_split.remove(day)

print('Split input after removing extracted data:')
print(conf_split)