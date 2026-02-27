"""dlt pipeline to ingest NYC Yellow Taxi trip data from a custom paginated API."""

import dlt
import requests

BASE_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"


@dlt.resource(name="rides", write_disposition="replace")
def taxi_rides():
    """Yield taxi trip records page by page; stops on empty response."""
    page = 1
    while True:
        response = requests.get(BASE_URL, params={"page": page}, timeout=30)
        response.raise_for_status()

        # API returns empty body (not JSON) when pages are exhausted
        if not response.content.strip():
            break

        data = response.json()
        if not data:
            break

        yield data
        page += 1


@dlt.source
def nyc_taxi_source():
    return taxi_rides()


pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    dataset_name="nyc_taxi_data",
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(nyc_taxi_source())
    print(load_info)  # noqa: T201
