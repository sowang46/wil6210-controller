all:
	@echo "\nbuild_time = '$(shell date)'" >> src/version.py
	@sleep 0.4 && python complier.py && head -1 src/version.py > /tmp/version.py && mv /tmp/version.py ./src
