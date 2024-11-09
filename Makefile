run:
	poetry run uvicorn --reload --reload-include '*.py' --reload-include '*.toml' --reload-include  '*.lock' main:app
