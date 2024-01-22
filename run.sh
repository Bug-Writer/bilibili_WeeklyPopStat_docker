echo "打包Spark程序..."
mvn clean package -Dproject.build.sourceEncoding=UTF-8 -Dproject.reporting.outputEncoding=UTF-8

echo "将jar包复制进入docker容器..."
docker cp target/BiliWeeklyPopStat-1.0-SNAPSHOT-jar-with-dependencies.jar spark-master:/opt
sleep 5

echo "将任务上传至Spark集群，访问Spark WebUI: http://8.219.190.155:8080/ 以查看更多信息"
docker exec -it spark-master /bin/bash -c \
	"cd ../../; spark-submit --class nooboo.BiliStat.Stat --master spark://10.0.2.100:7077 --deploy-mode cluster --conf 'spark.executor.extraJavaOptions=-Dfile.encoding=UTF-8' --conf 'spark.driver.extraJavaOptions=-Dfile.encoding=UTF-8' --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 BiliWeeklyPopStat-1.0-SNAPSHOT-jar-with-dependencies.jar"

