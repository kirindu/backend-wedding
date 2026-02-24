Para correr el proyecto


Si es primera vez hay que preparar el ambiente virtual :

pipx install virtualenv
pipx ensurepath
virtualenv entorno
source entorno/bin/activate
python3 -m pip install --upgrade pip 
python3 -m pip install "fastapi[standard]"
python3 -m pip install -r requirements.txt

Lueco cierra y abre el proyecto para que las librerias se refresquen

Luego solo nos aseguramos que seleccionamos el interpretador correcto, (SHIFT + CTRL + P) o en mac (SHIFT + COMMAND + P)

______________________________________________
Ya una vez teniendo el poyecto configurado solo lo corremos uno de estos dos comandos, el segundo activa la funcion hot reload
uvicorn main:app --port 3500
uvicorn main:app --reload --port 3500


___________________________________________________________________________________________

