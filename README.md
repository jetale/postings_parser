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
