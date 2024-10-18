import os
import subprocess
import hashlib
import time
from datetime import datetime

def log_message(message):
    """Zapisz wiadomość do pliku logu"""
    with open("system_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")
    print(message)

def document_vm_configuration():
    """Zapisuje informacje o konfiguracji maszyny wirtualnej do pliku"""
    try:
        # Pobierz podstawowe informacje o systemie
        uname_output = subprocess.check_output("uname -a", shell=True).decode()
        cpu_info = subprocess.check_output("lscpu", shell=True).decode()
        mem_info = subprocess.check_output("free -h", shell=True).decode()

        # Zapisz do pliku
        with open("vm_configuration.txt", "w") as file:
            file.write("=== Konfiguracja maszyny wirtualnej ===\n")
            file.write(f"System:\n{uname_output}\n")
            file.write(f"Informacje o procesorze:\n{cpu_info}\n")
            file.write(f"Informacje o pamięci:\n{mem_info}\n")

        log_message("Dokumentacja konfiguracji maszyny wirtualnej została zapisana.")
    except Exception as e:
        log_message(f"Błąd podczas dokumentacji konfiguracji: {e}")

def detect_and_mount_drive():
    """Automatycznie wykrywa nowe nośniki i montuje je w trybie read-only"""
    try:
        # Wykrywanie podłączonych urządzeń
        result = subprocess.check_output("lsblk -r -o NAME,MOUNTPOINT,TYPE", shell=True).decode()
        lines = result.strip().split("\n")
        drives = [line.split()[0] for line in lines if 'disk' in line and not any(m in line for m in ['/mnt', '/media'])]

        if not drives:
            log_message("Nie znaleziono nowych nośników.")
            return None

        # Zakładamy, że pierwszy znaleziony napęd jest tym, który należy zamontować
        drive = drives[0]
        mount_point = f"/mnt/{drive}"

        # Montowanie w trybie read-only
        os.makedirs(mount_point, exist_ok=True)
        subprocess.run(f"sudo mount -o ro /dev/{drive} {mount_point}", shell=True, check=True)
        log_message(f"Nośnik /dev/{drive} został zamontowany w {mount_point}.")

        return mount_point
    except Exception as e:
        log_message(f"Błąd podczas wykrywania i montowania nośnika: {e}")
        return None

def create_checksum_and_image(mount_point):
    """Tworzy sumę kontrolną oraz kopię obrazu nośnika"""
    try:
        image_path = f"{mount_point.replace('/mnt/', '')}_backup.img"
        checksum_path = f"{image_path}.sha256"

        # Tworzenie obrazu za pomocą dd
        log_message(f"Rozpoczęto tworzenie obrazu {image_path}...")
        subprocess.run(f"sudo dd if={mount_point} of={image_path} bs=4M status=progress", shell=True, check=True)
        log_message(f"Obraz nośnika zapisany jako {image_path}.")

        # Tworzenie sumy kontrolnej
        log_message(f"Tworzenie sumy kontrolnej dla {image_path}...")
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        with open(checksum_path, "w") as f:
            f.write(sha256_hash.hexdigest())

        log_message(f"Suma kontrolna zapisana w pliku {checksum_path}.")
    except Exception as e:
        log_message(f"Błąd podczas tworzenia obrazu lub sumy kontrolnej: {e}")

def main():
    """Główna funkcja kontrolująca działanie skryptu"""
    log_message("=== Rozpoczęcie pracy skryptu ===")
    
    # Krok 1: Dokumentacja konfiguracji VM
    document_vm_configuration()
    
    while True:
        # Krok 2: Wykrywanie i montowanie nowego nośnika
        mount_point = detect_and_mount_drive()
        if mount_point:
            # Krok 3: Tworzenie obrazu i sumy kontrolnej
            create_checksum_and_image(mount_point)

            # Odmontowanie nośnika po zakończeniu pracy
            subprocess.run(f"sudo umount {mount_point}", shell=True)
            log_message(f"Nośnik {mount_point} został odmontowany.")
        
        # Odczekaj przed kolejną iteracją (np. 60 sekund)
        time.sleep(60)

if __name__ == "__main__":
    main()
