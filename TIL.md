


#### General
 - If you know you're on bash, and still get this error, make sure you write the if with spaces.
	- `[[1==1]] # This outputs error`
	- `[[ 1==1 ]] # OK`


 - git commit -m "Title" -m "Description ..........";
 - To ignore if primary key already exists and keep inserting:
	```
	INSERT INTO mytable (id, col1, col2)
	VALUES (123, 'some_value', 'some_other_value')
	ON CONFLICT (id) DO NOTHING
	```
 - ```
	By default bash creates a copy of the current environment, executes the script in this environment, then destroys the copy.

	To execute a script in the current environment you should use this syntax:

	. /home/m/mydata/sourecCode
	echo $DEV_SRC
	or

	source /home/m/mydata/sourecCode
	echo $DEV_SRC
  ```


 - ```
 Each and every shell has its own environment. There's no Universal environment that will magically appear in all console windows. An environment variable created in one shell cannot be accessed in another shell.

It's even more restrictive. If one shell spawns a subshell, that subshell has access to the parent's environment variables, but if that subshell creates an environment variable, it's not accessible in the parent shell.

If all of your shells need access to the same set of variables, you can create a startup file that will set them for you. This is done in BASH via the $HOME/.bash_profile file (or through $HOME/.profile if $HOME/.bash_profile doesn't exist) or through $HOME/.bashrc. Other shells have their own set of startup files. One is used for logins, and one is used for shells spawned without logins (and, as with bash, a third for non-interactive shells). See the manpage to learn exactly what startup scripts are used and what order they're executed).

You can try using shared memory, but I believe that only works while processes are running, so even if you figured out a way to set a piece of shared memory, it would go away as soon as that command is finished. (I've rarely used shared memory except for named pipes). Otherwise, there's really no way to set an environment variable in one shell and have another shell automatically pick it up. You can try using named pipes or writing that environment variable to a file for other shells to pick it up.

Imagine the problems that could happen if someone could change the environment of one shell without my knowledge.
```

 - ```
	No, you will not have access to VAR when the script exits. Because a child process (the script) can not set the environment of the parent process (the shell/bash instance that runs the script).

	I set a number of environment variables and shell functions in my ~/.bashrc, so that they are available in the environment of every new shell I open. How is this achieved?

	You can execute the contents of a script in the current environment, by sourcing it, rather than running it as a new process. IIUC, bash executes the sourced script in a subroutine instead of a new process, keeping it in the same environment. It's essentially as if you typed it at the command line directly. You can source a script by preceding its path with a dot (.), or source:

	# Works in POSIX sh + bash
	. /path/to/env-var-script

	# Doesn't work with /bin/sh - bash only (maybe other shells?)
	source /path/to/env-var-script
	In man bash it states that ~/.bashrc is sourced when a new shell is started. Any lines in .bashrc, that source other scripts, will source those scripts in the current environment also. Personally, I have a single file each for env vars, functions, $PATH, aliases, etc. Splitting in to categories makes it easier to manage. You can also set up a directory where all files inside get sourced. That way if you have a new file, you need only move it there.

	You can put this line in .bashrc to do this:

	for i in /path/to/bash-env-dir/*; do
			. "$i"
	done
	If a script is made to be sourced, it does not need a shebang (#!/bin/bash).

	You can source any regular script, just by using the dot, or source. But scripts not designed to be sourced may sometimes have unexpected behaviour if they are sourced. Also, variables and functions in the script will persist in the current shell.

	Finally, export tells the shell to always export the given variable or function to the environment of all subsequent commands / child processes. export VAR=foo to set environment variables. export will not copy a variable from a script's environment to the parent shell. If the script is sourced though, you're directly changing the environment of the current shell.

	TLDR: You can't change the parent environment from a child process. Source the script with . /path/to/script to execute it in the current environment.
	```



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

### Terraform

### Ansible
