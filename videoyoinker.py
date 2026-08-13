import yt_dlp
import os

# Códigos de color ANSI
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Ruta de la descarga (modifica 'Escritorio' si tu SO está en otro idioma o quieres que se descargen por defecto en otra carpeta)
desktop_path = os.path.join(os.path.expanduser('~'), 'Escritorio')

def download_video(url, quality):
    # Configuración mejorada para yt-dlp
    ydl_opts = {
        'format': quality,  # Formato simplificado
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(desktop_path, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor', # Fuerza la conversión a mp4 por si falla
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegMetadata', # Añadir metadatos al video
            },
            {
                'key': 'EmbedThumbnail', # Incrustar miniatura (reemplazo más estable)
            },
        ],
        'writethumbnail': True, # Descargar la miniatura
        
        # Opciones adicionales para evitar errores
        'nocheckcertificate': True,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n{Colors.YELLOW}[!] Obteniendo información del video...{Colors.RESET}")
            
            try:
                info_dict = ydl.extract_info(url, download=False)
                print(f"\n{Colors.BLUE}📹 Vídeo: {Colors.RESET} {info_dict.get('title', 'Sin título')}")
                print(f"{Colors.BLUE}⏱️ Duración: {Colors.RESET} {info_dict.get('duration', 0) // 60} minutos")
            except Exception as info_error:
                print(f"{Colors.YELLOW} [!] No se pudo obtener información previa: {info_error}{Colors.RESET}")
                print(f"{Colors.YELLOW}    Intentando descarga directa...{Colors.RESET}")
            
            print(f"\nDescargando...")
            ydl.download([url])
            
            print(f"\n{Colors.GREEN}[+] ¡Descarga completada!{Colors.RESET}")
            print(f"{Colors.BLUE}[+] Guardado en: {desktop_path}{Colors.RESET}")

    except Exception as e:
        print(f"\n{Colors.RED}[*] Error al descargar: {e}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}[!] Sugerencias:{Colors.RESET}")
        print(f"   1. Actualiza yt-dlp: {Colors.CYAN}pip install --upgrade yt-dlp{Colors.RESET}")
        print("   2. Verifica que FFmpeg esté instalado")
        print("   3. Algunos sitios (TikTok, Instagram) pueden requerir cookies")
        print("   4. Prueba con otra calidad o URL diferente")

def main():
    print(f"""{Colors.MAGENTA}
        ╦  ╦╦╔╦╗╔═╗╔═╗  ╦ ╦╔═╗╦╔╗╔╦╔═╔═╗╦═╗
        ╚╗╔╝║ ║║║╣ ║ ║  ╚╦╝║ ║║║║║╠╩╗║╣ ╠╦╝
         ╚╝ ╩═╩╝╚═╝╚═╝   ╩ ╚═╝╩╝╚╝╩ ╩╚═╝╩╚═
    {Colors.RESET}""")
    print("=" * 51)
    print(f"{Colors.BOLD}        - Descargador Universal de Vídeos -{Colors.RESET}")

    print("            Compatible con 1800+ sitios")
    print("=" * 51)
    
    url = input(f"\n{Colors.BOLD} URL del video:{Colors.RESET} ").strip()
    
    if not url:
        print(f"{Colors.RED}[*] La URL no puede estar vacía.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD} Selecciona la calidad:{Colors.RESET}")
    print("  1. 1080p (Full HD)")
    print("  2. 720p (HD)")
    print("  3. 480p (SD)")
    print("  4. Mejor disponible")
    
    quality_option = input(f"\n{Colors.BOLD}Elige (1-4):{Colors.RESET} ").strip()

    # Formatos simplificados que funcionan mejor
    quality_map = {
        "1": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
        "2": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
        "3": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
        "4": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
    }

    quality = quality_map.get(quality_option)
    
    if not quality:
        print(f"{Colors.RED}[*] Opción no válida.{Colors.RESET}")
        return

    download_video(url, quality)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!]  Operación cancelada por el usuario.{Colors.RESET}")
        exit(0)