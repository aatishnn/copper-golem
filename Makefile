.PHONY: build run bot shell clean test

build:
	docker build -t copper-golem .

test: build
	docker run --rm \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		copper-golem python -c "import asyncio; from src.agent import chat; print(asyncio.run(chat('test', 'Remember I like pizza. Remind me to order dinner in 1 minute.')))"

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
