import pathlib
import typing as t

from oasdumper.models import (
    OASResponseContent,
)
from oasdumper.utils import endpoint_dir, response_description
from oasdumper.utils.decorators import ensure_dest_exists
from oasdumper.types import YAML


class OASResponseContentWriter:
    """
    description: Expected response to a valid request
    content:
      application/json:
        schema:
          type: object
          properties:
            id:
              type: integer
              format: int64
            name:
              type: string
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: str,
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
            / endpoint_dir(self.endpoint_path)
            / self.method
            / "responses"
            / str(self.status_code)
            / "_index.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build_response_content()
        self.dest.write_text(oas_yaml)

    def _build_response_content(self) -> YAML:
        description = response_description(self.status_code)
        model = OASResponseContent(
            dest=self.dest,
            description=description,
            content=self.response_content,
        )
        return model.build()
