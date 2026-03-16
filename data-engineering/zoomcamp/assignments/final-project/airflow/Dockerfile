FROM apache/airflow:2.10.4-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-jdk procps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV SPARK_HOME=/home/airflow/.local/lib/python3.11/site-packages/pyspark

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
