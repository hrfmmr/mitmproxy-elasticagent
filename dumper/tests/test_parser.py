import json
import logging

import pytest

from oasdumper.parser import OASParser

logger = logging.getLogger(__name__)


class TestOASParser:
    @pytest.mark.parametrize(
        ("schema_json", "expected"),
        [
            (
                {
                    "user": {
                        "id": 1,
                        "name": None,
                        "posts": [],
                    }
                },
                {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                            },
                        }
                    },
                },
            )
        ],
    )
    def test_parse(self, schema_json, expected):
        oas_schema = OASParser.parse(schema_json)
        logger.debug(f"📜oas_schema:\n{json.dumps(oas_schema, indent=2)}")
        assert oas_schema == expected
