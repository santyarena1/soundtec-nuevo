from scrapers.xtrabone import buscar_en_xtrabone

if __name__ == "__main__":
    producto = input("🔍 Ingresá el nombre o código del producto: ")
    resultados = buscar_en_xtrabone(producto)

    print("\n📦 Resultados encontrados:\n")
    for r in resultados:
        if "error" in r:
            print("❌ Error:", r["error"])
        else:
            print(f"""
📌 Código: {r['codigo']}
📄 Artículo: {r['articulo']}
💵 Precio: {r['precio']} / Final: {r['precio_final']}
🎯 Descuento: {r['descuento']} | Moneda: {r['moneda']}
🚚 LAREDO: {r['laredo']} | MIAMI: {r['miami']}
🏭 Info Fábrica: {r['info_fabrica']}
{'-'*40}
""")
