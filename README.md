
# 4Geeks Playground APIs

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
  pipenv install
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

## Acknowledgements

Thanks to [readme.so](https://readme.so) for this template.


