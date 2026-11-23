# Imagen de contenedor para la entrada de Tcl. Ejecútala con: sandbox/container/run-image.sh src/tcl-weird
# Nada que compilar: tclsh ejecuta el script. La base de ejecución trae Tcl/Tk, el paquete sqlite3 de Tcl,
# Xvfb y scrot (el arnés inicia la pantalla virtual y toma una captura de la ventana),
# y ningún compilador ni gestor de paquetes. La ventana se cierra sola cuando el arnés la detiene.
FROM cc-rt-tcl:local
COPY timecards.tcl /app/timecards.tcl
ENV CC_XVFB=1
ENV CC_GUI_SECONDS=4
ENV CC_RUN="tclsh8.6 /app/timecards.tcl --gui"
