from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("ETL_COVID").getOrCreate()

# --- INPUT ---
covid_path = "s3://proyecto-covid/raw/covid_*.csv"
hosp_path  = "s3://proyecto-covid/raw/info_hospitales_*.csv"

df_covid = spark.read.csv(covid_path, header=True, inferSchema=True)
df_hosp = spark.read.csv(hosp_path, header=True, inferSchema=True)

# limpieza básica
df_covid = df_covid.dropna(subset=["departamento_nom"])

df_join = df_covid.join(
    df_hosp,
    df_covid["departamento_nom"] == df_hosp["departamento"],
    "left"
)

df_join.write.mode("overwrite").parquet("s3://proyecto-covid/trusted/covid_hospitales/")

spark.stop()
