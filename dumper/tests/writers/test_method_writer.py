import json
import logging
import pathlib

import pytest
import yaml

from oasdumper.writer import (
    OASEndpointMethodWriter,
)

logger = logging.getLogger(__name__)


class TestOASEndpointMethodWriter:
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
                {
                    "operationId": "getPostComments",
                    "parameters": [
                        {
                            "in": "path",
                            "name": "post_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "query",
                            "name": "id",
                            "required": False,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {"$ref": "responses/_index.yml"},
                    "summary": "",
                },
            )
        ],
    )
    def test_write(self, input, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)
        logger.info(f"dest_root:{str(tmpdir)}")
        writer = OASEndpointMethodWriter(
            dest_root,
            input["endpoint_path"],
            "get",
            query=json.loads(input["_source"]["request"]["query"]),
        )
        writer.write()
        logger.debug(list(dest_root.glob("**/*")))
        logger.debug(writer.dest.read_text())
        logger.debug(yaml.safe_load(writer.dest.read_text()))

        assert yaml.safe_load(writer.dest.read_text()) == expected
