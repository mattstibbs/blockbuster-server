init:
	pip install -r requirements.txt

v-run-all:
	vagrant ssh -c "/vagrant/provision/start_all.sh"

v-run-server:
	vagrant ssh -c "/vagrant/provision/start_server.sh"

v-run-workers:
	vagrant ssh -c "/vagrant/provision/start_workers.sh"

test:
	nosetests tests