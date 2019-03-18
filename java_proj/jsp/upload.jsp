<!DOCTYPE html>
<%@ page language="java" pageEncoding="utf-8"%>
<html>
    <head>
        <meta charset="utf-8">
        <title>大测大悟</title>
    </head>
<body bgcolor='black'>
    <h1 align='center'><font size='5' face='Microsoft YaHei' color='red'>欢迎来到招聘信息排序算法测试页面</font></h1>
    <h2 align='center'><font size='3' face='Microsoft YaHei' color='red'>请随便找个招聘信息传上来哦！如果你敢注入SQL，我一定会杀了你</font></h2>
    <div align='center'>
        <form action="JobUpload" method="POST">
            <font size='4' face='Microsoft YaHei' color='red'>
            请输入招聘信息：<textarea style="width:300px;height:100px;" name="detail"></textarea>
            <input type="submit" value="提交"/>
        </form>
    </div>
</body>
</html>

