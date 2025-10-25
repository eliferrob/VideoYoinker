import yt_dlp
import os

# Ruta del escritorio del usuario
desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')

# Función para descargar el video
def download_video(url, quality):
    # Configuración de opciones para yt-dlp
    ydl_opts = {
        'format': f'{quality}+bestaudio[ext=mp4]',  # Video + Audio
        'merge_output_format': 'mp4',  # Formato de salida
        'outtmpl': os.path.join(desktop_path, '%(title)s.%(ext)s'),  # Ruta para guardar el archivo (en este caso, el escritorio)
        'postprocessors': [
            {
                'key': 'EmbedThumbnail',  # Incrustar miniatura (reemplazo más estable)
            },
            {
                'key': 'FFmpegMetadata',  # Añadir metadatos al video
            },
        ],
        'writethumbnail': True,  # Descargar la miniatura
    }

    try:
        # Crear una instancia de yt_dlp con las opciones configuradas
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Descargar el video
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)  # Ruta del archivo descargado

    except Exception as e:
        print(f"Hubo un problema al descargar el video: {e}")

# Función principal para el menú
def main():
    print("Menú de Descarga de Video")
    print("--------------------------")
    url = input("Introduce la URL del video: ")

    if not url:
        print("La URL no puede estar vacía.")
        return

    print("\nSelecciona la calidad del video:")
    print("1. 1080p")
    print("2. 720p")
    quality_option = input("Elige 1 o 2: ")

    if quality_option == "1":
        quality = 'bestvideo[height<=1080][ext=mp4]'
    elif quality_option == "2":
        quality = 'bestvideo[height<=720][ext=mp4]'
    else:
        print("Opción no válida.")
        return

    # Llamar a la función para descargar el video
    download_video(url, quality)

if __name__ == "__main__":
    main()
