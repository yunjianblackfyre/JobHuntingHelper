package cnblogs;

import java.util.*;
import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class JobMode
 */
@WebServlet("/JobMode")
public class JobMode extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private String currentSeason = "0";
    private String DB_URL = "jdbc:mysql://localhost:3306/db_documents";
    private String USER = "root";
    private String PASS = "worinimamaipi_caonimabi23333_yunjianblackfyre1815";
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public JobMode() {
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
        
        // 删除与样本JOB关联的某个资源JOB
        // if( request.getParameter("jobCompId")!=null && request.getParameter("jobResId")!=null )
        if(Util.checkRequestIntParam(request.getParameter("jobCompId")) &&
           Util.checkRequestIntParam(request.getParameter("jobResId")) &&
           Util.checkRequestIntParam(request.getParameter("jobSeasonId")))
        {
            String jobCompId = new String(request.getParameter("jobCompId").getBytes("ISO8859-1"),"UTF-8");
            String jobResId = new String(request.getParameter("jobResId").getBytes("ISO8859-1"),"UTF-8");
            String jobSeasonId = new String(request.getParameter("jobSeasonId").getBytes("ISO8859-1"),"UTF-8");
            
            String jobRelated = getJobRelated(jobCompId);
            if(jobRelated!=null)    // 必须有样本JOB，否则返回错误
            {
                String jobRelatedReconstruct = jobRelatedReconstruct(jobResId, jobRelated);
                if(jobRelatedReconstruct.equals(""))
                {
                    // 关系列表为空，告知用户
                    removeResFromComp(jobCompId, jobRelatedReconstruct);
                    insertErrorPair(jobSeasonId, jobCompId, jobResId);
                    request.getRequestDispatcher("/empty.jsp").forward(request, response);
                }
                else
                {
                    // 转发给列表页
                    if(qualifiedForRemoval(jobCompId, jobResId))
                    {
                        removeResFromComp(jobCompId, jobRelatedReconstruct);
                        insertErrorPair(jobSeasonId, jobCompId, jobResId);
                    }
                    request.getRequestDispatcher("/JobCompRes").forward(request, response);
                }
            }
            else
            {
                // 此请求未走标准程序，输出警告
                request.getRequestDispatcher("/warning.jsp").forward(request, response);
            }
        }
        else
        {
            // 没有提供资源JOB参数，输出拒绝
            request.getRequestDispatcher("/refuse.jsp").forward(request, response);
        }
        
    }
    
    // 处理 POST 方法请求的方法
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doGet(request, response);
    }
    
    private String jobRelatedReconstruct(String jobResId, String jobRelated){
        String jobRelatedReconstruct = "";
        for(String retval:jobRelated.split(",")){
            if(!jobResId.equals(retval))
            {
                jobRelatedReconstruct = jobRelatedReconstruct + "," + retval;
            }
        }
        
        jobRelatedReconstruct = jobRelatedReconstruct.replaceAll(",+$", "").replaceAll("^,+","");
        return jobRelatedReconstruct;
    }
    
    // 检查jobCompId，jobResId，以及两者组合是否存在
    private boolean qualifiedForRemoval(String jobCompId, String jobResId){
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        
        
        String sql_count = String.format("SELECT count(Fauto_id) as id FROM t_job_documents_compare where Fauto_id = %s", jobCompId);
        Vector<Vector<String>> DB_res_count = MysqlClientInstance.readFromDB(sql_count);
        Vector<String> row = DB_res_count.get(0);
        int jobCompCount = Integer.parseInt(row.get(0));
        if(jobCompCount==0)
        {
            return false;
        }
        
        String tableName = "t_job_documents_" + currentSeason;
        sql_count = String.format("SELECT count(Fauto_id) as id FROM %s where Fauto_id = %s", tableName, jobResId);
        DB_res_count = MysqlClientInstance.readFromDB(sql_count);
        row = DB_res_count.get(0);
        int jobResCount = Integer.parseInt(row.get(0));
        if(jobResCount==0)
        {
            return false;
        }
        
        sql_count = String.format("SELECT count(Fauto_id) as id FROM t_job_error_pair where Fjob_comp_id=%s and Fjob_res_id=%s", jobCompId, jobResId);
        DB_res_count = MysqlClientInstance.readFromDB(sql_count);
        row = DB_res_count.get(0);
        int jobGroupCount = Integer.parseInt(row.get(0));
        if(jobGroupCount==0)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    
    private void removeResFromComp(String jobCompId, String jobRelatedReconstruct) {
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        String sql = String.format("update t_job_documents_compare set Fjob_related='%s' where Fauto_id=%s limit 1", jobRelatedReconstruct, jobCompId);
        MysqlClientInstance.updateToDB(sql);
    }
    
    private void insertErrorPair(String jobSeasonId, String jobCompId, String jobResId) {
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        
        int season = Util.getCurrentSeason();
        String sql = String.format("insert into t_job_error_pair (Fjob_comp_id, Fjob_res_id, Fseason_id) values (%s, %s, %s)", jobCompId, jobResId, jobSeasonId);
        MysqlClientInstance.updateToDB(sql);
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

}