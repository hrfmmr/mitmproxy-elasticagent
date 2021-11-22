import logging
import pathlib
import pprint

import pytest
import yaml

from oasdumper.utils import endpoint_dir
from oasdumper.writer import (
    OASEndpointPatternWriter,
)

logger = logging.getLogger(__name__)


def touch_child(dest_root: pathlib.Path, endpoint_path: str):
    path = dest_root / endpoint_dir(endpoint_path)
    path.mkdir(parents=True, exist_ok=True)


class TestOASEndpointPatternWriter:
    @pytest.mark.parametrize(
        ("endpoints", "expected"),
        [
            (
                ("/v1/posts", "/v1/albums", "/v1/posts/1/comments/2"),
                dict(
                    path="paths/_index.yml",
                    yaml={
                        "/v1/albums": {"$ref": "v1-albums/_index.yml"},
                        "/v1/posts": {"$ref": "v1-posts/_index.yml"},
                        "/v1/posts/{post_id}/comments/{comment_id}": {
                            "$ref": "v1-posts-{post_id}-comments-{comment_id}/_index.yml"
                        },
                    },
                ),
            )
        ],
    )
    def test_write(self, endpoints, expected, tmpdir):
        dest_root = pathlib.Path(tmpdir)

        for e in endpoints:
            touch_child(dest_root, e)

        logger.info(f"dest_root:{str(tmpdir)}")
        writer = OASEndpointPatternWriter(dest_root)
        writer.write()
        logger.debug(pprint.pformat(list(dest_root.glob("**/*")), indent=2))
        logger.debug(f"📜yaml:\n{writer.dest.read_text()}")
        logger.debug(yaml.safe_load(writer.dest.read_text()))

        assert str(writer.dest) == str(dest_root / expected["path"])
        assert yaml.safe_load(writer.dest.read_text()) == expected["yaml"]
