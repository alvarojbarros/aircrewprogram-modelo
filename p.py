import time
from datetime import datetime,timedelta
import Tools

if __name__ == "__main__":

    t1 = datetime.strptime("2016-10-11", "%Y-%m-%d")
    t2 = datetime.strptime("2016-10-12", "%Y-%m-%d")
    print(t1)
    print(t2)
    print(t1>t2)
