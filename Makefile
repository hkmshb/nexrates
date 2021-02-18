
POETRY := pipx run poetry
SHELL := /bin/zsh
VERSION := 0.1
IMAGE_NAME := hazeltek/nexrates:$(VERSION)

include .env

.PHONY: help
# source: https://victoria.dev/blog/django-project-best-practices-to-keep-your-developers-happy/
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: env-shell
env-shell: ## Spawn a new shell with project virtualenv activated
	$(POETRY) shell

.PHONY: test
test: ## Run tests
	$(POETRY) run pytest

.PHONY: run-dev
run-dev: ## Run the FastAPI server with `--reload` flag
	$(POETRY) run uvicorn nexrates:app --reload

.PHONY: docker-build
docker-build: ## Build docker image for the application
	docker build -t $(IMAGE_NAME) .

.PHONY: docker-run
docker-run: ## Run application from within docker
	docker run --rm --name nexrates -p 8000:80 --env-file .env $(IMAGE_NAME)
