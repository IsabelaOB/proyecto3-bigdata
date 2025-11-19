import os
import pandas as pd

OUT_DIR = os.path.join('api', 'sample_data')
os.makedirs(OUT_DIR, exist_ok=True)

rows = [
    {'nombre_departamento': 'Antioquia', 'departamento': '05', 'camas': 1000, 'ucis': 100, 'casos_totales': 50000, 'fallecidos': 1200, 'recuperados': 48000},
    {'nombre_departamento': 'Bogotá', 'departamento': '11', 'camas': 2000, 'ucis': 250, 'casos_totales': 80000, 'fallecidos': 2300, 'recuperados': 76000},
    {'nombre_departamento': 'Valle del Cauca', 'departamento': '76', 'camas': 900, 'ucis': 80, 'casos_totales': 30000, 'fallecidos': 800, 'recuperados': 29000},
    {'nombre_departamento': 'Cundinamarca', 'departamento': '25', 'camas': 700, 'ucis': 60, 'casos_totales': 20000, 'fallecidos': 500, 'recuperados': 19000},
]

for r in rows:
    camas = r.get('camas') or 0
    casos = r.get('casos_totales') or 0
    r['tasa_ocupacion_camas_estimada'] = float(casos) / camas if camas and camas > 0 else None

df = pd.DataFrame(rows)
outfile = os.path.join(OUT_DIR, 'covid_summary.parquet')
df.to_parquet(outfile, index=False)
print(f'Wrote sample parquet to {outfile}')
