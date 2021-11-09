import typing as t
from enum import Enum
from dataclasses import dataclass


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
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
