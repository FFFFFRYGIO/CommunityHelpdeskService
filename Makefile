MANAGE=python manage.py

build:
	$(MANAGE) migrate
	$(MANAGE) loaddata fixtures/groups.json fixtures/users.json fixtures/articles.json fixtures/steps.json fixtures/reports.json
	$(MANAGE) collectstatic --noinput

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

test:
	$(MANAGE) test tests

install:
	pip install -r requirements.txt

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v
