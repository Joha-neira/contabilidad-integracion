from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_login import LoginManager
from conexionbd import getConn, cx_Oracle
from models import Venta
import requests
import boto3
import hashlib,hmac,base64
import json

app = Flask(__name__)
# app config 
# login_manager = LoginManager()
# login_manager.init_app(app)
# SECURITY_ENDPOINT = 'https://oawjeg21mb.execute-api.us-east-1.amazonaws.com/contabilidad'
USER_POOL_ID = 'us-east-1_NviZ9gz7U'
CLIENT_ID = '590svotmugpjsu58ljllft8bf3'
CLIENT_SECRET = 'n969na2slpnqkcnci5k5am3saf8k84bgq5aemnod5lkela36uis'

app.config['JSON_SORT_KEYS'] = False
app.secret_key = '_5#y2L"F4Q8z]/'

client = boto3.client('cognito-idp')

#probando primer endpoint
@app.route('/hola')
def holaMundo():
    return jsonify({"message": "Holi"})


#prueba objeto venta
venta1 = Venta(4123,'18841584-9','18/05/1994',339000,'factura.pdf',11)


#obtener id boleta desde la base de datos
@app.route('/get-id-boleta',methods=['GET'])
def getIdBoleta():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT last_number FROM user_sequences where sequence_name='BOLETA_SEQ'")
    result = crs.fetchall()
    idBoleta = result[0][0]
    conn.close()
    return jsonify({'idBoleta': idBoleta})

#obtener id Orden de compra desde la BD
@app.route('/get-id-orden-compra')
def getIdOrdenCompra():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT last_number FROM user_sequences where sequence_name='ORDENCOMPRA_SEQ'")
    result = crs.fetchall()
    idOrdenCompra = result[0][0]
    conn.close()
    return jsonify({'idOrdenCompra': idOrdenCompra})

#obtener id operacion de compra desde la BD
@app.route('/get-id-compra')
def getIdCompra():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT last_number FROM user_sequences where sequence_name='COMPRA_SEQ'")
    result = crs.fetchall()
    idCompra = result[0][0]
    conn.close()
    return jsonify({'idOperacionCompra': idCompra})

#obtener id Nota de credito desde la BD
@app.route('/get-id-nota-credito')
def getIdNotaCredito():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT last_number FROM user_sequences where sequence_name='NOTACREDITO_SEQ'")
    result = crs.fetchall()
    conn.close()
    return jsonify({'idNotaCredito': result})

#obtener boletas para enviar a postventas y hacer reversos
@app.route('/get-boletas')
def getBoletas():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT nroboleta, rutcliente, to_char(fecha,'dd/mm/yyyy'), totalneto, idtipopago FROM ventas")
    result = crs.fetchall()
    boletas= {}
    for boleta in result:
        if result[0][4] == 101:
            tipoPago = "Efectivo"
        else:
            tipoPago = "Transferencia"
        crs.execute("SELECT idproducto, cantidad FROM detalleventa where nroboleta=:nroboleta",nroboleta=boleta[0])
        detalles=crs.fetchall()
        details=[]
        for detalle in detalles:
            dict={
                "idProducto": detalle[0],
                "cantidad": detalle[1]
            }
            detail = dict
            details.append(detail)
        dict = {
        "idBoleta": boleta[0],
        "rutCliente": boleta[1],
        "fecha": boleta[2],
        "totalNeto": boleta[3],
        "tipoPago":tipoPago,
        "detalleVenta": details
        }
        string = 'boleta '+str(boleta[0])
        boletas[string] = dict
    return jsonify({'results':boletas})


