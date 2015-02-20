# CQF Final Project

This is currently hosted on heroku

http://fathomless-temple-4502.herokuapp.com/

Please that the performance critical parts have been re-written
using cython after profiling the code.These are the \*.pyx files
The respective python files are present as copy_\*.py files.

The core calculation logic has been moved into separate packages.

The app is presented as a flask webapp. Its deployed on heroku using
gunicorn + gevent.

Project Setup
-------------

```
# install pip
sudo easy_install pip

#install virtualenvwrapper
sudo pip install virtualenvwrapper

# create virtualenv
mkvirtualenv cqf

# switch virtualenv
workon cqf

# Clone repo
cd ~/Projects
git clone https://Gokulnath_Haribabu@bitbucket.org/Gokulnath_Haribabu/cqf.git

cd cqf

#Install dependencies

pip install -r dev_requirements.txt

```

```
# Run Flask server
./runserver.sh
```

Deployment
----------

```
# To push to heroku
git remote add heroku git@heroku.com:fathomless-temple-4502.git
git pull heroku master
git push heroku master:master
```

