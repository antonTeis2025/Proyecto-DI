# Falta

- Pestaña de facturas corregir errores

# Usar

Crear el venv y instalar las dependencias
```powershell
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```
Iniciar el programa
```powersell
python main.py
```
Compilar la interfaz
```powershell
pyuic6 -o nombre_archivo.py nombre_archivo.ui
```

Generar documentacion
```powershell
cd docs
.\make.bat html
```

Compilar a .exe
```powershell
pyinstaller --onefile --windowed --icon=img/logo.png main.py
```