import logging
import pathlib
import re
import typing as t

import yaml

from oasdumper.models import HTTPMethod, SchemaType
from oasdumper.utils import (
    schema_root_dir,
    to_endpoint_path,
    build_schema_identifier,
)
from oasdumper.utils.decorators import ensure_dest_exists
from oasdumper.types import YAML


logger = logging.getLogger(__name__)

method_patterns = "|".join([e.value for e in HTTPMethod])
REX_REQUEST_PARAMS = re.compile(
    r".*/components/schemas/(?P<endpoint_dir>.+)/(?P<method>{methods})/request_params.yml$".format(
        methods=method_patterns
    )
)
REX_REQUEST_BODY = re.compile(
    r".*/components/schemas/(?P<endpoint_dir>.+)/(?P<method>{methods})/request_body.yml$".format(
        methods=method_patterns
    )
)
REX_RESPONSE_BODY = re.compile(
    r".*/components/schemas/(?P<endpoint_dir>.+)/(?P<method>{methods})".format(
        methods=method_patterns
    )
    + r"/responses/(?P<status_code>\d{3})/.*.yml$"
)


class OASSchemaIndexWriter:
    """
    GetPostCommentRequestParams:
      $ref: v1-posts-{post_id}-comments/get/request_params.yml
    GetPostPhotoResponse:
      $ref: v1-posts-{post_id}-photos/get/responses/200/_index.yml
    PostPostsRequestBody:
      $ref: v1-posts/post/request_body.yml
    """

    def __init__(
        self,
        dest_root: pathlib.Path,
    ) -> None:
        self.dest_root = dest_root
        self.dest = self.dest_root / schema_root_dir() / "_index.yml"

    @ensure_dest_exists
    def write(self):
        oas_yaml = self._build()
        self.dest.write_text(oas_yaml)

    def _build(self) -> YAML:
        oas_json = {}
        for schema_id, path in self._extract_schemas():
            schema_path = path.relative_to(self.dest.parent)
            oas_json[schema_id] = {"$ref": str(schema_path)}
        return yaml.dump(oas_json)

    def _extract_schemas(
        self,
    ) -> t.Generator[t.Tuple[str, pathlib.Path], None, None]:
        paths = self.dest.parent.glob("**/*.yml")
        for p in paths:
            result = REX_REQUEST_PARAMS.match(str(p))
            if result:
                endpoint_dir = result.group("endpoint_dir")
                method = result.group("method")
                yield build_schema_identifier(
                    HTTPMethod(method),
                    to_endpoint_path(endpoint_dir),
                    SchemaType.REQUEST_PARAMS,
                ), p
                continue
            result = REX_REQUEST_BODY.match(str(p))
            if result:
                endpoint_dir = result.group("endpoint_dir")
                method = result.group("method")
                yield build_schema_identifier(
                    HTTPMethod(method),
                    to_endpoint_path(endpoint_dir),
                    SchemaType.REQUEST_BODY,
                ), p
                continue
            result = REX_RESPONSE_BODY.match(str(p))
            if result:
                endpoint_dir = result.group("endpoint_dir")
                method = result.group("method")
                yield build_schema_identifier(
                    HTTPMethod(method),
                    to_endpoint_path(endpoint_dir),
                    SchemaType.RESPONSE_BODY,
                ), p
                continue
            if not result:
                logger.warning(f"🚨 unexpected schema path:{str(p)}")
                continue
