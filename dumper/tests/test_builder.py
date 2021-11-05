import json
import pathlib
from pprint import pprint

import yaml

from builder import OASBuilder


def load_params(json_path):
    with open(json_path) as f:
        return json.load(f)


class TestBuilder:
    def test_build_response_content(self, tmpdir):
        endpoint_path = "/v1/home/layout"
        _source = load_params("tests/fixtures/_sources/v1_home_layout.json")
        pprint(_source)
        builder = OASBuilder(
            #  pathlib.Path(tmpdir) / "_index.yml", endpoint_path, _source
            pathlib.Path(".tmp"),
            endpoint_path,
            _source,
        )
        oas_resp_content = builder.build_response_content()
        pprint(oas_resp_content.build())
        oas_resp_content.write()
        with open(oas_resp_content.dest) as f:
            loaded = yaml.safe_load(f)
        expected = {
            "content": {
                "application/json": {
                    "schema": {
                        "properties": {
                            "sections": {
                                "items": {"type": "string"},
                                "type": "array",
                            }
                        },
                        "type": "object",
                    }
                }
            },
            "description": "Expected response to a valid request",
        }
        assert loaded == expected
