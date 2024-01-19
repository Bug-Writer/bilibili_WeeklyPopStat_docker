package nooboo.BiliStat;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.functions;
import org.apache.spark.sql.types.*;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.explode;

public class Stat {
    public static void main(String[] args) {
	Config config = ConfigFactory.load("mongo.conf");
	String mongoUri = config.getString("mongoConf");
        SparkSession spark = SparkSession.builder()
                .appName("BiliStat")
                .master("local")
		.config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8")
		.config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8")
                .config("spark.mongodb.input.uri", "mongodb://nooboo:luoyuyang@8.219.190.155:27017/biliStat.videoInfo?authSource=admin")
                .getOrCreate();
	StructType schema = new StructType(new StructField[] {
            new StructField("_id", DataTypes.StringType, true, Metadata.empty()),
            new StructField("video_title", DataTypes.StringType, true, Metadata.empty()),
            new StructField("video_time", DataTypes.StringType, true, Metadata.empty()),
            new StructField("video_tags", DataTypes.createArrayType(DataTypes.StringType), true, Metadata.empty())
        });

        Dataset<Row> df = spark.read().schema(schema).format("mongo").load();
	
	// 解构标签列表
        Dataset<Row> dfTags = df.withColumn("main_tag", col("video_tags").getItem(0))
                                .withColumn("sub_tag", col("video_tags").getItem(1))
                                .drop("video_tags");

        // 显示带有主标签和副标签的DataFrame
        dfTags.show();

        // 对主标签进行聚合统计
        dfTags.groupBy("main_tag").agg(functions.count("main_tag").as("main_tag_count"))
              .orderBy(col("main_tag_count").desc())
              .show();

        // 对副标签进行聚合统计
        dfTags.groupBy("sub_tag").agg(functions.count("sub_tag").as("sub_tag_count"))
              .orderBy(col("sub_tag_count").desc())
              .show();

        spark.stop();
    }
}
