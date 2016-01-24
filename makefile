check:
	bash check.sh

install: requirements.txt install.sh
	bash install.sh

run:
	source activate.sh && \
		python3 run.py

db:
	source activate.sh && \
		python3 run.py -db create

refresh: queue/*/models.py
	source activate.sh && \
		python3 run.py -db refresh

default:
	source activate.sh && \
		python3 run.py -s default

restore:
	source activate.sh && \
		python3 run.py -s override

tornado:
	source activate.sh && \
		python3 run.py --tornado
