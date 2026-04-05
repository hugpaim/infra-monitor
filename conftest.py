# conftest.py
import sys
from pathlib import Path

# Adiciona a raiz do projecto ao sys.path para que
# "from src.collectors..." funcione nos testes
sys.path.insert(0, str(Path(__file__).parent))
