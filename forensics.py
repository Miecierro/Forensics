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

def hash_file(mount_point):
    hash_obj = hashlib.sha256()
    output_file = f"{mount_point}_sha256.txt"
    file_path = f"/dev/{mount_point}"
    try:
        #wywoluje komende ktora tworzy hash i zapisuje do pliku
        f = open(output_file , "w")
        result = subprocess.run(["sudo","sha256sum", file_path], stdout=f)
        log_message(f" generowanie sumy kontrolnej przebieglo pomyslnie") 
    except IOError as e:
        log_message(f"Błąd podczas generowania sumy kontrolnej z pliku {e}") 
         
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

def detect_name_drive():
    """Automatycznie wykrywa nowe nośniki i montuje je w trybie read-only"""
    # Wykrywanie podłączonych urządzeń
    try:
        result = subprocess.run(["lsblk", "-r", "-o", "NAME"], capture_output=True, text=True)
        drives = result.stdout.strip().split("\n")
        loop_elements = [item for item in drives if re.match(r"loop\d+$", item)]
        recent = loop_elements[-1]
        return recent
    except Exception as e:
        log_message(f"Błąd podczas szukania urzadzenia: {e}")
      
def detect_and_mount_drive():
    """Automatycznie wykrywa nowe nośniki i montuje je w trybie read-only"""
        # Wykrywanie podłączonych urządzeń
    result = subprocess.run(["lsblk", "-r", "-o", "NAME"], capture_output=True, text=True)
    drives = result.stdout.strip().split("\n")
    print("Prosze podlaczyc nosnik danych...")
    new_device = None
    start_time = time.time()
    timeout = 60
    while True:
        result = subprocess.run(["lsblk", "-r", "-o", "NAME"],capture_output=True, text=True)
        drives_new = result.stdout.strip().split("\n")
        if time.time() - start_time > timeout:
             print("Blad, nie wykryto nowego urzadzenia")
             break
        added_device = [dev for dev in drives_new if dev not in drives]
        if added_device:
             new_device = added_device[0]
             print("nowe urzadzenie zostalo podlaczone:", new_device)
             return new_device
        # Zakładamy, że pierwszy znaleziony napęd jest tym, który należy zamontować
               
def create_checksum_and_image(mount_point):
    """Tworzy sumę kontrolną oraz kopię obrazu nośnika"""
    try:
        image_path = f"{mount_point.replace('/mnt/', '')}_backup.img"
        mount_point_path = f"/dev/{mount_point}"
        checksum_path = f"{image_path}.sha256"
        checksum_mount_path = f"{mount_point}.sha256"

        # Tworzenie obrazu za pomocą dd
        log_message(f"Rozpoczęto tworzenie obrazu {image_path}...")
        subprocess.run([f"sudo", "dd", f"if=/dev/{mount_point}", f"of={image_path}", "bs=4M", "status=progress"],check=True)
        log_message(f"Obraz nośnika zapisany jako {image_path}.")
        hash_file(mount_point)
        subprocess.run(['sudo','umount',f"/dev/{mount_point}"], check=True)
        print("mozesz wysunac nosnik danych")
    except Exception as e:
        log_message(f"Błąd podczas tworzenia obrazu: {e}")
        
        
def mount_from_img(mount_point):
    try: 
        image_path = f"{mount_point.replace('/mnt/', '')}_backup.img"
        log_message(f"Rozpoczęto montowanie obrazu {image_path}...")
        if not os.path.exists(f"/media/{mount_point}_backup"):
            subprocess.run(["sudo","mkdir", f"/media/{mount_point}_backup" ],text=True ,check=True)
        losetup_result = subprocess.run(['sudo','losetup', '--show', '-f', f"{mount_point}_backup.img"], capture_output=True, text=True ,check=True)
        loop_device = losetup_result.stdout.strip()
        subprocess.run(['sudo','mount',loop_device, f"/media/{mount_point}_backup"], check=True)
        log_message(f"Obraz nośnika poprawnie zamontowany.")
        hash_file(detect_name_drive())
    except Exception as e:
        log_message(f"Błąd podczas montowania obrazu {e}") 

def check_partition(mount_point): #gdzie mount_point /dev/NAME
    """Analizuje strukturę partycji za pomocą fdisk i mmls."""
    print("analizuje strukture partycji")
    # Sprawdzanie struktury partycji za pomocą `fdisk`
    path_to_mount = "/dev/"+mount_point
    fdisk_output = subprocess.run(["sudo","fdisk", "-l", path_to_mount], capture_output=True, text=True)
    if fdisk_output.returncode == 0:
        for line in fdisk_output.stdout.splitlines():
            #print(line)
            if "Units:" in line:  # Filtrujemy tylko linie dotyczące partycji
                match = re.search(r'(\d+)$', line)
                if match:
                    offset = match.group(1)  # Pobieramy znalezioną liczbę
        log_message(f"\nStruktura partycji przy użyciu fdisk zapisana do pliku raportu.")
        #print(fdisk_output)
        raport_message(f"\nStruktura partycji przy użyciu fdisk {fdisk_output.stdout}")
        
    else:
        print(f"Błąd fdisk: {fdisk_output.stderr}")
        log_message(f"Błąd fdisk: {fdisk_output.stderr}")



def file_analysis(mount_point):
    """Analizuje metadane plików za pomocą fls i istat."""
    # Użycie `fls` do wylistowania plików na pierwszej partycji
    path_to_mount = "/dev/"+mount_point
    fls_output = subprocess.run(["sudo","fls", path_to_mount], capture_output=True, text=True)  #gdzie mount_point /dev/NAME
	
    if fls_output.returncode == 0:
        raport_message(f"\nWylistowanie plików przy użyciu fls:")
        raport_message(fls_output.stdout)
        log_message(f"\nWylistowanie plików przy użyciu fls zapisana do pliku raportu.")	
        inode_ids = re.findall(r'\b\d{2,6}\b', fls_output.stdout)  # Pobranie numerów inode
        for inode in inode_ids:
            print(f"\nMetadane pliku o inode {inode}:")
            istat_output = subprocess.run(["sudo","istat", path_to_mount, inode], capture_output=True, text=True)
            print(istat_output.stdout)
            raport_message(istat_output.stdout)
            return 1
    else:
        print(f"Błąd fdisk: {fls_output.stderr}")
        log_message(f"Błąd fdisk: {fls_output.stderr}")
        return 0

        
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
            
            #zapontowanie nowego nosnika z obrazu 
            mount_from_img(mount_point)
            
            new_drive = detect_name_drive()
            
            # Krok 4: Badanie struktury partycji obrazu 
            check_partition(new_drive)
            
            # Ktok 5: Analiza plików
            if file_analysis(new_drive) == 1:
                break

            # Odmontowanie nośnika po zakończeniu pracy
            subprocess.run(f"sudo umount {mount_point}", shell=True)
            log_message(f"Nośnik {mount_point} został odmontowany.")
        
        # Odczekaj przed kolejną iteracją (np. 60 sekund)
        time.sleep(60)

if __name__ == "__main__":
    main()
