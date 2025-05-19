from playwright.sync_api import sync_playwright
import os, csv
from io import StringIO

USER_DATA_DIR = os.path.join(os.getcwd(), "playwright-session")

def obtener_productos_xtrabone():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False, accept_downloads=True)
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto("https://crestronlatam.xtrabone.mx/clientes/precios", timeout=20000)
            page.wait_for_load_state("networkidle")

            if page.url.startswith("https://crestronlatam.xtrabone.mx/login"):
                print("🔐 Iniciá sesión manualmente en el navegador persistente.")
                input("✅ Presioná ENTER una vez que estés logueado...")
                page.goto("https://crestronlatam.xtrabone.mx/clientes/precios", timeout=20000)
                page.wait_for_load_state("networkidle")

            # Mostrar todos
            try:
                selector = page.locator('select[name="tabla_precios_length"]')
                selector.select_option("-1")
                page.wait_for_timeout(5000)
            except Exception as e:
                print("⚠️ No se pudo seleccionar 'Todos':", e)

            # Descargar CSV
            page.wait_for_selector("button:has-text('Exportar')", timeout=10000)
            page.click("button:has-text('Exportar')")
            page.wait_for_timeout(500)

            with page.expect_download() as download_info:
                page.click("text=CSV")
            download = download_info.value
            download_path = download.path()

            with open(download_path, 'r', encoding='utf-8-sig') as f:
                csv_content = f.read()

            reader = csv.DictReader(StringIO(csv_content))
            print("ENCABEZADOS CSV:", reader.fieldnames)

            productos = []
            for row in reader:
                productos.append({
                    "codigo": row.get("Código de artículo", ""),
                    "articulo": row.get("Artículo", ""),
                    "precio": row.get("Precio", ""),
                    "descuento": row.get("Descuento", ""),
                    "precio_final": row.get("Precio final", ""),
                    "moneda": row.get("Moneda", ""),
                    "laredo": row.get("LAREDO", ""),
                    "miami": row.get("MIAMI", ""),
                    "info_fabrica": ""  # No está presente en el archivo
                })

            print(f"✅ Productos leídos: {len(productos)}")
            return productos

        except Exception as e:
            print("❌ Error durante la descarga del CSV:", e)
            return []
        finally:
            context.close()
