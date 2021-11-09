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
    pattern_set = set()
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
            if not (result["hits"] and result["hits"]["hits"]):
                continue
            logger.info(
                json.dumps(
                    result["hits"]["hits"], indent=2, ensure_ascii=False
                )
            )
            hits = result["hits"]["hits"]
            for hit in hits:
                info = hit["_source"]
                pattern = (
                    path,
                    info["request"]["method"],
                    info["response"]["status_code"],
                )
                if pattern in pattern_set:
                    continue
                logger.debug(json.dumps(info, indent=2, ensure_ascii=False))
                pattern_set.add(pattern)
                # TODO: write with
                # OASResponseContentWriter,
                # OASResponsePatternWriter,
                # OASEndpointMethodWriter,
            else:
                logger.debug(f"cannot extract info from path:{path}")
    # TODO: write with
    # OASEndpointPatternWriter
    # OASIndexWriter


if __name__ == "__main__":
    main()
