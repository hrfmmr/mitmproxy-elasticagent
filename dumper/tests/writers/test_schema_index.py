import json
import logging
import pathlib
import pprint
import typing as t

import pytest
import yaml

from oasdumper.models import HTTPMethod
from oasdumper.utils import (
    schema_root_dir,
)
from oasdumper.writer import (
    OASSchemaIndexWriter,
)

logger = logging.getLogger(__name__)


@pytest.fixture
def dummy_content():
    yield {
        "properties": {
            "name": {"type": "string"},
        },
        "required": sorted(["name"]),
        "type": "object",
    }


def touch_child(
    dest_root: pathlib.Path,
    schema_path: str,
    schema_content: t.Dict[str, t.Any],
):
    path = dest_root / schema_root_dir() / schema_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(schema_content))


class TestOASSchemaIndexWriter:
    @pytest.mark.parametrize(
        ("schema_paths", "expected"),
        [
            (
                [
                    "v1-posts-{post_id}-comments/get/request_params.yml",
                    "v1-posts/post/request_body.yml",
                    "v1-posts-{post_id}-photos/get/responses/200/_index.yml",
                ],
                dict(
                    path="components/schemas/_index.yml",
                    yaml={
                        "GetPostCommentResponse": {
                            "properties": {"name": {"type": "string"}},
                            "required": ["name"],
                            "type": "object",
                        },
                        "GetPostPhotoResponse": {
                            "properties": {"name": {"type": "string"}},
                            "required": ["name"],
                            "type": "object",
                        },
                        "PostPostsResponse": {
                            "properties": {"name": {"type": "string"}},
                            "required": ["name"],
                            "type": "object",
                        },
                    },
                ),
            ),
        ],
    )
    def test_write(self, schema_paths, expected, dummy_content, tmpdir):
        dest_root = pathlib.Path(tmpdir)

        for p in schema_paths:
            touch_child(dest_root, p, dummy_content)

        writer = OASSchemaIndexWriter(dest_root)
        writer.write()

        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(f"📜yaml:\n{writer.dest.read_text()}")
        logger.debug(yaml.safe_load(writer.dest.read_text()))
