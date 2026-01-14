## Material
https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform/docker-sql


- Slides
  https://docs.google.com/presentation/d/19pXcInDwBnlvKWCukP5sDoCAb69SPqgIoxJ_0Bikr00/edit?slide=id.p#slide=id.p

## Notes
Docker provides a isolated environment from the system where it runs on.

Running `docker run hello-world` will confirm that Docker is installed.
When running the `docker run` commadn, if the image doesn't exists locally, it will be pulled remotely

Adding the flag `-it` to the command `run` will run the container in interactive mode. eg:
`docker run -it ubuntu`

When running this OS, inside Docker, then, it will be isolated from my main OS.

Everytime we run a Docker container we create a container from an image, and our changes inside of it will be lost. It doesn't preserve its state.

Applyting `-slim` to the tag (i.e the string after the `:`) will download a smaller version of the image
`docker run -it python 3:13.11-slim`

To see `bash` instead of the REPL version of Python qe can override the entry point by running:
`docker run -it --entrypoint=bash python:latest`


as said containers are stateless, so if I create a file, `echo leavemehere > fsociety.dat` it won't be maintained once I restart/re-run the container

by running `docker ps -a` we can see all the Exited containers and we can recover the state, so containers are not entirely stateless. When I created the `.dat` file inside the container, it was saved somewhere, as a snapshot of the container itself.


By running `docker ps -aq` I can see the IDs of the exited containers, and by running 
```bash
docker rm `docker ps -aq`
```

`docker ps -a` should show nothing after


### Volumes
