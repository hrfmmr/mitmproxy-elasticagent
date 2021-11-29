import json
import logging
import pathlib
import pprint

import pytest
import yaml

from oasdumper.models import HTTPMethod
from oasdumper.utils import (
    schema_root_dir,
)
from oasdumper.writer import (
    OASSchemaIndexWriter,
)

logger = logging.getLogger(__name__)


def touch_child(dest_root: pathlib.Path, schema_path: str):
    path = dest_root / schema_root_dir() / schema_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


class TestOASSchemaIndexWriter:
    @pytest.mark.parametrize(
        ("schema_paths", "expected"),
        [
            (
                [
                    "v1-posts-{post_id}-comments/get/request_params.yml",
                ],
                dict(
                    path="",
                    yaml={},
                ),
            ),
        ],
    )
    def test_write(self, schema_paths, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)

        for p in schema_paths:
            touch_child(dest_root, p)
        writer = OASSchemaIndexWriter(dest_root)

        # 🐛debug
        writer._build()
        # 🐛debug

        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(f"📜yaml:\n{writer.dest.read_text()}")
        logger.debug(yaml.safe_load(writer.dest.read_text()))
        assert False, "💚"
