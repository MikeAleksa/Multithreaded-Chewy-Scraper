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

    no_proxies_acknowledged = False

    def __init__(self):
        """
        set up cycle of useragents and list of proxies
        """
        # set up useragents
        try:
            with open("useragents.txt", "r") as useragent_file:
                useragents = list()
                for useragent in useragent_file.readlines():
                    useragents.append(useragent)
                self.useragents = cycle(useragents)
        except FileNotFoundError:
            self.useragents = cycle(["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"])

        # set up proxies from proxybonanza, if credentials supplied
        try:
            with open("session_builder/api_data.json", "r") as api_data_file:
                self.api_data = json.load(api_data_file)
        except FileNotFoundError:
            self.api_data = None
        self.proxies = self.get_proxies_from_proxybonanza()

        # if no proxies available, seek acknowledgement to continue without proxies
        if self.proxies is None and not SessionBuilder.no_proxies_acknowledged:
            ack = str()
            while ack.upper() not in ['Y', 'N']:
                ack = input("No proxies available. Continue without proxies? (Y/N): ")
            if ack.upper() == 'Y':
                SessionBuilder.no_proxies_acknowledged = True
            else:
                raise Exception('No proxies available, ending...')

    def get_proxies_from_proxybonanza(self) -> list:
        """
        Get a list of proxies from proxybonanza using an api-key and an api-url, if supplied
        :return: list of proxies from proxybonanza, or None if no api data supplied to SessionHelper object
        """
        proxies = None

        if self.api_data is not None:
            response = requests.get(self.api_data["api-url"], headers={"Authorization": self.api_data["api-key"]})
            if not response.ok:
                response.raise_for_status()
            else:
                proxy_data = json.loads(response.content)["data"]
                if proxy_data['expiration_date_human'] != 'Expired':
                    login: str = proxy_data["login"]
                    password: str = proxy_data["password"]
                    proxies = []
                    for proxy in proxy_data["ippacks"]:
                        ip: str = proxy["ip"]
                        port: str = str(proxy["port_http"])
                        full_proxy_string = "http://{}:{}@{}:{}".format(login, password, ip, port)
                        proxies.append({"http": full_proxy_string, "https": full_proxy_string})
        return proxies

    def create_session(self) -> requests.session:
        """
        Create and return a new session using a new useragent and a random proxy from the list
        Use own ip if no proxies specified, or default to Firefox/15.0.1 useragent if no useragents were specified
        :return: requests.session object using the useragent and a random proxy
        """
        session = requests.Session()
        session.headers = {"User-Agent": next(self.useragents)}
        if self.proxies is not None:
            session.proxies = random.choice(self.proxies)
        return session
