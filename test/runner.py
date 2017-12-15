__author__ = 'aammundi'


from threading import Timer
import time
import sys
from api_test import *

def main():
    num_users = int(sys.argv[1])

    list_u = []
    for u in range(num_users):
        u = User()
        u.onboard_user()
        list_u.append(u)

    while True:
        for u in list_u:
            Timer(60, u.get_cards())

        time.sleep(60)

if __name__ == '__main__':

    main()