#obtener boleta unica con su id como parametro
@app.route('/get-boleta/<int:idBoleta>')
def getBoleta(idBoleta):
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT * FROM ventas WHERE nroboleta = :filtro", filtro = idBoleta)
    result = crs.fetchall()
    if result[0][4] == 101:
        tipoPago = "Efectivo"
    else:
        tipoPago = "Transferencia"
    #corregir serializacion de objeto BLOB
    boleta = {
        "idBoleta": result[0][0],
        "rutCliente": result[0][1],
        "fecha": result[0][2],
        "totalNeto": result[0][3],
        "tipoPago":tipoPago,
        "documento":'boleta'+str(result[0][0])+'.pdf'
    }
    return jsonify({'result':boleta})

#registrar nueva boleta en BD
@app.route('/agregar-boleta', methods=['POST'])
def addBoleta():
    conn=getConn()
    crs = conn.cursor()
#    nuevaVenta = Venta(request.json['boleta'],request.json['rutCliente'],request.json['fecha'],request.json['totalNeto'],"",request.json['tipoPago'])
    nroBoleta= request.json['boleta']
    rutcliente = request.json['rutCliente'] 
    fecha = request.json['fecha']
    totalneto = request.json['totalNeto'] 
    idtipopago  = request.json['tipoPago']
    #probar idtipo pago con 101 y 201
    detalleBoleta = request.json['detalleBoleta']
    sql = """INSERT INTO ventas (nroboleta,rutcliente,fecha,totalneto,idtipopago)
          VALUES (boleta_seq.nextval,:rutcliente,TO_DATE(:fecha,'YYYY-MM-DD'),:totalneto,:idtipopago)"""
    crs.execute(sql,[rutcliente,fecha,totalneto,idtipopago])
    for detalle in detalleBoleta:
        sql = """INSERT INTO detalleventa (idProducto,cantidad,nroboleta)
          VALUES (:idProducto,:cantidad,BOLETA_SEQ.currval)"""
        crs.execute(sql,[detalle['idProducto'],detalle['cantidad']])
    conn.commit()
    conn.close()
    return jsonify({"message": "Boleta registrada correctamente"})

#registrar nueva orden de compra en BD
@app.route('/agregar-orden-compra', methods=['POST'])
def addOrdenCompra():
    conn=getConn()
    crs = conn.cursor()
    nroOc = request.json['nroOrdenCompra']
    rutProveedor = request.json['rutProveedor']
    fecha = request.json['fecha']
    totalNeto = request.json['totalNeto']
    codTrabajador = request.json['codTrabajador']
    detalleOrden = request.json['detalleOrden']
    sql = """INSERT INTO ordenescompra (nrooc,rutproveedor,fecha,totalneto,codtrabajador)
          VALUES (ordencompra_seq.nextval,:rutproveedor,TO_DATE(:fecha,'YYYY-MM-DD'),:totalNeto,:codtrabajador)"""
    crs.execute(sql,[rutProveedor,fecha,totalNeto,codTrabajador])
    for detalle in detalleOrden:
        sql = """INSERT INTO detalleoc (idProducto,cantidad,nroOc)
          VALUES (:idProducto,:cantidad,ordencompra_seq.currval)"""
        crs.execute(sql,[detalle['idProducto'],detalle['cantidad']])
    conn.commit()
    conn.close()
    return jsonify({"message": "Orden de compra registrada correctamente"})

#registrar nueva nota de credito en BD
@app.route('/agregar-nota-credito', methods=['POST'])
def addNotaCredito():
    conn=getConn()
    crs = conn.cursor()
    nroNc = request.json['nroNotaCredito']
    rutCliente = request.json['rutCliente']
    fecha = request.json['fecha']
    totalNeto = request.json['totalNeto']
    nroBoleta = request.json['nroBoleta']
    detalleReverso = request.json['detalleReverso']
    sql = """INSERT INTO reversos (nroNc,rutCliente,fecha,totalNeto,nroBoleta)
          VALUES (notacredito_seq.nextval,:rutCliente,TO_DATE(:fecha,'YYYY-MM-DD'),:totalNeto,:nroBoleta)"""
    crs.execute(sql,[rutCliente,fecha,totalNeto,nroBoleta])
    conn.commit()
    for i in range(len(detalleReverso)):
        idProducto = detalleReverso[i]['idProducto']
        cantidad = detalleReverso[i]['cantidad']
        motivo = detalleReverso[i]['motivo']
        sql = """INSERT INTO detallereverso (idProducto,cantidad,motivo,nroNc)
          VALUES (:idProducto,:cantidad,:motivo,notacredito_seq.currval)"""
        crs.execute(sql,[idProducto,cantidad,motivo])
    conn.commit()
    conn.close()
    return jsonify({"message": "Nota de Credito registrada correctamente"})
    

