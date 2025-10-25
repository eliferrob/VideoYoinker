# VideoYoinker

Script creado en Python que emplea la herramienta **yt-dlp** para descargar vídeos de distintas plataformas multimedia (¡compatible con más de 1800 sitios web!). Ofrece la opción de elegir la calidad del vídeo (1080p, 720p, 480p o la mejor disponible) e incrusta, a su vez, la miniatura.
La descarga se hará con la mejor calidad de imagen y sonido en función de la opción seleccionada, y el fichero resultante se guardará en el escritorio del usuario en formato `mp4`.

## Requisitos

- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp/releases)
- [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases) (para fusionar audio/vídeo)

## Instalación

Tan sencillo como clonar el repositorio o descargarse el script.

```bash
git clone https://github.com/eliferrob/VideoYoinker.git
```

## Uso

```bash
python videoyoinker.py
```

Introduce la URL del vídeo y selecciona la calidad deseada.

Para ver la lista completa de sitios compatibles: `yt-dlp --list-extractors`
