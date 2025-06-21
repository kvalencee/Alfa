# AlfaIA - Aplicación Educativa con PyQt6 y NLP
# Estructura base del proyecto

import os
import sys
from pathlib import Path


def create_project_structure():
    """
    Crea la estructura completa de directorios para AlfaIA
    según las especificaciones técnicas
    """

    # Directorio raíz del proyecto
    project_root = Path("AlfaIA")

    # Estructura de directorios según especificaciones
    directories = [
        # Raíz
        "AlfaIA",

        # Configuración
        "AlfaIA/config",

        # Núcleo de la aplicación
        "AlfaIA/core",
        "AlfaIA/core/database",
        "AlfaIA/core/auth",
        "AlfaIA/core/utils",

        # Módulos funcionales
        "AlfaIA/modules",
        "AlfaIA/modules/nlp",
        "AlfaIA/modules/exercises",
        "AlfaIA/modules/games",
        "AlfaIA/modules/analytics",
        "AlfaIA/modules/content",

        # Interfaz de usuario
        "AlfaIA/ui",
        "AlfaIA/ui/windows",
        "AlfaIA/ui/widgets",
        "AlfaIA/ui/dialogs",
        "AlfaIA/ui/resources",

        # Datos de la aplicación
        "AlfaIA/data",
        "AlfaIA/data/models",
        "AlfaIA/data/content",
        "AlfaIA/data/exports",

        # Pruebas
        "AlfaIA/tests",
        "AlfaIA/tests/unit",
        "AlfaIA/tests/integration",
        "AlfaIA/tests/ui"
    ]

    # Crear directorios
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Creado: {directory}")

    # Crear archivos __init__.py para hacer los directorios paquetes Python
    init_files = [
        "AlfaIA/__init__.py",
        "AlfaIA/config/__init__.py",
        "AlfaIA/core/__init__.py",
        "AlfaIA/core/database/__init__.py",
        "AlfaIA/core/auth/__init__.py",
        "AlfaIA/core/utils/__init__.py",
        "AlfaIA/modules/__init__.py",
        "AlfaIA/modules/nlp/__init__.py",
        "AlfaIA/modules/exercises/__init__.py",
        "AlfaIA/modules/games/__init__.py",
        "AlfaIA/modules/analytics/__init__.py",
        "AlfaIA/modules/content/__init__.py",
        "AlfaIA/ui/__init__.py",
        "AlfaIA/ui/windows/__init__.py",
        "AlfaIA/ui/widgets/__init__.py",
        "AlfaIA/ui/dialogs/__init__.py",
        "AlfaIA/tests/__init__.py"
    ]

    for init_file in init_files:
        Path(init_file).touch()
        print(f"✓ Creado: {init_file}")

    print("\n🎉 Estructura del proyecto AlfaIA creada exitosamente!")
    print("\n📁 Estructura creada:")
    print("AlfaIA/")
    print("├── main.py")
    print("├── config/")
    print("│   ├── settings.py")
    print("│   ├── database_config.py")
    print("│   └── nlp_config.py")
    print("├── core/")
    print("│   ├── database/")
    print("│   ├── auth/")
    print("│   └── utils/")
    print("├── modules/")
    print("│   ├── nlp/")
    print("│   ├── exercises/")
    print("│   ├── games/")
    print("│   ├── analytics/")
    print("│   └── content/")
    print("├── ui/")
    print("│   ├── windows/")
    print("│   ├── widgets/")
    print("│   ├── dialogs/")
    print("│   └── resources/")
    print("├── data/")
    print("│   ├── models/")
    print("│   ├── content/")
    print("│   └── exports/")
    print("└── tests/")
    print("    ├── unit/")
    print("    ├── integration/")
    print("    └── ui/")


if __name__ == "__main__":
    create_project_structure()