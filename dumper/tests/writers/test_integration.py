import json
import logging
import pathlib
import pprint
import subprocess

import pytest
import yaml

from oasdumper.models import HTTPMethod

from oasdumper.writer import (
    OASResponseContentWriter,
    OASResponsePatternWriter,
    OASEndpointMethodWriter,
    OASEndpointMethodPatternWriter,
    OASEndpointPatternWriter,
    OASIndexWriter,
)

logger = logging.getLogger(__name__)


class TestIntegratedWriters:
    @pytest.mark.parametrize(
        ("spec", "inputs", "expected"),
        [
            (
                dict(
                    openapi_version="3.0.0",
                    version="0.0.1",
                    title="test api",
                    description="test description",
                    server_urls=["https://example.com"],
                ),
                [
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
                ],
                dict(
                    paths=[
                        "index.yml",
                        "paths/_index.yml",
                        "paths/v1_posts/_index.yml",
                        "paths/v1_posts/post/_index.yml",
                        "paths/v1_posts/post/responses/_index.yml",
                        "paths/v1_posts/post/responses/200/_index.yml",
                        "paths/v1_posts_{post_id}_comments/_index.yml",
                        "paths/v1_posts_{post_id}_comments/get/_index.yml",
                        "paths/v1_posts_{post_id}_comments/get/responses/_index.yml",
                        "paths/v1_posts_{post_id}_comments/get/responses/200/_index.yml",
                    ],
                    yaml={
                        "info": {
                            "description": "test description",
                            "title": "test api",
                            "version": "0.0.1",
                        },
                        "openapi": "3.0.0",
                        "paths": {
                            "/v1/posts": {
                                "post": {
                                    "operationId": "postPosts",
                                    "requestBody": {
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "properties": {
                                                        "body": {
                                                            "type": "string"
                                                        },
                                                        "title": {
                                                            "type": "string"
                                                        },
                                                        "userId": {
                                                            "type": "integer"
                                                        },
                                                    },
                                                    "type": "object",
                                                }
                                            }
                                        }
                                    },
                                    "responses": {
                                        "200": {
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "properties": {
                                                            "body": {
                                                                "type": "string"
                                                            },
                                                            "id": {
                                                                "type": "integer"
                                                            },
                                                            "title": {
                                                                "type": "string"
                                                            },
                                                            "userId": {
                                                                "type": "integer"
                                                            },
                                                        },
                                                        "type": "object",
                                                    }
                                                }
                                            },
                                            "description": "Expected response to a valid request",
                                        }
                                    },
                                    "summary": "",
                                }
                            },
                            "/v1/posts/{post_id}/comments": {
                                "get": {
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
                                    "responses": {
                                        "200": {
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "properties": {
                                                            "body": {
                                                                "type": "string"
                                                            },
                                                            "email": {
                                                                "type": "string"
                                                            },
                                                            "id": {
                                                                "type": "integer"
                                                            },
                                                            "name": {
                                                                "type": "string"
                                                            },
                                                            "postId": {
                                                                "type": "integer"
                                                            },
                                                        },
                                                        "type": "object",
                                                    }
                                                }
                                            },
                                            "description": "Expected response to a valid request",
                                        }
                                    },
                                    "summary": "",
                                }
                            },
                        },
                        "servers": [{"url": "https://example.com"}],
                    },
                ),
            )
        ],
    )
    def test_write(self, spec, inputs, expected, tmpdir):
        #  dest_root = pathlib.Path(tmpdir)
        # debug
        dest_root = pathlib.Path(".tmp")

        if dest_root.exists():
            from shutil import rmtree

            rmtree(".tmp")
        else:
            dest_root.mkdir()
        # debug

        for input in inputs:
            response_content_raw = input["_source"]["response"]["content"]
            try:
                response_content = (
                    json.loads(response_content_raw)
                    if response_content_raw
                    else None
                )
            except json.decoder.JSONDecodeError:
                response_content = None
            writer = OASResponseContentWriter(
                dest_root,
                input["endpoint_path"],
                HTTPMethod[input["_source"]["request"]["method"]],
                input["_source"]["response"]["status_code"],
                response_content,
            )
            writer.write()

            writer = OASResponsePatternWriter(
                dest_root,
                input["endpoint_path"],
                HTTPMethod[input["_source"]["request"]["method"]],
            )
            writer.write()

            request_content_raw = input["_source"]["request"]["content"]
            request_content = (
                json.loads(request_content_raw)
                if request_content_raw
                else None
            )
            writer = OASEndpointMethodWriter(
                dest_root,
                input["endpoint_path"],
                HTTPMethod[input["_source"]["request"]["method"]],
                query=json.loads(input["_source"]["request"]["query"]),
                request_content=request_content,
            )
            writer.write()

            writer = OASEndpointMethodPatternWriter(
                dest_root, input["endpoint_path"]
            )
            writer.write()

        writer = OASEndpointPatternWriter(dest_root)
        writer.write()

        writer = OASIndexWriter(
            dest_root,
            spec["openapi_version"],
            spec["version"],
            spec["title"],
            spec["description"],
            spec["server_urls"],
        )
        writer.write()

        logger.debug(
            pprint.pformat(list(dest_root.glob("**/*.yml")), indent=2)
        )
        logger.debug(writer.dest.read_text())

        for path, exp_path in zip(
            dest_root.glob("**/*.yml"), expected["paths"]
        ):
            assert str(path) == str(dest_root / exp_path)

        bundle_dest_path = pathlib.Path(".build/oas.yml")
        subprocess.run(
            [
                "./node_modules/.bin/swagger-cli",
                "bundle",
                str(writer.dest),
                "--outfile",
                str(bundle_dest_path),
                "--type",
                "yaml",
            ],
            check=True,
        )
        subprocess.run(
            [
                "./node_modules/.bin/spectral",
                "lint",
                str(bundle_dest_path),
            ],
            check=True,
        )
        logger.debug(f"📜yaml:\n{yaml.safe_load(bundle_dest_path.read_text())}")
        assert yaml.safe_load(bundle_dest_path.read_text()) == expected["yaml"]
