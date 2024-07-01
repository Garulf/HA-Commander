# -*- coding: utf-8 -*-
import sys
import string
from pathlib import Path

from pyflowlauncher import Plugin, ResultResponse, send_results
from pyflowlauncher.settings import settings
from pyflowlauncher.utils import score_results
from requests.exceptions import ReadTimeout, ConnectionError, HTTPError

from homeassistant import Client
from results import entity_results


plugin = Plugin()

@plugin.on_method
def query(query: str) -> ResultResponse:
    client = Client(
        settings().get("url"),
        settings().get("token"),
        settings().get("verify_ssl"),
    )
    states = client.states()
    results = entity_results(states)
    return send_results(score_results(query, results, match_on_empty=True))

