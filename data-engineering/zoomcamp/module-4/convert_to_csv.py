from fastparquet import ParquetFile

# Reading the data from Parquet File
pf = ParquetFile("fhv_tripdata_2019-01.parquet")

# Converting data in to pandas dataFrame
dataFrame = pf.to_pandas()

# Converting to CSV
dataFrame.to_csv("fhv_tripdata_2019-01.csv", index=False)
