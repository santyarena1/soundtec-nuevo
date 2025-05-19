from flask import Blueprint, request, jsonify
from db import get_connection

buscar_bp = Blueprint("buscar", __name__)

@buscar_bp.route("/buscar", methods=["POST"])
def buscar_producto():
    query = request.form.get("producto", "").strip()
    if not query:
        return jsonify([])

    conn = get_connection()
    resultados = []

    def get_extra_data(nombre, origen):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT descripcion, imagen_url, iva, mup, marca, categoria, descripcion_larga, descuento
                FROM producto_extra_data
                WHERE nombre = %s AND origen = %s
            """, (nombre, origen))
            row = cur.fetchone()
            return {
                "descripcion_extra": row[0],
                "imagen_url": row[1],
                "iva": float(row[2]) if row[2] is not None else 21,
                "mup": float(row[3]) if row[3] is not None else 1.3,
                "detalles_extra": {
                    "marca": row[4],
                    "categoria": row[5],
                    "descripcion_larga": row[6],
                    "descuento": float(row[7]) if row[7] is not None else 0
                }
            } if row else {}






    try:
        with conn.cursor() as cur:
            # Buscar en Xtrabone
            cur.execute("""
                SELECT codigo, articulo, precio, descuento, precio_final, moneda, laredo, miami, info_fabrica, mup, iva
                FROM productos_xtrabone
                WHERE LOWER(articulo) LIKE LOWER(%s)
                LIMIT 10
            """, (f"%{query}%",))
            for row in cur.fetchall():
                codigo = row[0]
                origen = "Xtrabone"
                producto = {
                    "codigo": codigo,
                    "articulo": row[1],
                    "precio": row[2],
                    "origen": origen,
                    "mup": float(row[9]) if row[9] is not None else 1.3,
                    "iva": float(row[10]) if row[10] is not None else 21,
                    "detalles": {
                        "descuento": row[3],
                        "precio_final": row[4],
                        "moneda": row[5],
                        "laredo": row[6],
                        "miami": row[7],
                        "info_fabrica": row[8]
                    }
                }

                
                extra = get_extra_data(row[1], "Xtrabone")  # row[1] es el artículo/nombre
                print("🧩 Extra data para", codigo, extra)
                producto.update(extra)
                producto["detalles"].update(extra.get("detalles_extra", {}))
                resultados.append(producto)




            
            # Buscar en Macaio
            cur.execute("""
                SELECT sku, nombre, descripcion, categoria, marca, stock, precio, iva, mup
                FROM productos_macaio
                WHERE LOWER(nombre) LIKE LOWER(%s)
                LIMIT 10
            """, (f"%{query}%",))
            for row in cur.fetchall():
                extra = get_extra_data(row[1], "Macaio")  # nombre = row[1]

                producto = {
                    "codigo": row[0],
                    "articulo": row[1],
                    "precio": row[6],
                    "origen": "Macaio",
                    "mup": extra.get("mup", float(row[8]) if row[8] not in (None, '', ' ') else 1.3),
                    "iva": extra.get("iva", float(row[7]) if row[7] not in (None, '', ' ') else 21),
                    "descripcion_extra": extra.get("descripcion_extra", ""),
                    "imagen_url": extra.get("imagen_url", ""),
                    "detalles": {
                        "descripcion": row[2],
                        "categoria": row[3],
                        "marca": row[4],
                        "stock": row[5]
                    }
                }

                # 🔄 Fusionar datos extra si existen
                producto["detalles"].update(extra.get("detalles_extra", {}))

                resultados.append(producto)

            # Buscar en Soundtube
            cur.execute("""
                SELECT sku, descripcion, retail_usa, supdist_usa, supdist_china, color,
                    upc, coo, url, product_line, categoria, tipo
                FROM productos_soundtube
                WHERE LOWER(sku) LIKE LOWER(%s) OR LOWER(descripcion) LIKE LOWER(%s)
                LIMIT 10
            """, (f"%{query}%", f"%{query}%"))

            for row in cur.fetchall():
                extra = get_extra_data(row[0], "Soundtube")  # row[0] = sku

                producto = {
                    "codigo": row[0],                    # SKU
                    "articulo": row[0],                  # Nombre visible
                    "precio": row[3],                    # supdist_usa
                    "origen": "Soundtube",
                    "mup": extra.get("mup", 1.3),
                    "iva": extra.get("iva", 21),
                    "descripcion_extra": row[1],         # Mismo que el nombre
                    "imagen_url": extra.get("imagen_url", ""),
                    "detalles": {
                        "marca": row[9],                 # product_line
                        "categoria": row[10],
                        "descripcion_larga": extra.get("detalles_extra", {}).get("descripcion_larga", ""),
                        "descuento": extra.get("detalles_extra", {}).get("descuento", 0)
                    }
                }
                # 🔄 Fusionar datos extra si existen
                producto["detalles"].update(extra.get("detalles_extra", {}))

                resultados.append(producto)





        

    finally:
        conn.close()

    return jsonify(resultados)


@buscar_bp.route("/actualizar_producto", methods=["POST"])
def actualizar_producto():
    data = request.json
    nombre = data.get("nombre")
    origen = data.get("origen")
    mup = data.get("mup")
    iva = data.get("iva")
    marca = data.get("marca")
    categoria = data.get("categoria")
    descripcion = data.get("descripcion")
    descripcion_larga = data.get("descripcion_larga")
    imagen_url = data.get("imagen_url")
    descuento = data.get("descuento")

    if not nombre or not origen:
        return jsonify({"success": False, "error": "Faltan datos"})

    conn = get_connection()
    with conn.cursor() as cur:
        # 🔍 Traer los valores actuales de la BD si no vienen desde el frontend
        cur.execute("""
            SELECT descripcion, imagen_url
            FROM producto_extra_data
            WHERE nombre = %s AND origen = %s
        """, (nombre, origen))
        row = cur.fetchone()
        descripcion_actual = row[0] if row else None
        imagen_url_actual = row[1] if row else None

        # Si vienen vacíos, usamos los que ya están
        descripcion = descripcion if descripcion else descripcion_actual
        imagen_url = imagen_url if imagen_url else imagen_url_actual

        cur.execute("""
            INSERT INTO producto_extra_data 
                (nombre, origen, iva, mup, marca, categoria, descripcion, descripcion_larga, imagen_url, descuento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (nombre, origen)
            DO UPDATE SET 
                iva = EXCLUDED.iva,
                mup = EXCLUDED.mup,
                marca = EXCLUDED.marca,
                categoria = EXCLUDED.categoria,
                descripcion = EXCLUDED.descripcion,
                descripcion_larga = EXCLUDED.descripcion_larga,
                imagen_url = EXCLUDED.imagen_url,
                descuento = EXCLUDED.descuento
        """, (
            nombre, origen, iva, mup,
            marca, categoria, descripcion, descripcion_larga, imagen_url, descuento
        ))
        conn.commit()
    conn.close()

    return jsonify({"success": True})







