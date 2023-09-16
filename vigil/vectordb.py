# https://github.com/deadbits/vigil-llm
import logging

import chromadb

from chromadb.config import Settings
from chromadb.utils import embedding_functions


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDB:
    def __init__(self, config_dict: dict):
        self.name = 'database:vector'

        if config_dict['embed_fn'] == 'openai':
            logger.info(f'[{self.name}] Using OpenAI embedding function')
            self.embed_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=config_dict['openai_key'],
                model_name='text-embedding-ada-002'
            )
        else:
            logger.info(f'[{self.name}] Using SentenceTransformer embedding function: {config_dict["embed_fn"]}')
            self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=config_dict['embed_fn']
            )

        self.collection_name = config_dict['collection_name']
        self.db_dir = config_dict['db_dir']
        self.n_results = int(config_dict['n_results'])

        if not hasattr(self.embed_fn, "__call__"):
            logger.error(f'[{self.name}] Embedding function is not callable')
            raise ValueError('[database:vectordb] Embedding function is not a function')

        self.client = chromadb.PersistentClient(
            path=self.db_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
        self.collection = self.get_or_create_collection(self.collection_name)
        logger.info(f'[{self.name}] Loaded database')

    def get_or_create_collection(self, name):
        logger.info(f'[{self.name}] Using collection: {name}')
        self.collection = self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embed_fn,
            metadata={'hnsw:space': 'cosine'}
        )
        return self.collection

    def add_texts(self, texts: list, ids: list):
        logger.info(f'[{self.name}] Adding {len(texts)} texts')
        try:
            self.collection.add(
                documents=texts,
                ids=ids
            )
        except Exception as err:
            logger.error(f'[{self.name}] Failed to add texts to collection: {err}')

    def add_embeddings(self, texts: list, embeddings: list, ids: list):
        logger.info(f'[{self.name}] Adding {len(texts)} embeddings')
        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                ids=ids
            )
        except Exception as err:
            logger.error(f'[{self.name}] Failed to add texts to collection: {err}')

    def query(self, text: str):
        logger.info(f'[{self.name}] Querying database for: {text}')
        try:
            return self.collection.query(
                query_texts=[text],
                n_results=self.n_results)
        except Exception as err:
            logger.error(f'[{self.name}] Failed to query database: {err}')