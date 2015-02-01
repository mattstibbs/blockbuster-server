# Using Vagrant With BlockBuster

## Pre-requisites
1. Ensure you have vagrant installed on your machine
2. Ensure you have Virtualbox installed on your machine
2. Clone the blockbuster-sms repository to your machine
3. Internet connectivity



## Getting Set Up
The blockbuster-sms is now set up to allow you to use Vagrant to support your development workflow. Spin up a vagrant environment following these steps:

Using a terminal:

1. Navigate to your local blockbuster-sms repo
2.  `vagrant up`
3.  Watch it do stuff (it'll will take several minutes to get everything provisioned)

Once finished, you will have:

A virtual machine running Ubuntu 14.04 LTS, containing:

* All necessary components for running a BlockBuster server (Python, Celery, etc.)
* Postgresql database server
* RabbitMQ message broker
* Nginx (not currently used, but will act as a reverse proxy for BlockBuster in the future)
* Gunicorn (WSGI compatible Python host, will be used with Nginx in the future)
* Git

You will also have a blockbuster database provisioned and ready to use.
(It doesn't currently come seeded with test data, but I will sort that out at some point)


## Running up a server
If you just want to get a BlockBuster server up and running, you can run the following command:

`make v-run-all`

or if you don't have Make installed:

`vagrant ssh -c /vagrant/provision/start_all.sh`

This should load a Tmux console with two panes:

1. The main blockbuster server
2. A Celery async background worker (to handle outbound messaging)


### Testing it's up
You can very quickly test that the server is running properly by going to a browswer on your local machine and navigating to:

[`http://127.0.0.1:15000/status`](http://127.0.0.1:15000/status)

You should get a response similar to "1.20.00 OK"

You can also try [`http://127.0.0.1:15000/stats`](http://127.0.0.1:15000/stats) for the daily statistics endpoint.

If you get this, it means that the stack is working as it should. The number is the database schema version and is retrieved directly from the database (thus proving that connectivity is there all the way through to the DB)

You can easily close the server processes down by using `Ctrl + C` with them in focus. The tmux windows should close as the processes end.


### Adding more background workers
If you want to add some more background workers to see them coordinating workload, you can run:

`make v-run-workers` or `vagrant ssh -c /vagrant/provision/start_workers.sh`

Note: You will need to open yourself a second terminal window to run the extra workers in as the existing tmux session
will still be running.


## Accessing source from the virtual machine
Vagrant by default shares your project directory (i.e. directory from which you are running the vagrant instance) inside the VM at path **/vagrant/**

As you make changes to the project on your local machine, they will be immediately available inside the virtual machine as well. This is useful as it means you can leave the server process running and Flask's change detection will automatically restart the service when you make changes.


## Configuration Files
Configuration is all contained within **config*.py** files in the main source directory (./blockbuster). It ships with a default configuration which:

* Gets the app talking to the DB on localhost
* Gets the app talking to the MQ on localhost
* Provides SMS and Email simulations in the background workers' outputs (rather than having to link it up to real services)

When you first provision your vagrant image, the bootstrap script will check to see if you have config files in your blockbuster directory, and if not will copy the example files into it.


## Networking
The default setup is for two ports to be mapped from the virtual machine back onto the host machine:

* 5432 on the virutal machine is mapped to 15432 on your local machine (Postgresql)
* 5000 virtual --> local 15000 (http)
* 443 virtual --> local 1443 (https)
* 15672 virtual --> local 15673 ([RabbitMQ WebUI](http://localhost:15673))


## Using Postgresql
I recommend using [Pgadmin3](http://www.pgadmin.org/index.php) as a graphical DB tool.

You can just configure a postgres connection to localhost on port 15432
