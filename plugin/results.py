from typing import Generator

from pyflowlauncher.result import Result
from pyflowlauncher.utils import score_results

from homeassistant import Entity




def entity_result(entity: Entity) -> Generator[Result, None, None]:
    yield Result(
        Title=str(entity.friendly_name or entity.entity_id),
        SubTitle=f'{entity.domain} {entity.state}',
        Glyph={
            "Glyph": entity.entity_id(),
            "FontFamily": "#Material Design Icons Desktop"
        }
    )


def entity_results(entities: list[Entity]) -> Generator[Result, None, None]:
    yield from (entity_result(entity) for entity in entities)

