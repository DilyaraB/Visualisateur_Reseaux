all: setup visualisateur
setup: requirements.txt
	pip3 install -r requirements.txt
visualisateur: 
	python3 visualisateur.py