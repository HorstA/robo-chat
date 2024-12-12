import psycopg
from utils import AppSettings
from datetime import datetime

settings = AppSettings.AppSettings()

conn_string = f"host={settings.PGVECTOR_HOST} port={settings.PGVECTOR_PORT} dbname={settings.PGVECTOR_DB} user={settings.PGVECTOR_USER} password={settings.PGVECTOR_PASSWORD}"


def pg_save_import(
    file_name: str, file_size: int, import_date: datetime, collection_name: str
) -> int:
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO imports (file_name, file_size, import_date, collection_name) VALUES (%s, %s, %s, %s) RETURNING id",
                (file_name, file_size, import_date, collection_name),
            )
            id = cur.fetchone()[0]
            conn.commit()
    return id


# def pg_is_imported(anlage_id: int) -> bool:
#     with psycopg.connect(conn_string) as conn:
#         with conn.cursor() as cur:
#             cur.execute(
#                 "SELECT EXISTS (SELECT 1 FROM imports WHERE anlage_id = %s)",
#                 (anlage_id,),
#             )
#             exists = cur.fetchone()[0]
#     return exists
