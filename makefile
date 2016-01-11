check:
	bash check.sh
	
install:
	bash install.sh

run:
	source activate.sh && \
		python3 run.py

db:
	python3 db.py
