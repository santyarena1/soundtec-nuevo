from playwright.sync_api import sync_playwright
import os

USER_DATA_DIR = os.path.join(os.getcwd(), "playwright-session")

with sync_playwright() as p:
    print("🧠 Abriendo navegador para iniciar sesión manual...")
    context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://crestronlatam.xtrabone.mx/login")

    print("\n🔐 Iniciá sesión manualmente en la pestaña abierta.")
    input("✅ Una vez logueado correctamente y dentro del sistema, presioná ENTER acá para guardar la sesión...")
    
    context.close()
    print("💾 Sesión guardada. Ya podés cerrar el navegador.")
