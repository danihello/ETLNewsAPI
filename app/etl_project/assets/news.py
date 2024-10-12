import pandas as pd
from pathlib import Path
import sys
from sqlalchemy import Table, MetaData

sys.path.append('c:\\Users\\danielp\\newsapp')
#print(sys.path)
from etl_project.connectors.news_api import NewsApiClient
from etl_project.connectors.postgres import PostgreSqlClient


def extract_news(
    news_api_client: NewsApiClient, category_reference_path: Path
) -> pd.DataFrame:
    """
    Perform extraction using a filepath which contains a list of cities.
    """
    df_categories = pd.read_csv(category_reference_path)
    consolidated_df = pd.DataFrame()
    for category in df_categories["categories"]:
        category_headline = news_api_client.get_top_headlines(country='us',category=category)
        news_df = pd.json_normalize(category_headline)
        news_df["category"] = category
        consolidated_df = pd.concat([consolidated_df, news_df])
    return consolidated_df

def transform(df_news: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the extracted news data by:
    - Disabling chained assignment warnings
    - Converting the 'publishedAt' column to separate 'published_day' and 'published_time' columns
    - Dropping the original 'publishedAt' column
    - Renaming columns to more descriptive names
    - Resetting the index of the DataFrame
    """
    
    pd.options.mode.chained_assignment = None  # default='warn'
    df_news['published_day'] = pd.to_datetime(df_news['publishedAt']).dt.date
    df_news['published_time'] = pd.to_datetime(df_news['publishedAt']).dt.time
    df_news.drop(columns=["publishedAt", "content"], inplace=True)
    df_news = df_news[df_news['title'] != '[Removed]']
    df_news = df_news.rename(
        columns={"source.id": "source_id",
                 "source.name": "source_name",
                 "urlToImage":"url_image"}
    )
    df_news = df_news.reset_index(drop=True)
    return df_news

def load(
    df: pd.DataFrame,
    postgresql_client: PostgreSqlClient,
    table: Table,
    metadata: MetaData,
    load_method: str = "upsert",
) -> None:
    """
    Load dataframe to a database.

    Args:
        df: dataframe to load
        postgresql_client: postgresql client
        table: sqlalchemy table
        metadata: sqlalchemy metadata
        load_method: supports one of: [insert, upsert, overwrite]
    """
    if load_method == "insert":
        postgresql_client.insert(
            data=df.to_dict(orient="records"), table=table, metadata=metadata
        )
    elif load_method == "upsert":
        postgresql_client.upsert(
            data=df.to_dict(orient="records"), table=table, metadata=metadata
        )
    elif load_method == "overwrite":
        postgresql_client.overwrite(
            data=df.to_dict(orient="records"), table=table, metadata=metadata
        )
    else:
        raise Exception(
            "Please specify a correct load method: [insert, upsert, overwrite]"
        )
    
if __name__ == "__main__":


    client = NewsApiClient(api_key="58c2489477ef49a6bb9dca4e5c7932c6")
    #path = "./etl_project/data/countries/countries.csv"
    full_path = "C:\\Users\\danielp\\newsapp\\etl_project\\data\\categories\\categories.csv"
    df = extract_news(client,full_path)
    df = transform(df)
