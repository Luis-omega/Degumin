
.PHONY: requirements run

sourceEnv=source .env/bin/activate

src="Degumin"

pythonFiles=$(find Degumin/ tests/ -name "*.py")

pythonSrc=$(find Degumin/ -name "*.py")

test:
	#@${sourceEnv};export PYTHONPATH=":";pytest
	@${sourceEnv};pytest

install: $(pythonSrc)
	@${sourceEnv};pip install -e .

uninstall:
	@${sourceenv};pip uninstall ${src}

run:
	@${sourceenv};megukin

gen-stub:
	@${sourceenv};stubgen ${src}

format:
	@${sourceenv};black ${src}/ tests/

requirements: 
	@${sourceenv};pip freeze > requirements.txt

watch:
	@${sourceenv};while sleep 0.5; do ls Degumin/**/*.py tests/*.py | entr -d make test; done

clean_cache:
	rm -rf build Degumin.egg-info .hypothesis .mypy_cache .pytest_cache .ropeproject
