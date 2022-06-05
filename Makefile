env:
	cp def.env .env

test:
	pytest tests

lint:
	isort -c tracking tests
	flake8 tracking tests
	pycln -c tracking tests
	black -c tracking tests

format:
	pycln -a tracking tests
	isort tracking tests
	black tracking tests
