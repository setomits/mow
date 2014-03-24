# Blogging system using Python 3.

## Requirements

"Mow" is a bloggging system using Python 3. Unfortunately, we *will not* support before Python 3.3.

As you see [requirements.txt](https://github.com/setomits/mow/blob/master/requirements.txt), "mow" uses popular Python libraries like [Flask](http://flask.pocoo.org/), [SQLAlchemy](http://www.sqlalchemy.org/), and so on.

Pages are shown faster if you use [memcached](http://memcached.org/).

## Clone Repository, Install Libraries and app
```
$ cd WORKING_DIRECTORY
$ git clone git@bitbucket.org:lilbit/mow.git
$ cd mow
$ pip install -r requirements.txt
$ ./init_db.py
$ ./register_user.py YOURNAME YOURPASSWORD
```

## Run Development Server
```
$ cd mow
$ ./runserver.py
```

## Testing
```
$ cd mow
$ ./testrunner.sh
```
