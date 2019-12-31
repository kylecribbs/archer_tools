"""Caos Client."""
from dataclasses import dataclass, field
from typing import Dict
from urllib.parse import urlencode

import requests


@dataclass
class CaosClient:
    """Simple CAOS Web Portal Client Library for Humans.

    Args:
        kwargs: See Kwargs.

    Kwargs:
        cert (str): Path to certificate.
        key (str): Path to key.
        proxies (dict): Pass HTTP_PROXY and HTTPS_PROXY.
        hostname (str): Provide the hostname for CAOS Portal.
        verify (str): CA Verify.
    """

    cert: str = None
    key: str = None
    proxies: dict = field(default_factory=dict)
    hostname: str = "portal.caos.proj.example.com"
    verify: str = None

    def __post_init__(self):
        """Post init"""
        cert = (self.cert, self.key)

        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.session.cert = cert
        self.session.verify = self.verify
        self.base_url = "https://{}".format(self.hostname)

    def url_helper(self, route: str, **kwargs) -> str:
        """Url Helper for building the URL

        Args:
            route (str): Route for CAOS.
            kwargs: Any kwarg for encoding in the url.

        Returns:
            str: URL String.
        """
        get_vars = urlencode(kwargs)
        route = "{}?{}".format(route, get_vars)
        url = "{}/{}".format(self.base_url, route)
        return url

    def accounts(self, **kwargs) -> Dict:
        """Account request data from CAOS Portal.

        Args:
            kwargs: See Kwargs

        Kwargs:
            requestor (str): Provide OIN for user.
            request_type (str): Select between Archer, EITA ArcSight, EITA
                                NetWitness, EVSS SecurityCenter, RedSeal, and
                                Xacta.
            scope (str): Select between Directorate, Enterprise, Site, and
                         System.
            poc_supervisor (str): Provide an OIN for the user.
            poc_gpoc (str): Provide OIN for the user.
            status (str): Select between Approved, Denied, and Pending.

        Returns:
            Dict: Response JSON

        """
        url = self.url_helper("accounts/request", **kwargs)
        resp = self.session.get(url)
        return resp.json()
