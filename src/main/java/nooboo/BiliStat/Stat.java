package nooboo.BiliStat;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.functions;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.explode;

public class Stat {
    public static void main(String[] args) {
	Config config = ConfigFactory.load("mongo.conf");
	String mongoUri = config.getString("mongoConf");
        SparkSession spark = SparkSession.builder()
                .appName("BiliStat")
                .master("local")
                .config("spark.mongodb.input.uri", "mongodb://nooboo:luoyuyang@8.219.190.155:27017/biliStat.videoInfo?authSource=admin")
                .getOrCreate();

        Dataset<Row> df = spark.read().format("mongo").load();
	
	// 解构标签列表
        Dataset<Row> dfTags = df.withColumn("tag", explode(df.col("video_tags")))
                                .withColumn("main_tag", col("tag").getItem(0))
                                .withColumn("sub_tag", col("tag").getItem(1))
                                .drop("tag");

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
