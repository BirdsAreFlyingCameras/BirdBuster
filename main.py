import requests as r
import re
import socket as s
import threading as t
from concurrent.futures import ThreadPoolExecutor
from PyEnhance import Loading, Counter
Loading = Loading.Loading

PostiveStatusCodes = [200, 201, 202, 203, 204, 205, 206,
                      300, 301, 302, 303, 304, 305, 307,
                      308, 401]
DirsChecked = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}


def main():
    global ThreadCount

    global URL
    global TheadCount

    URL = input("Enter URL: ")
    ThreadCount = input("Enter Thread Count: ")

    if ThreadCount.isdigit():
        ThreadCount = int(ThreadCount)

    else:
        print("Thread Count must be a number")
        exit()

    def FetchTLDS():

        global TLDSs
        global TLDS

        TLDSs = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
        print("getting TLDSs")
        response = r.get(TLDSs, headers=headers)
        response.raise_for_status()

        # The file uses line breaks for each TLD, and we filter out comments which start with '#'
        TLDS = [line.strip().lower() for line in response.text.splitlines() if not line.startswith('#')]

    FetchTLDS()

    def CheckTLDS():
        global TLDSValid
        global URL
        TLDSValid = False

        for i in TLDS:
            if URL.endswith("/"):
                URL = URL[:-1]
            if URL.endswith(i):
                TLDSValid = True
                break

        if TLDSValid is False:
            input(f"URL does not have a valid TLDS Do you want to continue? [Y/N] ")
            if input == "y" or "Y":
                print("Continuing...")
            else:
                print("Exiting...")

    CheckTLDS()

    def IsURLAnIP():
        global IsURLAnIPOutput

        try:
            s.inet_aton(URL)
            IsURLAnIPOutput = True
            if IsURLAnIPOutput == True:
                print(f"URL is an IP address")

        except s.error:
            IsURLAnIPOutput = False
            if IsURLAnIPOutput == False:
                print(f"URL is not an IP address")

    IsURLAnIP()

    def refactor(URL):  # defines the refactor function and passes the URL variable as a parameter
        global URLHTTPS, URLHTTP  # Sets the variables URL HTTPS and URL HTTP to global variables meaning they can be called outside of this function.
        global TLDSValid
        TLDSValid = False

        if URL.endswith("/"):  # Checks if the URL ends with a forward slash
            URL = URL[:-1]  # Removes the forward slash from the URL

        for i in "https://", "http://":
            if URL.startswith(i):
                if i == "https://":
                    URLHTTPS = URL
                    URLHTTP = URL.replace("https://", "http://")

                if i == "http//":
                    URLHTTP = URL
                    URLHTTPS = URL.replace("http://", "https://")

                break
            else:
                URLHTTP = f"http://{URL}"
                URLHTTPS = f"https://{URL}"




    refactor(URL)  # Calls the refactor function with the parameter URL

    def Checks():

        def HTTPcheck():

            global HTTPValid

            GetReqStatus = r.get(url=URLHTTP)

            if GetReqStatus.status_code in PostiveStatusCodes:

                HTTPValid = True

            else:
                print(f"{URL} is not a valid URL")

                HTTPValid = False

        def HTTPScheck():

            global HTTPSValid

            getreqstatus = r.get(url=URLHTTPS)

            if getreqstatus.status_code == 200:

                HTTPSValid = True

            else:
                print(f"{URL} is not a valid URL")

                HTTPSValid = False

        HTTPcheck()
        HTTPScheck()

    Checks()

    def ListChoiceFunc():
        global List
        global Replace
        Replace = ['\\r', '\\n', 'b', "'", '[', ']', ',']

        print("""
        \r[1] Common List
        \r[2] Small List
        \r[3] Medium List
        \r[4] Large List
        \r[5] Custom List
        """)
        ListChoice = input("")

        if ListChoice == '1':
            with open('wordlist\\CommonList.txt', 'rb') as List:

                List = List.readlines()

                for i in Replace:
                    List = str(List).replace(i, "")

                List = List.split(" ")

        if ListChoice == '2':
            with open('wordlist\\directory-list-2.3-small.txt', 'rb') as List:

                List = List.readlines()

                for i in Replace:
                    List = str(List).replace(i, "")

                List = List.split(" ")

        if ListChoice == '3':
            with open('wordlist\\directory-list-2.3-medium.txt', 'rb') as List:

                List = List.readlines()

                for i in Replace:
                    List = str(List).replace(i, "")

                List = List.split(" ")

        if ListChoice == '4':
            with open('wordlist\\directory-list-2.3-big.txt', 'rb') as List:

                List = List.readlines()

                for i in Replace:
                    List = str(List).replace(i, "")

                List = List.split(" ")

        if ListChoice == '5':
            ListDir = input("Enter list Dir: ")

            if ListDir.endswith(".txt"):
                pass
            else:
                print("List must be a .txt file")
                exit()

            with open(ListDir, 'rb') as List:

                List = List.readlines()

                for i in Replace:
                    List = str(List).replace(i, "")
                List = List.split(" ")

    ListChoiceFunc()

    ListCounter = Counter.Counter

    def Bust(i):
        lock = t.Lock()
        lock.acquire()
        global ListLen
        ListLen = len(List)
        try:
            print('test')

            for Dir in List:
                ListCounter.Add()
                Loading.Stats(List=List, ListCounter=ListCounter)
                if Dir in DirsChecked:
                    continue

                else:
                    DirsChecked.append(Dir)

                FURL = f'{URLHTTP}/{Dir}'

                Request = r.get(FURL, headers=headers)

                if Request.status_code in PostiveStatusCodes:
                    print(f'\r/{Dir} Returned status code {str(Request.status_code)}')

        finally:
            lock.release()


    Bust(ThreadCount)

    thread_pool = ThreadPoolExecutor(max_workers=ThreadCount)

    for i in range(ThreadCount):
        thread_pool.submit(Bust, i)

    thread_pool.shutdown(wait=True)


if __name__ == '__main__':
    main()
