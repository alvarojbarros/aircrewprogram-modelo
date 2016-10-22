
if __name__ == "__main__":

    from urllib.request import Request, urlopen
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
        #print(response.read())