---
layout: page
title: "Docker Basics"
permalink: /data-engineering/zoomcamp/docker-postgres-terraform
---

ToC
[Docker Basics](#docker-basics)
[Postgres with Docker](#postgres-with-docker)
[Terraform with Docker](#terraform-with-docker)
# Docker Basics

## Material
- [GitHub: DataTalksClub Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform/docker-sql)
- [Slides](https://docs.google.com/presentation/d/19pXcInDwBnlvKWCukP5sDoCAb69SPqgIoxJ_0Bikr00/edit?slide=id.p#slide=id.p)

## Notes

Docker provides an isolated environment from the system where it runs on.

Running `docker run hello-world` will confirm that Docker is installed.
When running the `docker run` command, if the image doesn't exist locally, it will be pulled remotely.

Adding the flag `-it` to the command `run` will run the container in interactive mode. eg:
`docker run -it ubuntu`

When running this OS, inside Docker, then, it will be isolated from my main OS.

Everytime we run a Docker container we create a container from an image, and our changes inside of it will be lost. It doesn't preserve its state.

Applying `-slim` to the tag (i.e the string after the `:`) will download a smaller version of the image:
`docker run -it python:3.13.11-slim`

To see `bash` instead of the REPL version of Python we can override the entry point by running:
`docker run -it --entrypoint=bash python:latest`


As said containers are stateless, so if I create a file, `echo leavemehere > fsociety.dat` it won't be maintained once I restart/re-run the container.

By running `docker ps -a` we can see all the Exited containers and we can recover the state, so containers are not entirely stateless. When I created the `.dat` file inside the container, it was saved somewhere, as a snapshot of the container itself.


By running `docker ps -aq` I can see the IDs of the exited containers, and by running:
```bash
docker rm `docker ps -aq`
```

`docker ps -a` should show nothing after.


### Volumes

Let's say we have three files on our machine:
```bash
mkdir example
cd example
touch file{1..3}.txt
echo "Hello, World" > file1.txt
```
and we want to list the files and their content using a previously created script `list_files.py`
```python
from pathlib import Path

current_dir = Path.cwd()
current_file = Path(__file__).name

print(f"Files in {current_dir}")
for filepath in current_dir.iterdir():
    if filepath.name == current_file:
        continue

    print(f" - {filepath.name}")

    if filepath.is_file():
        content = filepath.read_text(encoding="utf-8")
        print(f"   Content:\n{content}")
```

I can map the content of this folder to a Python container
```bash
docker run -it \
  --rm \
  -v "$(pwd)/example:/app/example" \
# -w /app/example \ Will take the user directly into the container's directory
  --entrypoint=bash \
  python:latest
```

`-v ${pwd}/example:/app/example`
On the right we have the path of the host machine and on the left the location inside the container


## Data Pipelines

A data pipeline is an automated system that collects raw data from various sources, transforms it (cleans, filters, aggregates) for consistency and usability, and then moves it to a destination like a data warehouse or lake for analysis, reporting, or machine learning

For this Workshop we will use the [NYC Taxis data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

The file `pipeline.py` will be our pipeline to ingest data and output it.

### Virtual Environment

If there are missing dependencies we could use Virtual Environments to avoid installing the missing dependencies on our host machine.
A virtual environment is an isolated Python environment that keeps dependencies for the project separate from other projects and the host system.

`uv` will manage the packages for us
`pip install uv`

To initialize a Python project:
`uv init --python=3.13`

To compare the Python versions, i.e the one in the virtual environment, and the one on the host:
```bash
uv run which python  # Python in the virtual environment
uv run python -V

which python        # Python on the host
python -V
```
After creating a project a `.toml` file will be created containing the project details

`uv add pandas` will add the dependency to the project
`uv run python pipeline.py 12` will run our project


---
### Dockerfile

To Dockerize the pipeline we will use the `Dockerfile`, a file containing all the instructions to create a Docker image.

```Dockerfile
FROM python:latest

RUN pip install pandas pyarrow

WORKDIR /code
COPY pipeline.py .
```

After finishing editing the Dockerfile we build the image by using
`docker build -t test:panda .`
and after the build is complete we run it using:
`docker run -it --entrypoint=bash --rm test:panda`

using the `--rm` flag will flush all the changes to the container and our host filesystem will less likely have leftovers files.

after running the container we are in the `/code` directory, as stated in the directive `WORKDIR /code`, in the Dockerfile


Now we are executing the Python file by manually running it.
We can change this behaviour by adding
`ENTRYPOINT ["python", "pipeline.py"]` to the Dockerfile.
So now when we run `docker run --rm test:pandas 12` we see the output from the Python file
```bash
> docker run --rm test:pandas 12
  arguments ['pipeline.py', '12']
  Running pipeline for month 12
    day  passengers  month
  0    1           3     12
  1    2           4     12
```

We are still not using `uv` in our Docker container, so we can update the image, we can use the following command in the Dockerfile
`COPY --from=docker.io/astral/uv:latest /uv /bin/`,
So we are copy another Docker image in our.
[DockerHub documentation](https://hub.docker.com/r/astral/uv)

The final Dockerfile will look like this
```Dockerfile
FROM python:latest
COPY --from=docker.io/astral/uv:latest /uv /bin/

WORKDIR /code
# We are copying the following host files into the WORKDIR
COPY pyproject.toml .python-version uv.lock ./

# It is going to copy the dependencies in the lock file
RUN uv sync --locked

COPY pipeline.py .

ENTRYPOINT ["uv","run","python", "pipeline.py"]
```

Starting the container will output the same data but now we are using `uv`
```bash
> docker run --rm test:pandas 12
    arguments ['pipeline.py', '12']
    Running pipeline for month 12
      day  passengers  month
    0    1           3     12
    1    2           4     12
```

### Alternative: Using PATH instead of `uv run`

Instead of using `ENTRYPOINT ["uv","run","python", "pipeline.py"]`, we can add this line to the Dockerfile:

```Dockerfile
ENV PATH="/code/.venv/bin:$PATH"
```

And then simplify the entrypoint to:

```Dockerfile
ENTRYPOINT ["python", "pipeline.py"]
```

**How this works:**

When `uv sync` runs, it creates a virtual environment at `/code/.venv/` with all the installed packages. Inside `.venv/bin/` there are executable scripts including `python`, `pip`, and any CLI tools from installed packages.

The `PATH` environment variable is a list of directories (separated by `:`) where the shell looks for executables. When you type `python`, the shell searches each directory in `PATH` from left to right until it finds a matching executable.

By prepending `/code/.venv/bin` to `PATH`:
- The shell will find `/code/.venv/bin/python` **before** the system Python (`/usr/local/bin/python`)
- This virtual environment Python already has all the dependencies installed by `uv sync`
- So running `python pipeline.py` automatically uses the correct Python with all packages available

**Why this is cleaner:**
- No need to prefix every command with `uv run`
- The container behaves like a normal Python environment
- Any script or command that calls `python` will use the virtual environment automatically

**Comparison:**

| Approach | ENTRYPOINT | How it works |
|----------|------------|--------------|
| `uv run` | `["uv","run","python", "pipeline.py"]` | `uv` activates the venv for each command |
| `PATH` | `["python", "pipeline.py"]` | Shell finds venv Python first via PATH |

Both approaches achieve the same result - running Python with the correct dependencies. The `PATH` approach is more idiomatic for Docker containers since it makes the environment "just work" without requiring a wrapper command.


# Postgres with Docker
We can run a containerized version of Postgres that doesn't require any installation steps. We only need to provide a few environment variables to it as well as a volume for storing data.


```bash
    $ mkdir ny_taxi_postgres_data
    $ docker run -it --rm \
      -e POSTGRES_USER="root" \
      -e POSTGRES_PASSWORD="root" \
      -e POSTGRES_DB="ny_taxi" \
      -v ny_taxi_postgres_data:/var/lib/postgresql \
      -p 9868:5432 \
      postgres:18
  ```
- The flags using `-e` are Environmental Variables used to configure the application.
So in this case we are creating a password and a user called `root`, and a database called `ny_taxi`.

- `v` refers to a volume, that is the storage location of the container's file. Hence we can preserve our data for the next time the container is run.

- Finally, the `p` flag refers to the ports mapped from the container to the host machine.

Once the container is running, we can log into our database with [pgcli](https://www.pgcli.com/).

```bash
uv add --dev pgcli
```

The `--dev` flag marks this as a development dependency (not needed in production). It will be added to the [dependency-groups] section of pyproject.toml instead of the main dependencies section.
In production we will use a different tool than `pgcli`.


After installing `pgcli` we can connect to the Postgres db using the following command:
`uv run pgcli -h localhost -p 9868 -u root -d ny_taxi`

- uv run executes a command in the context of the virtual environment
- -h is the host. Since we're running locally we can use localhost.
- -p is the port.
- -u is the username.
- -d is the database name.
- The password is not provided; it will be requested after running the command.
- 
### NY Taxi Dataset and Data Ingestion
We will now create a Jupyter Notebook `notebook.ipynb` file which we will use to read a CSV file and export it to Postgres.

To install Jupyter we use:
```bash
uv add --dev jupyter
```

and to create a Jupyter notebook the command is:
```bash
uv run jupyter notebook
```
This will open a browser window on `localhost:8888/tree`.

We are going to use the [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
Specifically, we will use the [Yellow taxi trip records CSV file for January 2021](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz).

The data dictionary of the set is available at:
[NYC TLC Trip Record Data Dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf)



**Data Types**
We encountered an error:
```python
/tmp/ipykernel_25483/2933316018.py:1: DtypeWarning: Columns (6) have mixed types. Specify dtype option on import or set low_memory=False.
```

An important difference between .csv and .parquet files is the absence of schemas in the former. Having a aschema make it easier for Pandas to infer the data types.

To help Pandas knowing the correct types we need to set the following schema:
```python
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

df = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    nrows=100,
    dtype=dtype,
    parse_dates=parse_dates
)
```
# Terraform with Docker