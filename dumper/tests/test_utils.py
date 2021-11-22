import pytest

from oasdumper.utils import (
    parameterized_endpoint_path,
    to_endpoint_dir,
    to_endpoint_path,
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
