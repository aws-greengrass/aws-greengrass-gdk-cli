lint:
	flake8 gdk tests uat --count --max-complexity=10 --max-line-length=127 --show-source --statistics

tests_unit:
	coverage run --source=gdk -m pytest -v -s tests && coverage xml --fail-under=99