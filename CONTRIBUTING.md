# CONTRIBUTING

## Initing virtual env
```
python -m venv .venv
```

## Docker compose build

```
docker compose up --build --force-recreate --no-deps web
```

## How to build docker image

```
docker build -t IMAGE_NAME  .
```

## How to run the Dockerfile locally

```
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" IMAGE_NAME sh -c "flask run --host 0.0.0.0"
```