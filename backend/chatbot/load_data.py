import json
import os
from langchain_core.documents import Document
from backend.chatbot.path_config import PathConfig
from backend.chatbot.data_processing.data_loader import Loader
from backend.chatbot.data_processing.data_mapper import Mapper, Builder


def prepare_documents(path_config: PathConfig) -> list:
    loader = Loader(path_config)
    mapper = Mapper(path_config)
    builder = Builder()

    print("Loading files...")
    data = loader.load_files()
    print(f"Loaded {len(data)} files.")

    print("Mapping data...")
    mappings = mapper.map_data(data)
    print("Mapped data successfully.")

    print("Building documents...")
    documents = builder.build_document(mappings)
    print(f"Built {len(documents)} documents.")

    documents_path = path_config.data / "documents.json"
    with open(documents_path, "w", encoding="utf-8") as f:
        json.dump([doc.model_dump() for doc in documents], f, indent=4)

    return documents


def load_documents() -> list:
    path_config = PathConfig()
    documents_path = path_config.data / "documents.json"

    if not os.path.exists(documents_path):
        print("Documents file not found. Preparing new documents...")
        return prepare_documents(path_config)

    print("Loading documents from file...")
    with open(documents_path, "r", encoding="utf-8") as f:
        documents_data = json.load(f)

    documents = [Document(**doc) for doc in documents_data]
    print(f"Loaded {len(documents)} documents.")
    return documents