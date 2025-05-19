from playwright.sync_api import sync_playwright

def obtener_info_crestron(nombre_producto):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto("https://www.crestron.com/", timeout=30000)

            # Abrir buscador
            page.click("svg[viewBox='0 0 16 16']")
            page.wait_for_timeout(1000)
            page.wait_for_selector("input[type='search']", timeout=8000)

            # Buscar producto
            page.fill("input[type='search']", nombre_producto)
            page.keyboard.press("Enter")
            page.wait_for_timeout(3000)

            # Esperamos que aparezca el primer botón de "Learn More"
            boton = page.locator("div.button-v2.filled.button-blue", has_text="Learn More").first

            # Obtenemos el href real desde el contenedor padre (accedemos al DOM con evaluate)
            href = boton.evaluate("node => node.getAttribute('href')")

            if href:
                page.goto("https://www.crestron.com" + href)
                page.wait_for_timeout(3000)
            else:
                print("❌ No se encontró el enlace del producto.")
                return None



            # Buscar la primera imagen del producto seleccionada
            img_url = ""
            try:
                img_url = page.get_attribute(".mz-thumb-selected.mz-thumb img", "src")
            except:
                pass

            # Fallback si no se encuentra
            if not img_url:
                img_url = page.get_attribute("a:has-text('Download PNG')", "href")

            print(f"🖼️ Imagen encontrada: {img_url}")


            # 📝 Buscar descripción en el <p> dentro del contenedor
            descripcion = page.text_content(".model-short-description p")

            if not descripcion and not img_url:
                print(f"⚠️ Producto sin detalles: {nombre_producto}")
                return None

            return {
                "descripcion": descripcion.strip() if descripcion else "",
                "imagen_url": img_url if img_url else ""
            }


        except Exception as e:
            print(f"❌ Error buscando {nombre_producto}: {e}")
            return None
        finally:
            try:
                browser.close()
            except:
                pass
