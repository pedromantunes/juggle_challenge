######################################################################
# API makefile

# Project name.
PROJECT := api

# Python path.
PYTHONPATH := ../

# App configs.

######################################################################
# Dev targets

.PHONY: runserver smoke test

smoke:
	python -m $(PROJECT).smoke

docker-smoke:
	./scripts/run-docker-smoke $(PROJECT)