PYTEST=docker-compose run --user 1000 apistartkit sh -c "pytest"
EXPORT_REQ=poetry export -f requirements.txt --output contrib/requirements.txt

.PHONY: test export

test:
	$(PYTEST)

create-requirements:
	$(EXPORT_REQ)
