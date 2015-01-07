# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  
  config.vm.box = "ubuntu/trusty64"

  config.vm.network "forwarded_port", guest: 5432, host: 15432
  config.vm.network "forwarded_port", guest: 5000, host: 15000
  config.vm.network "forwarded_port", guest: 80, host:10080
  config.vm.network "forwarded_port", guest: 15672, host: 15673

  config.vm.synced_folder "~/Source/blockbuster-app", "/var/www/blockbuster-app"

  config.vm.provider "virtualbox" do |v|
    v.name = "BlockBuster Vagrant Image"
    v.customize ["modifyvm", :id, "--memory", "512"]
    v.customize ["modifyvm", :id, "--cpus", "1"]
  end

  config.vm.provision :shell, path: "provision/bootstrap.sh"
  config.vm.provision :shell, path: "provision/bootstrap-python.sh"
  config.vm.provision :shell, path: "provision/bootstrap-config.sh"
  config.vm.provision :shell, path: "provision/bootstrap-postgres.sh"

end
