from typing import List, Dict, Any, Tuple
from backend.chatbot.data_processing.data_loader import Data
from backend.chatbot.path_config import PathConfig
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
import json


class Builder:
    def build_document(self, mappings) -> List[Document]:
        documents: List[Document] = []

        for mapping in mappings:
            documents.extend(self._convert(mapping))

        return documents

    def _convert(self, mapping) -> List[Document]:
        documents = []

        for sequence, qa_pair in enumerate(mapping["data"], 1):
            page_content = self._get_page_content(qa_pair)
            metadata = self._get_metadata(mapping, sequence=sequence)

            documents.append(Document(page_content=page_content, metadata=metadata))

        return documents

    def _get_page_content(self, qa_pair: Dict[str, str]) -> str:
        return f"Question: {qa_pair['question']}\nAnswer: {qa_pair['answer']}"

    def _get_metadata(self, mapping: Dict[str, Any], **additional_fields: Any) -> Dict[str, Any]:
        metadata = {
            "sequence": additional_fields["sequence"],
            "id": mapping["id"],
            "source": mapping["source"],
            "main_category": mapping["main_category"],
        }
        return metadata


class Mapper:
    def __init__(
            self,
            path_config: PathConfig,
            model_name="gpt-4o-mini",
            temperature=0,
    ):
        self.path_config = path_config
        self._model_name = model_name
        self._temperature = temperature

        self.llm = ChatOpenAI(model_name=self._model_name, temperature=self._temperature)

        self.output_parser = None
        self.prompt = None
        self.chain = None

        self._build_response_schema()
        self._build_prompt()
        self._create_chain()

    def _build_response_schema(self):
        response_schemas = [
            ResponseSchema(name="id", description="The unique ID of the document."),
            ResponseSchema(name="source", description="The source of the document."),
            ResponseSchema(name="main_category", description="The main category extracted from the document."),
            ResponseSchema(
                name="data",
                description="A list containing JSON objects with created question-answer pairs, such as `[{'question': '...', 'answer': '...'}, ...]`.",
            ),
        ]

        self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    def _build_prompt(self):
        system_template = """
        You will be given a document with an ID, source, main_category, and content.

        Your task is to generate multiple question-answer pairs that effectively summarize and extract key information from the document.

        Ensure that the extracted questions fully represent the document's core topics.
        {format_instructions}
        """

        human_template = """
        Here is the document information:
        id: {id}
        source: {source}
        main_category: {main_category}

        Content of the document: |START|{data}|END|
        """

        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(system_template),
                HumanMessagePromptTemplate.from_template(human_template),
            ],
            input_variables=["id", "source", "main_category", "data"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )

    def _create_chain(self):
        self.chain = self.prompt | self.llm | self.output_parser

    def _batch_process(self, data: List[Dict[str, Any]]) -> tuple[list[Any], Any]:
        input_data = [d.to_dict() for d in data]
        valid_responses = []

        with get_openai_callback() as callback:
            response = self.chain.batch(input_data)

        for idx, item in enumerate(response):
            try:
                if not item.get("main_category"):
                    continue

                valid_responses.append(item)

            except Exception as e:
                print(f"❌ Error [{idx}]: {e} ➝ Skipped")

        return valid_responses, callback.total_cost

    def map_data(self, data: List[Dict[str, Any]]) -> Dict:
        if self.path_config.mappings.exists():
            with open(self.path_config.mappings, "r", encoding="utf-8") as f:
                mappings = json.load(f)
        else:
            mappings, cost = self._batch_process(data)

            with open(self.path_config.mappings, "w", encoding="utf-8") as f:
                json.dump(mappings, f, indent=4, ensure_ascii=False)

        return mappings