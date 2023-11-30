
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
	@${sourceEnv};pip uninstall ${src}

run:
	@${sourceEnv};Degumin

gen-stub:
	@${sourceEnv};stubgen ${src}

format:
	@${sourceEnv};black ${src}/ tests/

check-format:
	@${sourceEnv};black --check ${src}/ tests/

dev-requirements: 
	@${sourceEnv};pip freeze > dev-requirements.txt

watch:
	@${sourceEnv};while sleep 0.5; do ls Degumin/**/*.py tests/*.py | entr -d make test; done

clean_cache:
	rm -rf build Degumin.egg-info .hypothesis .mypy_cache .pytest_cache .ropeproject
