package cnblogs;

import java.util.*;
import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

/**
 * Servlet implementation class JobGateway
 */
@WebServlet("/JobGateway")
public class JobGateway extends HttpServlet {
    private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public JobGateway() {
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

        // 获取密码
        if(request.getParameter("password")==null)
        {
            request.getRequestDispatcher("/refuse.jsp").forward(request, response);
            return;
        }
        
        String passWord = new String(request.getParameter("password").getBytes("ISO8859-1"),"UTF-8");
        String correctPassWord = Util.getPassWord();
        if(passWord.equals(correctPassWord))
        {
            String passWordComplex = Util.genPassWordComplex(passWord);
            Cookie ckPassWord = new Cookie("pass_word", passWordComplex); // 最好将密码进行编码
            response.addCookie( ckPassWord );
            request.getRequestDispatcher("/upload.jsp").forward(request, response);
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
}
