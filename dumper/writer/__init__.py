import pathlib
import typing as t

from models import (
    OASResponseContent,
)

from utils import endpoint_dir, response_description


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

    def write(self):
        oas_resp_content = self._build_response_content()
        oas_resp_content.write()

    def _build_response_content(self) -> OASResponseContent:
        dest = (
            endpoint_dir(self.endpoint_path)
            / self.method
            / "responses"
            / str(self.status_code)
            / "_index.yml"
        )
        description = response_description(self.status_code)
        return OASResponseContent(
            dest=self.dest_root / dest,
            description=description,
            content=self.response_content,
        )


class OASResponsePatternWriter:
    """
    '200':
      $ref: '200/_index.yml'
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
    ) -> None:
        self.dest_root = dest_root


class OASEndpointMethodWriter:
    """
    summary: Info for a specific pet
    operationId: showPetById
    tags:
      - pets
    responses:
      $ref: "responses/_index.yml"
    """

    pass


class OASEndpointMethodPatternWriter:
    """
    get:
      $ref: 'get/_index.yml'
    post:
      $ref: 'post/_index.yml'
    """

    pass
