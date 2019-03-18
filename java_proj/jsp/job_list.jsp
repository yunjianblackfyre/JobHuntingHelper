<!DOCTYPE html>
<%@ page language="java" import="java.util.*" pageEncoding="utf-8"%>
<html>
    <head>
        <title>大测大悟</title>
        <style type="text/css">
        #longer{height:70px;overflow:auto;word-break: normal;}
        #long{overflow:hidden;word-break: normal;}
        </style>
    </head>
    <body bgcolor="black">
        <h1 align="center"><font size="5" face="Microsoft YaHei" color="red">欢迎来到招聘信息排序算法测试页面</font></h1>
        <h2 align="center"><font size="4" face="Microsoft YaHei" color="red">今天又是操蛋的一天</font></h2>
            <%@ page import="cnblogs.Job" %>
            <%
                //获得集合List<Job>
            out.write("<div align='center'>您提供的样本职位如下</div>");
            out.write("<table border='1' align='center' cellspacing='0'>");
            List<Job> jobCompList = (List<Job>)request.getAttribute("jobCompList");
            if(jobCompList!=null){
                for(Job job : jobCompList){
                    out.write("<tr>");
                    out.write("<td id=long><div id=longer><font size='2' face='Microsoft YaHei' color='red'>"+job.getSummary()+"</font></div></td>");
                    out.write("<td id=long><div id=longer><font size='2' face='Microsoft YaHei' color='red'>"+job.getTagDetail()+"</font></div></td>");
                    out.write("</tr>");
                }
            }
            out.write("</table>");
            
            out.write("<div align='center'>与该职位最相似的职位如下</div>");
            out.write("<table border='1' align='center' cellspacing='0'>");
            List<Job> jobList = (List<Job>)request.getAttribute("jobList");
            if(jobList!=null){
                for(Job job : jobList){
                    out.write("<tr>");
                    out.write("<td><font size='3' face='Microsoft YaHei' color='red'>"+job.getId()+"</font></td>");
                    out.write("<td><font size='3' face='Microsoft YaHei' color='red'>"+job.getTitle()+"</font></td>");
                    out.write("<td id=long><div id=longer><font size='2' face='Microsoft YaHei' color='red'>"+job.getSummary()+"</font></div></td>");
                    out.write("<td id=long><div id=longer><font size='2' face='Microsoft YaHei' color='red'>"+job.getTagDetail()+"</font></div></td>");
                    out.write("<td><a href='" + job.getModeLink() + "'><font size='3' face='Microsoft YaHei' color='red'>点此链接删除异常排列元素</font></a></td>");
                    out.write("</tr>");
                }
            }
            out.write("</table>");
            
            out.write("<div align='center'>");
            
            int pageNo = (int)request.getAttribute("pageNo");
            int jobListLength = (int)request.getAttribute("jobListLength");
            String jobCompId = (String)request.getAttribute("jobCompId");
            
            if(pageNo*10 < jobListLength)
            {
                int nextPage = pageNo + 1;
                String nextPageString = Integer.toString(nextPage);
                String nextUrl = String.format("http://119.28.26.222:8080/SIBYL_SYSTEM/JobCompRes?jobCompId=%s&pageNo=%s",jobCompId, nextPageString);
                out.write("<a href='" + nextUrl + "'><font size='4' face='Microsoft YaHei' color='red'>下一页</a>");
            }
            if(pageNo > 1)
            {
                int previousPage = pageNo - 1;
                String previousPageString = Integer.toString(previousPage);
                String previousUrl = String.format("http://119.28.26.222:8080/SIBYL_SYSTEM/JobCompRes?jobCompId=%s&pageNo=%s",jobCompId, previousPageString);
                out.write("<a href='" + previousUrl + "'><font size='4' face='Microsoft YaHei' color='red'>上一页</a>");
            }
            
            out.write("</div>");
            %>
    </body>
</html>
        
