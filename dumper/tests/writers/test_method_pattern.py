import json
import logging
import pathlib
import pprint

import pytest
import yaml

from oasdumper.models import HTTPMethod
from oasdumper.utils import endpoint_dir
from oasdumper.writer import (
    OASEndpointMethodPatternWriter,
)

logger = logging.getLogger(__name__)


def touch_child(
    dest_root: pathlib.Path, endpoint_path: str, method: HTTPMethod
):
    path = (
        dest_root
        / endpoint_dir(endpoint_path)
        / method.value
        / "responses"
        / "200"
        / "_index.yml"
    )
    path.mkdir(parents=True, exist_ok=True)
    path.touch()


class TestOASEndpointMethodPatternWriter:
    @pytest.mark.parametrize(
        ("methods", "endpoint_path", "expected"),
        [
            (
                ("GET", "POST"),
                "/v1/posts",
                dict(
                    path="paths/v1_posts/_index.yml",
                    yaml={
                        "get": {"$ref": "get/_index.yml"},
                        "post": {"$ref": "post/_index.yml"},
                    },
                ),
            )
        ],
    )
    def test_write(self, methods, endpoint_path, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)

        for m in methods:
            touch_child(dest_root, endpoint_path, HTTPMethod[m])

        logger.info(f"dest_root:{str(tmpdir)}")
        writer = OASEndpointMethodPatternWriter(dest_root, endpoint_path)
        writer.write()
        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(writer.dest.read_text())
        logger.debug(yaml.safe_load(writer.dest.read_text()))

        assert str(writer.dest) == str(dest_root / expected["path"])
        assert yaml.safe_load(writer.dest.read_text()) == expected["yaml"]