#registrar nueva compra en BD
@app.route('/agregar-compra', methods=['POST'])
def addCompra():
    conn=getConn()
    crs = conn.cursor()
    nroOperacion = request.json['nroOperacion']
    nroFactura = request.json['nroFactura']
    rutProveedor = request.json['rutProveedor']
    fecha = request.json['fecha']
    totalNeto = request.json['totalNeto']
    codTrabajador = request.json['codTrabajador']
    nroOrdenCompra = request.json['nroOrdenCompra']
    idDepartamento = request.json['idDepartamento']
    detalleCompra = request.json['detalleCompra']
    sql = """INSERT INTO compras (nrooperacion,nrofactura,rutproveedor,fecha,totalneto,codtrabajador,nrooc,iddepartamento)
          VALUES (compra_seq.nextval,:nrofactura,:rutproveedor,TO_DATE(:fecha,'YYYY-MM-DD'),:totalNeto,:codtrabajador,:nrooc,:iddepartamento)"""
    crs.execute(sql,[nroFactura,rutProveedor,fecha,totalNeto,codTrabajador,nroOrdenCompra,idDepartamento])
    print(idDepartamento)
    for detalle in detalleCompra:
        sql = """INSERT INTO detallecompra (idProducto,cantidad,nrooperacion)
          VALUES (:idProducto,:cantidad,compra_seq.currval)"""
        crs.execute(sql,[detalle['idProducto'],detalle['cantidad']])
    conn.commit()
    conn.close()
    return jsonify({"message": "Compra registrada correctamente"})

@app.route('/get-ordenes-compra')
def getOrdenesCompra():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT nrooc, rutproveedor, to_char(fecha,'dd/mm/yyyy'), totalneto, codtrabajador FROM ordenescompra order by nrooc")
    result = crs.fetchall()
    ordenesCompra = {}
    for oc in result:
        crs.execute("SELECT idproducto, cantidad FROM detalleoc where nrooc=:nrooc",nrooc=oc[0])
        detalles=crs.fetchall()
        details=[]
        for detalle in detalles:
            dict={
                "idProducto": detalle[0],
                "cantidad": detalle[1]
            }
            detail = dict
            details.append(detail)
        dict = {
        "nroOrdenCompra": oc[0],
        "rutProveedor": oc[1],
        "fecha": oc[2],
        "totalNeto": oc[3],
        "codTrabajador":oc[4],
        "detalleOrdenCompra": details
        }
        string = 'ordenCompra '+str(oc[0])
        ordenesCompra[string] = dict
    return jsonify({"results":ordenesCompra})

@app.route('/get-notas-credito')
def getNotasCredito():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT nronc, rutcliente, to_char(fecha,'dd/mm/yyyy'), totalneto, nroboleta FROM reversos order by nronc")
    result = crs.fetchall()
    notasCredito = {}
    for nc in result:
        crs.execute("SELECT idproducto, cantidad, motivo FROM detallereverso where nronc=:nronc",nronc=nc[0])
        detalles=crs.fetchall()
        details=[]
        for detalle in detalles:
            dict={
                "idProducto": detalle[0],
                "cantidad": detalle[1],
                "motivo": detalle[2]
            }
            detail = dict
            details.append(detail)
        dict = {
        "nroNotaCredito": nc[0],
        "rutCliente": nc[1],
        "fecha": nc[2],
        "totalNeto": nc[3],
        "nroBoleta":nc[4],
        "detalleNotaCredito": details
        }
        string = 'notaCredito '+str(nc[0])
        notasCredito[string] = dict
    return jsonify({"results":notasCredito})

