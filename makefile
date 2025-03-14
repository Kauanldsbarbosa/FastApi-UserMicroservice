.PHONY: test create-requirements makemigrations migrate

test:
	docker-compose run --rm --user 1000 apistartkit sh -c "pytest"

create-requirements:
	poetry export -f requirements.txt --without-hashes --output contrib/requirements.txt

makemigrations:
	docker-compose run --rm --user 1000 apistartkit sh -c "alembic revision --autogenerate -m 'migration'"

migrate:
	docker-compose run --rm --user 1000 apistartkit sh -c "alembic upgrade head"
