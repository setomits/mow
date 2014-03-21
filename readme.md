#Blogging system using Python 3.

### Environment Setup

#### Install Virtualenv and Virtualenvwrapper
```
$ pip install virtualenv virtualenvwrapper
$ echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bash_profile
```

#### Install Python 3
```
$ brew install python3
```

#### Make virtualenv for mow
```
$ mkvirtualenv mow -p /usr/local/bin/python3
```

#### Clone Repository, Install Libraries and app
```
$ cd WORKING_DIRECTORY
$ git clone git@bitbucket.org:lilbit/mow.git
$ cd mow
$ pip install -r requirements.txt
$ ./init_db.py
$ ./register_user.py YOURNAME YOURPASSWORD
```

### Run Development Server
```
$ workon mow
$ cd WORKING_DIRECTORY
$ cd mow
$ ./runserver.py
```


## Testing

Run testrunner.sh
```
$ ./testrunner.sh
```
