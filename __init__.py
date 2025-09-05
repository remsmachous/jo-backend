try:
    import pymysql  
    pymysql.install_as_MySQLdb()
except Exception:
    # En prod, mysqlclient ; en local si PyMySQL absent on ignore.
    pass
