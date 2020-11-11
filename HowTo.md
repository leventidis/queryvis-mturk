# Useful HOW TO's during the mturk development process for QueryViz

## Setup config.py and .env
First get out of the virtual environment and install autoenv
```
deactivate
pip install autoenv
```
Then add the information of the .env file in the .bashrc file
```
echo "source `which activate.sh`" >> ~/.bashrc
source ~/.bashrc
```
Now cd'ing into the directory again the virtual environment will be 
automatically be stared with all the appropriate variables in the .env file

## Basic/useful Postgres psql commands
To connect in psql as user aristotle: `sudo -u aristotle psql postgres`\
To check information about current connection from psql: `\conninfo`\
Drop a database: `dropdb 'database name'`\
\
Give user create database rights
```
su postgres
psql
alter user aristotle createdb;
```
Check the database in heroku: `heroku pg:psql`\
Delete all data from a table: `Truncate Table;`

## Performing migration
To initialize the process: `python manage.py db init`\
\
To perform a migration locally
```
python manage.py db migrate
python manage.py db upgrade
```
\
To perform a migration on heroku on our server:
```
heroku run python manage.py db migrate --app afternoon-waters-70012
heroku run python manage.py db upgrade --app afternoon-waters-70012
```
Then login into heroku and drop the table `users` and run `db_create.py` to re-create it based on the updated schema.\
\
Copying a local database to heroku: `heroku pg:push postgresql:///queryvis heroku_database_name`

## Heroku useful commands
Login to heroku server
```
heroku login
heroku run bash
```
\
Get config variables: `heroku config --app afternoon-waters-70012`\
\
To add the postgres user to the sudo group: `sudo usermod -a -G sudo postgres`\
\
Run script on heroku: `heroku run python script.py`\
\
Dump database content in a CSV file: `\copy (SELECT * from users) TO dump.csv CSV DELIMITER ',' CSV HEADER`

## Useful online SQL/Text/Image formatters/converters
SQL to HTML: http://hilite.me/ \
SQL to HTML: https://htmlcodeeditor.com/ \
Removes non-ascii characters: https://pteo.paranoiaworks.mobi/diacriticsremover/ \
PDF to PNG: https://pdf2png.com/