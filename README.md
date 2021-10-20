# Promotions
NYU Devops2021 Promotions

## Download & Build
### Vagrant
```shell
    git clone git@github.com:NYU-Devops2021-Promotion/promotions.git
    cd promotions
    vagrant up
    vagrant ssh
```
### Exit and shut down the vm
```shell
    exit
    $ vagrant halt
```
### Testing
You need enter the vagrant by ```vagrant ssh``` to do the next:
```shell
    cd /vagrant
    nosetests
```
### What's featured in the project?

    * app/routes.py -- the main Service routes using Python Flask
    * app/models.py -- the data model using SQLAlchemy
    * tests/test_service.py -- test cases against the Promotion service
    * tests/test_model.py -- test cases against the Promotion model
