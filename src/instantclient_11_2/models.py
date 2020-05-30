import datetime

class Venta:
    nroBoleta: int
    rutCliente: str
    fecha: str
    totalNeto: int
    documento: str
    def __init__(self, nroBoleta, rutCliente, fecha, totalNeto, documento):
      self.nroBoleta = nroBoleta
      self.rutCliente = rutCliente
      self.fecha = fecha
      self.totalNeto = totalNeto
      self.documento = documento


class OrdenCompra:
    nroOc: int
    rutProveedor: str
    fecha: str
    totalNeto: int
    codTrabajador: int
    documento: str
    def __init__(self, nroOc, rutProveedor, fecha, totalNeto, codTrabajador, documento):
        self.nroOc = nroOc
        self.rutProveedor = rutProveedor
        self.fecha = fecha
        self.totalNeto = totalNeto
        self.codTrabajador = codTrabajador
        self.documento = documento

class Compra:
    nroOperacion: int
    nroFactura: int
    rutProveedor: str
    fecha: str
    totalNeto: int
    codTrabajador: int
    documento:str
    def __init__(self, nroOperacion, nroFactura, rutProveedor, fecha, totalNeto, codTrabajador, documento):
        self.nroOperacion = nroOperacion
        self.nroFactura = nroFactura
        self.rutProveedor = rutProveedor
        self.fecha = fecha
        self.totalNeto = totalNeto
        self.codTrabajador = totalNeto
        self.documento = documento


class Reverso:
    nroNotaCredito: int
    rutCliente: str
    fecha : str
    totalNeto: int
    documento: str
    def __init__(self, nroNotaCredito, rutCliente, fecha, totalNeto, documento):
        self.nroNotaCredito = nroNotaCredito
        self.rutCliente = rutCliente
        self.fecha = fecha
        self.totalNeto = totalNeto
        self.documento = documento



