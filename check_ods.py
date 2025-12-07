import pandas as pd

try:
    df = pd.read_excel(r"c:\Users\Ayoub\Desktop\Proyecto_Avisos\.venv\Libro1.ods", engine="odf")
    print("Columns found:")
    for col in df.columns:
        print(f"- {col}")
except Exception as e:
    print(f"Error reading ODS: {e}")
