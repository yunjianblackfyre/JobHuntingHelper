#   AUTHOR: Sibyl System
#     DATE: 2018-04-19
#     DESC: MySQL客户端

import mysql.connector

from ResumeAutometa.Foundations.exception import Exc
from ResumeAutometa.Foundations.utils import StopWatch


ERROR_RECORD_EXISTS = -1012
ERROR_INVALID_PARAM = -1013
ERROR_CONNECT_FAILED = -1014
ERROR_SQL = -1015


class MysqlClient(object):

    def __init__(self, **kwargs):
        self._host = kwargs['host']
        self._port = kwargs['port']
        self._user = kwargs['user']
        self._password = kwargs['password']
        self._connection_timeout = kwargs['connection_timeout']
        self._cnx = None
        self._cursor = None
        self._db = None
        self._table = None
        
        if not isinstance(self._host, str) or \
           not isinstance(self._port, int) or \
           not isinstance(self._user, str) or \
           not isinstance(self._password, str) or \
           not isinstance(self._connection_timeout, int):
            raise Exc(ERROR_INVALID_PARAM, 'invalid param')
        
        self.connect()

    def connect(self):
        data = {
            'host': self._host,
            'port': self._port,
            'user': self._user,
            'password': self._password,
            'connection_timeout': self._connection_timeout,
            'autocommit': False,
            'charset': 'utf8',
            'use_unicode': True,
            'use_pure': True,
            'raw': False
        }
            
        try:
            self._cnx = mysql.connector.connect(**data)
            self._cursor = self._cnx.cursor(buffered=True, dictionary=True)
        except mysql.connector.Error as e:
            raise Exc(e.errno, e.msg)
        
    def destroy(self):
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None
            
        if self._cnx is not None:
            self._cnx.close()
            self._cnx = None
            
    def commit(self):
        self._cnx.commit()

    def rollback(self):
        if self._cnx.is_connected() is False:
            self._cnx.reconnect()
        self._cnx.rollback()

    def escape(self, sql_param):
        return self._cnx.converter.escape(sql_param)
        
    def execute(self, sql, b_many=False, args=None):
        stop_watch = StopWatch()

        if self._cnx.is_connected() is False:
            self._cnx.reconnect()
        try:
            if b_many:
                self._cursor.executemany(sql, args)
            else:
                self._cursor.execute(sql, args)
        except mysql.connector.Error as e:
            raise Exc(e.errno, e.msg)
        except Exception as e:
            raise Exc(-1, e)
            
        delay = stop_watch.get_elapsed_milliseconds()

    def insert(self, val):
        """data: dict or list
        """
        
        data = self.dict2list(val)
        keys = data[0].keys()
        values = []
        for k in data:
            item = []
            for k2 in keys:
                item.append(k[k2])
            values.append(item)
        
        sql = 'insert into %s.%s (%s) values(%s) ' % (
                                self.get_db_name(),
                                self.get_table_name(), 
                                self.convert_list_string(keys),
                                ",".join(['%s'] * len(keys)))
        self.execute(sql, True, values)
        return self._cursor.lastrowid
        
    def update(self, data, where):
        sql = 'update %s.%s set %s where %s' % (
                                self.get_db_name(),
                                self.get_table_name(), 
                                ', '.join(['%s=%s' % (self.escape(k), '%s') for k in data.keys()]),
                                where)
        values = []
        for i in data.values():
            values.append(i)
        
        return self.execute(sql, False, values)
        
    def update_batch(self, field_list, data_list):
        if not isinstance(field_list, list) or not isinstance(data_list, list):
            raise Exc(ERROR_SQL, 'field_list or data_list param is not list or string')
        
        field_eq_str = ', '.join([field + '=values(' + field + ')' for field in field_list])
        data_str = ','.join(data_list)

        sql = 'insert into %s.%s (%s) values %s on duplicate key update %s' % (
                                self.get_db_name(),
                                self.get_table_name(),
                                self.convert_list_string(field_list),
                                data_str,
                                field_eq_str)
        self.execute(sql)

    def query(self, field_list, where, other='', b_distinct=False, log_open=True):

        if not isinstance(field_list, list):
            raise Exc(ERROR_SQL, 'field_list param is not list')
        
        str_distinct = 'distinct' if b_distinct else ''
        sql = 'select %s %s from %s.%s where %s %s' % (
                                    str_distinct, 
                                    self.convert_list_string(field_list),
                                    self.get_db_name(), 
                                    self.get_table_name(),
                                    where,
                                    other)
        self.execute(sql)
        data = self._cursor.fetchall()
        self.commit()
        return data
    
    def set(self, data, where):
        ret = self.query(['*'], where)
        if ret:
            ret = self.update(data, where)
        else:
            ret = self.insert(data)
        return ret
    
    def affected_rows(self):
        return self._cursor.rowcount
    
    def set_db_table(self, db, table):
        self._db = db
        self._table = table

    def get_db_name(self):
        return self._db

    def get_table_name(self):
        return self._table
    
    def dict2list(self, val):
        if isinstance(val, dict):
            return [val]
        return val
    
    def convert_list_string(self, val):
        if isinstance(val, list):
            data = val
        else:
            data = list(val)
        return ','.join(map(self.escape, data))


if __name__ == '__main__':
    import time
    
    config = {
        'host': '119.28.26.222',
        'port': 3306,
        'user': 'root',
        'password': 'worinimamaipi_caonimabi23333_yunjianblackfyre1815',
        'connection_timeout': 5000
    }
    db = MysqlClient(**config)
    
    # insert
    data = {
        'Ftitle': '软件工程师',
        'Fh5_url': 'https://www.ff.com',
        'Fcontent': '杀了一个程序猿祭天',
        'Fcreate_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'Fmodify_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'Flstate': 0
    }
    db.set_db_table('db_crawlers', 't_csdn_detail')
    '''
    data_list = [
        "('机器学习', 1, 0.5, '2016-09-30 10:12:31', '2017-09-30 10:12:31')",
        "('数据挖掘', 2, 0.4, '2016-09-30 10:12:31', '2017-09-30 10:12:31')",
        "('大数据', 3, 0.3, '2016-09-30 10:12:31', '2017-09-30 10:12:31')"
    ]
    field_list = ['Fword','Fdoc_id','Fweight','Fcreate_time','Fmodify_time']
    db.update_batch(field_list, data_list)
    '''
    db.insert(data)
    db.commit()
    
    '''
    #query
    db.set_db_table('d_wyp', 't_stat')
    field_list = ['Fname', 'Fsex', 'Fage']
    where = "1=1"
    d = db.query(field_list, where)
    print(d)
    '''
    
    # update
    '''
    db.set_db_table('d_wyp', 't_stat')
    data = {'Fage' : 18}
    where = "Fname='eugenechen'"
    db.update(data, where)
    db.commit()
    '''
    
    db.destroy()
