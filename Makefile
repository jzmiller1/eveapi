all:
	@echo "EVE Online API"
	@echo ""
	@echo "Tests: "
	@echo "make test"
	@echo "make unittest"
	@echo "make apitest"

test: unittest apitest

unittest:
	python tests/unit.py

apitest:
	python tests/api.py
