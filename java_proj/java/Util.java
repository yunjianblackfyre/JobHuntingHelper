package cnblogs;

import java.time.*;
import java.util.*;
import java.lang.NumberFormatException;
import java.text.SimpleDateFormat;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.xml.bind.DatatypeConverter;

public class Util 
{
    public static int genPageNo(String pageNoString){
        int pageNo = 1;
        try{
            pageNo = Integer.parseInt(pageNoString);
        }catch(NumberFormatException nfe){
            nfe.printStackTrace(); 
        }finally{
            if(pageNo <= 1 || pageNo > 20)
            {
                pageNo = 1;
            }
            
        }
        return pageNo;
    }
    
    public static int getCurrentSeason(){
        Date date = new Date();
        LocalDate localDate = date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
        int month = localDate.getMonthValue();
        int season = month/3;
        return season;
    }
    
    public static String getCurrentDate(){
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd"); // 完整的时间格式为yyyy-MM-dd HH:mm:ss.SSS
        Date now = new Date();
        String strDate = sdf.format(now);
        return strDate;
    }
    
    public static String getCurrentHour(){
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH"); // 完整的时间格式为yyyy-MM-dd HH:mm:ss.SSS
        Date now = new Date();
        String strDate = sdf.format(now);
        return strDate;
    }
    
    public static String getPassWord(){
        String passWord = "laputa123456";
        return passWord;
    }
    
    public static boolean checkRequestIntParam(String param){    // 检测整形输入参数是否合格
        boolean result = false;
        if(param==null)
        {
            result = false;
        }
        else{
            try{
                int paramInt = Integer.parseInt(param);
                result = true;
            }catch(NumberFormatException nfe){
                nfe.printStackTrace(); 
                result = false;
            }finally{
                // do nothing
            }
        }
        return result;
    }
    
    public static String genPassWordComplex(String passWord){
        String hashEncodePassWord = "FFFFFFFFFFFFFFFF";
        try{
            String passWordComplex = passWord + Util.getCurrentHour();
            System.out.println(passWordComplex);
            MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(passWordComplex.getBytes());
            byte[] digest = md.digest();
            hashEncodePassWord = DatatypeConverter.printHexBinary(digest).toUpperCase();
        }catch(NoSuchAlgorithmException ale){
            ale.printStackTrace();
        }catch(Exception e){
            e.printStackTrace();
        }finally{
            // System.out.println("Do nothing!");
        }
        return hashEncodePassWord;
    }
    
    
    public static void main(String[] args){
        Util.getCurrentSeason();
    }
}