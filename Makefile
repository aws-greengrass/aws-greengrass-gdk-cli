lint:
	flake8 gdk tests integration_tests uat --count --max-complexity=10 --max-line-length=127 --show-source --statistics

tests_unit:
	coverage run --source=gdk -m pytest -v -s tests && coverage xml --fail-under=99

tests_integration:
	coverage run --source=gdk -m pytest -v -s integration_tests && coverage xml --fail-under=90

tests_uat:
	coverage run --source=gdk -m behave -v uat/ -D instrumented=true && coverage xml --fail-under=77