@app.route('/get-gastos')
def getGastos():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("""SELECT nrooperacion, nrofactura, rutproveedor, to_char(fecha,'dd/mm/yyyy'), 
    totalneto, codtrabajador, nrooc, documento, iddepartamento FROM compras""")
    result = crs.fetchall()
    gastos = {}
    for gasto in result:
        if gasto[8] == 101:
            deptoTrabajador = "adquisiciones"
        else:
            deptoTrabajador = "creacion de productos"
        # tener en cosideracion mas adelante integrar el documento
        crs.execute("SELECT idproducto, cantidad FROM detallecompra where nrooperacion=:nrooperacion",nrooperacion=gasto[0])
        detalles=crs.fetchall()
        details=[]
        for detalle in detalles:
            dict={
                "idProducto": detalle[0],
                "cantidad": detalle[1]
            }
            detail = dict
            details.append(detail)
        dict = {
        "nroOperacion": gasto[0],
        "nroFactura": gasto[1],
        "rutProveedor": gasto[2],
        "fecha": gasto[3],
        "totalNeto": gasto[4],
        "codTrabajador":gasto[5],
        "nroOrdenCompra": gasto[6],
        "departamento": deptoTrabajador,
        "detalleCompra": details
        }
        string = 'Operacion '+str(gasto[0])
        gastos[string] = dict
    return jsonify({'results': gastos})


@app.route('/get-balances-mensuales-ventas')
def getBalancesVentasMensuales():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("""select to_char(fecha,'mm/yyyy'), sum(totalneto), sum(d.cantidad)
    from ventas v join detalleventa d
    on v.nroboleta=d.nroboleta
    group by to_char(fecha,'mm/yyyy')
    """)
    result = crs.fetchall()
    return jsonify({'results':result})


# rutas de templates
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        global client
        if client == None:
            client = boto3.client('cognito-idp')
        resp, msg = initiate_auth(username, password)
    
        if msg != None:
            res_auth = {'message': msg, 
                "error": True, "success": False, "data": None}
            flash('Nombre de usuario y/o contraseña incorrectos')
            return redirect(url_for('login'))
        
        if resp.get("AuthenticationResult"):
            res_auth = {'message': "success", 
                    "error": False, 
                    "success": True, 
                    "data": {
                    "id_token": resp["AuthenticationResult"]["IdToken"],
                    "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                    "access_token": resp["AuthenticationResult"]["AccessToken"],
                    "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                    "token_type": resp["AuthenticationResult"]["TokenType"]
                    }}
            session['username'] = username
            return redirect(url_for('home'))
        else: #this code block is relevant only when MFA is enabled
            res_auth = {"error": True, 
                    "success": False, 
                    "data": None, "message": None}
            flash('Nombre de usuario y/o contraseña incorrectos')
            return render_template('login.html')
            # session['username'] = request.form['username']
        # return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/iniciar-sesion', methods=['POST'])
def iniciarSesion():
    return redirect(url_for('home'))

@app.route('/')
def home():
    if 'username' in session:
        usuario = session['username']
        return render_template('index.html', nombreUsuario = usuario)
    flash("Debes iniciar sesion para acceder")
    return redirect(url_for('login'))

