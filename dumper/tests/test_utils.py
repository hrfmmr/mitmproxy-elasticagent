import pytest

from oasdumper.models import HTTPMethod, SchemaType
from oasdumper.utils import (
    parameterized_endpoint_path,
    to_endpoint_dir,
    to_endpoint_path,
    build_operation_id,
    build_schema_identifier,
)


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("/v1/posts", "v1-posts"),
        ("/v1/ai_recommended_menus", "v1-ai_recommended_menus"),
    ],
)
def test_to_endpoint_dir(input, expected):
    assert to_endpoint_dir(input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("v1-posts", "/v1/posts"),
        (
            "v1-posts-{post_id}-comments-{comment_id}",
            "/v1/posts/{post_id}/comments/{comment_id}",
        ),
    ],
)
def test_to_endpoint_path(input, expected):
    assert to_endpoint_path(input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (
            "/v1/posts/100/comments/2",
            "/v1/posts/{post_id}/comments/{comment_id}",
        ),
    ],
)
def test_parameterized_endpoint_path(input, expected):
    assert parameterized_endpoint_path(input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (
            (HTTPMethod.GET, "/v1/posts/100/comments/2"),
            "getPostComment",
        ),
    ],
)
def test_build_operation_id(input, expected):
    assert build_operation_id(*input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (
            (
                HTTPMethod.GET,
                "/v1/posts/100/comments/2",
                SchemaType.REQUEST_PARAMS,
            ),
            "GetPostCommentRequestParams",
        ),
        (
            (
                HTTPMethod.POST,
                "/v1/albums",
                SchemaType.REQUEST_BODY,
            ),
            "PostAlbumsRequestBody",
        ),
        (
            (
                HTTPMethod.GET,
                "/v1/posts/100/comments/2",
                SchemaType.RESPONSE_BODY,
            ),
            "GetPostCommentResponse",
        ),
    ],
)
def test_build_schema_identifier(input, expected):
    assert build_schema_identifier(*input) == expected
