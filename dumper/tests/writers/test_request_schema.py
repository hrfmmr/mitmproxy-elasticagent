import json
import logging
import pathlib
import pprint

import pytest
import yaml

from oasdumper.models import HTTPMethod
from oasdumper.writer import (
    OASRequestParamsSchemaWriter,
    OASRequestBodySchemaWriter,
)

logger = logging.getLogger(__name__)


class TestOASRequestParamsSchemaWriter:
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


class TestOASRequestBodySchemaWriter:
    @pytest.mark.parametrize(
        ("input", "expected"),
        [
            (
                dict(
                    endpoint_path="/v1/posts",
                    _source={
                        "request": {
                            "method": "POST",
                            "query": "{}",
                            "content": '{"title": "foo", "body": "bar", "userId": 1}',
                        },
                        "response": {
                            "status_code": 200,
                            "content": '{"id": 101, "title": "foo", "body": "bar", "userId": 1}',
                        },
                    },
                ),
                dict(
                    path="components/schemas/v1-posts/post/request_body.yml",
                    yaml={
                        "properties": {
                            "body": {"type": "string"},
                            "title": {"type": "string"},
                            "userId": {"type": "integer"},
                        },
                        "type": "object",
                    },
                ),
            )
        ],
    )
    def test_write(self, input, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)
        writer = OASRequestBodySchemaWriter(
            dest_root,
            input["endpoint_path"],
            HTTPMethod[input["_source"]["request"]["method"]],
            request_content=json.loads(input["_source"]["request"]["content"]),
        )
        writer.write()
        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(writer.dest.read_text())
        logger.debug(yaml.safe_load(writer.dest.read_text()))
        assert str(writer.dest) == str(dest_root / expected["path"])
        assert yaml.safe_load(writer.dest.read_text()) == expected["yaml"]
