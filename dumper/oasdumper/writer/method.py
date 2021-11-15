import logging
import pathlib
import re
import typing as t

import yaml

from oasdumper.models import OASParameter, OASParameterSchema
from oasdumper.parser import OASParser
from oasdumper.utils import endpoint_dir, parameterized_endpoint_path
from oasdumper.utils.decorators import ensure_dest_exists
from oasdumper.types import YAML

logger = logging.getLogger(__name__)


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
        query: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> None:
        self.dest_root = dest_root
        self.endpoint_path = endpoint_path
        self.method = method
        self.query = query
        #  TODO: fix 'v1_posts_1_comments'
        self.dest = (
            self.dest_root
            / endpoint_dir(self.endpoint_path)
            / self.method
            / "_index.yml"
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
        params = []
        path_params = self._build_path_params()
        if path_params:
            params.extend(
                [
                    OASParameter(
                        _in="path",
                        name=k,
                        required=True,
                        schema=OASParameterSchema(
                            type=OASParser.gettype(type(v).__name__)
                        ),
                    )
                    for k, v in path_params.items()
                ]
            )
        if self.query:
            params.extend(
                [
                    OASParameter(
                        _in="query",
                        name=k,
                        required=False,
                        schema=OASParameterSchema(
                            type=OASParser.gettype(type(v).__name__)
                        ),
                    )
                    for k, v in self.query.items()
                ]
            )
        # TODO: append body params if exists
        if params:
            oas_json["parameters"] = [p.build_oas_json() for p in params]
        return yaml.dump(oas_json)

    def _build_path_params(self) -> t.Dict[str, t.Any]:
        path_params = {}
        parameterized_path = parameterized_endpoint_path(self.endpoint_path)
        rex_path_param = re.compile(r"^{(?P<res_id>.*_?id)}$")
        orig_components = self.endpoint_path.split("/")
        for i, c in enumerate(parameterized_path.split("/")):
            result = rex_path_param.match(c)
            if result:
                path_params[result.group("res_id")] = int(orig_components[i])
        return path_params

    def _build_operation_id(self) -> str:
        """
        eg.
            in: ('get', '/v1/posts/1/comments')
            out: 'getPostComments'
        """
        rex = re.compile(r"^/v[\d]+/(?P<path>.+)")
        result = re.match(rex, self.endpoint_path)
        path_without_version = result.group("path")
        path_params = self._build_path_params()
        operation_id = "".join(
            [self.method]
            + [
                s.capitalize()[:-1]
                if [k for k in path_params if s[:-1] in k]
                else s.capitalize()
                for s in path_without_version.split("/")
                if not s.isdigit()
            ]
        )
        return operation_id
