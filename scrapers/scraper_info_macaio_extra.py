# scraper_info_macaio_extra.py
from playwright.sync_api import sync_playwright

def obtener_info_macaio(nombre_producto):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://macaio.ar/lista-de-precios/", timeout=30000)
            page.wait_for_timeout(3000)

            # Buscar manualmente con Ctrl+F simulando
            if not page.is_visible("input[type='search']"):
                return None

            page.fill("input[type='search']", nombre_producto)
            page.wait_for_timeout(3000)

            # Buscar descripción y src de imagen
            fila = page.locator("tr").filter(has_text=nombre_producto).first

            descripcion = fila.locator("td").nth(2).inner_text()
            img = fila.locator("img").first.get_attribute("src")

            return {
                "descripcion": descripcion.strip() if descripcion else "",
                "imagen_url": img if img else ""
            }

        except Exception as e:
            print(f"❌ Error Macaio: {e}")
            return None
        finally:
            browser.close()
