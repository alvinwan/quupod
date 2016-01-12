check:
	bash check.sh

install:
	bash install.sh

run:
	source activate.sh && \
		python3 run.py

db:
	source activate.sh && \
		python3 dbcreate.py

refresh:
	source activate.sh && \
		python3 dbrefresh.py
