# ETL News API Project

This project is an ETL (Extract, Transform, Load) pipeline that retrieves news data via an API, processes it, and loads the transformed data into a PostgreSQL database. This README contains all necessary information to understand the project structure, set it up locally, run it using Docker, and deploy it in a cloud environment.

## Project Tree

The project's folder structure is organized as follows:

```text
ETLNewsAPI/
├── .env                  # Environment variables file 
├── .gitignore            # Git ignore file
├── Dockerfile            # Docker setup to containerize the project
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
└── app/
    └── etl_project/
        ├── assets/
        │   ├── metadata_logging.py
        │   ├── news.py
        │   ├── pipeline_logging.py
        │   ├── utils.py
        │   └── __init__.py
        ├── connectors/
        │   ├── news_api.py
        │   ├── postgres.py
        │   └── __init__.py
        ├── data/
        │   └── categories/
        │       └── categories.csv
        ├── logs/
        │   └── .gitkeep
        └── pipelines/
            ├── news.py
            └── news.yaml
```

## Prerequisites

To run this project, you will need the following installed:

- Python 3.8+
- Docker
- PostgreSQL database instance
- `pip` for installing dependencies
- API Key obtained [here](https://newsapi.org)

### Environment Variables

The project relies on several environment variables defined in the `.env` file:

- `API_KEY`: API key to access the news API.
- `SERVER_NAME`: Hostname for the main database server.
- `DATABASE_NAME`: Name of the main PostgreSQL database.
- `DB_USERNAME`: Username for connecting to the main PostgreSQL database.
- `DB_PASSWORD`: Password for connecting to the main PostgreSQL database.
- `PORT`: Port for the main PostgreSQL database connection.
- `LOGGING_SERVER_NAME`: Hostname for the logging database server.
- `LOGGING_DATABASE_NAME`: Name of the logging PostgreSQL database.
- `LOGGING_USERNAME`: Username for connecting to the logging PostgreSQL database.
- `LOGGING_PASSWORD`: Password for connecting to the logging PostgreSQL database.
- `LOGGING_PORT`: Port for the logging PostgreSQL database connection.

## Installation and Setup

### Running Locally

1. **Clone the Repository**

   ```sh
   git clone <repository_url>
   cd ETLNewsAPI
   ```

2. **Install Dependencies**   Make sure you have Python 3.8+ installed. Then, install the required dependencies using:

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**   Create an `.env` file in the root directory of the project, and set the necessary environment variables mentioned above.

4. **Run the ETL Pipeline**   Run the ETL pipeline script:

   ```sh
   python -m etl_project.pipelines.news
   ```

### Running Locally with Docker

1. **Build Docker Image**   Use the provided Dockerfile to create a Docker image:

   ```sh
   docker build -t etlnewsapi:latest .
   ```

2. **Run Docker Container**   Run the Docker container:

   ```sh
   docker run -it --rm --env-file .env etlnewsapi:latest
   ```

### Running in the Cloud (AWS/Google Cloud)

To deploy and run the Docker image in a cloud environment, follow these general steps for AWS or Google Cloud.

#### AWS (using ECS)

1. **Push Docker Image to AWS ECR**

   - Tag the image and push it to AWS Elastic Container Registry (ECR).

2. **Deploy on ECS**

   - Use AWS ECS to create a service and task definition to deploy the Docker container.
   - Set environment variables in ECS using the `.env` file values.

3. **Run the Service**

   - Run the ECS service to start the ETL process.

#### Google Cloud (using Google Kubernetes Engine)

1. **Push Docker Image to Google Container Registry (GCR)**

   - Tag the Docker image and push it to GCR.

2. **Create Kubernetes Deployment**

   - Use Google Kubernetes Engine (GKE) to create a deployment for the Docker container.
   - Set up a Kubernetes Secret or ConfigMap to provide environment variables.

3. **Run the Deployment**

   - Deploy and run the ETL job on GKE.

## Contributing

Feel free to open an issue or create a pull request if you have suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
