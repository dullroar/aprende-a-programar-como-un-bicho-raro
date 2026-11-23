# Imagen de contenedor para la entrada Python/Tk. Ejecútala con: sandbox/container/run-image.sh --out ./results src/PythonChallenge1
# No hay nada que compilar. La base trae Python 3 con Tk, una pantalla virtual (Xvfb) y una herramienta de capturas, y no tiene pip ni
# compilador. La ventana de Tk se abre en la pantalla virtual dentro del contenedor; el punto de entrada le hace una captura
# tras unos segundos y la cierra. El programa escribe data/ junto a sí mismo, así que se ejecuta desde una copia privada.
FROM cc-rt-pytk:local
COPY program.py /app/program.py
ENV CC_RUN="python3 program.py" CC_WORKDIR=/work/run CC_COPY_APP=1 CC_XVFB=1 CC_SCREEN=800x500x24
