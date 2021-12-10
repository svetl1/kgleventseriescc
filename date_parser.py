import re

# Original signature
conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, January 8-9, 2018'

# Tests for different date formats (DO NOT FORGET TO COMMENT THE LINE ABOVE BEFORE TESTING!):
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 8-9 January, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, December 31 - January 3, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 31 December - 3 January, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, Jan 8-9, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 8-9 Jan, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, Dec 31 - Jan 3, 2018'
# conf = 'Proceedings of the ACM SIGPLAN Workshop on Partial Evaluation and Program Manipulation, Los Angeles, CA, USA, 31 Dec - 3 Jan, 2018'

conf_split = re.split('[, \-:]+', conf)

print('Original string after splitting:')
print(conf_split)

months =  ['January', 'Jan', 'February', 'Feb', 'March', 'Mar', 'April', 'Apr', 'May', 'June', 'Jun', 'July', 'Jul', 'August', 'Aug', 'September', 'Sept', 'October', 'Oct', 'November', 'Nov', 'December', 'Dec']

months_found = [m for m in conf_split if m in months]

d = []

day_after = True 

if(len(months_found) == 2):
    i = conf_split.index(months_found[0])
    if(conf_split[i-1].isdigit()):
        day_after = False 
    for m in months_found:
        if(day_after):
            d.append(m + ' ' + conf_split[i+1])
            i = conf_split.index(months_found[1])
        else:
            d.append(m + ' ' + conf_split[i-1])
            i = conf_split.index(months_found[1])
elif(len(months_found) == 1):
    i = conf_split.index(months_found[0])
    if(conf_split[i-1].isdigit()):
        d.append(months_found[0] + ' ' + conf_split[i-2])
        d.append(months_found[0] + ' ' + conf_split[i-1])
    else:
        d.append(months_found[0] + ' ' + conf_split[i+1])
        d.append(months_found[0] + ' ' + conf_split[i+2])

print('Extracted dates:')
print(d)