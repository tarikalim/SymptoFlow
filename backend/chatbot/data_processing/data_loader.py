from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Iterable
from uuid import uuid4 as uuid
from backend.chatbot.path_config import PathConfig


@dataclass
class Data:
    id: str
    source: str
    main_category: str
    data: dict

    @classmethod
    def from_path(cls, path: Path) -> Optional["Data"]:
        def _clean_text(text: str) -> str:
            text = text.replace('"', '"').replace('"', '"')
            text = text.replace("'", "'").replace("'", "'")
            text = text.replace("\u2018", "'").replace("\u2019", "'")
            text = text.replace("\u201c", '"').replace("\u201d", '"')
            text = text.replace("\u200b", "").replace("\ufeff", "")
            return " ".join(text.split())

        id = uuid().hex
        source = path.stem

        main_category = source.split("-")[0]

        try:
            with open(path, "r", encoding="utf-8") as f:
                text_content = f.read()
                text_content = _clean_text(text_content)

            data = {"content": text_content}

        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return None

        return cls(id=id, source=source, main_category=main_category, data=data)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "main_category": self.main_category,
            "data": self.data.get("content", "")
        }


class Loader:
    def __init__(self, path_config: PathConfig):
        self.path_config = path_config

    def _glob_files(self, document_type: str = "txt", all_files: bool = True):
        return self.path_config.content.glob(f"{('*' if all_files else '')}.{document_type}")

    def _load(self) -> Iterable[Data]:
        document_glob = self._glob_files()

        for index, document_path in enumerate(document_glob):
            document = Data.from_path(document_path)
            if document is not None:
                yield document

    def load_files(self) -> List[Data]:
        return list(self._load())

    def __iter__(self):
        return self._load()
