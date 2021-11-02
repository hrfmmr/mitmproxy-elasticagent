import json
import pathlib
import typing as t

from models import (
    HTTPMethod,
    OASEndpointList,
    OASEndpoint,
    OASPathMethodList,
    OASPathMethod,
    OASResponseList,
    OASResponse,
    OASResponseContent,
)
from constants import BUILD_DEST_DIR
from utils import endpoint_dir, response_description


class OASBuilder:
    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        _source: t.Dict[str, t.Any],
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self._source = _source

    def build_response_content(self) -> OASResponseContent:
        method = HTTPMethod[self._source["request"]["method"]]
        status_code = self._source["response"]["status_code"]
        response_content = json.loads(self._source["response"]["content"])
        dest = (
            endpoint_dir(self.endpoint_path)
            / method.value
            / "responses"
            / str(status_code)
            / "_index.yml"
        )
        description = response_description(status_code)
        return OASResponseContent(
            dest=self.dest_root / dest,
            description=description,
            content=response_content,
        )
