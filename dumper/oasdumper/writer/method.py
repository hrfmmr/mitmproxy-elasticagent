import pathlib
import re
import typing as t

import yaml

from oasdumper.parser import OASParser
from oasdumper.utils import endpoint_dir
from oasdumper.utils.decorators import ensure_dest_exists
from oasdumper.types import YAML


class OASEndpointMethodWriter:
    """
    summary: Info for a specific pet
    operationId: showPetById
    tags:
      - pets
    responses:
      $ref: "responses/_index.yml"
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: str,
        query: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method
        self.query = query
        self.dest = (
            self.dest_root
            / endpoint_dir(self.endpoint_path)
            / self.method
            / "_index.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        oas_json = {
            "summary": "",
            "operationId": self._build_operation_id(),
            "responses": {"$ref": "responses/_index.yml"},
        }
        if self.query:
            parameters = [
                {
                    "in": "query",
                    "name": k,
                    "required": False,
                    "schema": {"type": OASParser.gettype(type(v).__name__)},
                }
                for k, v in self.query.items()
            ]
            oas_json["parameters"] = parameters
        return yaml.dump(oas_json)

    def _build_operation_id(self) -> str:
        rex = re.compile(r"^/v[\d]+/(?P<path>.+)")
        result = re.match(rex, self.endpoint_path)
        path_without_version = result.group("path")
        operation_id = "".join(
            [self.method]
            + [s.capitalize() for s in path_without_version.split("/")]
        )
        return operation_id
