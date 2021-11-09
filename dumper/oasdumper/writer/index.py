import pathlib
from dataclasses import asdict

import yaml

from oasdumper.models import OASIndexInfo
from oasdumper.types import YAML


class OASIndexWriter:
    """
    openapi: "3.0.0"
    info:
      version: 1.0.0
      title: Swagger Petstore
      description: Multi-file boilerplate for OpenAPI Specification.
      license:
        name: MIT
    servers:
      - url: http://petstore.swagger.io/v1
    paths:
      /pets:
        $ref: "paths/pets/_index.yml"
    """

    def __init__(self, dest_root: pathlib.Path, info: OASIndexInfo) -> None:
        self.dest_root = dest_root
        self.info = info
        self.dest = self.dest_root / "index.yml"

    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        oas_json = asdict(self.info)
        return yaml.dump(oas_json)
