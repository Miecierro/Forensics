# Forensics


**Temat:** System pasywnego pozyskiwania danych oraz metadanych z nośników z wykorzystaniem systemów dedykowanych do informatyki śledczej

**Opis projektu:** 
Stworzenie systemu mającego usprawnić proces biegłego sądowego mającego przeprowadzić proces analizy nośników danych. W ramach działania programu śledczy zostanie poinstruowany w celu minimalizacji błędów podczas pracy z nośnikiem minimalizując ryzyko zniszczenia dowodów. 
Jednocześnie system dokumentuje podjęte kroki zapewniając transparentność procesu. System ma na celu zapewnienie integralności oraz autentyczności danych pochodzących z nośnika przy jednoczesnym uzyskaniu niezbędnych informacji w tym metadanych. 
Całość procesu kończy się przygotowaniem stosownego raportu. 

---
**Cel projektu:**
Zwiększenie efektywności przy jednoczesnym zmniejszeniu inwazyjności procesu jakim jest pasywne pozyskiwanie danych z nośników.

---

**Informacje techniczne:**
- System operacyjny - Antix 23.2 x64
- Python 3.11.2
- Pip 23.0.1
- Karta SD
- Pendrive
- Czytnik kart SD
  
---

**Przygotowanie środowiska:**
Pobierz repozytorium kodu na systemie Linux. Aby poprawnie zainstalować wszystkie biblioteki należy postępować zgodnie z poniższą instrukcją.
1. Pobierz kod źródłowy z repozytorium dostępnego w poniższym linku:
      ```webside
         https://github.com/Miecierro/Forensics/
      ```
      Lub skorzyztaj z poniższego polecenia:

3. Utwórz nowe wirtualne środowisko wykonując poniższe polecenie:
       ```cmd
       python3 -m venv sledcza
       ```
5. Aktywuj środowisko wykonując poniższą komendę
       ```cmd
        source slecza/bin/activate
       ```
4. Zainstaluj wszystkie biblioteki z pliku requirements.txt
      ```cmd
        pip install -r requirements.txt
      ```


