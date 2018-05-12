import time
import sys
from datetime import datetime
#hour ----> 'Intensity/RED/GREEN/BLUE'

CR = {
0:'005454FF',
1:'00545454',
2:'00545454',
3:'00545454',
4:'00545454',
5:'88545454',
6:'FF7FFFFF',
7:'FF7FFFFF',
8:'FF7FFFFF',
9:'FF7FFFFF',
10:'FF1E90FF',
11:'FF1E90FF',
12:'FF87CEFA',
13:'FF87CEFA',
14:'FF87CEFB',
15:'FF87CEFC',
16:'FF87CEFA',
17:'88545454',
18:'00545454',
19:'00545454',
20:'00545454',
21:'00545454',
22:'00545454',
23:'00545454'}

#print CR

while True:
    now = datetime.now()
    print ('%d:%d RGB:%s' %(now.hour,now.minute,CR.get(now.hour, None)))
    time.sleep(2)
