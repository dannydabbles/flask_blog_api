# Flask Blog API

Simple blogging app and REST API

## Docker Quickstart

To test out the application, including DB setup, tests, and a production server, simply run:

```bash
./run.sh
```

This app can be run completely using `Docker` and `docker-compose`. **Using Docker is recommended, as it guarantees the application is run using compatible versions of Python and Node**.

There are three main services:

To run the development version of the app

```bash
docker-compose up flask-dev
```

To run the production version of the app

```bash
docker-compose up flask-prod
```

The list of `environment:` variables in the `docker-compose.yml` file takes precedence over any variables specified in `.env`.

To run any commands using the `Flask CLI`

```bash
docker-compose run --rm manage <<COMMAND>>
```

Therefore, to initialize a database you would run

```bash
touch dev.db # If it doesn't exist
docker-compose run --rm manage db init
docker-compose run --rm manage db migrate
docker-compose run --rm manage db upgrade
```

A docker volume `node-modules` is created to store NPM packages and is reused across the dev and prod versions of the application. For the purposes of DB testing with `sqlite`, the file `dev.db` is mounted to all containers. This volume mount should be removed from `docker-compose.yml` if a production DB server is used.

### Running locally

Run the following commands to bootstrap your environment if you are unable to run the application using Docker

```bash
cd flask_blog_api
pip install -r requirements/dev.txt
npm install
npm start  # run the webpack dev server and flask server using concurrently
```

You will see a pretty welcome screen.

#### Database Initialization (locally)

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration

```bash
flask db init
flask db migrate
flask db upgrade
```

## Deployment

When using Docker, reasonable production defaults are set in `docker-compose.yml`

```text
FLASK_ENV=production
FLASK_DEBUG=0
```

Therefore, starting the app in "production" mode is as simple as

```bash
docker-compose up flask-prod
```

