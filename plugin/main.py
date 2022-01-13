# -*- coding: utf-8 -*-
import sys
import string
from pathlib import Path


from flox import Flox
from flox.clipboard import Clipboard
from homeassistant import Client
from requests.exceptions import ReadTimeout, ConnectionError, HTTPError

PLUGIN_JSON = "./plugin.json"
MAX_ITEMS = 100


def match(query, entity, friendly_name):
    fq = query.rstrip("_" + string.digits)
    if (
        fq in entity.lower()
        or fq in friendly_name.lower().replace(" ", "_")
        or fq in entity.lower().replace(" ", "")
    ):
        return True
    return False


class Commander(Flox, Clipboard):
    def init_hass(self):
        self.client = Client(
            self.settings.get("url"),
            self.settings.get("token"),
            self.settings.get("verify_ssl"),
        )

    def query(self, query):
        try:
            self.init_hass()
        except (ReadTimeout, ConnectionError, HTTPError):
            self.add_item(
                title=f"Could not connect to Home Assistant!",
                subtitle="Please check your settings or network and try again.",
            )
            return
        else:
            states = self.client.states()
            q = query.lower().replace(" ", "_")
            # Filter domains
            if query.startswith("#"):
                for domain in self.client.get_domains(states):
                    if match(q.replace("#", ""), "", domain):
                        self.add_item(
                            title=domain,
                            subtitle="Search for entities in this domain",
                            # icon=self.get_icon(domain),
                            method=self.change_query,
                            parameters=[f"{self.user_keyword} {domain}."],
                            dont_hide=True,
                            glyph=self.client.grab_icon(domain),
                            font_family=str(
                                Path(self.plugindir).joinpath(
                                    "#Material Design Icons Desktop"
                                )
                            ),
                        )
                return
            # logbook
            if query.startswith("@"):
                for entry in self.client.logbook(query.replace("@", "")):
                    self.add_item(
                        title=entry.get("name"),
                        subtitle=f"{entry.get('message')} @{entry.get('when')}",
                        method=self.change_query,
                        parameters=[f'{self.user_keyword} {entry.get("entity_id")}'],
                        glyph=self.client.grab_icon("history"),
                        font_family=str(
                            Path(self.plugindir).joinpath(
                                "#Material Design Icons Desktop"
                            )
                        ),
                        dont_hide=True,
                    )
                return
            # error log
            if query.startswith("!"):
                for entry in self.client.error_log():
                    split_error = entry.split(" ")
                    title = " ".join(split_error[0:2])
                    subtitle = " ".join(split_error[2:])
                    self.add_item(title=title, subtitle=subtitle)
                    if len(self._results) >= MAX_ITEMS:
                        return
                return
            # Main results
            for entity in states:
                if match(
                    q, entity.entity_id, entity.friendly_name
                ) and entity.entity_id not in self.settings.get("hidden_entities", []):
                    subtitle = f"[{entity.domain}] {entity.state}"
                    if q.split("_")[-1].isdigit() and self.client.domain(
                        entity.entity_id, "light"
                    ):
                        subtitle = f"{subtitle} - Press ENTER to change brightness to: {q.split('_')[-1]}%"
                    self.add_item(
                        title=f"{entity.friendly_name or entity.entity_id}",
                        subtitle=subtitle.replace("_", " ").title(),
                        # icon=self.get_icon(entity.domain, entity.state),
                        context=[entity._entity],
                        method="action",
                        parameters=[entity._entity, q],
                        glyph=entity._icon(),
                        font_family=str(
                            Path(self.plugindir).joinpath(
                                "#Material Design Icons Desktop"
                            )
                        ),
                    )

                if len(self._results) > MAX_ITEMS:
                    break

            if len(self._results) == 0:
                self.add_item(title="No Results Found!")

    def context_menu(self, data):
        self.init_hass()
        entity = self.client.create_entity(data[0])
        for attr in dir(entity):
            if not attr.startswith("_"):
                if callable(getattr(entity, attr)):
                    self.add_item(
                        title=getattr(getattr(entity, attr), "name", ""),
                        subtitle=getattr(entity, attr).__doc__,
                        method=self.action,
                        parameters=[data[0], "", attr],
                        glyph=self.client.grab_icon(
                            getattr(getattr(entity, attr), "icon", "image_broken")
                        ),
                        font_family=str(
                            Path(self.plugindir).joinpath(
                                "#Material Design Icons Desktop"
                            )
                        ),
                    )
                    if getattr(getattr(entity, attr), "_service", False):
                        self._results.insert(0, self._results.pop(-1))
                elif not str(getattr(entity, attr)).startswith("{"):
                    self.add_item(
                        title=str(getattr(entity, attr)),
                        subtitle=str(attr.replace("_", " ").title()),
                        glyph=self.client.grab_icon("information"),
                        font_family=str(
                            Path(self.plugindir).joinpath(
                                "#Material Design Icons Desktop"
                            )
                        ),
                        method=self.put,
                        parameters=[str(getattr(entity, attr))],
                    )
        self.add_item(
            title="Hide Entity",
            subtitle="Hide this entity from the results",
            icon=self.icon,
            method=self.hide_entity,
            parameters=[entity.entity_id],
        )

    def action(self, entity_id, query="", service="_default_action"):
        self.init_hass()
        entity = self.client.create_entity(entity_id)
        try:
            if (
                self.client.domain(entity.entity_id, "light")
                and query.split("_")[-1].isdigit()
            ):
                entity._brightness_pct(int(query.split("_")[-1]))
            else:
                getattr(entity, service)()
        except (HTTPError, ReadTimeout, ConnectionError):
            sys.exit(1)

    def hide_entity(self, entity_id):
        hidden_entities = self.settings.setdefault("hidden_entities", [])
        hidden_entities.append(entity_id)
        self.settings.update({"hidden_entities": hidden_entities})
        self.show_msg(
            "Entity hidden", f"{entity_id} will no longer be shown in the results."
        )


if __name__ == "__main__":
    Commander()
