# Creating the database on Heroku

There are two steps to creating the database on Heroku.

1. Create the database
2. Run a script to create the database tables

## Pre-Requisites

A number of pre-requisites need to be completed before the database can be created on Heroku.

1. Create a free Heroku account and an initial application
2. Install the Heroku CLI on your local development machine
3. Install a Command Line tool locally in order to access the Heroku database. One option is pgsql. On a Mac, this can be installed using Homebrew

## Create the Postgres database on Heroku

On the command line on your development machine, enter the below. Replace `<NAME OF APP>` with the name of the application already created on Heroku. The database will be associated with this application.

```shell
heroku addons:create heroku-postgresql:hobby-dev -a <NAME OF APP>
```

It takes a few minutes for the database to be created. If you run

```shell
heroku pg:wait
```

then this command will wait and complete when the database is ready.

Once it is ready, execute the below to see the database connection string. It will look something like `postgres://asdfggh:fggfg2g2g@xxx.yyy.amazonaws.com:5432/zzzz`
. You will need this full string later.

```shell
heroku config
```

Further details on creating a new database are on the [Heroku site](https://devcenter.heroku.com/articles/heroku-postgresql#provisioning-heroku-postgres)

## Add the database tables

Now you can add the database tables to this new database. This will be performed by connecting to the postgres database from your development machine and executing a SQL script.

Assuming you have a tool such as pgsql installed on your local machine, inside a shell or Terminal navigate to the folder containing the `diversitycorp.sql` file, and execute the following to connect to the database.

Replace `<DATABASE CONNECTION STRING>` with the connection details output by the `heroku config` command earlier.

```shell
psql <DATABASE CONNECTION STRING>
```

Now execute the SQL script that will create the tables and relationships. You will see the script's progress output to the terminal.

```shell
\i diversitycorp.sql
```

Finally, enter this command to see the new tables.

```shell
\dt
```
