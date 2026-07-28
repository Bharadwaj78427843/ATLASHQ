.PHONY: setup dev up down clean

setup:
	pnpm install
	cd services/api-gateway && python -m venv venv && venv/Scripts/pip install -r requirements.txt
	cd services/authentication-service && python -m venv venv && venv/Scripts/pip install -r requirements.txt

dev:
	pnpm dev

up:
	docker compose up -d

down:
	docker compose down

clean:
	rm -rf node_modules apps/*/node_modules packages/*/node_modules
	rm -rf services/*/venv
