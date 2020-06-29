import cx_Oracle

#Connect to Database
#connstr = cx_Oracle.connect("user/password@server/ServiceName")
connstr = "admin/admin123@dbconta.c82paqlf0zlv.us-east-1.rds.amazonaws.com:1521/dbconta"
try:
    conn = cx_Oracle.connect(connstr)
except Exception as e:
    print("No se pudo conectar a la bd. Error: "+str(e))
else:
    print("Conexion establecida lista para trabajar")
    cnx = True
    conn.close()

def getConn():
    if cnx == True:
        conn = cx_Oracle.connect(connstr)
        return conn
    return


