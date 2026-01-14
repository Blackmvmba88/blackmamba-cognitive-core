"""
BlackMamba Cognitive Core
Motor cognitivo modular para construir aplicaciones interactivas basadas en IA
"""

__version__ = "0.1.0"
__author__ = "BlackMamba"

from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.core.response_generator import ResponseGenerator

__all__ = [
    "CognitiveEngine",
    "InputProcessor",
    "ResponseGenerator",
]
