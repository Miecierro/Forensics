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

def hash_file_original(ext_drive):
    """Obliczenie hasha"""
    output_file = f"{ext_drive}_sha256.txt"
    file_path = f"/dev/{ext_drive}"

    try:
        # Wywoluje komende ktora tworzy hash i zapisuje do pliku
        with open(output_file, "a") as f:
            subprocess.run(["sudo", "sha1sum", file_path], stdout=f, check=True)
        log_message(f" Generowanie sumy kontrolnej przebieglo pomyslnie")

    # Błąd podczas uruchamiania polecenia subprocess
    except subprocess.CalledProcessError as e:
        log_message("Błąd podczas generowani sumy kontrolnej: {e}")

    # Błąd podczas pracy z plikiem
    except IOError as e:
        log_message(f"Błąd podczas zapisu do pliku: {e}")

def hash_file_copy(ext_drive):
    """Obliczenie hasha"""
    output_file = f"{ext_drive}_backup_sha256.txt"
    file_path = f"{ext_drive}_backup.img"

    try:
    # Wywoluje komende ktora tworzy hash i zapisuje do pliku
        with open(output_file, "a") as f:
            subprocess.run(["sudo", "sha1sum", file_path ], stdout=f, check=True)
        log_message(f" Generowanie sumy kontrolnej przebieglo pomyslnie")

    # Błąd podczas uruchamiania polecenia subprocess
    except subprocess.CalledProcessError as e:
        log_message("Błąd podczas generowani sumy kontrolnej: {e}")

    # Błąd podczas pracy z plikiem
    except IOError as e:
        log_message(f"Błąd podczas zapisu do pliku: {e}")

def document_vm_configuration():
    """Zapisuje informacje o konfiguracji maszyny wirtualnej do pliku"""
    try:
        # Pobiera podstawowe informacje o systemie
        uname_output = subprocess.check_output("uname -a", shell=True).decode()
        cpu_info = subprocess.check_output("lscpu", shell=True).decode()
        mem_info = subprocess.check_output("free -h", shell=True).decode()

        # Zapisuje do pliku
        with open("vm_configuration.txt", "w") as file:
            file.write("=== Konfiguracja maszyny wirtualnej ===\n")
            file.write(f"System:\n{uname_output}\n")
            file.write(f"Informacje o procesorze:\n{cpu_info}\n")
            file.write(f"Informacje o pamięci:\n{mem_info}\n")

        log_message("Dokumentacja konfiguracji maszyny wirtualnej została zapisana.")
    except Exception as e:
        log_message(f"Błąd podczas dokumentacji konfiguracji: {e}")

def detect_name_drive():
    """Automatyczne wykrywanie nowych nośników"""
    # Wykrywanie podłączonych urządzeń
    try:
        result = subprocess.run(["lsblk", "-r", "-o", "NAME"], capture_output=True, text=True)
        drives = result.stdout.strip().split("\n")
        loop_elements = [item for item in drives if re.match(r"loop\d+$", item)]
        if loop_elements:
            recent = loop_elements[-1]
            return recent
        else:
            log_message("Nie znaleziono żadnych urządzeń typu loop")
            return None
    except Exception as e:
        log_message(f"Błąd podczas szukania urzadzenia: {e}")
        return None

def detect_drive():
    """Automatyczne wykrywanie nowych nośników i montowanie ich w trybie read-only"""
    # Wykrywanie podłączonych urządzeń
    try:
            initial_drives = subprocess.run(["lsblk", "-r", "-o", "NAME"], capture_output=True, text=True, check=True).stdout.strip().split("\n")
            log_message("Proszę podłączyć nośnik danych...")
            start_time = time.time()
            timeout = 60

            while time.time() - start_time < timeout:
                current_drives = subprocess.run(["lsblk", "-r", "-o", "NAME"], capture_output=True, text=True, check=True).stdout.strip().split("\n")
                new_device = [dev for dev in current_drives if dev not in initial_drives]
                if new_device:
                    log_message(f"Nowe urządzenie zostało podłączone: {new_device[0]}")
                    return new_device[0]
                time.sleep(2)
            log_message(f"Nie wykryto nowego urządzenia w czasie oczekiwania.")
            return None

    except subprocess.SubprocessError as e:
            log_message(f"Błąd podczas wykrywania urządzeń: {e}")
            return None

