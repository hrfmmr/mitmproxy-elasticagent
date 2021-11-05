import pathlib
from pprint import pprint

from writer import OASResponseContentWriter


class TestOASResponseContentWriter:
    def test_write(self):
        """
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: str,
        status_code: int,
        response_content: t.Dict[str, t.Any],
        """
        endpoint_path = "/v1/home/layout"
        content = {
            "response": {
                "status_code": 200,
                "content": '{"sections":["announcement","todays_recipe","ai_recommended_menus","meal_reports","dietary_concern_themes","recipe_suggestions"]}',
            }
        }
        dest_root = pathlib.Path(".tmp")
        writer = OASResponseContentWriter(
            dest_root, endpoint_path, "get", 200, content
        )
        writer.write()
        pprint(list(dest_root.glob("**/*.yml")))
        assert False
