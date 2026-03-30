
try:
    import pymysql
except ImportError:
    # Local installations may use mysqlclient instead.
    pass
else:
    pymysql.install_as_MySQLdb()
