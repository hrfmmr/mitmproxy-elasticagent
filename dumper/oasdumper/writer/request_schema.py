import logging
import pathlib
import typing as t

import yaml

from oasdumper.models import HTTPMethod
from oasdumper.parser import OASParser
from oasdumper.utils import (
    endpoint_schema_dir,
)
from oasdumper.utils.decorators import ensure_dest_exists
from oasdumper.types import YAML

logger = logging.getLogger(__name__)

RES_DELIMITER = "_"


class OASRequestParamsSchemaWriter:
    """
    parameters:
      - in: query
        name: GetTodosRequestParams
        schema:
          type: object
          properties:
            userId:
              type: integer
            completed:
              type: boolean
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: HTTPMethod,
        query: t.Dict[str, t.Any],
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method
        self.query = query
        self.dest = (
            self.dest_root
            / endpoint_schema_dir(self.endpoint_path)
            / self.method.value
            / "request_params.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        schema = OASParser.parse(self.query)
        return yaml.dump(schema)


class OASRequestBodySchemaWriter:
    """
    schema:
      type: object
      properties:
        name:
          type: string
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: HTTPMethod,
        request_content: t.Dict[str, t.Any],
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method
        self.request_content = request_content
        self.dest = (
            self.dest_root
            / endpoint_schema_dir(self.endpoint_path)
            / self.method.value
            / "request_body.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        schema = OASParser.parse(self.request_content)
        schema["required"] = sorted(list(self.request_content.keys()))
        return yaml.dump(schema)
