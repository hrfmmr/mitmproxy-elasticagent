import json
import logging
import subprocess
import os
import pathlib
from collections import defaultdict
from urllib.parse import urlparse, parse_qs

from elasticsearch import Elasticsearch

from oasdumper.logging import setup_logger
from oasdumper.models import HTTPMethod
from oasdumper.writer import (
    OASResponseContentWriter,
    OASResponsePatternWriter,
    OASEndpointMethodWriter,
    OASEndpointMethodPatternWriter,
    OASEndpointPatternWriter,
    OASIndexWriter,
)
from oasdumper.utils import parameterized_endpoint_path

ELASTICSEARCH_INDEX = os.environ["ELASTICSEARCH_INDEX"]
OAS_TMP_DEST = ".tmp"
OAS_BUNDLED_YAML = ".bundle/oas.yml"
OAS_BUNDLED_HTML = ".bundle/index.html"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        logger.debug(f"parsed:{parsed}")
        parameterized_path = parameterized_endpoint_path(parsed.path)
        path_query_map[parameterized_path].append(parse_qs(parsed.query))
    dest_root = pathlib.Path(OAS_TMP_DEST)
    pattern_set = set()
    for path in list(path_query_map.keys()):
        logger.debug(f"path:{path}")
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
        logger.debug(
            json.dumps(result["hits"]["hits"], indent=2, ensure_ascii=False)
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

            response_content_raw = info["response"]["content"]
            try:
                response_content = (
                    json.loads(response_content_raw)
                    if response_content_raw
                    else None
                )
            except json.decoder.JSONDecodeError:
                response_content = None
            writer = OASResponseContentWriter(
                dest_root,
                path,
                HTTPMethod[info["request"]["method"]],
                info["response"]["status_code"],
                response_content,
            )
            writer.write()

            writer = OASResponsePatternWriter(
                dest_root,
                path,
                HTTPMethod[info["request"]["method"]],
            )
            writer.write()

            request_content_raw = info["request"]["content"]
            request_content = (
                json.loads(request_content_raw)
                if request_content_raw
                else None
            )
            writer = OASEndpointMethodWriter(
                dest_root,
                path,
                HTTPMethod[info["request"]["method"]],
                query=json.loads(info["request"]["query"]),
                request_content=request_content,
            )
            writer.write()
        writer = OASEndpointMethodPatternWriter(dest_root, path)
        writer.write()
    writer = OASEndpointPatternWriter(dest_root)
    writer.write()

    writer = OASIndexWriter(
        dest_root,
        openapi_version="3.0.0",
        version="0.0.1",
        title="test api",
        description="test description",
        server_urls=["https://example.com"],
    )
    writer.write()

    bundle_dest_path = pathlib.Path(OAS_BUNDLED_YAML)
    subprocess.run(
        [
            "./node_modules/.bin/swagger-cli",
            "bundle",
            str(writer.dest),
            "--outfile",
            str(bundle_dest_path),
            "--type",
            "yaml",
        ],
        check=True,
    )
    subprocess.run(
        [
            "./node_modules/.bin/spectral",
            "lint",
            str(bundle_dest_path),
        ],
        check=True,
    )
    subprocess.run(
        [
            "node_modules/.bin/redoc-cli",
            "bundle",
            str(bundle_dest_path),
            "--output",
            OAS_BUNDLED_HTML,
            "--options.onlyRequiredInSamples",
        ],
        check=True,
    )
    print(f"👉Check the output:{pathlib.Path(OAS_BUNDLED_HTML).resolve()}")
    print("✨Done")


if __name__ == "__main__":
    main()
