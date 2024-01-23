docker run -d -p 7070:7070 -p 8080:8080 --network bridge --name spark-master bitnami/spark /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.master.Master
docker run -d --network bridge --name spark-worker bitnami/spark /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://10.88.0.2:7077
