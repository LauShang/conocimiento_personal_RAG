import logging
#from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.schema.document import Document
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate as ChatPromptTemplate_prompts
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from src.utils import Config

logger = logging.getLogger(__name__)


class PersonalKnowleged:
    """
    Clase para gestionar un sistema de conocimiento personal utilizando modelos de lenguaje y búsqueda vectorial.

    Esta clase configura un pipeline de Recuperación-Augmentada-Generación (RAG) usando:
    - Un modelo para generación de respuestas.
    - Pinecone como vectorstore para recuperación de documentos.
    - HuggingFaceEmbeddings para generar embeddings de texto.
    - Un paso de compresión para reducir ruido en los documentos recuperados.
    - Un prompt personalizado que obliga a responder solo si la información está en el contexto.
    """

    def __init__(self, config: Config):
        logger.info("Iniciando el sistema de conocimiento personal.")
        self.config = config
        self.embedding_model_name = self.config.model.get('embedding_model_name')
        self.model_name = self.config.model.get('model_name')
        self.temperature = self.config.model.get('temperature')
        self.pinecone_index = self.config.creds.get('pinecone_index')
        self.pinecone_api_key = self.config.creds.get('pinecone_api_key')
        self.openai_key = self.config.creds.get('openai_api_key')

        # Modelo LLM principal
        self.model = ChatOpenAI(api_key=self.openai_key, model=self.model_name, temperature=self.temperature)
        self.parser = StrOutputParser()
        self.ollama_model = self.model | self.parser

        # Embeddings y Vectorstore
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self.vectorstore = PineconeVectorStore(
            pinecone_api_key=self.pinecone_api_key,
            index_name=self.pinecone_index,
            embedding=self.embeddings
        )
        # Compresor de contexto
        compression_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Eres un asistente experto en extracción de información relevante. "
                "Tienes una tarea principal, parafrasear el texto que se te proporciona, mantenido la idea y longitud similar del texto\n"
                "**No inventes información.**"
            ),
            HumanMessagePromptTemplate.from_template(
                "Contexto:\n{context}"
            )
        ])
        self.compressor_chain = compression_prompt | self.model | self.parser
        # retriever
        self.retriever = self.vectorstore.as_retriever()

        # Pipeline RAG
        # Prompt
        template = """
Instrucciones:
Responde con base en el contexto que te proporciona el documento.
Prioriza el tema central de la pregunta para dar una respuesta más acertada, ya que puede haber información que no este directamente relacionada con la pregunta.
Si no puedes, responde exactamente con: "No tengo suficiente información para responder esa pregunta."

Sé breve, claro y preciso respecto a la información que proporciones.
No inventes información. No agregues opiniones ni explicaciones si no se piden, pues el objetivo es darle al usuario información clara con base en el contexto.

Contexto:
{context}

Pregunta:
{question}
"""
        self.rag_prompt = ChatPromptTemplate_prompts.from_template(template)
        # RAG LLM
        self.rag_chain = self.rag_prompt | self.ollama_model

    def similarity_check(self, question: str, k: int = 4) -> list:
        """
        Busca documentos semánticamente similares a la pregunta en el almacén vectorial.
        """
        return self.vectorstore.similarity_search(question, k=k)

    def retrieval_answer(self, question: str, k:int = 4, threshold:float = 0.5) -> str:
        """
        Responde a una pregunta utilizando el pipeline RAG con compresión de contexto.
        """
        # Recupera documentos relevantes
        context_compresed = ""
        docs = self.vectorstore.similarity_search_with_score(question, k=k)
        filtered_docs = [(doc, score) for doc, score in docs if score >= threshold]
        # Filtra documentos por score
        logger.debug(f"docs relevante: {len(filtered_docs)} de {len(docs)}")
        for doc in docs:
            context_compresed += (self.compressor_chain.invoke(
                {
                    'context': doc[0].page_content
                }
            ) + "\n\n")
        promt = {"context": context_compresed, "question": question}
        # Ejecuta el pipeline RAG
        return self.rag_chain.invoke(promt)

    def add_documents(self, documents: list[Document]) -> None:
        """
        Agrega un nuevo documento al almacén vectorial.
        """
        self.vectorstore.add_documents(documents)
        logger.info(f"Documentos añadidos: {len(documents)}") 
