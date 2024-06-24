


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


 -```
 Each and every shell has its own environment. There's no Universal environment that will magically appear in all console windows. An environment variable created in one shell cannot be accessed in another shell.

It's even more restrictive. If one shell spawns a subshell, that subshell has access to the parent's environment variables, but if that subshell creates an environment variable, it's not accessible in the parent shell.

If all of your shells need access to the same set of variables, you can create a startup file that will set them for you. This is done in BASH via the $HOME/.bash_profile file (or through $HOME/.profile if $HOME/.bash_profile doesn't exist) or through $HOME/.bashrc. Other shells have their own set of startup files. One is used for logins, and one is used for shells spawned without logins (and, as with bash, a third for non-interactive shells). See the manpage to learn exactly what startup scripts are used and what order they're executed).

You can try using shared memory, but I believe that only works while processes are running, so even if you figured out a way to set a piece of shared memory, it would go away as soon as that command is finished. (I've rarely used shared memory except for named pipes). Otherwise, there's really no way to set an environment variable in one shell and have another shell automatically pick it up. You can try using named pipes or writing that environment variable to a file for other shells to pick it up.

Imagine the problems that could happen if someone could change the environment of one shell without my knowledge.
```