## How to use
Use https://flask.palletsprojects.com/en/1.1.x/quickstart/ to run app if you are not familiar with flask.
* navigate to CSE-312-Web_Apps
* run: sudo docker-compose up -d
* You will need docker and docker-compose installed
* It could take a little while to spin up the first time, dont panick if the website doesn't run immediately
* If you can get docker working but want to run the website you could just run wsgi.py but this will require you having an instance of mysql running with an appropriatly named db, and will require you to change the parameters in the database.py file

## Design Philosophy
Our website is designed for the modern consciensous user. Its designed to be:
* fast
* flexible
* most importantly functional
* Also designed to be as unaddictive as possible and contains no ads

We hope that users can share their stories and connect with friends without being consumed by internet addiction.

## Features
On this website they will be able to:
* share photos or stories
* allow their friends to view them and comment/vote
* DM their friends to catch up.
