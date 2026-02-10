# Para desarrolladores

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

## Documentación

Generar documentacion
```powershell
cd docs
.\make.bat html
```

## Distribución del programa

Compilar a .exe
```powershell
pyinstaller --onefile --windowed --icon=img/logo.png main.py
```


## Tests unitarios

Ejecutar tests unitarios (carpeta tests)
```powershell
python -m unittest test.tests
```

Métodos para test
![img.png](img.png)