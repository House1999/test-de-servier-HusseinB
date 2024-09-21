Table of contents :
- [Commands](#commands)
- [Améliorations](#améliorations)
- [Ad-hoc](#ad-hoc)
- [SQL](#sql)

# Commands

This repository is hosting the codebase of Servier's Data Engineering technical test

```
cd app
export $(cat .env | xargs)
poetry run python main.py
```

or

```
poetry shell
cd app
export $(cat .env | xargs)
python main.py
```

or

```
docker build -t test-servier-app:latest -f Dockerfile .
docker run -i -t test-servier-app:latest


cd app
export $(cat .env | xargs)
python main.py
```

# Améliorations

# Ad-hoc

# SQL
