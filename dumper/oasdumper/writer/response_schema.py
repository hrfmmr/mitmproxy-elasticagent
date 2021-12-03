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


class OASResponseSchemaWriter:
    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: HTTPMethod,
        status_code: int,
        response_content: t.Dict[str, t.Any],
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method
        self.status_code = status_code
        self.response_content = response_content
        self.dest = (
            self.dest_root
            / endpoint_schema_dir(self.endpoint_path)
            / self.method.value
            / "responses"
            / str(self.status_code)
            / "_index.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        schema = OASParser.parse(self.response_content)
        schema["required"] = sorted(list(self.response_content.keys()))
        return yaml.dump(schema)
