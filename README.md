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
### Disconnect the vagrant
```shell
    exit
```
### Testing
You need enter the vagrant by ```vagrant ssh``` to do the next:
```shell
    cd /vagrant
    nosetests
```