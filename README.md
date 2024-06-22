## README
![example workflow](https://github.com/jetale/postings_parser/actions/workflows/main.yml/badge.svg)


- To access postgres terminal if postgres is running in wsl2. Here `dev` is the user and `postgres` is the database name - `psql -U dev -h 127.0.0.1 -d postgres`




## Questions -
- Best way to string compare, find in string. Is regex better? at what load should you switch from "s" in string to regex
- To declare a variable or not




## Notes -
- If you want to print directory structure use this command. This samples command ignores env and lib directory - `tree -I 'env|lib'`
- TO remove a file from remote after adding it to `.gitignore` -
	- `git rm --cached file`
	- `git add .`
	- `git commit -m "msg"`
	- `git push`


### Docker -
 - Dockerfile is used to run single container. docker-compose is used to run multiple containers
 - In Dockerfile, each step builds a layer on the base image so it is important to order them somewhat sensibely. There is new flag --squash I think which squashes all the layers into one. This reduces image size potentialy
 - Also, it is important to layer then sensibely because if there is a change in a layer e.g. change in pip install command or if you are copying project files into image then if there is a change in any file then all layers below that line are rebuilt
 - Process:
	- The process is as follows - build image from a base image -> run the docker container
	- After you are done building your project or if you want to start building with docker then you can use mounting directory
	- Step 1 - Create a `Dockerfile` in your projects root directory. It can be in another directory but having it in home directory makes things easier
	- Step 2 - To build docker image from Dockerfile use the command -
		- ` docker build -t postings_parser_image .`
	- Step 2 - To run the container use the following command. Here 5432:5432 specifies to map port 5432 of internal docker container to outside
		- ` docker run -p 5432:5432 postings_parser_image`

 - TIL:
	- In docker if you are connecting to services on the host machine (I was connecting to a postgres server on wsl2), then put this in the address field of that. Otherwise you will have problem connecting to the service
		- `'host.docker.internal'`
	- To pass environment variables while running container use this command format. There are other better ways to pass environment variables but I just wanted to test so used this
		- `docker run -p 5432:5432 -e PGHOST='${{secrets.PGHOST}}' -e PGDATABASE='${{secrets.PGDATABASE}}' postings_parser_image`
	- To delete stopped containers
		- `docker container prune`
	- To delete dangling images. Delete stopped container before this step as sometimes stopped containers are assosiated with some of the dangling images so they won't be deleted\
		- `docker image prune`
	- Add workdir or dir where your project is located to pythonpath in docker. This was causing problems for me
		- `ENV PYTHONPATH "${PYTHONPATH}:/app/"`

### Postgres

### Selenium

### Scrapy

### Github actions

### Data
 - Data hosted at - https://neon.tech/



### TODO -
 [] add linter
 [] add pre-commit hooks
 [] add static checker
