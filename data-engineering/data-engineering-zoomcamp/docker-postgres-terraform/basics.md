---
layout: page
title: "Docker Basics"
permalink: /data-engineering/zoomcamp/docker-postgres-terraform
---

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
