from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("COVID-ANALYSIS").getOrCreate()

trusted_path = "s3://proyecto-covid/trusted/covid_final_joined/"
refined_output = "s3://proyecto-covid/refined/covid_summary/"

df = spark.read.parquet(trusted_path)

df_summary = (
    df.groupBy(
        "departamento_nom",
        "departamento",
        "camas",
        "ucis"
    )
    .agg(
        F.count("*").alias("casos_totales"),
        F.sum(F.when(F.col("Estado") == "Fallecido", 1).otherwise(0)).alias("fallecidos"),
        F.sum(F.when(F.col("Recuperado") == "Recuperado", 1).otherwise(0)).alias("recuperados")
    )
    .withColumn(
        "tasa_ocupacion_camas_estimada",
        F.when((F.col("camas").isNotNull()) & (F.col("camas") > 0),
               (F.col("casos_totales") / F.col("camas")).cast("double"))
         .otherwise(None)
    )
)

# Estandarizar nombre para consultas (ej. Athena)
df_summary = df_summary.withColumnRenamed("departamento_nom", "nombre_departamento")

df_summary.write.mode("overwrite").parquet(refined_output)

spark.stop()
