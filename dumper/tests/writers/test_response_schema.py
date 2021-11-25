import json
import logging
import pathlib
import pprint

import pytest
import yaml

from oasdumper.models import HTTPMethod
from oasdumper.writer import (
    OASResponseSchemaWriter,
)

logger = logging.getLogger(__name__)


class TestOASResponseSchemaWriter:
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
                    path="components/schemas/v1-posts-{post_id}-comments/get/responses/200/_index.yml",
                    yaml={
                        "properties": {
                            "body": {"type": "string"},
                            "email": {"type": "string"},
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "postId": {"type": "integer"},
                        },
                        "required": sorted(
                            ["postId", "id", "name", "email", "body"]
                        ),
                        "type": "object",
                    },
                ),
            )
        ],
    )
    def test_write(self, input, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)
        response_content_raw = input["_source"]["response"]["content"]
        try:
            response_content = (
                json.loads(response_content_raw)
                if response_content_raw
                else None
            )
        except json.decoder.JSONDecodeError:
            response_content = None
        writer = OASResponseSchemaWriter(
            dest_root,
            input["endpoint_path"],
            HTTPMethod[input["_source"]["request"]["method"]],
            input["_source"]["response"]["status_code"],
            response_content,
        )
        writer.write()
        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(writer.dest.read_text())
        logger.debug(yaml.safe_load(writer.dest.read_text()))
        assert str(writer.dest) == str(dest_root / expected["path"])
        assert yaml.safe_load(writer.dest.read_text()) == expected["yaml"]
