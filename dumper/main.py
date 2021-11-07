import json
import logging
import pathlib
import re
from dataclasses import dataclass, field
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import typing as t

from elasticsearch import Elasticsearch

from oasdumper.logging import setup_logger

REGEX_PATH_PARAM = re.compile(r"\b(?P<id>[0-9]+)")
REGEX_VERSIONED_ENDPOINT_PATH = re.compile(r"(?P<version>^v[\d]+)")
PATH_PARAM_ID = "{id}"

ELASTICSEARCH_INDEX = "ios-kenko"

logger = logging.getLogger(__name__)


class OASPath:
    def __init__(self, path: str, method: str):
        path_endpoint = path.replace("/", "_")[1:]
        self.ref = str(
            pathlib.Path(".")
            / "paths"
            / path_endpoint
            / f"{method.lower()}.yml"
        )


@dataclass
class OASServer:
    url: str


@dataclass
class OASInfo:
    version: str = "0.0.1"
    title: str = "Kenko API"
    description: str = "API of oishi-kenko"


@dataclass
class OASBase:
    openapi: str = "3.0.0"
    info: OASInfo = OASInfo()
    servers: t.List[OASServer] = field(default_factory=list)
    paths: t.Dict[str, t.Any] = field(default_factory=dict)


def main():
    setup_logger()
    es = Elasticsearch("http://localhost:9200")

    result = es.search(
        index=ELASTICSEARCH_INDEX,
        aggs=dict(
            requestpaths=dict(
                terms=dict(field="request.path.keyword", size=10_000)
            )
        ),
        _source=[
            "request.path",
        ],
    )
    path_query_map = defaultdict(list)
    for bucket in result["aggregations"]["requestpaths"]["buckets"]:
        path = bucket["key"]
        parsed = urlparse(path)
        parameterized_path = REGEX_PATH_PARAM.sub(PATH_PARAM_ID, parsed.path)
        path_query_map[parameterized_path].append(parse_qs(parsed.query))
    for path in list(path_query_map.keys()):
        if path == "/v1/home/layout":
            result = es.search(
                index=ELASTICSEARCH_INDEX,
                query=dict(term={"request.path.keyword": path}),
                _source=[
                    "request.method",
                    "request.query",
                    "request.content",
                    "response.status_code",
                    "response.content",
                ],
            )
            if result["hits"] and result["hits"]["hits"]:
                info = result["hits"]["hits"][0]["_source"]
                logger.debug(json.dumps(info, indent=2, ensure_ascii=False))
                # TODO: write OAS yaml
            else:
                logger.debug(f"cannot extract info from path:{path}")


if __name__ == "__main__":
    main()
