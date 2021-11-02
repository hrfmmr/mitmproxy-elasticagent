import json
import pathlib
import re
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from pprint import pprint
from urllib.parse import urlparse, parse_qs
import typing as t

from elasticsearch import Elasticsearch

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

REGEX_PATH_PARAM = re.compile(r"\b(?P<id>[0-9]+)")
REGEX_VERSIONED_ENDPOINT_PATH = re.compile(r"(?P<version>^v[\d]+)")
PATH_PARAM_ID = "{id}"

ELASTICSEARCH_INDEX = "ios-kenko"


def snake_to_camel(w: str):
    return "".join(x.capitalize() or "_" for x in w.split("_"))


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
    es = Elasticsearch("http://localhost:9200")
    #  pprint(es.info())
    indices = es.cat.indices(index="*", h="index").splitlines()
    #  pprint(indices)

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
    # request.pathでGROUP BY的に集約してdistinctなpathsを抽出する
    for bucket in result["aggregations"]["requestpaths"]["buckets"]:
        path = bucket["key"]
        parsed = urlparse(path)
        parameterized_path = REGEX_PATH_PARAM.sub(PATH_PARAM_ID, parsed.path)
        path_query_map[parameterized_path].append(parse_qs(parsed.query))
    # pathをkeyに、[method,query,req_content,resp_content]の単位リクエスト情報のdictをリスト要素としてつっこむ箱(あとで、param長が最大になるようにmergeできるようにひとまず全リクエストをつっこんでいく)
    #  endpoints = defaultdict(list)
    for path in list(path_query_map.keys()):
        #  print(f"path:{path}")
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
                #  pprint(info)
                print(json.dumps(info, indent=2, ensure_ascii=False))
            else:
                print(f"cannot extract info from path:{path}")


def build_endpoint(_source: t.Dict[str, t.Any]) -> OASEndpoint:
    pass


def build_response_content(
    endpoint_path: str, _source: t.Dict[str, t.Any]
) -> OASResponseContent:
    # paths/pets/get/responses/200/_index.yml
    method = HTTPMethod[_source["request"]["method"]]
    status_code = _source["response"]["status_code"]
    response_content = json.loads(_source["response"]["content"])
    dest = (
        endpoint_dir(endpoint_path)
        / method.value
        / "responses"
        / str(status_code)
        / "_index.yml"
    )
    description = response_description(status_code)
    return OASResponseContent(
        dest=pathlib.Path(BUILD_DEST_DIR) / dest,
        description=description,
        content=response_content,
    )


if __name__ == "__main__":
    main()
