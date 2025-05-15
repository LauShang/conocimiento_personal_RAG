"""
Utility functions for the project.
author: Lauro Reyes
"""
import sys
import logging
import yaml

logger = logging.getLogger(__name__)

class Config:
    """Credentials configuration"""

    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config = self.read_configuration()
        self.creds = self.config["credentials"]

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


def setup_logging(debug_mode,file) -> None:
    """
    Configura el logger para el proceso ETL.
    - Los logs de nivel INFO y superiores se guardan en logs/{file}.log.
    - Si `debug_mode` es True, los logs de nivel DEBUG también se imprimen en la consola.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Formato de los logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s')
    
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

    # Reducir el nivel de logging de Werkzeug a WARNING
    #logging.getLogger("urllib3").setLevel(logging.WARNING)
    

