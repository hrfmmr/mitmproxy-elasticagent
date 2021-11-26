import json
import logging
import pathlib
import pprint

import pytest
import yaml

from oasdumper.models import HTTPMethod
from oasdumper.writer import (
    OASRequestParamsSchemaWriter,
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
                    path="components/schemas/v1-posts-{post_id}-comments/get/request_params.yml",
                    yaml={
                        "properties": {"id": {"type": "string"}},
                        "type": "object",
                    },
                ),
            )
        ],
    )
    def test_write(self, input, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)
        writer = OASRequestParamsSchemaWriter(
            dest_root,
            input["endpoint_path"],
            HTTPMethod[input["_source"]["request"]["method"]],
            query=json.loads(input["_source"]["request"]["query"]),
        )
        writer.write()
        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(writer.dest.read_text())
        logger.debug(yaml.safe_load(writer.dest.read_text()))
        assert str(writer.dest) == str(dest_root / expected["path"])
        assert yaml.safe_load(writer.dest.read_text()) == expected["yaml"]
