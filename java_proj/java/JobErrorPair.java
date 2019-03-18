package cnblogs;

import java.util.*;
import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class JobErrorPair
 */
@WebServlet("/JobErrorPair")
public class JobErrorPair extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private int pairListLength = 0;
    List<Job> jobResList = null;
    List<Job> jobCompList = null;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public JobErrorPair() {
        super();
        // TODO Auto-generated constructor stub
        jobResList = new ArrayList<Job>();
        jobCompList = new ArrayList<Job>();
    }

    /**
     * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
     */
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        // 设置响应内容类型
        // response.setContentType("text/html;charset=UTF-8");
        response.setCharacterEncoding("UTF-8");
        
        // 将JOB列表传给JSP
        String pageNoString = "1";
        if(Util.checkRequestIntParam(request.getParameter("pageNo")))
        {
            pageNoString = new String(request.getParameter("pageNo").getBytes("ISO8859-1"),"UTF-8");
        }
        
        int pageNo = Util.genPageNo(pageNoString);
        getErrorPairList(pageNo);
        
        if(jobCompList.size()==0)
        {
            request.getRequestDispatcher("/empty.jsp").forward(request, response);
        }
        else
        {
            request.setAttribute("pageNo", pageNo);
            
            request.setAttribute("pairListLength", pairListLength);
            request.setAttribute("jobCompList", jobCompList);
            request.setAttribute("jobResList", jobResList);
            // System.out.println(pageNo);
            // System.out.println(pairListLength);
            request.getRequestDispatcher("/error_pair_list.jsp").forward(request, response);
        }
        
    }
    
    // 处理 POST 方法请求的方法
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doGet(request, response);
    }
    
    private void getErrorPairList(int pageNo) {
        String DB_URL = "jdbc:mysql://localhost:3306/db_documents";
        String USER = "root";
        String PASS = "worinimamaipi_caonimabi23333_yunjianblackfyre1815";
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        int offset = 10 * (pageNo-1);
        String sql = String.format("SELECT Fjob_comp_id, Fjob_res_id, Fseason_id FROM t_job_error_pair order by Fcreate_time limit 10 offset %d", offset);
        
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);

        
        for(int idx=0; idx < DB_res.size(); idx++)
        {
            Vector<String> row = DB_res.get(idx);
            String jobCompId = row.get(0);
            String jobResId = row.get(1);
            String seasonId = row.get(2);
            String resTableName = "t_job_documents_" + seasonId;
            String compTableName = "t_job_documents_compare";
            String sql_res = String.format("SELECT Fauto_id, Fjob_name, Fjob_detail FROM %s where Fauto_id=%s limit 1", resTableName);
            String sql_comp = String.format("SELECT Fauto_id, Fjob_name, Fjob_detail FROM %s where Fauto_id=%s limit 1", compTableName);
            Vector<Vector<String>> DB_res_job_res = MysqlClientInstance.readFromDB(sql_res);
            Vector<Vector<String>> DB_res_job_comp = MysqlClientInstance.readFromDB(sql_comp);
            
            if (DB_res_job_comp.size()!=0)
            {
                Vector<String> row_comp = DB_res_job_comp.get(0);
                Job jobTmp = new Job(Integer.parseInt(row_comp.get(0)), row_comp.get(1), row_comp.get(2));
                jobCompList.add(jobTmp);
            }
            else
            {
                Job jobTmp = new Job(Integer.parseInt(jobCompId), "", "");
                jobCompList.add(jobTmp);
            }
            
            if (DB_res_job_res.size()!=0)
            {
                Vector<String> row_res = DB_res_job_res.get(0);
                Job jobTmp = new Job(Integer.parseInt(row_res.get(0)), row_res.get(1), row_res.get(2));
                jobResList.add(jobTmp);
            }
            else
            {
                Job jobTmp = new Job(Integer.parseInt(jobResId), "", "");
                jobResList.add(jobTmp);
            }
        }
        
        String sql_count = String.format("SELECT count(Fauto_id) as id FROM t_job_error_pair order by Fcreate_time limit 10 offset %d", offset);
        Vector<Vector<String>> DB_res_count = MysqlClientInstance.readFromDB(sql_count);
        Vector<String> row = DB_res_count.get(0);
        pairListLength = Integer.parseInt(row.get(0));
    }
}