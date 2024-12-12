import os
import pathlib
import re
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, File, UploadFile
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    AsyncHtmlLoader,
)
from loguru import logger
from utils.aiutils import get_splitter
from utils.AppSettings import AppSettings
from utils.fileutils import save_file
from utils.pgutils import pg_save_import
from utils.retriever import get_vectorstore
from uuid import uuid4

settings = AppSettings()

router = APIRouter(
    prefix="/file",
    tags=["file"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/import",
    name="import data",
    description="Upload a file and save data with embedding in the vector db",
)
def import_file(
    file_upload: UploadFile = File(...),
    filename: str = "",
    splitter_type: Literal["recursive", "semantic"] = "recursive",
    collection_name: str = settings.PGVECTOR_COLLECTION,
):
    logger.debug(f"Starting import_file, collection_name: {collection_name}")

    new_filename, save_to = save_file(file_upload, filename=filename)
    logger.debug(f"file {new_filename} saved")
    import_id = pg_save_import(
        file_name=new_filename,
        file_size=os.path.getsize(save_to),
        import_date=datetime.now(),
        collection_name=collection_name,
    )

    suffix = pathlib.Path(new_filename).suffix.lower()
    if suffix == ".pdf":
        loader = PyPDFLoader(save_to)
    elif suffix == ".docx":
        loader = Docx2txtLoader(save_to)
    else:
        loader = TextLoader(save_to, autodetect_encoding=True)

    pages = loader.load()

    for i, page in enumerate(pages):
        page.metadata["source"] = new_filename
        page.metadata["import_id"] = import_id
        if not suffix == ".pdf":
            page.metadata["page"] = i

    text_splitter = get_splitter(splitter_type)
    doc_splits = text_splitter.split_documents(pages)

    # beautify after splitting
    for doc in doc_splits:
        doc.page_content = re.sub(
            r"(\d)([a-zA-Z])", r"\1 \2", doc.page_content.replace("\n", "")
        )

    vectorstore = get_vectorstore(collection_name=collection_name)
    # uuids = [str(uuid4()) for _ in range(len(doc_splits))]
    ids = vectorstore.add_documents(doc_splits)
    return {"ids": ids}


@router.post(
    "/import-web",
    name="import web data",
    description="Scrape a website and save data with embedding in the vector db",
)
def import_web(
    url: str = "",
    splitter_type: Literal["recursive", "semantic"] = "recursive",
    collection_name: str = settings.PGVECTOR_COLLECTION,
):
    logger.debug(f"Starting import_web...")

    loader = AsyncHtmlLoader(url)
    pages = loader.load()

    for i, page in enumerate(pages):
        page.metadata["source"] = url
        page.metadata["import_id"] = 0

    text_splitter = get_splitter(splitter_type)
    doc_splits = text_splitter.split_documents(pages)

    vectorstore = get_vectorstore(collection_name=collection_name)
    # uuids = [str(uuid4()) for _ in range(len(doc_splits))]
    ids = vectorstore.add_documents(doc_splits)
    return {"ids": ids}
