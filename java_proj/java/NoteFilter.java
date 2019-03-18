package cnblogs;
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;
import java.util.*;

public class NoteFilter implements Filter {
    private String blackList = null;
    private String ipblock = null;
    private FilterConfig config = null;
    
    public void init(FilterConfig config) throws ServletException {
        System.out.println("NoteFilter: init()");
        this.config = config;
        
        ipblock = config.getInitParameter("ipblock");
        blackList = config.getInitParameter("blackList");
    }
    
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
        throws IOException, ServletException{
        System.out.println("NoteFilter: doFilter()");
        if(!checkCookie(request, response))return;
            
        chain.doFilter(request, response);
    }
    
    public boolean checkCookie(ServletRequest request, ServletResponse response)
        throws ServletException, IOException{
        HttpServletRequest httpRequest = (HttpServletRequest)request;
        
        Cookie cookie = null;
        Cookie[] cookies = null;
        
        cookies = httpRequest.getCookies();
        
        if (cookies!= null){
            boolean isUserQualified = false;
            String correctPassWord = Util.getPassWord();
            String passWordComplex = Util.genPassWordComplex(correctPassWord);
            for (int i = 0; i < cookies.length; i++)
            {             
                cookie = cookies[i];
                if(cookie.getName().equals("pass_word"))
                {
                    if(cookie.getValue().equals(passWordComplex))
                    {
                        isUserQualified = true;
                        break;
                    }
                }
            }
            if(isUserQualified)
            {
                return true;
            }
            else
            {
                response.setContentType("text/html;charset=UTF-8");
                PrintWriter out = response.getWriter();
                out.println("<h1>抱歉，我不认识你，请滚</h1>");
                out.flush();
                return false;
            }
        } 
        else{
            return true;
        }
    }
    
    public void destroy(){
        System.out.println("NoteFilter: destroy()");
        config = null;
    }
}