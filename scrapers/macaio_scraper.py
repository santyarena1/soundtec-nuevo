from playwright.sync_api import sync_playwright
import os
import pandas as pd

USER_DATA_DIR = os.path.join(os.getcwd(), "playwright-session-macaio")


def obtener_productos_macaio():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False, accept_downloads=True)
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto("https://macaio.ar/lista-de-precios/", timeout=20000)
            page.wait_for_load_state("networkidle")

            # Detectar si necesita login
            if page.locator("text=iniciá sesión").is_visible():
                print("🔐 Necesita login, haciendo clic en 'iniciá sesión'...")
                page.click("text=iniciá sesión")
                print("🧑 Iniciá sesión manualmente con el usuario 'compras@soundtec.com.ar'.")
                input("✅ Presioná ENTER una vez que estés logueado y redirigido a la lista de precios...")

            page.goto("https://macaio.ar/lista-de-precios/", timeout=20000)
            page.wait_for_load_state("networkidle")

            # Descargar el Excel
            page.wait_for_timeout(2000)  # esperar que se acomode la UI
            export_btn = page.locator("text=Exportar en .xslx")
            export_btn.wait_for(timeout=10000)
            with page.expect_download() as download_info:
                export_btn.click()
            download = download_info.value
            download_path = download.path()

            # Leer archivo XLSX
            df = pd.read_excel(download_path)
            productos = []
            for _, row in df.iterrows():
                productos.append({
                    "sku": str(row.get("SKU", "")),
                    "nombre": str(row.get("Nombre", "")),
                    "descripcion": str(row.get("Descripción", "")),
                    "categoria": str(row.get("Categoría", "")),
                    "marca": str(row.get("Marca", "")),
                    "stock": str(row.get("Stock", "")),
                    "precio": str(row.get("Precio", "")),
                    "iva": str(row.get("Porcentaje IVA", "")),
                })

            print(f"✅ Productos de Macaio leídos: {len(productos)}")
            return productos

        except Exception as e:
            print("❌ Error al obtener productos de Macaio:", e)
            return []

        finally:
            context.close()