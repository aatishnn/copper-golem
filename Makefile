.PHONY: build run bot shell clean

build:
	docker build -t copper-golem .

run: build
	docker run -it --rm \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		copper-golem

bot: build
	docker run -it --rm \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		copper-golem python bot.py

shell: build
	docker run -it --rm \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		copper-golem /bin/bash

clean:
	docker rmi copper-golem 2>/dev/null || true
	rm -rf data/
