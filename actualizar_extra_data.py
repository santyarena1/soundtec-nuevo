from db import get_connection
from scrapers.scraper_info_crestron_extra import obtener_info_crestron
from scrapers.scraper_info_macaio_extra import obtener_info_macaio

def producto_ya_existente(cur, nombre, origen):
    cur.execute("""
        SELECT 1 FROM producto_extra_data WHERE nombre = %s AND origen = %s
    """, (nombre, origen))
    return cur.fetchone() is not None

def guardar_datos(cur, nombre, origen, descripcion, imagen_url, iva=21, mup=1.3):
    cur.execute("""
        INSERT INTO producto_extra_data (nombre, origen, descripcion, imagen_url, iva, mup)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (nombre, origen)
        DO UPDATE SET 
            descripcion = EXCLUDED.descripcion,
            imagen_url = EXCLUDED.imagen_url,
            iva = EXCLUDED.iva,
            mup = EXCLUDED.mup
    """, (nombre, origen, descripcion, imagen_url, iva, mup))


def actualizar_datos_extra():
    conn = get_connection()
    cur = conn.cursor()

    # 🔹 Buscar productos de Xtrabone
    cur.execute("SELECT DISTINCT articulo FROM productos_xtrabone ORDER BY articulo")
    productos_xtrabone = [row[0] for row in cur.fetchall()]

    for nombre in productos_xtrabone:
        print(f"🔍 Buscando info Xtrabone: {nombre}")
        try:
            if not producto_ya_existente(cur, nombre, "Xtrabone"):
                data = obtener_info_crestron(nombre)
                if data:
                    guardar_datos(cur, nombre, "Xtrabone", data["descripcion"], data["imagen_url"], iva=21, mup=1.3)

        except Exception as e:
            print(f"❌ Error con {nombre}: {e}")

    # 🔹 Buscar productos de Macaio
    cur.execute("SELECT DISTINCT nombre FROM productos_macaio ORDER BY nombre")
    productos_macaio = [row[0] for row in cur.fetchall()]

    for nombre in productos_macaio:
        print(f"🔍 Buscando info Macaio: {nombre}")
        try:
            if not producto_ya_existente(cur, nombre, "Macaio"):
                data = obtener_info_macaio(nombre)
                if data:
                    guardar_datos(cur, nombre, "Macaio", data["descripcion"], data["imagen_url"], iva=21, mup=1.3)

        except Exception as e:
            print(f"❌ Error con {nombre}: {e}")

    conn.commit()

    # ✅ Verificación
    print("\n✅ Primeros productos guardados:")
    cur.execute("SELECT nombre, origen, descripcion, imagen_url FROM producto_extra_data ORDER BY nombre LIMIT 4")
    for row in cur.fetchall():
        print("🔹", row[0])
        print("📄", row[2])
        print("🖼️", row[3])
        print("-" * 40)

    conn.close()

if __name__ == "__main__":
    actualizar_datos_extra()
