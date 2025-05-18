from langchain_ollama import ChatOllama
from langchain.chains import LLMChain
from langchain.schema.document import Document
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate as ChatPromptTemplate_prompts
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from src.utils import Config


class PersonalKnowleged:
    """
    Clase para gestionar un sistema de conocimiento personal utilizando modelos de lenguaje y búsqueda vectorial.

    Esta clase configura un pipeline de Recuperación-Augmentada-Generación (RAG) usando:
    - Un modelo Ollama para generación de respuestas.
    - Pinecone como vectorstore para recuperación de documentos.
    - HuggingFaceEmbeddings para generar embeddings de texto.
    - Un paso de compresión para reducir ruido en los documentos recuperados.
    - Un prompt personalizado que obliga a responder solo si la información está en el contexto.
    """

    def __init__(self, config: Config):
        self.config = config
        self.model_name = self.config.model.get('embedding_model_name')
        self.ollama_model_name = self.config.model.get('ollama_model')
        self.ollama_temperature = self.config.model.get('temperature')
        self.pinecone_index = self.config.creds.get('pinecone_index')
        self.pinecone_api_key = self.config.creds.get('pinecone_api_key')

        # Modelo LLM principal
        self.model = ChatOllama(model=self.ollama_model_name, temperature=self.ollama_temperature)
        self.parser = StrOutputParser()
        self.ollama_model = self.model | self.parser

        # Embeddings y Vectorstore
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
        self.vectorstore = PineconeVectorStore(
            pinecone_api_key=self.pinecone_api_key,
            index_name=self.pinecone_index,
            embedding=self.embeddings
        )
        # Compresor de contexto
        compression_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Eres un asistente experto en extracción de información relevante. "
                "Tienes dos tareas principales, resumir el texto que se te proporciona y después de forma breve "
                "poner la relación que tiene el texto con la pregunta. \n"
                "El resumen es **Obligatorio**, mientras que la relación es **Opcional** (Si el texto no es útil, devuelve una cadena vacía.)\n"
                "**No inventes información.**"
                "La respueta debe seguir el siguiente formato: \nResumen: [tu resumen]\n\nRelación: [tu relación con la pregunta]"
            ),
            HumanMessagePromptTemplate.from_template(
                "Contexto:\n{context}\n\nPregunta:\n{question}"
            )
        ])
        compressor_chain = compression_prompt | self.model

        custom_extractor = LLMChainExtractor(llm_chain=compressor_chain)
        # Retriever con compresión
        self.retriever = ContextualCompressionRetriever(
            base_compressor=custom_extractor,
            base_retriever=self.vectorstore.as_retriever()
        )

        # Pipeline RAG
        # Prompt
        template = """
Instrucciones:
Responde solo si puedes encontrar la información directamente en el contexto. Si no puedes, responde exactamente con: "No tengo suficiente información para responder esa pregunta."

Sé directo y preciso. No inventes información. No agregues opiniones ni explicaciones si no se piden.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
        self.prompt = ChatPromptTemplate_prompts.from_template(template)
        self.setup = RunnableParallel(context=self.retriever, question=RunnablePassthrough())
        self.chain = self.setup | self.prompt | self.ollama_model

    def similarity_check(self, question: str, k: int = 4) -> list:
        """
        Busca documentos semánticamente similares a la pregunta en el almacén vectorial.
        """
        return self.vectorstore.similarity_search(question, k=k)

    def retrieval_answer(self, question: str) -> str:
        """
        Responde a una pregunta utilizando el pipeline RAG con compresión de contexto.
        """
        return self.chain.invoke(question)

    def add_document(self, documents: list[Document]) -> None:
        """
        Agrega un nuevo documento al almacén vectorial.
        """
        self.vectorstore.add_documents(documents)
