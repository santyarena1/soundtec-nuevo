from flask import Blueprint, render_template, request, jsonify
from db import get_connection
from scrapers.xtrabone_scraper import obtener_productos_xtrabone

base_datos_bp = Blueprint("base_datos", __name__)

@base_datos_bp.route("/base-datos")
def vista_base_datos():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM productos_xtrabone")
        cantidad = cur.fetchone()[0]
    conn.close()
    return render_template("base_datos.html", cantidad=cantidad)


@base_datos_bp.route("/actualizar_db_xtrabone", methods=["POST"])
def actualizar_db():
    try:
        productos = obtener_productos_xtrabone()
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM productos_xtrabone")
            for p in productos:
                cur.execute("""
                    INSERT INTO productos_xtrabone 
                    (codigo, articulo, precio, descuento, precio_final, moneda, laredo, miami, info_fabrica)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    p['codigo'], p['articulo'], p['precio'], p['descuento'],
                    p['precio_final'], p['moneda'], p['laredo'], p['miami'], p['info_fabrica']
                ))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "total": len(productos)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@base_datos_bp.route("/cantidad_xtrabone")
def cantidad():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM productos_xtrabone")
        cantidad = cur.fetchone()[0]
    conn.close()
    return jsonify({"cantidad": cantidad})


@base_datos_bp.route("/subir_excel_soundtube", methods=["POST"])
def subir_excel_soundtube():
    if 'archivo' not in request.files:
        return jsonify({"success": False, "error": "No se encontró el archivo"})

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"success": False, "error": "Nombre de archivo vacío"})

    try:
        filename = secure_filename(archivo.filename)
        path_temporal = os.path.join("uploads", filename)
        archivo.save(path_temporal)

        df = pd.read_excel(path_temporal, header=1)
        df.columns = df.columns.str.strip()
        df.columns = [
            "sku", "descripcion", "retail_usa", "supdist_usa", "supdist_china",
            "color", "upc", "coo", "url", "product_line", "categoria", "tipo"
        ]

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM productos_soundtube")
            for _, row in df.iterrows():
                sku = row.get("sku")
                if not sku or str(sku).strip() == "":
                    continue

                cur.execute("""
                    INSERT INTO productos_soundtube 
                    (sku, item, descripcion, retail_usa, supdist_usa, supdist_china, color, upc, coo, url, product_line, categoria, tipo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (sku) DO NOTHING
                """, (
                    sku, sku, row.get("descripcion"), row.get("retail_usa"),
                    row.get("supdist_usa"), row.get("supdist_china"), row.get("color"),
                    row.get("upc"), row.get("coo"), row.get("url"), row.get("product_line"),
                    row.get("categoria"), row.get("tipo")
                ))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "filas": len(df)})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
