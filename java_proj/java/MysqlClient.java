package cnblogs;
 
import java.sql.*;
import java.util.*;
 
public class MysqlClient {
    // static final String JDBC_DRIVER = "com.mysql.jdbc.Driver";
    Statement stmt = null;
    Connection conn = null;
    String UserName;
    String PassWord;
    String DB_URL;
    
    // 初始化Mysql客户端，需要用户名，密码以及DB
    public MysqlClient(String USER, String PASS, String URL) {
        UserName = USER;
        PassWord = PASS;
        DB_URL = URL;
        
        try{
            Class.forName("com.mysql.jdbc.Driver");
            System.out.println("Connecting to Mysql Server......");
            conn = DriverManager.getConnection(DB_URL,UserName,PassWord);
            stmt = conn.createStatement();
        }catch(SQLException se){
            se.printStackTrace();
        }catch(Exception e){
            // 处理 Class.forName 错误
            e.printStackTrace();
        }finally{
            // System.out.println("Do nothing!");
        }
    }
    
    public Vector<Vector<String>> readFromDB(String SQL){
        Vector<Vector<String>> ret_list = new Vector<Vector<String>>();
        try{
            ResultSet rs = stmt.executeQuery(SQL);
            ResultSetMetaData rsmd = rs.getMetaData();
            int columnsNumber = rsmd.getColumnCount();
            // 展开结果集数据库
            while(rs.next()){
                // 通过字段检索
                Vector<String> row = new Vector<String>();
                for(int i=1; i <= columnsNumber; i++)
                {
                    String stringElement = rs.getString(i);
                    row.add(stringElement);
                }
                ret_list.add(row);
            }
            rs.close();
            // conn.close();
            // stmt.close();
        }catch(SQLException se){
            // 处理 JDBC 错误
            se.printStackTrace();
        }catch(Exception e){
            // 处理 Class.forName 错误
            e.printStackTrace();
        }finally{
            // 关闭你个鸡儿
            // System.out.println("Do nothing!");
        }
        System.out.println("Goodbye!");
        return ret_list;
    }
    
    public void updateToDB(String SQL){
        try{
            String sql = SQL;
            stmt.executeUpdate(sql);
            stmt.close();
            
        } catch (SQLException e) {
            e.printStackTrace();
        }catch(Exception e){
            // 处理 Class.forName 错误
            e.printStackTrace();
        }finally{
            // 关闭你个鸡儿
            // System.out.println("Do nothing!");
        }
    }
    
    public void insertJob(Job J){
        try{
            String sql = "insert into t_job_documents_compare(Fauto_id, Fjob_summary, Ftag_detail, Fjob_related)values(?,?,?,?)";
            PreparedStatement ps = conn.prepareStatement(sql); // prepareStatement有escape的作用
            //设置占位符对应的值
            ps.setInt(1, J.getId());
            ps.setString(2, J.getSummary());
            ps.setString(3, J.getTagDetail());
            ps.setString(4, J.getJobRelated());
            
            ps.executeUpdate();
            ps.close();
            
        } catch (SQLException e) {
            e.printStackTrace();
        }catch(Exception e){
            // 处理 Class.forName 错误
            e.printStackTrace();
        }finally{
            // 关闭你个鸡儿
            // System.out.println("Do nothing!");
        }
    }
    
    public static void main(String[] args) {
        String DB_URL = "jdbc:mysql://localhost:3306/db_documents";
        String USER = "root";
        String PASS = "worinimamaipi_caonimabi23333_yunjianblackfyre1815";
        MysqlClient MysqlClientInstance = new MysqlClient(USER, PASS, DB_URL);
        String sql = "SELECT Fauto_id, Fjob_name, Fjob_url FROM t_job_documents_2 limit 10";
        Vector<Vector<String>> DB_res = MysqlClientInstance.readFromDB(sql);
        
        for(int idx=0; idx < DB_res.size(); idx++)
        {
            Vector<String> row = DB_res.get(idx);
            System.out.print("ID: " + row.get(0));
            System.out.print(", JOB名称: " + row.get(1));
            System.out.print(", JOBURL: " + row.get(2));
            System.out.print("\n");
        }

    }
}