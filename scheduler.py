import schedule
import time
import subprocess
from datetime import datetime

def tarea_diaria():
    print(f"\n🕒 Ejecutando actualización diaria: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        subprocess.run(["python", "actualizar_extra_data.py"], check=True)
        print("✅ Actualización completada correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando el script: {e}")

# 🔁 Ejecutar una vez al día a las 03:00 AM
schedule.every(72).hours.do(tarea_diaria)

print("🛠️ Programador iniciado. Esperando a la hora programada...\n")

# 🔄 Bucle principal
while True:
    schedule.run_pending()
    time.sleep(60)  # Espera 1 minuto entre chequeos
