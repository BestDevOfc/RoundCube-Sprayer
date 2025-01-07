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
            "referer": "https://www.google.com",
            "origin": "https://www.google.com"

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
        maybe

    def main(self):
        self.normalize_urls()
        self.pbar = tqdm(total=len(self.urls), desc="Checking...")

        self.username = input(f"[ Username to spray ]: ").strip().rstrip()
        self.password = input(f"[ Password to spray ]: ").strip().rstrip()

        self.login(f"http://198.18.2.187")
        # with ThreadPoolExecutor(max_workers=100) as executor:
        #     executor.map( self.login, self.urls )


if __name__ == "__main__":
    urls = list(set(open("urls.txt", 'r').readlines()))
    checkerObj = Sprayer( urls )
    checkerObj.main()
        
