import Tools
from datetime import datetime,timedelta,time

if __name__ == "__main__":

    d1 = time(2,0)
    d2 = datetime.now()
    print(d1)
    print(d2)
    dif1 = Tools.timeDiff(d2,d1)
    dif2 = Tools.addDaysToDatetime(1,Tools.timeDiff(d2,d1))
    print(dif1)
    print(dif2)
    print(dif1.seconds)
    print(dif2.seconds)

    ''' from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
    req = Request("http://www.google.com")
    try:
        response = urlopen(req)
    except HTTPError as e:
        # do something
        print('Error code: ', e.code)
    except URLError as e:
        # do something
        print('Reason: ', e.reason)
    else:
        # do something
        f = open('google.html','w')
        f.write(str(response.read()))
        f.close()
        #print(response.read()) '''