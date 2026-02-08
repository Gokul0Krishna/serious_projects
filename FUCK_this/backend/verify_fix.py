import sys
import os

def verify():
    print(f"Python version: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    try:
        import numpy
        print(f"NumPy version: {numpy.__version__}")
        if numpy.__version__.startswith('2.'):
            print("!!! WARNING: NumPy 2.x detected. This is known to cause crashes in sentence-transformers.")
    except ImportError:
        print("NumPy not found")

    try:
        import sentence_transformers
        print("Sentence-Transformers loaded successfully!")
    except Exception as e:
        print(f"!!! FAILED to load Sentence-Transformers: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