@app.route('/libro-diario')
def libroDiario():
    if 'username' in session:
        conn=getConn()
        crs = conn.cursor()
        crs.execute("""SELECT l.nroasiento, to_char(l.fecha,'dd/mm/yyyy'), l.glosa, t.descripcion, 
        nvl(l.nrooperacion,0), nvl(l.nronc,0), nvl(l.nroboleta,0) FROM librodiario l join tipooperacion t on l.idtipooperacion=t.idtipooperacion order by 1""")
        results = crs.fetchall()
        asientos = []
        for result in results:
            crs.execute("SELECT d.debe, d.haber, c.descripcion FROM detalleasiento d join cuentas c on d.idcuenta=c.idcuenta where d.nroasiento=:nroasiento",nroasiento=result[0])
            detalles=crs.fetchall()
            res=list(result)
            res.append(detalles)
            asientos.append(res)
        conn.close()
        return render_template('libro-diario.html', asientos=asientos)
    else:
        flash("Debes iniciar sesion para acceder")
        return redirect(url_for('login'))

@app.route('/balance-ventas')
def balanceVentas():
    if 'username' in session:
        conn=getConn()
        crs = conn.cursor()
        crs.execute("SELECT nroboleta, rutcliente, to_char(fecha,'dd/mm/yyyy'), totalneto, idtipopago FROM ventas ORDER BY to_char(fecha,'dd/mm/yyyy'), nroboleta")
        results = crs.fetchall()
        ventas=[]
        for result in results:
            crs.execute("SELECT idproducto, cantidad FROM detalleventa where nroboleta=:nroboleta",nroboleta=result[0])
            detalles=crs.fetchall()
            res=list(result)
            if len(detalles)>0:
                details=[]
                for detalle in detalles:
                    detail=list(detalle)
                    r=get_detalle_producto(detalle[0])
                    jerr={'detail': 'Not found.'}
                    if r!=jerr:
                        r2=json.dumps(r)
                        js_dict=json.loads(r2)
                        detail.append(js_dict["DESCRIPCION"])
                    details.append(detail)
            res.append(details)
            ventas.append(res)
        conn.close()
        return render_template('balance-ventas.html', boletas = ventas)
    else:
        flash("Debes iniciar sesion para acceder")
        return redirect(url_for('login'))

@app.route('/balance-gastos')
def balanceGastos():
    if 'username' in session:
        conn=getConn()
        crs = conn.cursor()
        crs.execute("""SELECT nrooperacion, nrofactura, rutproveedor, to_char(fecha,'dd/mm/yyyy'), 
        totalneto, codtrabajador, nrooc, documento, iddepartamento FROM compras ORDER BY to_char(fecha,'dd/mm/yyyy'),nrooperacion""")
        results = crs.fetchall()
        gastos=[]
        for result in results:
            crs.execute("SELECT idproducto, cantidad FROM detallecompra where nrooperacion=:nrooperacion",nrooperacion=result[0])
            detalles=crs.fetchall()
            res=list(result)
            if len(detalles)>0:
                details=[]
                for detalle in detalles:
                    detail=list(detalle)
                    r=get_detalle_producto(detalle[0])
                    jerr={'detail': 'Not found.'}
                    if r!=jerr:
                        r2=json.dumps(r)
                        js_dict=json.loads(r2)
                        detail.append(js_dict["DESCRIPCION"])
                    details.append(detail)
            res.append(details)
            gastos.append(res)
        conn.close()
        return render_template('balance-gastos.html',gastos = gastos)
    else:
        flash("Debes iniciar sesion para acceder")
        return redirect(url_for('login'))

@app.route('/balance-reversos')
def balanceReversos():
    if 'username' in session:
        conn=getConn()
        crs = conn.cursor()
        crs.execute("SELECT nronc, rutcliente, to_char(fecha,'dd/mm/yyyy'), totalneto, nroboleta FROM reversos ORDER BY nronc")
        results = crs.fetchall()
        reversos=[]
        for result in results:
            crs.execute("SELECT idproducto, cantidad, motivo FROM detallereverso where nronc=:nronc",nronc=result[0])
            detalles=crs.fetchall()
            res=list(result)
            if len(detalles)>0:
                details=[]
                for detalle in detalles:
                    detail=list(detalle)
                    r=get_detalle_producto(detalle[0])
                    jerr={'detail': 'Not found.'}
                    if r!=jerr:
                        r2=json.dumps(r)
                        js_dict=json.loads(r2)
                        detail.append(js_dict["DESCRIPCION"])
                    details.append(detail)
            res.append(details)
            reversos.append(res)
        conn.close()
        return render_template('balance-reversos.html', reversos = reversos)
    else:
        flash("Debes iniciar sesion para acceder")
        return redirect(url_for('login'))



