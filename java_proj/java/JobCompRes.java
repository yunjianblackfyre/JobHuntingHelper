package cnblogs;

import java.util.*;
import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class JobCompRes
 */
@WebServlet("/JobCompRes")
public class JobCompRes extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private int jobListLength = 0;
    private String currentSeason = "0";
    private String DB_URL = "jdbc:mysql://localhost:3306/db_documents";
    private String USER = "root";
    private String PASS = "worinimamaipi_caonimabi23333_yunjianblackfyre1815";
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public JobCompRes() {
        super();
        // TODO Auto-generated constructor stub
        currentSeason = Integer.toString(Util.getCurrentSeason());
    }

    /**
     * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
     */
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        // 设置响应内容类型
        // response.setContentType("text/html;charset=UTF-8");
        response.setCharacterEncoding("UTF-8");
        
        // 将JOB列表传给JSP
        //if(request.getParameter("jobCompId")!=null)
        if(Util.checkRequestIntParam(request.getParameter("jobCompId")))
        {
            String jobCompId = new String(request.getParameter("jobCompId").getBytes("ISO8859-1"),"UTF-8");
            String jobRelated = getJobRelated(jobCompId);
            
            if(jobRelated!=null)
            {
                String pageNoString = "1";
                if(request.getParameter("pageNo")!=null)
                {
                    pageNoString = new String(request.getParameter("pageNo").getBytes("ISO8859-1"),"UTF-8");
                }
                
                List<Job> jobCompList = getJobComp(jobCompId);
                if(jobCompList.size()==0)
                {
                    request.getRequestDispatcher("/empty.jsp").forward(request, response);
                }
                else{
                    String jobSeasonId = jobCompList.get(0).getSeasonId();
                    int pageNo = Util.genPageNo(pageNoString);
                    String jumpUrl = String.format("http://119.28.26.222:8080/SIBYL_SYSTEM/JobMode?jobSeasonId=%s&jobCompId=%s",jobSeasonId, jobCompId);
                    List<Job> jobList = getJobTable(jobSeasonId, jobRelated, jumpUrl, pageNo);
                    
                    if(jobList.size()==0)
                    {
                        request.getRequestDispatcher("/empty.jsp").forward(request, response);
                    }
                    else
                    {
                        request.setAttribute("jobCompList", jobCompList);
                        request.setAttribute("pageNo", pageNo);
                        request.setAttribute("jobList", jobList);
                        request.setAttribute("jobListLength", jobListLength);
                        request.setAttribute("jobCompId", jobCompId);
                        // System.out.println(pageNo);
                        // System.out.println(jobListLength);
                        request.getRequestDispatcher("/job_list.jsp").forward(request, response);
                    }
                }

            }
            else
            {
                String jumpUrl = (request.getRequestURL().toString())+ "?" + "jobCompId=" + jobCompId;
                request.setAttribute("jumpUrl", jumpUrl);
                request.getRequestDispatcher("/wait.jsp").forward(request, response);
            }
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
    
    private String getJobRelated(String jobCompId) {
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        String sql = String.format("SELECT Fjob_related FROM t_job_documents_compare where Fauto_id=%s limit 1", jobCompId);
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        List<Job> jobList = new ArrayList<Job>();
        if (DB_res.size()==0)
        {
            return null;
        }
        else
        {
            Vector<String> row = DB_res.get(0);
            String jobRelated = row.get(0);
            String jobRelatedNew = jobRelated.trim();
            if(!jobRelatedNew.equals(""))
            {
                return jobRelatedNew;
            }
            else
            {
                return null;
            }
        }
    }
    
    private List<Job> getJobComp(String jobCompId){
        String sql = String.format("SELECT Fseason_related, Fjob_summary, Ftag_detail FROM t_job_documents_compare where Fauto_id=%s limit 1", jobCompId);
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        List<Job> jobList = new ArrayList<Job>();
        
        if(DB_res.size() > 0)
        {
            Vector<String> row = DB_res.get(0);
            Job job = new Job(row.get(0), row.get(1), row.get(2));
            jobList.add(job);
        }
        return jobList;
    }
    
    private List<Job> getJobTable(String jobSeasonId, String jobRelated, String jumpUrl, int pageNo) {
        String jobRelatedNew = "(" + jobRelated + ")";
        String tableName = "t_job_documents_" + jobSeasonId;
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        int offset = 10 * (pageNo-1);
        String sql = String.format("SELECT Fauto_id, Fjob_name, Fjob_detail, Ftag_detail FROM %s where Fauto_id in %s limit 10 offset %d",tableName, jobRelatedNew, offset);
        
        System.out.println(sql);
        
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        List<Job> jobList = new ArrayList<Job>();
        
        String jobTable = "";
        for(int idx=0; idx < DB_res.size(); idx++)
        {
            Vector<String> row = DB_res.get(idx);
            String jobJumpUrl = jumpUrl + String.format("&jobResId=%s", row.get(0));
            Job jobTmp = new Job(Integer.parseInt(row.get(0)), row.get(1), row.get(2), row.get(3), jobJumpUrl);
            jobList.add(jobTmp);
        }
        
        String sql_count = String.format("SELECT count(Fauto_id) as id FROM %s where Fauto_id in %s",tableName, jobRelatedNew);
        Vector<Vector<String>> DB_res_count = MysqlClientInstance.readFromDB(sql_count);
        Vector<String> row = DB_res_count.get(0);
        jobListLength = Integer.parseInt(row.get(0));
        
        return jobList;
    }
}