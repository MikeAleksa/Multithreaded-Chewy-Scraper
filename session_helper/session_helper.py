import json
import random
from itertools import cycle

import requests


def read_user_agents() -> list:
    useragents = []
    try:
        with open("useragents.txt", "r") as useragent_file:
            for useragent in useragent_file.readlines():
                useragents.append(useragent.strip())
    except FileNotFoundError:
        useragents.append("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1")
    finally:
        return useragents


def get_proxy_data() -> list:
    # adapted from https://github.com/victormartinez/python_proxy_bonanza
    with open("api_data/api_data.json", "r") as api_data_file:
        api_data = json.load(api_data_file)
    response = requests.get(api_data["api-url"], headers={"Authorization": api_data["api-key"]})
    if not response.ok:
        response.raise_for_status()
    else:
        json_result = json.loads(response.content)
        return json_result["data"]


class SessionHelper:

    def __init__(self):
        self.useragents = cycle(read_user_agents())
        self.proxies = []

        proxy_data = get_proxy_data()
        login: str = proxy_data["login"]
        password: str = proxy_data["password"]
        for proxy in proxy_data["ippacks"]:
            ip: str = proxy["ip"]
            port: str = str(proxy["port_http"])
            full_proxy_string = "http://{}:{}@{}:{}".format(login, password, ip, port)
            self.proxies.append({"http": full_proxy_string, "https": full_proxy_string})

    def create_session(self) -> requests.session:
        session = requests.Session()
        session.headers = {"User-Agent": next(self.useragents)}
        session.proxies = random.choice(self.proxies)
        return session