#    result = subprocess.run(["lsblk", "-r", "-o", "NAME"], capture_output=True, text=True)
#   drives = result.stdout.strip().split("\n")
#    print("Prosze podłączyc nośnik danych...")
#    new_device = None
#    start_time = time.time()
#    timeout = 60
#    # Jeżeli w wyniku komendy lsblk rozponano nowe urządzone, rejestrowany jest nowy nośnik
#    while True:
#        result = subprocess.run(["lsblk", "-r", "-o", "NAME"],capture_output=True, text=True)
#        drives_new = result.stdout.strip().split("\n")
#        # Niewykrycie nowego nośnika
#        if time.time() - start_time > timeout:
#             print("Błąd: Nie wykryto nowego urzadzenia")
#             break
#        # Wykrycie nowego nośnika
#        added_device = [dev for dev in drives_new if dev not in drives]
#        if added_device:
#             new_device = added_device[0]
#             print("Nowe urządzenie zostało podłączone:", new_device)
#             return new_device
#        # Zakładamy, że pierwszy znaleziony napęd jest tym, który należy zamontować

def create_checksum_and_image(ext_drive):
    """Tworzy sumę kontrolną oraz kopię obrazu nośnika"""
    try:
        image_path = f"{ext_drive.replace('/mnt/', '')}_backup.img"
        """Obliczenie hasha przed kopiowaniem"""
        hash_file_original(ext_drive)
        log_message(f" Generowanie sumy kontrolnej przed kopiowaniem obrazu")

        # Tworzenie obrazu za pomocą dd
        log_message(f"Rozpoczęto tworzenie obrazu {image_path}...")

        subprocess.run([f"sudo", "dd", f"if=/dev/{ext_drive}", f"of={image_path}", "bs=4M", "status=progress"], check=True)
        log_message(f"Obraz nośnika zapisany jako {image_path}.")

        # Tworzenie sumy kontrolnej oryginalnego nośnika
        """Obliczenie hasha po kopiowaniu"""
        hash_file_original(ext_drive)
        log_message(f" Generowanie sumy kontrolnej po kopiowaniu obrazu")

        ## Odmontywanie oryginalnego nośnika
        #subprocess.run(['sudo','umount',f"/dev/{ext_drive}"], check=True)
        #print("Mozesz wysunac nosnik danych")

    except Exception as e:
        log_message(f"Błąd podczas tworzenia obrazu: {e}")


def mount_from_img(ext_drive):
    # Montowanie nowego nośnika dysku
    try:
        image_path = f"{ext_drive.replace('/mnt/', '')}_backup.img"
        log_message(f"Rozpoczęto montowanie obrazu {image_path}...")
        """Obliczenie hasha przed zamontowaniem"""
        hash_file_copy(ext_drive)
        log_message(f" Generowanie sumy kontrolnej przed zamontowaniem obrazu")

        # Tworzenie katalogu dla kopii zapasowej
        if not os.path.exists(f"/media/{ext_drive}_backup"):
            subprocess.run(["sudo","mkdir", f"/media/{ext_drive}_backup" ],text=True ,check=True)

        # Tworzenie urządzenia loopback dla pliku obrazu
        losetup_result = subprocess.run(['sudo','losetup', '--show', '-f', f"{ext_drive}_backup.img"], capture_output=True, text=True ,check=True)
        loop_device = losetup_result.stdout.strip()

        # Montowanie kopii zapasowej nośnika
        subprocess.run(['sudo','mount', '-ro', loop_device, f"/media/{ext_drive}_backup"], check=True)
        log_message(f"Obraz kopii nośnika poprawnie zamontowany.")

        # Generowanie sumy kontrolnej dla nowego nośnika po zamontowaniu
        """Obliczenie hasha po zamontowaniu"""
        hash_file_copy(ext_drive)
        log_message(f" Generowanie sumy kontrolnej po zamontowaniu obrazu")


    except Exception as e:
        log_message(f"Błąd podczas montowania obrazu {e}")

def check_partition(ext_drive): #gdzie mount_point /dev/NAME
    """Analizuje strukturę partycji za pomocą fdisk i mmls."""
    log_message("Analiza struktury partycji za pomocą fdisk")

    # Sprawdzanie struktury partycji za pomocą `fdisk`
    path_to_mount = "/dev/"+ ext_drive

    try:
        fdisk_output = subprocess.run(["sudo","fdisk", "-l", path_to_mount], capture_output=True, text=True, check=True)

        if fdisk_output.returncode == 0:
            for line in fdisk_output.stdout.splitlines():
                if "Units:" in line:  # Filtrujemy tylko linie dotyczące partycji
                    match = re.search(r'(\d+)$', line)
                    if match:
                    #    offset = match.group(1)  # Pobieramy znalezioną liczbę ### NIGDZIE NIE JEST UŻYTA ZMIENNA PO CO ONA
                        log_message(f"\nStruktura partycji przy użyciu fdisk zapisana do pliku raportu.")
                        raport_message(f"\nStruktura partycji przy użyciu fdisk {fdisk_output.stdout}")

    except subprocess.CalledProcessError as e:
        log_message(f"Błąd podczas analizy partycji za pomocą fdisk: {e}")
        raport_message(f"Błąd fdisk:\n{e.stderr}")

    except Exception as e:
        log_message(f"Nieoczekiwany błąd: {e}")

