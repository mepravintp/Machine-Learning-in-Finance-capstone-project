"""NovaFin capstone toolkit (Vineet's version). Every module imports it, so validation and reporting look the same
everywhere and Module 9 can read every module's handoff record."""
from . import evaluate, explain, finance, handoff, splits
from .config import ASSUMPTIONS, CRORE, DATA, FIGURES, LAKH, MODULES, RESULTS, ROOT, SEED, load, use_module
