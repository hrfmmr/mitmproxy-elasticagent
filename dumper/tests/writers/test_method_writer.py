import json
import logging
import pathlib

import pytest
import yaml

from oasdumper.models import HTTPMethod
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
                dict(
                    path="paths/v1-posts-{post_id}-comments/get/_index.yml",
                    yaml={
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
                ),
            ),
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
                    path="paths/v1-posts/post/_index.yml",
                    yaml={
                        "operationId": "postPosts",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "properties": {
                                            "body": {"type": "string"},
                                            "title": {"type": "string"},
                                            "userId": {"type": "integer"},
                                        },
                                        "type": "object",
                                    }
                                }
                            }
                        },
                        "responses": {"$ref": "responses/_index.yml"},
                        "summary": "",
                    },
                ),
            ),
            (
                dict(
                    endpoint_path="/v1/foo_bar_baz",
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
                    path="paths/v1-foo_bar_baz/post/_index.yml",
                    yaml={
                        "operationId": "postFooBarBaz",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "properties": {
                                            "body": {"type": "string"},
                                            "title": {"type": "string"},
                                            "userId": {"type": "integer"},
                                        },
                                        "type": "object",
                                    }
                                }
                            }
                        },
                        "responses": {"$ref": "responses/_index.yml"},
                        "summary": "",
                    },
                ),
            ),
        ],
    )
    def test_write(self, input, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)
        logger.info(f"dest_root:{str(tmpdir)}")
        request_content_raw = input["_source"]["request"]["content"]
        request_content = (
            json.loads(request_content_raw) if request_content_raw else None
        )
        writer = OASEndpointMethodWriter(
            dest_root,
            input["endpoint_path"],
            HTTPMethod[input["_source"]["request"]["method"]],
            query=json.loads(input["_source"]["request"]["query"]),
            request_content=request_content,
        )
        writer.write()
        logger.debug(list(dest_root.glob("**/*")))
        logger.debug(writer.dest.read_text())
        logger.debug(yaml.safe_load(writer.dest.read_text()))

        assert str(writer.dest) == str(dest_root / expected["path"])
        assert yaml.safe_load(writer.dest.read_text()) == expected["yaml"]
