"""dlt pipeline to ingest data from the Open Library REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def open_library_source():
    """Define dlt resources from Open Library API endpoints."""
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://openlibrary.org/",
        },
        "resource_defaults": {
            "write_disposition": "replace",
        },
        "resources": [
            {
                "name": "books",
                "endpoint": {
                    "path": "search.json",
                    "params": {
                        "q": "python programming",
                        "limit": 100,
                        "page": 1,
                    },
                    "data_selector": "docs",
                },
            },
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="open_library_pipeline",
    destination="duckdb",
    dataset_name="open_library_data",
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(open_library_source())
    print(load_info)  # noqa: T201
