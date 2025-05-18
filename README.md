# Sistema de Gestión de Conocimiento Personal

## Descripción General

El Sistema de Gestión del Conocimiento es una aplicación web basada en Flask diseñada para gestionar y recuperar información personal. Proporciona una interfaz fácil de usar para interactuar con diversas fuentes de datos, incluyendo videos de YouTube, archivos MP3, entradas de texto y documentos PDF. El sistema utiliza modelos de lenguaje avanzados y almacenes de vectores para procesar y almacenar información para una recuperación eficiente.

## Características

- **Interfaz de Chat**: Haz preguntas y obtén respuestas basadas en el conocimiento almacenado.
- **Ingreso de Datos**: Carga y procesa datos desde múltiples fuentes:
  - YouTube videos: Extrae y transcribe el audio.
  - Archivos MP3: Transcribe el contenido de audio.
  - Texto: Procesa y almacena el texto proporcionado por el usuario.
  - Documentos PDF: Extrae y almacena el contenido de archivos PDF.

## Instalación

### Requisitos Previos

- Python 3.10 o superior
- [Poetry](https://python-poetry.org/) (para gestionar dependencias y el archivo `pyproject.toml`)
```bash
poetry install
```
O también puedes ejecutar directamente con Poetry sin activar el entorno:
```bash
poetry run python app.py
```

Configura el archivo de configuración:
* Edita config.yaml para incluir tus claves API y otras configuraciones.

Ejecuta la aplicación:

```{Bash}
python app.py
```
Abre tu navegador y navega a:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

## Estructura del Proyecto
El proyecto está organizado de la siguiente manera:
```
conocimiento_personal_RAG/
├── app.py                 # Main Flask application
├── config.yaml            # Configuration file
├── src/                   # Source code
│   ├── model_cp.py        # Core model logic
│   ├── utils.py           # Utility functions
├── templates/             # HTML templates
│   ├── chat.html          # Chat page
│   ├── input.html         # Input data page
├── static/                # Static files
│   ├── styles.css         # CSS styles
│   ├── scripts.js         # JavaScript logic
│   ├── chat.js            # Chat-specific JavaScript
├── docs/                  # Sample documents for testing
├── logs/                  # Log files
└── README.md              # Project documentation
├── LICENSE                # License file
├── pyproject.toml         # Python dependencies
```

## Contribuciones

¡Las contribuciones son bienvenidas! Por favor, haz un fork del repositorio y envía una solicitud de extracción (pull request).

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para obtener más detalles.

## Agradecimientos

Agradecimiento especial [Rod Rivera](https://github.com/rodriveracom) por la clase de Temas Selectos de Análisis de Datos impartida en el ITAM.