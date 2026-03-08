# cinedos

Sitio para coordinar compañeros de promociones 2x1 en cines del GBA.

## Puesta en marcha

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear las tablas
python manage.py migrate

# 4. Correr los tests
pytest -v
```

## Estructura del proyecto

```
cinedos/
├── cinedos/          # Configuración Django
│   └── settings.py
├── cartelera/        # App principal
│   ├── models.py
│   └── tests/
│       ├── factories.py
│       └── test_models.py
├── pytest.ini
├── requirements.txt
└── manage.py         # (generado por django-admin startproject)
```

## Correr solo una clase de tests

```bash
pytest cartelera/tests/test_models.py::TestShowtimeModel -v
```
