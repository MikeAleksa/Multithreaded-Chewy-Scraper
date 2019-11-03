import json
import random
from itertools import cycle

import requests


class SessionBuilder:
    """
    The SessionBuilder class is used to create and return request.session objects using different useragents and
    proxies on a per-session basis

    Proxies are obtained using an API key from ProxyBonanza

    If no useragents are supplied, a default Firefox useragent is used
    If no API data is supplied for ProxyBonanza, no proxies are used
    """

    def __init__(self, api_data: dict = None, useragents: list = None):
        # set up useragents
        if useragents is not None:
            self.useragents = cycle(useragents)
        else:
            self.useragents = cycle(["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"])

        # set up proxies using api-url and api-key for proxybonanza, if supplied
        self.proxies = None
        if api_data is not None:
            response = requests.get(api_data["api-url"], headers={"Authorization": api_data["api-key"]})
            if not response.ok:
                response.raise_for_status()
            else:
                proxy_data = json.loads(response.content)["data"]
                login: str = proxy_data["login"]
                password: str = proxy_data["password"]
                self.proxies = []
                for proxy in proxy_data["ippacks"]:
                    ip: str = proxy["ip"]
                    port: str = str(proxy["port_http"])
                    full_proxy_string = "http://{}:{}@{}:{}".format(login, password, ip, port)
                    self.proxies.append({"http": full_proxy_string, "https": full_proxy_string})

    def create_session(self) -> requests.session:
        """
        Create and return a new session using a new useragent and a random proxy from the list
        Use own ip if no proxies specified
        Use default Firefox/15.0.1 useragent if no useragents were specified
        :return: requests.session object
        """
        session = requests.Session()
        session.headers = {"User-Agent": next(self.useragents)}
        if self.proxies is not None:
            session.proxies = random.choice(self.proxies)
        return session
