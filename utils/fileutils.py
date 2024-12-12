import shutil
import time
from typing import List, Tuple
import urllib.request
import os

from fastapi import UploadFile
from langchain_core.documents import Document
from loguru import logger
from pathvalidate import is_valid_filename


def save_file(file_upload: UploadFile, filename: str) -> Tuple[str, str]:
    if not filename and file_upload.filename == "file_upload":
        logger.warning(
            "Konnte Dateityp nicht ermitteln. Verwende Default 'pdf'. Bitte verwenden Sie den Parameter 'filename'"
        )

    if filename:
        new_filename = filename
    else:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        if file_upload.filename == "file_upload":
            new_filename = f"{timestr}_uploaddata.pdf"
        else:
            new_filename = file_upload.filename

    save_to = f"./data/upload/{new_filename}"
    with open(save_to, "wb") as buffer:
        shutil.copyfileobj(file_upload.file, buffer)

    return new_filename, save_to


def save_file_url(href: str, filename: str = None) -> Tuple[str, str]:

    if filename:
        new_filename = filename
    else:
        new_filename = os.path.basename(href)

        if not is_valid_filename(new_filename):
            timestr = time.strftime("%Y%m%d-%H%M%S")
            new_filename = f"{timestr}_uploaddata.undef"

    save_to = f"./data/upload/{new_filename}"

    urllib.request.urlretrieve(href, save_to)
    return new_filename, save_to


def is_scanned(docs: List[Document]) -> bool:
    """Checks whether the document has been scanned. Intended for PDFLoader.
       Put in the loader.load() result. If the max text length is less than 20 chars, the document has been scanned.
       sample:
        loader = PyPDFLoader(filename)
        docs = loader.load()
        is_scanned(docs)
    Args:
        docs (List[Document]): the loader.load docs

    Returns:
        bool: doc is scanned
    """
    max_text_len = max([len(doc.page_content) for doc in docs])
    return max_text_len < 20
