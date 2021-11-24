# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  # config.vm.box = "ubuntu/focal64"
  config.vm.box = "bento/ubuntu-21.04"
  config.vm.hostname = "ubuntu"

  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.56.10"

  # Mac users can comment this next line out but
  # Windows users need to change the permission of files and directories
  # so that nosetests runs without extra arguments.
  config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=755,fmode=644"]

  ############################################################
  # Provider for VirtuaBox on Intel
  ############################################################
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
    vb.cpus = 2
    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

 ############################################################
  # Provider for Docker
  ############################################################
  config.vm.provider :docker do |docker, override|
    override.vm.box = nil
    # Chromium driver does not work with ubuntu so we use debian

    docker.image = "rofrano/vagrant-provider:debian"
    docker.remains_running = true
    docker.has_ssh = true
    docker.privileged = true
    docker.volumes = ["/sys/fs/cgroup:/sys/fs/cgroup:ro"]
    # Uncomment to force arm64 for testing images on Intel
    # docker.create_args = ["--platform=linux/arm64"] 
  end


  ######################################################################
  # Copy files to personalize the environment
  ######################################################################

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy the ssh keys into the vm for git access
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  # Copy your .vimrc file so that your vi looks like you expect
  if File.exists?(File.expand_path("~/.vimrc"))
    config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
  end

  # Copy your IBM Cloud API Key if you have one
  if File.exists?(File.expand_path("~/.bluemix/apikey.json"))
    config.vm.provision "file", source: "~/.bluemix/apikey.json", destination: "~/.bluemix/apikey.json"
  end

  ######################################################################
  # Create a Python 3 development environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "****************************************"
    echo " INSTALLING PYTHON 3 ENVIRONMENT..."
    echo "****************************************"
    # Install Python 3 and dev tools 
    apt-get update
    apt-get install -y git vim tree python3 python3-pip python3-venv python3-selenium
    apt-get -y autoremove
    
    # Need PostgreSQL development library to compile on arm64
    apt-get install -y libpq-dev

    # Install Chromium Driver
    apt-get install chromium-browser
    apt-get install chromium-driver
    chromedriver --version

    # Create a Python3 Virtual Environment and Activate it in .profile
    sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'
    sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'
    
    # Install app dependencies in virtual environment as vagrant user
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && pip install -U pip && pip install wheel'
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && cd /vagrant && pip install -r requirements.txt'
  SHELL

  ######################################################################
  # Add PostgreSQL docker container for database
  ######################################################################
  # docker run -d --name postgres -p 5432:5432 -v psqldata:/var/lib/postgresql/data postgres
  config.vm.provision :docker do |d|
    d.pull_images "postgres:alpine"
    d.run "postgres:alpine",
       args: "-d --name postgres -p 5432:5432 -v psqldata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres"
  end

  ######################################################################
  # Setup a Bluemix and Kubernetes environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "\n************************************"
    echo " Installing IBM Cloud CLI..."
    echo "************************************\n"
    # WARNING!!! This only works on Intel computers
    # Install IBM Cloud CLI as Vagrant user
    ARCH=$(dpkg --print-architecture)
    if [ "$ARCH" == "amd64" ]
    then
      curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
      sudo -H -u vagrant bash -c '
          echo "alias ic=/usr/local/bin/ibmcloud" >> ~/.bash_aliases &&
          ibmcloud cf install'
    else
      echo "*** WARNING: IBM Cloud CLI does not suport your architecture :("; \
    fi

    echo "\n************************************"
    echo ""
    echo "If you have an IBM Cloud API key in ~/.bluemix/apikey.json"
    echo "You can login with the following command:"
    echo ""
    echo "ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apikey.json -r us-south"
    echo "\nibmcloud target --cf"
    echo "\n************************************"
  SHELL

end