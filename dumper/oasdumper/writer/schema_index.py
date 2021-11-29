import logging
import pathlib
import typing as t

import yaml

from oasdumper.models import HTTPMethod
from oasdumper.parser import OASParser
from oasdumper.utils import (
    schema_root_dir,
)
from oasdumper.utils.decorators import ensure_dest_exists
from oasdumper.types import YAML


logger = logging.getLogger(__name__)


class OASSchemaIndexWriter:
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
    ) -> None:
        self.dest_root = dest_root
        self.dest = self.dest_root / schema_root_dir() / "_index.yml"

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        paths = self.dest.parent.glob("**/*.yml")
        import pprint

        # TODO: schema yamlのpath componentsから、schema_identifierをビルドしてOAS yaml(ie. GetPosts: $ref: path/to/*.yml)をビルドする
        logger.debug(f"🐛 {pprint.pformat(list(paths))}")
