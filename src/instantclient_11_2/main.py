from flask import Flask, jsonify, request
from conexionbd import getConn, cx_Oracle
from models import Venta




app = Flask(__name__)


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
        dict = {
        "idBoleta": boleta[0],
        "rutCliente": boleta[1],
        "fecha": boleta[2],
        "totalNeto": boleta[3],
        "tipoPago":tipoPago,
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

@app.route('/get-notas-credito')
def getNotasCredito():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT nronc, rutcliente, to_char(fecha,'dd/mm/yyyy'), totalneto, nroboleta FROM reversos")
    result = crs.fetchall()
    notasCredito = {}
    for nc in result:
        dict = {
        "nroNotaCredito": nc[0],
        "rutCliente": nc[1],
        "fecha": nc[2],
        "totalNeto": nc[3],
        "nroBoleta":nc[4]
        }
        string = 'notaCredito'+str(nc[0])
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
        dict = {
        "nroOperacion": gasto[0],
        "nroFactura": gasto[1],
        "rutProveedor": gasto[2],
        "fecha": gasto[3],
        "totalNeto": gasto[4],
        "codTrabajador":gasto[5],
        "nroOrdenCompra": gasto[6],
        "departamento": deptoTrabajador
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)