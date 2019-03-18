package cnblogs;

import java.util.*;
import java.io.IOException;
import java.io.StringWriter;

import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import redis.clients.jedis.Jedis;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class JobUpload
 */
@WebServlet("/JobUpload")
public class JobUpload extends HttpServlet {
    private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public JobUpload() {
        super();
        // TODO Auto-generated constructor stub
    }

    /**
     * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
     */
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        // 设置响应内容类型
        // response.setContentType("text/html;charset=UTF-8");
        response.setCharacterEncoding("UTF-8");

        // 查看是否有内容输入
        if(request.getParameter("detail")!=null)
        {
            // 写入MySQL与Redis
            int jobCount = getTodayInsertedJobCount();
            if(jobCount > 100)  // 先写死，以后再优化吧，fuck
            {
                // 一天插入的样本job不能超过某个阈值
                request.getRequestDispatcher("/refuse.jsp").forward(request, response);
            }
            String jobDetail = new String(request.getParameter("detail").getBytes("ISO8859-1"),"UTF-8");
            int jobId = writeCompJobToMysql(jobDetail);
            writeCompJobToRedis(jobId, jobDetail);
            
            String jumpUrl = String.format("http://119.28.26.222:8080/SIBYL_SYSTEM/JobCompRes?jobCompId=%d",jobId);
            request.setAttribute("jumpUrl", jumpUrl);
            request.getRequestDispatcher("/inform.jsp").forward(request, response);
        }
        else
        {
            request.getRequestDispatcher("/refuse.jsp").forward(request, response);
        }
    }
    
    // 处理 POST 方法请求的方法
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doGet(request, response);
    }
    
    // 检查插入的JOB是否已经达到今日上限
    private int getTodayInsertedJobCount()
    {
        String DB_URL = "jdbc:mysql://localhost:3306/db_documents";
        String USER = "root";
        String PASS = "worinimamaipi_caonimabi23333_yunjianblackfyre1815";
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        
        String today = Util.getCurrentDate();
        today = today + " 01:01:01";
        
        String sql = String.format("SELECT count(Fauto_id) as Fauto_id_count FROM t_job_documents_compare where Fcreate_time > '%s'", today);
        System.out.println(sql);
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        int todayJobInsertedCount = Integer.parseInt(DB_res.get(0).get(0));
        return todayJobInsertedCount;
    }
    
    private int writeCompJobToMysql(String jobDetail)
    {
        String DB_URL = "jdbc:mysql://localhost:3306/db_documents?useUnicode=true&characterEncoding=utf-8";
        String USER = "root";
        String PASS = "worinimamaipi_caonimabi23333_yunjianblackfyre1815";
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        String sql = "SELECT max(Fauto_id) as Fauto_id FROM t_job_documents_compare limit 1";
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        
        int compareJobId = 0;
        if(DB_res.size()==0)
        {
            compareJobId = 1;
        }
        else if(DB_res.get(0).get(0)==null)
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
    
    private void writeCompJobToRedis(int jobId, String jobDetail)
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
            jedis.select(0);
            jedis.set(Integer.toString(jobId), jsonText);
            
        }catch(IOException ie){
            ie.printStackTrace();
        }finally{
            // System.out.println("Do nothing!");
        }
        
    }
}
