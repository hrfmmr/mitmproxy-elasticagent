"""
Configuration:

    cat > ~/.mitmproxy/config.yaml <<EOF
    # Dump target Elasticsearch url
    es_dest_url: "https://elastic.search.local/my-index/my-type"
    # Target host for dumping
    es_target_host: api.example.com

    EOF
"""
import asyncio
import gzip
import json
import traceback
from threading import Thread
from typing import Optional, Any, Dict, List, Union
from urllib.parse import urlparse

import aiohttp
import brotli
from mitmproxy import ctx

JSON = Any


class ElasticAgentAddon:
    fields = {
        "timestamp": (
            ("error", "timestamp"),
            ("request", "timestamp_start"),
            ("request", "timestamp_end"),
            ("response", "timestamp_start"),
            ("response", "timestamp_end"),
        ),
        "headers": (
            ("request", "headers"),
            ("response", "headers"),
        ),
        "content": (
            ("request", "content"),
            ("response", "content"),
        ),
    }

    def __init__(self):
        self.url: Optional[str] = None
        self.host: Optional[str] = None
        self.content_encoding: Optional[str] = None
        self.transformations: Optional[List[Dict[str, Any]]] = None
        self.worker_pool: Optional[ElasticAgentWorkerPool] = None

    def load(self, loader):
        loader.add_option(
            "es_dest_url", str, "", "Target Elasticsearch url for dumping"
        )
        loader.add_option("es_target_host", str, "", "Target host for dumping")

    def configure(self, _):
        self.url = ctx.options.es_dest_url
        self.host = ctx.options.es_target_host
        self._init_transformations()
        self.worker_pool = ElasticAgentWorkerPool(self.url)
        self.worker_pool.start()

    def response(self, flow):
        """
        Dump request/response pairs.
        """
        if flow.request.host != self.host:
            return
        path = urlparse(flow.request.path).path
        query = json.dumps({k: v for k, v in flow.request.query.fields})
        self.content_encoding = None
        for k, v in flow.response.headers.items():
            if k.lower() == "content-encoding":
                self.content_encoding = v
                break
        state = flow.get_state()
        del state["client_conn"]
        del state["server_conn"]
        state["request"]["query"] = query
        state["request"]["path"] = path
        for tfm in self.transformations:
            for field in tfm["fields"]:
                self.transform_field(state, field, tfm["func"])
        frame = self.convert_to_strings(state)
        self.worker_pool.put(frame)

    def _init_transformations(self):
        def map_content(
            content: Optional[bytes],
        ) -> Union[Optional[bytes], Any]:
            if self.content_encoding:
                try:
                    content = Decoding.decode(content, self.content_encoding)
                except gzip.BadGzipFile:
                    ctx.log.info(f"map_content::content was not gzip!!!????")
            return content

        self.transformations = [
            {
                "fields": self.fields["headers"],
                "func": dict,
            },
            {
                "fields": self.fields["timestamp"],
                "func": lambda t: int(t * 1000),
            },
            {"fields": self.fields["content"], "func": map_content},
        ]

    @staticmethod
    def transform_field(obj, path, func):
        """
        Apply a transformation function `func` to a value
        under the specified `path` in the `obj` dictionary.
        """
        for key in path[:-1]:
            if not (key in obj and obj[key]):
                return
            obj = obj[key]
        if path[-1] in obj and obj[path[-1]]:
            obj[path[-1]] = func(obj[path[-1]])

    @classmethod
    def convert_to_strings(cls, obj):
        """
        Recursively convert all list/dict elements of type `bytes`
        into strings.
        """
        if isinstance(obj, dict):
            return {
                cls.convert_to_strings(key): cls.convert_to_strings(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list) or isinstance(obj, tuple):
            return [cls.convert_to_strings(element) for element in obj]
        elif isinstance(obj, bytes):
            return obj.decode("utf-8")
        return obj


class Decoding:
    class __Methods:
        @staticmethod
        def identity(content: bytes) -> str:
            return str(content)

        @staticmethod
        def decode_gzip(content: bytes) -> str:
            if not content:
                return ""
            return str(gzip.decompress(content), "utf-8")

        @staticmethod
        def decode_brotli(content: bytes) -> str:
            if not content:
                return ""
            return str(brotli.decompress(content), "utf-8")

    decoding_maps = {
        "none": __Methods.identity,
        "gzip": __Methods.decode_gzip,
        "br": __Methods.decode_brotli,
    }

    @classmethod
    def decode(cls, encoded: bytes, encoding: str) -> Optional[str]:
        if encoding not in cls.decoding_maps:
            return None
        return cls.decoding_maps[encoding](encoded)


class ElasticAgentWorkerPool(Thread):
    def __init__(self, url: str, num_workers: int = 10):
        super().__init__(name="ElasticAgentWorkerPool", daemon=True)
        self.url = url
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.queue: Optional[asyncio.Queue[JSON]] = None
        self.num_workers = num_workers

    def run(self):
        loop = asyncio.new_event_loop()
        self.loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run_loop())
        except Exception as e:
            ctx.log.error(e)
            ctx.log.error(traceback.format_exc())
        else:
            if not loop.is_closed():
                loop.close()
            ctx.log.info("ElasticAgentWorkerPool's event loop closed")

    def put(self, frame: JSON):
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.queue.put_nowait, frame)

    async def _run_loop(self):
        self.queue = asyncio.Queue()
        await asyncio.gather(*(self.post_worker(i) for i in range(self.num_workers)))

    async def post_worker(self, id: int):
        while True:
            ctx.log.info(f"worker[{id}]:waiting...")
            frame = await self.queue.get()
            ctx.log.info(f"worker[{id}]:got task")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=frame) as resp:
                    ctx.log.info(f"worker[{id}]:Done")
                    ctx.log.info(await resp.text())


addons = [ElasticAgentAddon()]
