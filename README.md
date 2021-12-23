# mitmproxy-elasticagent
A [mitmproxy](https://mitmproxy.org/)'s addon for dumping json response to Elasticsearch

## Usage

### Prerequisites

```bash
# install additional dependencies
$ $(brew --prefix mitmproxy)/libexec/bin/pip install aiohttp

# or if you installed mitmproxy with pipx
$ pipx inject mitmproxy aiohttp
```

### Add script

* `~/.mitmproxy/config.yml`
    ```yaml
    scripts:
      - /path/to/mitmproxy-elasticagent/jsondump.py
    # Dump target Elasticsearch url
    es_dest_url: "https://elastic.search.local/my-index/my-type"
    # Target host for dumping
    es_target_host: api.example.com
    ```

### Run mitmproxy

```bash
# ensure Elasticsearch is running
# start mitmproxy
$ mitmdump

# run json API request with proxy(another session)
$ curl --proxy http://localhost:8080 https://jsonplaceholder.typicode.com/posts/1
```
