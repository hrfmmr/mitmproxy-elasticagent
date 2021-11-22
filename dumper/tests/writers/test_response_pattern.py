import json
import logging
import pathlib
import pprint

import pytest
import yaml

from oasdumper.models import HTTPMethod
from oasdumper.utils import endpoint_dir
from oasdumper.writer import (
    OASResponsePatternWriter,
)

logger = logging.getLogger(__name__)


def touch_child(dest_root: pathlib.Path, input):
    path = (
        dest_root
        / endpoint_dir(input["endpoint_path"])
        / HTTPMethod[input["_source"]["request"]["method"]].value
        / "responses"
        / str(input["_source"]["response"]["status_code"])
        / "_index.yml"
    )
    path.mkdir(parents=True, exist_ok=True)
    path.touch()


class TestOASResponsePatternWriter:
    @pytest.mark.parametrize(
        ("input", "expected"),
        [
            (
                dict(
                    endpoint_path="/v1/posts/1/comments",
                    _source={
                        "request": {
                            "method": "GET",
                            "query": '{"id": "1"}',
                            "content": "",
                        },
                        "response": {
                            "status_code": 200,
                            "content": '{ "postId": 1, "id": 1, "name": "id labore ex et quam laborum", "email": "Eliseo@gardner.biz", "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos" }',
                        },
                    },
                ),
                dict(
                    path="paths/v1-posts-{post_id}-comments/get/responses/_index.yml",
                    yaml={"200": {"$ref": "200/_index.yml"}},
                ),
            )
        ],
    )
    def test_write(self, input, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)

        touch_child(dest_root, input)

        logger.info(f"dest_root:{str(tmpdir)}")
        writer = OASResponsePatternWriter(
            dest_root,
            input["endpoint_path"],
            HTTPMethod[input["_source"]["request"]["method"]],
        )
        writer.write()
        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(writer.dest.read_text())
        logger.debug(yaml.safe_load(writer.dest.read_text()))

        assert str(writer.dest) == str(dest_root / expected["path"])
        assert yaml.safe_load(writer.dest.read_text()) == expected["yaml"]
