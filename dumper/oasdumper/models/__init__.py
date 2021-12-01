import logging
import typing as t
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class SchemaType(Enum):
    REQUEST_PARAMS = "RequestParams"
    REQUEST_BODY = "RequestBody"
    RESPONSE_BODY = "Response"


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


@dataclass
class OASServer:
    url: str


@dataclass
class OASSpecInfo:
    version: str
    title: str
    description: str


@dataclass
class OASIndexInfo:
    openapi: str
    info: OASSpecInfo
    servers: t.List[OASServer]
    paths: t.Dict[str, t.Any]
    components: t.Dict[str, t.Any]


@dataclass
class OASParameterSchema:
    type: str


@dataclass
class OASParameter:
    _in: str
    name: str
    required: bool
    schema: OASParameterSchema

    def build_oas_json(self) -> t.Dict[str, t.Any]:
        return asdict(self, dict_factory=self._dict_factory)

    def _dict_factory(self, data) -> t.Dict[str, t.Any]:
        if data[0][0] == "_in":
            data[0] = ("in", data[0][1])
        return dict(data)
