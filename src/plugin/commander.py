from __future__ import annotations

import asyncio
import string
from functools import lru_cache, partial
from typing import Iterable, List

from pyflowlauncher import Plugin, api
from requests.exceptions import HTTPError, RequestException

import icons
from homeassistant import Client
from launcher import KEEP_OPEN, HassLauncher
from results import ICON, HassResult, make_result, preview, settings_result

DEFAULT_URL = "http://localhost:8123"
DEFAULT_MAX_RESULTS = 50

plugin = Plugin(launcher=HassLauncher())


def match(query, entity, friendly_name):
    fq = query.rstrip("_" + string.digits)
    if (
        fq in entity.lower()
        or fq in friendly_name.lower().replace(" ", "_")
        or fq in entity.lower().replace(" ", "")
    ):
        return True
    return False


def as_bool(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def max_results() -> int:
    try:
        return int(plugin.settings.get("max_results") or DEFAULT_MAX_RESULTS)
    except (TypeError, ValueError):
        return DEFAULT_MAX_RESULTS


def hidden_entities() -> List[str]:
    return list(plugin.settings.get("hidden_entities") or [])


def full_query(text: str) -> str:
    keyword = plugin.launcher.action_keyword
    return f"{keyword} {text}" if keyword else text


@lru_cache(maxsize=1)
def _client(url: str, token: str, verify_ssl: bool) -> Client:
    return Client(url, token, verify_ssl)


def hass() -> Client:
    settings = plugin.settings
    return _client(
        (settings.get("url") or DEFAULT_URL).rstrip("/"),
        settings.get("token") or "",
        as_bool(settings.get("verify_ssl"), default=True),
    )


async def run_blocking(func, *args):
    """Run blocking Home Assistant I/O off the event loop so Flow Launcher can cancel stale queries."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args))


@plugin.on_method
async def query(query: str):
    if not plugin.settings.get("token"):
        return [settings_result(
            "Connect HA-Commander to Home Assistant",
            "Add your Home Assistant URL and long-lived access token in the plugin settings.",
        )]
    client = hass()
    try:
        return await run_blocking(search, client, query)
    except HTTPError as error:
        if error.response is not None and error.response.status_code == 401:
            return [settings_result(
                "Home Assistant rejected the access token",
                "Check the long-lived access token in the plugin settings.",
            )]
        return [settings_result("Home Assistant returned an error", str(error))]
    except RequestException:
        return [settings_result(
            "Could not connect to Home Assistant!",
            "Please check your settings or network and try again.",
        )]


def search(client: Client, query: str) -> List[HassResult]:
    q = query.lower().replace(" ", "_")
    if query.startswith("#"):
        return domain_results(client, q[1:])
    if query.startswith("@"):
        return logbook_results(client, q[1:])
    if query.startswith("!"):
        return error_log_results(client)
    return entity_results(client, q) or [make_result("No Results Found!")]


def domain_results(client: Client, q: str) -> List[HassResult]:
    return [
        make_result(
            domain,
            "Search for entities in this domain",
            icons.entity_icon(domain),
        ).add_action(change_query, [full_query(f"{domain}.")])
        for domain in client.get_domains(client.states())
        if match(q, "", domain)
    ]


def logbook_results(client: Client, q: str) -> List[HassResult]:
    results = []
    entries: Iterable[dict] = reversed(client.logbook())
    for entry in entries:
        entity_id = entry.get("entity_id") or ""
        name = entry.get("name") or entity_id
        if not match(q, entity_id, name):
            continue
        result = make_result(
            name,
            f"{entry.get('message')} @{entry.get('when')}",
            icons.icon("history"),
            score=max_results() - len(results),
        )
        if entity_id:
            result.add_action(change_query, [full_query(entity_id)])
        results.append(result)
        if len(results) >= max_results():
            break
    return results


def error_log_results(client: Client) -> List[HassResult]:
    results = []
    for entry in reversed(client.error_log()):
        split_error = entry.split(" ")
        results.append(make_result(
            " ".join(split_error[0:2]),
            " ".join(split_error[2:]),
            copy_text=entry,
            score=max_results() - len(results),
        ))
        if len(results) >= max_results():
            break
    return results


def entity_results(client: Client, q: str) -> List[HassResult]:
    results = []
    hidden = hidden_entities()
    brightness = q.split("_")[-1]
    for entity in client.states():
        if entity.entity_id in hidden or not match(q, entity.entity_id, entity.friendly_name):
            continue
        subtitle = f"[{entity.domain}] {entity.state}"
        if brightness.isdigit() and client.domain(entity.entity_id, "light"):
            subtitle = f"{subtitle} - Press ENTER to change brightness to: {brightness}%"
        results.append(make_result(
            entity.friendly_name or entity.entity_id,
            subtitle.replace("_", " ").title(),
            entity._icon(),
            context_data=[entity._entity],
            copy_text=entity.entity_id,
            preview=preview(f"{entity.entity_id}\n{entity.state}"),
        ).add_action(action, [entity._entity, q]))
        if len(results) >= max_results():
            break
    return results


@plugin.on_method
def context_menu(data):
    if not data:
        return []
    client = hass()
    entity = client.create_entity(data[0])
    results = []
    for attr in dir(entity):
        if attr.startswith("_"):
            continue
        value = getattr(entity, attr)
        if callable(value):
            result = make_result(
                getattr(value, "name", ""),
                value.__doc__,
                icons.icon(getattr(value, "icon", "image-broken")),
            ).add_action(action, [data[0], "", attr])
            if getattr(value, "_service", False):
                results.insert(0, result)
            else:
                results.append(result)
        elif value is not None and not str(value).startswith("{"):
            results.append(make_result(
                str(value),
                attr.replace("_", " ").title(),
                icons.icon("information"),
            ).add_action(api.copy_to_clipboard(str(value))))
    results.append(make_result(
        "Hide Entity",
        "Hide this entity from the results",
        icons.icon("eye-off"),
        settings_change={"hidden_entities": hidden_entities() + [entity.entity_id]},
    ).add_action(api.show_msg(
        "Entity hidden", f"{entity.entity_id} will no longer be shown in the results.", ICON,
    )))
    return results


@plugin.on_method
async def action(entity, query="", service="_default_action"):
    try:
        await run_blocking(call_service, hass(), entity, query, service)
    except RequestException as error:
        return api.show_msg("Home Assistant error", str(error), ICON)


def call_service(client: Client, data: dict, query: str, service: str) -> None:
    entity = client.create_entity(data)
    brightness = query.split("_")[-1]
    if client.domain(entity.entity_id, "light") and brightness.isdigit():
        entity._brightness_pct(int(brightness))
    else:
        getattr(entity, service)()


@plugin.on_method
async def change_query(query: str):
    await plugin.launcher.api.invoke(api.change_query(query))
    return KEEP_OPEN
