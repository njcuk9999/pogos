"""
PYTHONSTARTUP=/scratch3/jwst/pogos/pogos/.idea/plot_debugger.py
"""

# pycharm_debug_startup.py
import sys

# Only run when inside the PyCharm debugger
if "pydevd" in sys.modules:
    import matplotlib
    try:
        # Force a non-Qt backend so inline plots don't explode
        matplotlib.use("TkAgg")
    except Exception as e:
        print(f"Could not set matplotlib backend: {e}")