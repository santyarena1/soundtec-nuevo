from flask import Blueprint, jsonify
from db import get_connection
from scrapers.macaio_scraper import obtener_productos_macaio

macaio_bp = Blueprint("macaio", __name__)

@macaio_bp.route("/actualizar_db_macaio", methods=["POST"])
def actualizar_db_macaio():
    try:
        productos = obtener_productos_macaio()
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM productos_macaio")
            for p in productos:
                cur.execute("""
                    INSERT INTO productos_macaio 
                    (sku, nombre, descripcion, categoria, marca, stock, precio, iva)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    p['sku'], p['nombre'], p['descripcion'], p['categoria'],
                    p['marca'], p['stock'], p['precio'], p['iva']
                ))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "total": len(productos)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@macaio_bp.route("/cantidad_macaio")
def cantidad_macaio():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM productos_macaio")
        cantidad = cur.fetchone()[0]
    conn.close()
    return jsonify({"cantidad": cantidad})
