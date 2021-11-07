import pathlib
import re
import typing as t

import yaml

from oasdumper.models import (
    HTTPMethod,
)
from oasdumper.utils import endpoint_dir
from oasdumper.utils.decorators import ensure_dest_exists
from oasdumper.types import YAML


class OASEndpointMethodPatternWriter:
    """
    get:
      $ref: 'get/_index.yml'
    post:
      $ref: 'post/_index.yml'
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.dest = (
            self.dest_root / endpoint_dir(self.endpoint_path) / "_index.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        methods = self._find_endpoint_methods()
        oas_json = {m: {"$ref": f"{m}/_index.yml"} for m in methods}
        return yaml.dump(oas_json)

    def _find_endpoint_methods(self) -> t.Set[str]:
        rex = re.compile(
            r".*/(?P<method>({methods}))/".format(
                methods="|".join([e.value for e in HTTPMethod])
            )
            + r"responses/\d{3}/.*.ya?ml$"
        )
        paths = self.dest.parent.glob("**/*.yml")
        methods: t.Set[str] = set()
        for p in paths:
            result = re.match(rex, str(p))
            if not result:
                continue
            methods.add(result.group("method"))
        return methods
