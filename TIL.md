


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
