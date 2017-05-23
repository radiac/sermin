# Vagrant configuration for creating a VM for testing

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |vb|
     vb.memory = "4048"
   end

  config.vm.synced_folder ".", "/home/ubuntu/source"

  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    sudo apt-get --yes install python-minimal python-setuptools python-pip git
    pip install --upgrade pip
    pip install virtualenv
    if [ ! -d /home/ubuntu/venv ]; then
        virtualenv /home/ubuntu/venv
    fi
    source /home/ubuntu/venv/bin/activate
    pip install -e /home/ubuntu/source[dev]
    sudo git config --system user.email "test@example.com"
    sudo git config --system user.name "Test User"
  SHELL

end