def file_analysis(ext_drive):
    """Analizuje metadane plików za pomocą fls i istat."""
    log_message(f"Analiza metadanych plików na urządzeniu {ext_drive}.")

    path_to_mount = "/dev/"+ ext_drive

    try:
        fls_output = subprocess.run(["sudo","fls", path_to_mount], capture_output=True, text=True, check=True)

        raport_message(f"\nWylistowanie plików przy użyciu fls:")
        raport_message(fls_output.stdout)
        log_message(f"\nWylistowanie plików przy użyciu fls zapisana do pliku raportu.")

        #Pobieranie numerów inode
        inode_ids = re.findall(r'\b\d{2,6}\b', fls_output.stdout)
        if not inode_ids:
            log_message("Nie znaleziono żadnych numerów inode w wynikach fls")
            raport_message("Nie znaleziono żadnych numerów inode w wynikach fls")

        for inode in inode_ids:
            log_message(f"\nAnaliza metadanych o inode {inode}:")
            istat_output = subprocess.run(["sudo","istat", path_to_mount, inode], capture_output=True, text=True, check=True)
            raport_message(f"\n=== Metadane pliku o inode {inode} ===\n")
            raport_message(istat_output.stdout)
            log_message(f"Metadane pliku o inode {inode} zapisano do raportu")

        """Obliczenie hasha po analizie obrazu"""
        hash_file_copy(ext_drive)
        log_message(f" Generowanie sumy kontrolnej po analizie obrazu")
        return 1

    except subprocess.CalledProcessError as e:
        log_message(f"Błąd podczas analizy plików za pomocą fls lub istat: {e.stderr}")
        raport_message(f"Błąd podczas analizy plików: {e.stderr}")
        return 0
    except Exception as e:
        log_message(f"Nieoczekiwany błąd podczas analizy plików: {e}")
        return 0


def main():
    """Główna funkcja kontrolująca działanie skryptu"""
    log_message("=== Rozpoczęcie pracy skryptu ===")

    # Krok 1: Dokumentacja konfiguracji VM
    document_vm_configuration()

    while True:
        # Krok 2: Wykrywanie i montowanie nowego nośnika
        ext_drive = detect_drive()

        # Działanie na zamontowanym oryginalnym nośniku
        if ext_drive:
            # Krok 3: Tworzenie kopii oraz sumy kontrolnej oryginalnego obrazu i odmontowanie go
            create_checksum_and_image(ext_drive)

            # Krok 3: Zamontowanie nowego nosnika z obrazu
            mount_from_img(ext_drive)

            # Zapisanie nazwy ścieżki do zmiennej
            # Z TEGO CO ROZUMIEM TO ZAPISUJE ŚĆIEŻKĘ DO TEGO ORYGINALNEGO NOŚNIKA | W TYM MOMENCIE JUŻ NIE POWINNIŚMY NA NIM PRACOWAĆ | W SENSIE NIE MA TO AŻŻŻŻŻ TAKIEJ RÓŻNICY, BO JEST TO W READ-ONLY, ALE TO NIE JEST DOBRA PRAKTYKA
            new_drive = detect_name_drive()

            # Krok 4: Badanie struktury partycji obrazu
            check_partition(new_drive)

            # Ktok 5: Analiza plików
            if file_analysis(new_drive) == 1:
                break

            # Odmontowanie nośnika po zakończeniu pracy 
            subprocess.run(f"sudo umount {ext_drive}", shell=True)
            log_message(f"Nośnik {ext_drive} został odmontowany.")

            """Obliczenie hasha po odmontowaniu"""
            hash_file_copy(ext_drive)
            log_message(f" Generowanie sumy kontrolnej po odmontowaniu obrazu")

        # Odczekaj przed kolejną iteracją (np. 60 sekund)
        time.sleep(60)

if __name__ == "__main__":
    main()