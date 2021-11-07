import json
import logging
import pathlib
from pprint import pprint

from oasdumper.writer import (
    OASResponseContentWriter,
    OASResponsePatternWriter,
    OASEndpointMethodWriter,
    OASEndpointMethodPatternWriter,
)

logger = logging.getLogger(__name__)


class TestWriter:
    def test_write(self):
        """
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: str,
        status_code: int,
        response_content: t.Dict[str, t.Any],
        """
        endpoint_path = "/v1/home/layout"
        info = {
            "request": {
                "method": "GET",
                "query": '{"platform": "ios"}',
                "content": "",
            },
            "response": {
                "status_code": 200,
                "content": '{"sections":["announcement","todays_recipe","ai_recommended_menus","meal_reports","dietary_concern_themes","recipe_suggestions"]}',
            },
        }
        # debug
        dest_root = pathlib.Path(".tmp")

        if dest_root.exists():
            from shutil import rmtree

            rmtree(".tmp")
        else:
            dest_root.mkdir()
        # debug

        dest_root = pathlib.Path(".tmp")
        writer = OASResponseContentWriter(
            dest_root, endpoint_path, "get", 200, info["response"]
        )
        writer.write()
        logger.info(list(dest_root.glob("**/*.yml")))

        writer = OASResponsePatternWriter(dest_root, endpoint_path, "get")
        writer.write()
        logger.info(list(dest_root.glob("**/*.yml")))

        writer = OASEndpointMethodWriter(
            dest_root,
            endpoint_path,
            "get",
            query=json.loads(info["request"]["query"]),
        )
        writer.write()
        logger.info(list(dest_root.glob("**/*.yml")))

        writer = OASEndpointMethodPatternWriter(dest_root, endpoint_path)
        writer.write()
        logger.info(list(dest_root.glob("**/*.yml")))

        assert False, "💚"
