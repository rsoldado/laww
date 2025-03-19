# LAWW
Custom app that downloads, compares and uploads to a repository the most recent copy of a certain list (text document). Used to be deployed with Docker.

## Table of Contents
- [Preparation](#preparation)
- [Deployment](#deployment)

---

## Preparation

Follow these steps to set up the development environment for the project.

### 1. Set the environment variables
A file `.env` with the format specified in `.env.example` must be created with the parameters desired.

```
LIST_URL=<list_url>
GITHUB_USER=<github_user>
GITHUB_REPO=<github_repo>
GITHUB_FILE=<github_file>
GITHUB_TOKEN=<github_token>
```

### 2. Set Up a Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Deployment
To build and run the container, execute:

To deploy the project using Docker Compose, follow these steps:
```bash
docker-compose up --build -d
```

To stop the container, run:
```bash
docker-compose down
```

## Next steps
- Adaptative algorithm
- Set date on list
- Graphic statistics
- Implement Zeronet