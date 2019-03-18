package cnblogs;

import java.util.*;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import redis.clients.jedis.Jedis;
import java.sql.*;
import java.io.StringWriter;
import java.io.IOException;

class Test {

    public int writeCompJobToMysql(String jobDetail)
    {
        String DB_URL = "jdbc:mysql://localhost:3306/db_hiddens";
        String USER = "root";
        String PASS = "caonimabi";
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        String sql = "SELECT max(Fauto_id) as Fauto_id FROM t_job_documents_compare limit 1";
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        
        int compareJobId = 0;
        if(DB_res.get(0).get(0)==null)
        {
            compareJobId = 1;
        }
        else
        {
            compareJobId = Integer.parseInt(DB_res.get(0).get(0)) + 1;  // 将String对象转化为Int
        }
        Job jobCompare = new Job(compareJobId, jobDetail);
        MysqlClientInstance.insertJob(jobCompare);
        return compareJobId;
        // System.out.print("This compare job has id: " + compareJobId + "\n");
    }
    
    public void readCompJobFromMysql(String sqlInCondition)
    {
        String DB_URL = "jdbc:mysql://localhost:3306/db_hiddens";
        String USER = "root";
        String PASS = "caonimabi";
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        String sql = "SELECT Ftag_detail FROM t_job_documents_hidden where Fauto_id in " +  sqlInCondition + " limit 10";
        System.out.println(sql);
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        
        int rowNo = DB_res.size();
        for(int i=0; i < rowNo; i++)
        {
            Vector<String> row = DB_res.get(i);
            int colNo = row.size();
            for(int j=0; j < colNo; j++)
            {
                String element = row.get(j);
                System.out.println(element);
            }
        }
        // System.out.print("This compare job has id: " + compareJobId + "\n");
    }
    
    public void writeCompJobToRedis(int jobId, String jobDetail)
    {
        try{
            JSONObject obj = new JSONObject();
            JSONArray jarray = new JSONArray();
        
            obj.put("detail", jobDetail);
            obj.put("status", -1);
            obj.put("candidates", jarray);
        
            StringWriter out = new StringWriter();
            obj.writeJSONString(out);
            String jsonText = out.toString();
            
            Jedis jedis = new Jedis("localhost");
            jedis.select(1);
            jedis.set(Integer.toString(jobId), jsonText);
            
        }catch(IOException ie){
            ie.printStackTrace();
        }finally{
            // System.out.println("Do nothing!");
        }
        
    }
    
    public String readCompJobFromRedis(String key)
    {
        String sqlInCondition = "";
        try{
            Jedis jedis = new Jedis("localhost");
            jedis.select(1);
            String value = jedis.get(key);
            
            JSONParser parser = new JSONParser();
            JSONObject obj = (JSONObject) parser.parse(value);
            
            JSONArray candidates = (JSONArray)obj.get("candidates");
            int candNo = candidates.size();
            
            if(candNo > 0)
            {
                StringJoiner joiner = new StringJoiner(",");
                for(int i=0; i < candNo; i++){
                    String candidate = candidates.get(i).toString();
                    joiner.add(candidate);
                }
                sqlInCondition ="(" + joiner.toString() + ")";
                System.out.println(sqlInCondition);
            }
        }catch(ParseException pe){
            pe.printStackTrace();
        }
        finally{
            return sqlInCondition;
        }
    }
    
    public static void main(String[] args)
    {
        Test mytest = new Test();
        // String jobDetail = "All work and no play makes Jack a dull boy";
        // String jobDetail = "只有工作，没有玩乐，杰克呆若木鸡";
        
        // int jobId = mytest.writeCompJobToMysql(jobDetail);
        // mytest.writeCompJobToRedis(jobId, jobDetail);
        String sqlInCondition = mytest.readCompJobFromRedis("1");
        mytest.readCompJobFromMysql(sqlInCondition);

    }
}