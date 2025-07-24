# LAWW

![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)

LAWW es una aplicación para monitorizar y gestionar descargas de ficheros de forma sencilla y automatizada. Está pensada para facilitar la descarga de listas de IPTV en Zeronet y crear copias de seguridad periódicas.

## ¿Cómo funciona?
Mediante la configuración de `targets` es posible especificar qué archivos monitorizar. LAWW se encarga de descargar, comprobar y guardar según haya sido configurado, ofreciendo diferentes opciones de personalización.

## Características
- Monitorización de varios archivos a la vez.
- Compatible con Zeronet.
- Subida de ficheros automática a repositorio en GitHub.
- Listo para desplegar en Docker.

## Despliegue
1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/rsoldado/laww.git
   cd laww
   ```
2. **Configuración:**
   - Crea los ficheros de configuración `config.yaml` y `.env` con las preferencias de configuración y archivos objetivos.

3. **Arranca el servicio:**
   ```bash
   docker-compose up -d --build
   ```

## Configuración
- El archivo `config.yaml` controla el comportamiento de la aplicación y es necesario para el despliegue. El fichero `example.config.yaml` contiene ejemplos de configuración sobre los ficheros objetivos.
- Para algunos casos, puedes necesitar crear un fichero `.env` con variables de entorno opcionales. El fichero `example.env` contiene ejemplos de variables de entorno opcionales.

## Información adicional
- Los archivos descargados se guardan en `data/downloads` y los logs en `data/logs`.
- Puedes modificar los puertos y rutas en `docker-compose.yml` si lo necesitas, por defecto se expone el puerto de Zeronet para crear un proxy.

