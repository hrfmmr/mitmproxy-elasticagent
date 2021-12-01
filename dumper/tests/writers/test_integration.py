import json
import logging
import pathlib
import pprint
import subprocess

import pytest
import yaml

from oasdumper.constants import TEMPLATE_OAS_REF, OAS_REF
from oasdumper.models import HTTPMethod
from oasdumper.writer import (
    OASRequestParamsSchemaWriter,
    OASRequestBodySchemaWriter,
    OASResponseSchemaWriter,
    OASResponseContentWriter,
    OASResponsePatternWriter,
    OASEndpointMethodWriter,
    OASEndpointMethodPatternWriter,
    OASEndpointPatternWriter,
    OASSchemaIndexWriter,
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
                        "paths/v1-posts-{post_id}-comments/_index.yml",
                        "paths/v1-posts-{post_id}-comments/get/_index.yml",
                        "paths/v1-posts-{post_id}-comments/get/responses/_index.yml",
                        "paths/v1-posts-{post_id}-comments/get/responses/200/_index.yml",
                        "paths/v1-posts/_index.yml",
                        "paths/v1-posts/post/_index.yml",
                        "paths/v1-posts/post/responses/_index.yml",
                        "paths/v1-posts/post/responses/200/_index.yml",
                    ],
                    yaml={
                        "components": {
                            "schemas": {
                                "GetPostCommentsRequestParams": {
                                    "properties": {"id": {"type": "string"}},
                                    "type": "object",
                                },
                                "GetPostCommentsResponse": {
                                    "properties": {
                                        "body": {"type": "string"},
                                        "email": {"type": "string"},
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"},
                                        "postId": {"type": "integer"},
                                    },
                                    "required": [
                                        "body",
                                        "email",
                                        "id",
                                        "name",
                                        "postId",
                                    ],
                                    "type": "object",
                                },
                                "PostPostsRequestBody": {
                                    "properties": {
                                        "body": {"type": "string"},
                                        "title": {"type": "string"},
                                        "userId": {"type": "integer"},
                                    },
                                    "required": ["body", "title", "userId"],
                                    "type": "object",
                                },
                                "PostPostsResponse": {
                                    "properties": {
                                        "body": {"type": "string"},
                                        "id": {"type": "integer"},
                                        "title": {"type": "string"},
                                        "userId": {"type": "integer"},
                                    },
                                    "required": [
                                        "body",
                                        "id",
                                        "title",
                                        "userId",
                                    ],
                                    "type": "object",
                                },
                            }
                        },
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
                                                    "$ref": "#/components/schemas/PostPostsRequestBody"
                                                }
                                            }
                                        }
                                    },
                                    "responses": {
                                        "200": {
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "$ref": "#/components/schemas/PostPostsResponse"
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
                                            "name": "GetPostCommentsRequestParams",
                                            "required": False,
                                            "schema": {
                                                "$ref": "#/components/schemas/GetPostCommentsRequestParams"
                                            },
                                        },
                                    ],
                                    "responses": {
                                        "200": {
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "$ref": "#/components/schemas/GetPostCommentsResponse"
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
        dest_root = pathlib.Path(".test")

        if dest_root.exists():
            from shutil import rmtree

            rmtree(".test")
        else:
            dest_root.mkdir()
        # debug

        for input in inputs:
            endpoint_path = input["endpoint_path"]
            method = HTTPMethod[input["_source"]["request"]["method"]]
            query = json.loads(input["_source"]["request"]["query"])
            request_content_raw = input["_source"]["request"]["content"]
            request_content = (
                json.loads(request_content_raw)
                if request_content_raw
                else None
            )
            response_content_raw = input["_source"]["response"]["content"]
            try:
                response_content = (
                    json.loads(response_content_raw)
                    if response_content_raw
                    else None
                )
            except json.decoder.JSONDecodeError:
                response_content = None
            status_code = input["_source"]["response"]["status_code"]

            if query:
                writer = OASRequestParamsSchemaWriter(
                    dest_root,
                    endpoint_path,
                    method,
                    query=query,
                )
                writer.write()

            if request_content:
                writer = OASRequestBodySchemaWriter(
                    dest_root,
                    endpoint_path,
                    method,
                    request_content=request_content,
                )
                writer.write()

            writer = OASResponseSchemaWriter(
                dest_root,
                endpoint_path,
                method,
                status_code,
                response_content,
            )
            writer.write()

            writer = OASResponseContentWriter(
                dest_root,
                endpoint_path,
                method,
                status_code,
                response_content,
            )
            writer.write()

            writer = OASResponsePatternWriter(
                dest_root,
                endpoint_path,
                method,
            )
            writer.write()

            writer = OASEndpointMethodWriter(
                dest_root,
                endpoint_path,
                method,
                query=query,
                request_content=request_content,
            )
            writer.write()

            writer = OASEndpointMethodPatternWriter(dest_root, endpoint_path)
            writer.write()

        writer = OASEndpointPatternWriter(dest_root)
        writer.write()

        schema_index_writer = OASSchemaIndexWriter(dest_root)
        schema_index_writer.write()

        writer = OASIndexWriter(
            dest_root,
            openapi_version=spec["openapi_version"],
            version=spec["version"],
            title=spec["title"],
            description=spec["description"],
            server_urls=spec["server_urls"],
            components={
                "schemas": yaml.safe_load(schema_index_writer.dest.read_text())
            },
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

        bundle_dest_path = pathlib.Path(".test/bundle.yml")
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
        raw_oas_yaml = bundle_dest_path.read_text()
        ref_enabled = raw_oas_yaml.replace(TEMPLATE_OAS_REF, OAS_REF)
        bundle_dest_path.write_text(ref_enabled)
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
