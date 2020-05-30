from flask import Flask, jsonify, request
from conexionbd import getConn
from models import Venta



app = Flask(__name__)


@app.route('/hola')
def holaMundo():
    return jsonify({"message": "Hola ctm"})


#prueba objeto venta
venta1 = Venta(4123,'18841584-9','18/05/1994',339000,'factura.pdf')
#obtener id boleta desde la base de datos
@app.route('/idBoleta',methods=['GET'])
def getIdBoleta():
    return jsonify({'Id boleta': venta1.nroBoleta,'Rut cliente': venta1.rutCliente})

#obtener id Orden de compra desde la BD
@app.route('/idOrdenCompra')
def getIdOrdenCompra():
    return jsonify({"index": "5"})

#obtener id Nota de credito desde la BD
@app.route('/idNotaCredito')
def getIdNotaCredito():
    return jsonify({"index": "7"})

#obtener boletas para enviar a postventas y hacer reversos
@app.route('/boletas')
def getBoletas():
    return jsonify({"index": "7"})

#obtener boleta unica con su id como parametro
@app.route('/boletas/<int:idBoleta>')
def getBoleta(idBoleta):
    return jsonify({"Total Neto de boleta "+str(idBoleta): venta1.totalNeto})

#registrar nueva boleta en BD
@app.route('/boleta', methods=['POST'])
def addBoleta():
    print(request.json)
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)