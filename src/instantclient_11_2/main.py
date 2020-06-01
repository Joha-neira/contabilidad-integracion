from flask import Flask, jsonify, request
from conexionbd import getConn, cx_Oracle
from models import Venta




app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

#probando primer endpoint
@app.route('/hola')
def holaMundo():
    return jsonify({"message": "Hola ctm"})


#prueba objeto venta
venta1 = Venta(4123,'18841584-9','18/05/1994',339000,'factura.pdf',11)


#obtener id boleta desde la base de datos
#crear seq en base de datos y cambiar nombre
@app.route('/idBoleta',methods=['GET'])
def getIdBoleta():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT boleta_seq.currval FROM DUAL")
    result = crs.fetchall()
    conn.close()
    return jsonify({'Id boleta': result})

#obtener id Orden de compra desde la BD
#crear seq en base de datos y reemplazar despues
@app.route('/idOrdenCompra')
def getIdOrdenCompra():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT ordencompra_seq.currval FROM DUAL")
    result = crs.fetchall()
    conn.close()
    return jsonify({'Id Orden de compra': result})

#obtener id Nota de credito desde la BD
#crear seq en base de datos y reemplazar
@app.route('/idNotaCredito')
def getIdNotaCredito():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT notacredito_seq.currval FROM DUAL")
    result = crs.fetchall()
    conn.close()
    return jsonify({'Id Nota de Credito': result})

#obtener boletas para enviar a postventas y hacer reversos
@app.route('/boletas')
def getBoletas():
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT * FROM ventas")
    result = crs.fetchall()
    return jsonify({'Boletas encontradas ':result})

#obtener boleta unica con su id como parametro
@app.route('/boletas/<int:idBoleta>')
def getBoleta(idBoleta):
    conn=getConn()
    crs = conn.cursor()
    crs.execute("SELECT * FROM ventas WHERE nroboleta = :filtro", filtro = idBoleta)
    result = crs.fetchall()
    return jsonify({'Boleta encontrada ':result})

#registrar nueva boleta en BD
@app.route('/boleta', methods=['POST'])
def addBoleta():
    conn=getConn()
    crs = conn.cursor()
#    nuevaVenta = Venta(request.json['boleta'],request.json['rutCliente'],request.json['fecha'],request.json['totalNeto'],"",request.json['tipoPago'])
    nroBoleta= request.json['boleta']
    rutcliente = request.json['rutCliente'] 
    fecha = request.json['fecha']
    totalneto = request.json['totalNeto'] 
    idtipopago  = request.json['tipoPago']
    # probar con id tipo pago = 22
    sql = """INSERT INTO ventas (nroboleta,rutcliente,fecha,totalneto,idtipopago)
          VALUES (:nroboleta,:rutcliente,TO_DATE(:fecha,'YYYY-MM-DD'),:totalneto,:idtipopago)"""
    crs.execute(sql,[nroBoleta,rutcliente,fecha,totalneto,idtipopago])
    print(request.json)
    conn.commit()
    conn.close()
    return 'received'

#registrar nueva orden de compra en BD
@app.route('/ordenCompra', methods=['POST'])
def addOrdenCompra():
    print(request.json)
    return 'received'

#registrar nueva nota de credito en BD
@app.route('/notaCredito', methods=['POST'])
def addNotaCredito():
    print(request.json)
    return 'received'

#registrar nueva compra en BD
@app.route('/compra', methods=['POST'])
def addCompra():
    print(request.json)
    return 'received'

