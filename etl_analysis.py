from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("COVID-ANALYSIS").getOrCreate()

trusted_path = "s3://proyecto-covid/trusted/covid_final_joined/"
refined_output = "s3://proyecto-covid/refined/covid_summary/"

df = spark.read.parquet(trusted_path)

df_summary = (
    df.groupBy(
        "Nombre departamento",
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
        (F.col("casos_totales") / F.col("camas")).cast("double")
    )
)

df_summary.write.mode("overwrite").parquet(refined_output)

spark.stop()
