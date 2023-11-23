PROJECT_NAME = $(shell pwd | rev | cut -f1 -d'/' - | rev)
NEW_VERSION = $(shell expr $(CURRENT_VERSION) + 1 )


clean:
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete

lint:
	poetry run pre-commit install && poetry run pre-commit run -a -v

pyformat:
	poetry run pre-commit run -a -v isort && poetry run pre-commit run -a -v black

install:
	poetry install

build-image:
	docker build -t config-transport-f5 .

tag-image:
	docker tag config-transport-f5:latest juniorwerner/config-transport-f5:v24