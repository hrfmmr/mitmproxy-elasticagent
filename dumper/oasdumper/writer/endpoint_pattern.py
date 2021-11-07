import logging
import pathlib
import re
import typing as t

import yaml

from oasdumper.utils import (
    endpoint_root_dir,
    to_endpoint_dir,
    to_endpoint_path,
)
from oasdumper.types import YAML

logger = logging.getLogger(__name__)


class OASEndpointPatternWriter:
    """
    /pets:
      $ref: "pets/_index.yml"
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
    ) -> None:
        self.dest_root = dest_root
        self.dest = self.dest_root / endpoint_root_dir() / "_index.yml"

    def write(self):
        # TODO: ⚓ from HERE!!!
        pass

    def _build(self) -> YAML:
        oas_json = {
            x: {"$ref": f"{to_endpoint_dir(x)}/_index.yml"}
            for x in self._find_endpoint_paths()
        }
        return yaml.dump(oas_json)

    def _find_endpoint_paths(self) -> t.Iterator[str]:
        paths = self.dest.parent.glob("*")
        rex_endpoint_dir = re.compile(r".*/paths/(?P<endpoint_dir>[\w]+)")
        for p in paths:
            if p.is_file():
                continue
            result = re.match(rex_endpoint_dir, str(p))
            if not result:
                logger.warning(
                    f"⚠ extracting endpoint_dir regex not match for path:{str(p)}"
                )
                continue
            dir_name = result.group("endpoint_dir")
            endpoint = to_endpoint_path(dir_name)
            yield endpoint
