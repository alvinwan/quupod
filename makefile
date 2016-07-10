check:
	bash check.sh

install: requirements.txt install.sh
	bash install.sh

run:
	source activate quupod3.5 && \
		python3 run.py

db:
	source activate quupod3.5 && \
		python migrate.py db init

migrate:
	source activate quupod3.5 && \
		python migrate.py db migrate && \
		python migrate.py db upgrade

tornado:
	source activate quupod3.5 && \
		python3 run.py --tornado
