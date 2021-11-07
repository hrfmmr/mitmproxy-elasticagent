import logging
import pathlib
import re
import typing as t
from functools import wraps
from pprint import pprint

import yaml

from models import (
    OASResponseContent,
)

from utils import endpoint_dir, response_description

logger = logging.getLogger(__name__)
YAML = str


def ensure_dest_exists(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.dest.is_file():
            assert f"dest:{self.dest} must be file"
        logger.debug(f"self:{self} create dest:{str(self.dest)}")
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        return f(self, *args, **kwargs)

    return wrapper


class OASResponseContentWriter:
    """
    description: Expected response to a valid request
    content:
      application/json:
        schema:
          type: object
          properties:
            id:
              type: integer
              format: int64
            name:
              type: string
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: str,
        status_code: int,
        response_content: t.Dict[str, t.Any],
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method
        self.status_code = status_code
        self.response_content = response_content
        self.dest = (
            self.dest_root
            / endpoint_dir(self.endpoint_path)
            / self.method
            / "responses"
            / str(self.status_code)
            / "_index.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build_response_content()
        logger.debug(f"🐛 oas_yaml:{oas_yaml}")
        self.dest.write_text(oas_yaml)

    def _build_response_content(self) -> YAML:
        description = response_description(self.status_code)
        model = OASResponseContent(
            dest=self.dest,
            description=description,
            content=self.response_content,
        )
        return model.build()


class OASResponsePatternWriter:
    """
    '200':
      $ref: '200/_index.yml'
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: str,
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method

        self.dest = (
            self.dest_root
            / endpoint_dir(self.endpoint_path)
            / self.method
            / "responses"
            / "_index.yml"
        )
        pprint(self.dest)
        self.rex_status_code = re.compile(
            r"^{}/(?P<status_code>[\d]+)/_index.ya?ml$".format(
                str(self.dest.parent)
            )
        )

    def _build(self) -> YAML:
        paths = self.dest.parent.glob("**/*.yml")
        oas_json = {}
        for p in paths:
            result = re.match(self.rex_status_code, str(p))
            status_code = result.group("status_code")
            oas_json[status_code] = {"$ref": f"{status_code}/_index.yml"}

        pprint(oas_json)
        return yaml.dump(oas_json)

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)


class OASEndpointMethodWriter:
    """
    summary: Info for a specific pet
    operationId: showPetById
    tags:
      - pets
    responses:
      $ref: "responses/_index.yml"
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
        endpoint_path: str,
        method: str,
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method
        self.dest = (
            endpoint_dir(self.endpoint_path) / self.method / "_index.yml"
        )

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        oas_json = {
            "summary": "",
            "operationId": self._build_operation_id(),
            "responses": {"$ref": "responses/_index.yml"},
        }
        return yaml.dump(oas_json)

    def _build_operation_id(self) -> str:
        rex = re.compile(r"^/v[\d]+/(?P<path>.+)")
        result = re.match(rex, self.endpoint_path)
        path_without_version = result.group("path")
        operation_id = "".join(
            [self.method]
            + [s.capitalize() for s in path_without_version.split("/")]
        )
        return operation_id


class OASEndpointMethodPatternWriter:
    """
    get:
      $ref: 'get/_index.yml'
    post:
      $ref: 'post/_index.yml'
    """

    pass
