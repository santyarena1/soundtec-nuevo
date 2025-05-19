from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from urllib.parse import quote_plus
from db import get_connection
from routes.base_datos_routes import base_datos_bp
from routes.buscar_producto import buscar_bp
from routes.macaio_routes import macaio_bp
#from routes.soundtube_routes import soundtube_bp

import os


app = Flask(__name__)
app.secret_key = 'clave-super-secreta'

# Registrar las rutas externas
app.register_blueprint(base_datos_bp)
app.register_blueprint(buscar_bp)
app.register_blueprint(macaio_bp)


@app.route('/')
def home():
    return render_template('buscador.html')

@app.route('/carrito')
def carrito():
    carrito = session.get('carrito', [])
    total = 0
    for item in carrito:
        try:
            precio = float(item['precio_final'].replace('$', '').replace(',', '').strip())
            total += precio
        except:
            continue

    mensaje = "🛒 Pedido desde Soundtec:\n"
    for i, p in enumerate(carrito, 1):
        mensaje += f"{i}) {p['articulo']} ({p['codigo']}) - {p['precio_final']} {p['moneda']}\n"
    mensaje += f"\nTOTAL: ${total:,.2f} USD"
    link_whatsapp = f"https://wa.me/5491140859342?text={quote_plus(mensaje)}"

    return render_template('carrito.html', carrito=carrito, total=total, whatsapp_link=link_whatsapp)

@app.route('/agregar-carrito', methods=['POST'])
def agregar_carrito():
    producto = request.get_json()
    carrito = session.get('carrito', [])
    carrito.append(producto)
    session['carrito'] = carrito
    return '', 204

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


