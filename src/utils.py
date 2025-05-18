"""
Utility functions for the project.
author: Lauro Reyes
"""
import sys
import logging
import yaml
import yt_dlp
import whisper
import tempfile
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

logger = logging.getLogger(__name__)


class Config:
    """Credentials configuration"""

    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config = self.read_configuration()
        self.creds = self.config["credentials"]
        self.model = self.config["model"]
        self.app = self.config["app"]

    def read_configuration(self):
        """
        Read and load configuration from a YAML file.

        Returns:
            dict: Loaded configuration as a dictionary.

        Raises:
            FileNotFoundError: If the specified configuration file is not found.
            yaml.YAMLError: If there is an error in parsing the YAML file.
        """
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                logger.info("Yaml config found and read successfully.")
                return config
        except FileNotFoundError as err:
            logger.error("Failed to load configuration file: %s", err)
            sys.exit()
        except yaml.scanner.ScannerError as err:
            logger.error("Yaml config file has errors: %s", err)
            sys.exit()


def setup_logging(debug_mode, file) -> None:
    """
    Configura el logger para la aplicación.
    - Los logs de nivel INFO y superiores se guardan en logs/{file}.log.
    - Si `debug_mode` es True, los logs de nivel DEBUG también se imprimen en la consola.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    # Formato de los logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s"
    )

    # Manejador para archivo (INFO y superiores)
    file_handler = logging.FileHandler(file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Manejador para consola (solo DEBUG si debug_mode es True)
    if debug_mode:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Reducir el nivel de logging de paquetes de terceros
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("langsmith.client").setLevel(logging.WARNING)


def download_youtube_audio_and_transcribe(url: str) -> str:
    """
    Descarga el audio de un video de YouTube, lo transcribe usando Whisper y retorna el texto transcrito.

    Parameters:
        url (str): URL del video de YouTube a descargar.

    Returns:
        str: Texto transcrito.
    """
    logger.debug("Creando directorio temporal para descarga de audio.")
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "audio.%(ext)s")
        ydl_opts = {"format": "bestaudio/best", "outtmpl": output_path, "quiet": True}

        logger.debug(f"Iniciando descarga del audio desde {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        logger.debug("Buscando archivo de audio descargado.")
        audio_file = next(
            (
                os.path.join(tmpdir, f)
                for f in os.listdir(tmpdir)
                if f.endswith((".mp3", ".m4a", ".webm", ".opus"))
            ),
            None,
        )

        if not audio_file:
            logger.error("No se encontró archivo de audio descargado.")
            return None

        logger.debug(f"Archivo de audio encontrado: {audio_file}")
        transcription = transcribe_audio(audio_file)
        return transcription


def transcribe_audio(audio_file: str) -> str:
    """
    Transcribe un archivo de audio usando Whisper.

    Parameters:
        audio_file (str): Ruta al archivo de audio a transcribir.

    Returns:
        str: Texto transcrito.
    """
    logger.debug("Cargando modelo Whisper.")
    whisper_model = whisper.load_model("base")

    logger.debug("Iniciando transcripción con Whisper.")
    transcription = whisper_model.transcribe(audio_file, fp16=False)["text"].strip()

    logger.debug("Transcripción completada")
    return transcription


def generate_documents(
    transcription: str,
    chunk_size: int = 800,
    chunk_overlap: int = 300,
    metadata: dict = None,
) -> list[Document]:
    """
    Divide el texto transcrito en fragmentos y los convierte en objetos Document de LangChain.

    Parameters:
        transcription (str): Texto transcrito a dividir.
        chunk_size (int): Tamaño máximo de cada fragmento de texto.
        chunk_overlap (int): Número de caracteres que se superponen entre fragmentos.
        splitter (str): Tipo de divisor a utilizar ("recursive" o "character").
        metadata (dict): Metadatos a adjuntar a cada documento.

    Returns:
        list[Document]: Lista de objetos Document generados a partir de la transcripción.
    """
    logger.debug("Dividiendo la transcripción en fragmentos.")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    fragments = text_splitter.split_text(transcription)
    logger.debug(f"Fragmentos generados: {len(fragments)}")
    documents = [
        Document(page_content=fragment, metadata=metadata or {})
        for fragment in fragments
    ]

    logger.info(
        f"Transcripción y división completadas. Fragmentos generados: {len(documents)}"
    )
    return documents