@app.route('/balance-general')
def balanceGeneral():
    if 'username' in session:
        conn=getConn()
        crs = conn.cursor()
        crs.execute("SELECT c.descripcion, c.tipocuenta, sum(d.debe), sum(d.haber) from cuentas c join detalleasiento d on c.idcuenta=d.idcuenta group by c.descripcion,c.tipocuenta")
        results = crs.fetchall()
        cuentas=[]
        for result in results:
            res=list(result)
            if result[2] > result[3]:
                deudor=result[2]-result[3]
                acreedor=0
            elif result[2]<result[3]:
                deudor=0
                acreedor=result[3]-result[2]
            else:
                deudor=0
                acreedor=0
            res.append(deudor)
            res.append(acreedor)
            if result[1] == 'Activo' or result[1] == 'Pasivo':
                res.append(deudor)
                res.append(acreedor)
                res.append(0)
                res.append(0)
            else:
                res.append(0)
                res.append(0)
                res.append(deudor)
                res.append(acreedor)
            cuentas.append(res)
        print(cuentas)
        conn.close()
        return render_template('balance-general.html', cuentas = cuentas)
    else:
        flash("Debes iniciar sesion para acceder")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

# funcion que retorna detalle de productos por id (valor de prueba = "123456789ABCDEFG")
def get_detalle_producto(id_producto):
    url_get_producto = "http://ec2-54-146-107-251.compute-1.amazonaws.com/producto/{}/".format(id_producto)
    r = requests.get(url_get_producto).json()
    return r

#funcion que retorna detalle de proveedor segun id (valor de prueba = "PRIMER_RUT")
def get_detalle_proveedor(id_proveedor):
    url_get_proveedor = "http://ec2-54-146-107-251.compute-1.amazonaws.com/proveedor/{}/".format(id_proveedor)
    r = requests.get(url_get_proveedor).json()
    return r


def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2
    
def initiate_auth(username, password):
    client = boto3.client('cognito-idp',region_name='us-east-1')
    print(client)
    secret_hash = get_secret_hash(username)
    print('desde Login_user')
    print(username)
    print(password)
    try:
        resp = client.initiate_auth(
                 #UserPoolId=USER_POOL_ID,
                 ClientId=CLIENT_ID,
                 #AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                 AuthFlow='USER_PASSWORD_AUTH',
                 #AuthFlow='ADMIN_NO_SRP_AUTH',
                 AuthParameters={
                     'USERNAME': username,
                     'SECRET_HASH': secret_hash,
                     'PASSWORD': password,
                  },
                ClientMetadata={
                  'username': username,
                  'password': password,
              })
    except client.exceptions.NotAuthorizedException as e:
        print("error {}".format(e))
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e._str_()
    return resp, None


def lambda_handler(username,password):
    global client
    if client == None:
        client = boto3.client('cognito-idp')
    resp, msg = initiate_auth(username, password)
    
    if msg != None:
        return {'message': msg, 
              "error": True, "success": False, "data": None}
    
    if resp.get("AuthenticationResult"):
        return {'message': "success", 
                "error": False, 
                "success": True, 
                "data": {
                "id_token": resp["AuthenticationResult"]["IdToken"],
                "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                "access_token": resp["AuthenticationResult"]["AccessToken"],
                "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                "token_type": resp["AuthenticationResult"]["TokenType"]
                }}
    else: #this code block is relevant only when MFA is enabled
        return {"error": True, 
                "success": False, 
                "data": None, "message": None}

# r = initiate_auth("johans.neira","Duoc2020.")
# print(r)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)


