<!DOCTYPE html>
<%@ page language="java" pageEncoding="utf-8"%>
<html>
    <head>
        <meta charset="utf-8">
        <title>大测大悟</title>
    </head>
<body bgcolor='black'>
    <h1 align='center'><font size='5' face='Microsoft YaHei' color='red'>欢迎来到招聘信息排序算法测试页面</font></h1>
    <h2 align='center'><font size='3' face='Microsoft YaHei' color='red'>您的样本已提交，请点击下面链接</font></h2>
    <div align='center'>
    <%@ page import="cnblogs.Job" %>
    <%
        String jumpUrl = (String)request.getAttribute("jumpUrl");
        out.write("<a href='" + jumpUrl + "'><font size='4' face='Microsoft YaHei' color='red'>倍儿爽 嘿嘿嘿</a>");
    %>
    </div>
</body>
</html>