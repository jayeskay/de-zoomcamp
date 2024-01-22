import sys
import sqlalchemy
import pandas as pd

print(f"EXECUTING {sys.argv[-1]}")
print(f"sqlalchemy version: {sqlalchemy.__version__}")
print(f"pandas version: {pd.__version__}")
