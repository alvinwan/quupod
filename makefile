check:
	bash check.sh

install: requirements.txt install.sh
	bash install.sh

run:
	source activate.sh && \
		python3 run.py

db:
	source activate.sh && \
		python migrate.py db init

migrate:
	source activate.sh && \
		python migrate.py db migrate && \
		python migrate.py db upgrade

tornado:
	source activate.sh && \
		python3 run.py --tornado
