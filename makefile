check:
	bash check.sh

install: requirements.txt install.sh
	bash install.sh

run:
	source activate.sh && \
		python3 run.py

db:
	source activate.sh && \
		python3 dbcreate.py

refresh: queue/*/models.py
	source activate.sh && \
		python3 dbrefresh.py
