# 4Geeks Playground APIs

[![Tests](https://github.com/dotfortun/4geeks-apis-light/actions/workflows/python-app.yml/badge.svg)](https://github.com/dotfortun/4geeks-apis-light/actions/workflows/python-app.yml)

Resources for Teachers and Students using the [BreatheCode Platform](https://breatheco.de).

Built with [FastAPI](https://github.com/tiangolo/fastapi).

## Run Locally

Clone the project

```bash
  git clone https://github.com/dotfortun/4geeks-apis-light
```

Go to the project directory

```bash
  cd 4geeks-apis-light
```

Install dependencies

```bash
  pipenv install --dev
```

Copy `.env.example` to `.env`

```bash
  cp .env.example .env
```

Start the server

```bash
  pipenv run dev
```

## Creating a new api

To make a new api for the playground, run `pipenv run utils create <module name>`, and a boilerplate API module will be bootstrapped into the `api` folder.


## Reset your database

```bash
  pipenv run utils drop
```

## Testing

```bash
  pipenv run test
```

## Env Vars

`DB_URL`: Database connection string, defaults to `sqlite:///./playground.sqlite`

## Acknowledgements

Thanks to [readme.so](https://readme.so) for this template.