If running without Docker

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export DATABASE_URL="<YOUR DATABASE URL>"
npm run build   # build assets with webpack
flask run       # start the flask server
```

## Shell

To open the interactive shell, run

```bash
docker-compose run --rm manage db shell
flask shell # If running locally without Docker
```

By default, you will have access to the flask `app`.

## Running Tests/Linter

To run all tests, run

```bash
docker-compose run --rm manage test
flask test # If running locally without Docker
```

To run the linter, run

```bash
docker-compose run --rm manage lint
flask lint # If running locally without Docker
```

The `lint` command will attempt to fix any linting/style errors in the code. If you only want to know if the code will pass CI and do not wish for the linter to make changes, add the `--check` argument.

## Migrations

Whenever a database migration needs to be made. Run the following commands

```bash
docker-compose run --rm manage db migrate
flask db migrate # If running locally without Docker
```

This will generate a new migration script. Then run

```bash
docker-compose run --rm manage db upgrade
flask db upgrade # If running locally without Docker
```

To apply the migration.

For a full migration command reference, run `docker-compose run --rm manage db --help`.

If you will deploy your application remotely (e.g on Heroku) you should add the `migrations` folder to version control.
You can do this after `flask db migrate` by running the following commands

```bash
git add migrations/*
git commit -m "Add migrations"
```

Make sure folder `migrations/versions` is not empty.

## Asset Management

Files placed inside the `assets` directory and its subdirectories
(excluding `js` and `css`) will be copied by webpack's
`file-loader` into the `static/build` directory. In production, the plugin
`Flask-Static-Digest` zips the webpack content and tags them with a MD5 hash.
As a result, you must use the `static_url_for` function when including static content,
as it resolves the correct file name, including the MD5 hash.
For example

```html
<link rel="shortcut icon" href="{{static_url_for('static', filename='build/img/favicon.ico') }}">
```

If all of your static files are managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in ``.env``:

```text
SEND_FILE_MAX_AGE_DEFAULT=31556926  # one year
```

## REST API

__*Note:*__ Before you may use the REST API, you must first sign up for a blog account at http://0.0.0.0:5000/register/ .

The REST API provides basic tools to manage users and blog posts.  The specific endpoints, and the actions they allow,
are listed as follows:

* /api/v0
   * /user                [GET, POST]
      * /{username}       [GET, PUT, DELETE]
         * /posts         [GET, POST]
            * /{post_id}  [GET, PUT, DELETE]

In addition to the built-in unit tests, below are included a set of curl commands for testing out the REST API:

```bash
#############################################################################
# Create a  <username> and <password> first at http://0.0.0.0:5000/register/
#
# Note: The below examples assume a username/password of testuser/testtest.
#       Please modify the calls as appropriate for your created user.
#############################################################################
# Check our current user
$ curl -u testuser:testtest -XGET "http://0.0.0.0:5000/api/v0/users/testuser"
{"username": "testuser", "email": "testuser@test.com", "first_name": "Test", "last_name": "User", "created_at": "2020-03-03 19:55:09.702396", "is_admin": false}

# Make a user
$ curl -u testuser:testtest -XPOST "http://0.0.0.0:5000/api/v0/users" -d "username=Test&email=test@test.com&password=secretpassword&first_name=Test&last_name=Testington&is_admin="
{"username": "Test", "email": "test@test.com", "first_name": "Test", "last_name": "Testington", "created_at": "2020-03-03 19:56:18.227055", "is_admin": false}

# Get a user
$ curl -u testuser:testtest -XGET "http://0.0.0.0:5000/api/v0/users/Test"
{"username": "Test", "email": "test@test.com", "first_name": "Test", "last_name": "Testington", "created_at": "2020-03-03 19:56:18.227055", "is_admin": false}

# Update a user
$ curl -u testuser:testtest -XPUT "http://0.0.0.0:5000/api/v0/users/Test" -d "first_name=Tester"
{"username": "Test", "email": "test@test.com", "first_name": "Tester", "last_name": "Testington", "created_at": "2020-03-03 19:56:18.227055", "is_admin": false}

# Delete a user
curl -u testuser:testtest -XDELETE "http://0.0.0.0:5000/api/v0/users/Test"
{}

# Make a post (visible at http://0.0.0.0:5000/users/ when signed in as <username>)
$ curl -XPOST -u testuser:testtest "http://0.0.0.0:5000/api/v0/users/testuser/posts" -d "title=mytitle&content=mycontent&active=True"
{"id": 1, "user": "Test User", "created_at": "2020-03-03 20:00:55.216256", "active": true, "title": "mytitle", "content": "mycontent"}

# Make a post (invisible at http://0.0.0.0:5000/users/ when signed in as <username>)
$ curl -XPOST -u testuser:testtest "http://0.0.0.0:5000/api/v0/users/testuser/posts" -d "title=mytitle&content=mycontent&active="
{"id": 2, "user": "Test User", "created_at": "2020-03-03 20:02:13.800586", "active": false, "title": "mytitle", "content": "mycontent"}

# Get all posts for user <username>
$ curl -XGET -u testuser:testtest "http://0.0.0.0:5000/api/v0/users/testuser/posts"{"posts": [{"id": 1, "user": "Test User", "created_at": "2020-03-03 20:00:55.216256", "active": true, "title": "mytitle", "content": "mycontent"}, {"id": 2, "user": "Test User", "created_at": "2020-03-03 20:02:13.800586", "active": false, "title": "mytitle", "content": "mycontent"}]}

# Get a particular post for user <username> by ID
$ curl -XGET -u testuser:testtest "http://0.0.0.0:5000/api/v0/users/testuser/posts/1" 
{"post": {"id": 1, "user": "Test User", "created_at": "2020-03-03 20:00:55.216256", "active": true, "title": "mytitle", "content": "mycontent"}}

# Update a particular post for user <username> by ID
$ curl -XPUT -u testuser:testtest "http://0.0.0.0:5000/api/v0/users/testuser/posts/1" -d "title=abettertitle"
{"id": 1, "user": "Test User", "created_at": "2020-03-03 20:00:55.216256", "active": true, "title": "abettertitle", "content": "mycontent"}

# Delete a post
$ curl -XDELETE -u testuser:testtest "http://0.0.0.0:5000/api/v0/users/testuser/posts/1"
{}
```
