from playwright.sync_api import sync_playwright
import os

USER_DATA_DIR = os.path.join(os.getcwd(), "playwright-session")

def buscar_en_xtrabone(producto):
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
        page = context.pages[0] if context.pages else context.new_page()

        try:
            # Ir a la página de precios
            page.goto("https://crestronlatam.xtrabone.mx/clientes/precios", timeout=20000)
            page.wait_for_load_state("networkidle")

            # Si redirige al login, pedir login manual
            if page.url.startswith("https://crestronlatam.xtrabone.mx/login"):
                print("🔐 Iniciá sesión manualmente en el navegador abierto.")
                input("✅ Presioná ENTER una vez logueado correctamente...")
                page.goto("https://crestronlatam.xtrabone.mx/clientes/precios", timeout=20000)
                page.wait_for_load_state("networkidle")

            # Seleccionar 'Todos' en la cantidad de registros
            try:
                selector = page.locator('select[name=\"tabla_precios_length\"]')
                selector.select_option("-1")  # Mostrar todos
                page.wait_for_timeout(2000)
            except Exception as e:
                print("⚠️ No se pudo cambiar selector a 'Todos':", e)

            # Buscar producto
            print(f"🔍 Buscando: {producto}")
            page.fill('input[type=\"search\"]', producto)
            page.keyboard.press("Enter")
            page.wait_for_timeout(2000)

            # Obtener todas las filas visibles
            filas = page.locator("table tbody tr")
            total = filas.count()
            if total == 0:
                return []

            resultados = []
            for i in range(total):
                fila = filas.nth(i)
                celdas = fila.locator("td:not(.d-none)")

                data = {
                    "codigo": celdas.nth(0).inner_text(),
                    "articulo": celdas.nth(1).inner_text(),
                    "precio": celdas.nth(2).inner_text(),
                    "descuento": celdas.nth(3).inner_text(),
                    "precio_final": celdas.nth(4).inner_text(),
                    "moneda": celdas.nth(5).inner_text(),
                    "laredo": celdas.nth(6).inner_text(),
                    "miami": celdas.nth(7).inner_text(),
                    "info_fabrica": celdas.nth(8).inner_text(),
                }

                resultados.append(data)

            return resultados

        except Exception as e:
            return [{"error": str(e)}]
        finally:
            context.close()
