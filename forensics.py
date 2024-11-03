import os
import subprocess
import hashlib
import time
from datetime import datetime
import re

def log_message(message):
    """Zapisz wiadomość do pliku logu"""
    with open("system_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")
    print(message)
    
def raport_message(message):
    """Zapisz wiadomość do pliku raportu"""
    with open("raport_mess.txt", "a") as log_file:
        log_file.write(f"{message}\n")
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

def check_partition(mount_point): #gdzie mount_point /dev/NAME
    """Analizuje strukturę partycji za pomocą fdisk i mmls."""
    
    # Sprawdzanie struktury partycji za pomocą `fdisk`
    fdisk_output = subprocess.run(["sudo","fdisk", "-l", mount_point], capture_output=True, text=True)
    if fdisk_output.returncode == 0:
        for line in fdisk_output.stdout.splitlines():
            if "Units:" in line:  # Filtrujemy tylko linie dotyczące partycji
                match = re.search(r'(\d+)$', line)
                if match:
                    offset = match.group(1)  # Pobieramy znalezioną liczbę
        log_message(f"\nStruktura partycji przy użyciu fdisk zapisana do pliku raportu.")
        raport_message(f"\nStruktura partycji przy użyciu fdisk:")
        raport_message(fdisk_output.stdout)
        
    else:
        print(f"Błąd fdisk: {fdisk_output.stderr}")
        log_message(f"Błąd fdisk: {fdisk_output.stderr}")
    return offset

def file_analysis(mount_point):
    """Analizuje metadane plików za pomocą fls i istat."""
    # Użycie `fls` do wylistowania plików na pierwszej partycji
    try:
        fls_output = subprocess.run(["sudo","fls", mount_point])  #gdzie mount_point /dev/NAME
        
        if fls_output.returncode == 0:
            raport_message(f"\nWylistowanie plików przy użyciu fls:")
            raport_message(fls_output.stdout)
            log_message(f"\nWylistowanie plików przy użyciu fls zapisana do pliku raportu.")
            
            inode_ids = re.findall(r"\* (\d+):", fls_output)  # Pobranie numerów inode
            for inode in inode_ids:
                print(f"\nMetadane pliku o inode {inode}:")
                istat_output = subprocess.run(["sudo","istat", mount_point, inode])
                print(istat_output)
        else:
            print(f"Błąd fdisk: {fls_output.stderr}")
            log_message(f"Błąd fdisk: {fls_output.stderr}")
    except Exception as e:
        log_message(f"Błąd podczas wykrywania i montowania nośnika: {e}")
        return None


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
            
            # Krok 4: Badanie struktury partycji obrazu 
            check_partition(mount_point)
            
            # Ktok 5: Analiza plików
            file_analysis(mount_point)

            # Odmontowanie nośnika po zakończeniu pracy
            subprocess.run(f"sudo umount {mount_point}", shell=True)
            log_message(f"Nośnik {mount_point} został odmontowany.")
        
        # Odczekaj przed kolejną iteracją (np. 60 sekund)
        time.sleep(60)

if __name__ == "__main__":
    main()
