# AUA Smart Course Planner

# Application setup

```bash
# Clone the repository
git clone git@github.com:iamdianaaa/AUA-Course-Planner.git
```

This project uses Docker and Docker Compose to run the Flask backend and Redis in separate containers.

### Prerequisites
- Python 3.11+
- [Docker and Docker Compose](https://www.docker.com/)


## Running the application with docker

```bash
docker-compose up --build
```

This will 
- Build the Flask app image from the Dockerfile
- Start Redis as a background service
- Run Backend on http://localhost:5000

## Stop the application just run:

```bash
docker-compose down
```