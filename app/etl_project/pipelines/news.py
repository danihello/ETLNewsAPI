from dotenv import load_dotenv
import os
from etl_project.connectors.news_api import NewsApiClient
from etl_project.connectors.postgres import PostgreSqlClient
from sqlalchemy import Table, MetaData, Column, Integer, String, Float, PrimaryKeyConstraint
from etl_project.assets.news import (
    extract_news,
    transform,
    load,
)
from etl_project.assets.metadata_logging import MetaDataLogging, MetaDataLoggingStatus
from etl_project.assets.pipeline_logging import PipelineLogging
import yaml
from pathlib import Path



def pipeline(config: dict, pipeline_logging: PipelineLogging):
    """
    Runs the pipeline for extracting, transforming, and loading news data from the News API and CSV files into a PostgreSQL database.
    
    This function performs the following steps:
    1. Logs the start of the pipeline run.
    2. Retrieves the necessary environment variables for the News API and PostgreSQL connection.
    3. Creates a NewsApiClient instance using the API key.
    4. Extracts news data from the News API and CSV files.
    5. Transforms the extracted data.
    6. Connects to the PostgreSQL database and creates a table for the news data.
    7. Loads the transformed data into the PostgreSQL table using an upsert operation.
    8. Logs the successful completion of the pipeline run.
    
    The function takes the following parameters:
    - `config`: A dictionary containing the pipeline configuration, including the log folder path.
    - `pipeline_logging`: A PipelineLogging instance for logging the pipeline run.
    """
    pipeline_logging.logger.info("Starting pipeline run")
    # set up environment variables
    pipeline_logging.logger.info("Getting pipeline environment variables")
    API_KEY = os.environ.get("API_KEY")
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    PORT = os.environ.get("PORT")

    pipeline_logging.logger.info("Creating Weather API client")
    news_api_client = NewsApiClient(api_key=API_KEY)

    # extract
    pipeline_logging.logger.info("Extracting data from News API and CSV files")
    df_news = extract_news(
        news_api_client=news_api_client,
        category_reference_path=config.get("category_reference_path")
    )
    # transform
    pipeline_logging.logger.info("Transforming dataframes")
    df_transformed = transform(df_news=df_news)
    # load
    pipeline_logging.logger.info("Loading data to postgres")
    postgresql_client = PostgreSqlClient(
        server_name=SERVER_NAME,
        database_name=DATABASE_NAME,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        port=PORT,
    )
    metadata = MetaData()
    table = Table(
        "news_data",
        metadata,
        Column("author", String),
        Column("title", String),
        Column("description", String),
        Column("url", String),
        Column("url_image", String),
        Column("source_id", String),
        Column("source_name", String),
        Column("category", String),
        Column("published_day", String),
        Column("published_time", String),
        PrimaryKeyConstraint("url","title",name="news_data_pk"),
    )
    load(
        df=df_transformed,
        postgresql_client=postgresql_client,
        table=table,
        metadata=metadata,
        load_method="upsert",
    )
    pipeline_logging.logger.info("Pipeline run successful")

def run_pipeline(
    pipeline_name: str,
    postgresql_logging_client: PostgreSqlClient,
    pipeline_config: dict,
):
    """
    Runs the pipeline and logs the start, success, or failure of the pipeline run.
    
    This function sets up the pipeline logging and metadata logging, runs the pipeline,
    and logs the status of the pipeline run. If the pipeline run is successful, it logs
    the pipeline logs. If the pipeline run fails, it logs the error.
    """
    pipeline_logging = PipelineLogging(
        pipeline_name=pipeline_config.get("name"),
        log_folder_path=pipeline_config.get("config").get("log_folder_path"),
    )
    metadata_logger = MetaDataLogging(
        pipeline_name=pipeline_name,
        postgresql_client=postgresql_logging_client,
        config=pipeline_config.get("config"),
    )
    try:
        metadata_logger.log()  # log start
        pipeline(
            config=pipeline_config.get("config"), pipeline_logging=pipeline_logging
        )
        metadata_logger.log(
            status=MetaDataLoggingStatus.RUN_SUCCESS, logs=pipeline_logging.get_logs()
        )  # log end
        pipeline_logging.logger.handlers.clear()
    except BaseException as e:
        pipeline_logging.logger.error(f"Pipeline run failed. See detailed logs: {e}")
        metadata_logger.log(
            status=MetaDataLoggingStatus.RUN_FAILURE, logs=pipeline_logging.get_logs()
        )  # log error
        pipeline_logging.logger.handlers.clear()

if __name__ == "__main__":
    load_dotenv(override=True)
    LOGGING_SERVER_NAME = os.environ.get("LOGGING_SERVER_NAME")
    LOGGING_DATABASE_NAME = os.environ.get("LOGGING_DATABASE_NAME")
    LOGGING_USERNAME = os.environ.get("LOGGING_USERNAME")
    LOGGING_PASSWORD = os.environ.get("LOGGING_PASSWORD")
    LOGGING_PORT = os.environ.get("LOGGING_PORT")

    # get config variables
    yaml_file_path = __file__.replace(".py", ".yaml")
    if Path(yaml_file_path).exists():
        with open(yaml_file_path) as yaml_file:
            pipeline_config = yaml.safe_load(yaml_file)
            PIPELINE_NAME = pipeline_config.get("name")
    else:
        raise Exception(
            f"Missing {yaml_file_path} file! Please create the yaml file with at least a `name` key for the pipeline name."
        )

    postgresql_logging_client = PostgreSqlClient(
        server_name=LOGGING_SERVER_NAME,
        database_name=LOGGING_DATABASE_NAME,
        username=LOGGING_USERNAME,
        password=LOGGING_PASSWORD,
        port=LOGGING_PORT,
    )

    run_pipeline(
        pipeline_name=PIPELINE_NAME,
        postgresql_logging_client=postgresql_logging_client,
        pipeline_config=pipeline_config,
    )