# Amazon Mechanical Turk (AMT) codebase for the QueryVis User Study 
Some code structure and workflow was adapted from https://github.com/akuznets0v/quickstart-mturk and https://github.com/akuznets0v/mturk-lean-external-question which provide a nice template for deploying a simple AMT test with Heroku and Flask.

# Remarks
Notice that some fields such as: `DATABASE_URL`, `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY` need to be specified accordingly when setting up the postgres database on heroku and using AWS keys with MTURK.

# Mturk Quick Setup
* Register on mturk.com and https://requester.mturk.com/developer/sandbox
* Deploy to heroku by commiting and pushing the repository with `git push heroku master`.
* Run `post_hits.py` to post the hits on Amazon Mechanical Turk
* Amazon Mechanical Turk will post your HIT, and IFrame your url in when a user accepts it.
* Once a user completes the hit it will be logged in the database. For more options check the hit_manager.py

# Useful Commands
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



