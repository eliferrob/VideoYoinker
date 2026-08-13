import yt_dlp
import os
import sys
import subprocess
import re

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

# Sin 'formats: duplicate', yt-dlp oculta pistas de audio repetidas y solo
# muestra la marcada como "default". Sin forzar varios 'player_client',
# YouTube tampoco expone todas las pistas dobladas al cliente por defecto
# (android_vr/web/web_safari). Con esta combinación aparecen todas.
YOUTUBE_EXTRACTOR_ARGS = {
    'youtube': {
        'formats': ['duplicate'],
        'player_client': ['web', 'web_embedded', 'android', 'tv'],
    }
}


def get_available_audio_tracks(url):
    """Extrae la lista de pistas de audio disponibles (idiomas) para el video."""
    ydl_opts_probe = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': YOUTUBE_EXTRACTOR_ARGS,
    }
    tracks = {}
    with yt_dlp.YoutubeDL(ydl_opts_probe) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        for f in formats:
            lang = f.get('language')
            acodec = f.get('acodec')
            if lang and acodec and acodec != 'none':
                # Distinguimos pista original vs doblada vs "descriptive" (audiodescripción)
                note = f.get('format_note', '') or ''
                is_original = f.get('language_preference', 0) is not None and f.get('language_preference', 0) >= 10
                tag = ''
                if 'descriptive' in note.lower():
                    tag = ' - audiodescripción'
                elif is_original:
                    tag = ' - original'
                else:
                    tag = ' - doblado'
                label = f"{lang}{tag}"
                # Evita sobreescribir una entrada "original" con un duplicado peor etiquetado
                if lang not in tracks or 'original' in label:
                    tracks[lang] = label
    return info, tracks


def get_available_subtitles(info):
    """Combina subtítulos manuales y автоgenerados disponibles en el video."""
    manual_subs = info.get('subtitles', {}) or {}
    auto_subs = info.get('automatic_captions', {}) or {}
    return manual_subs, auto_subs


def download_video(url, quality, audio_lang, sub_langs, sub_source):
    """
    audio_lang: código de idioma de audio elegido o None (por defecto)
    sub_langs: lista de códigos de idioma de subtítulos a incrustar, o [] si no se quieren
    sub_source: 'manual', 'auto' o None
    """
    # Formato de descarga: si se especifica idioma de audio, se filtra por él
    if audio_lang:
        format_str = (
            f"bestvideo[ext=mp4]+bestaudio[language={audio_lang}][ext=m4a]/"
            f"bestvideo[ext=mp4]+bestaudio[language={audio_lang}]/"
            f"{quality}"
        )
    else:
        format_str = quality

    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(desktop_path, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegMetadata',
            },
            {
                'key': 'EmbedThumbnail',
            },
        ],
        'writethumbnail': True,
        'nocheckcertificate': True,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'extractor_args': YOUTUBE_EXTRACTOR_ARGS,
    }

    # Configuración de subtítulos
    if sub_langs:
        ydl_opts['writesubtitles'] = (sub_source == 'manual')
        ydl_opts['writeautomaticsub'] = (sub_source == 'auto')
        ydl_opts['subtitleslangs'] = sub_langs
        ydl_opts['subtitlesformat'] = 'srt/best'
        # Incrusta los subtítulos directamente en el contenedor mp4
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegEmbedSubtitle',
            'already_have_subtitle': False,
        })

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
        print("   2. Verifica que FFmpeg esté instalado y en el PATH")
        print("   3. Es posible que la pista de audio o subtítulo elegido no exista")
        print("   4. Prueba con otra calidad, idioma o URL diferente")


def elegir_pista_audio(url):
    """Muestra las pistas de audio disponibles y devuelve el código elegido (o None)."""
    print(f"\n{Colors.YELLOW}[!] Consultando pistas de audio disponibles...{Colors.RESET}")
    try:
        info, tracks = get_available_audio_tracks(url)
    except Exception as e:
        print(f"{Colors.RED}[*] No se pudo obtener información del video: {e}{Colors.RESET}")
        return None, None

    if not tracks:
        print(f"{Colors.YELLOW}[!] No se detectaron pistas de audio múltiples. Se usará el audio por defecto.{Colors.RESET}")
        return None, info

    print(f"\n{Colors.BOLD} Pistas de audio disponibles:{Colors.RESET}")
    codes = list(tracks.keys())
    for i, code in enumerate(codes, start=1):
        print(f"  {i}. {tracks[code]} [{code}]")
    print(f"  0. Usar audio por defecto")

    choice = input(f"\n{Colors.BOLD}Elige pista de audio (0-{len(codes)}):{Colors.RESET} ").strip()

    if choice == "0" or choice == "":
        return None, info
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(codes):
            return codes[idx], info
    except ValueError:
        pass

    print(f"{Colors.YELLOW}[!] Opción no válida, se usará el audio por defecto.{Colors.RESET}")
    return None, info


def elegir_subtitulos(info):
    """Muestra los subtítulos disponibles y devuelve (lista_idiomas, fuente)."""
    manual_subs, auto_subs = get_available_subtitles(info)

    if not manual_subs and not auto_subs:
        print(f"{Colors.YELLOW}[!] Este video no tiene subtítulos disponibles.{Colors.RESET}")
        return [], None

    quiere_subs = input(f"\n{Colors.BOLD}¿Incrustar subtítulos en el video? (s/n):{Colors.RESET} ").strip().lower()
    if quiere_subs != 's':
        return [], None

    # Preferimos subtítulos manuales (más precisos); si no hay, ofrecemos automáticos
    if manual_subs:
        source = 'manual'
        available = manual_subs
        print(f"\n{Colors.BOLD} Subtítulos manuales disponibles:{Colors.RESET}")
    else:
        source = 'auto'
        available = auto_subs
        print(f"\n{Colors.BOLD} Solo hay subtítulos automáticos disponibles:{Colors.RESET}")

    codes = list(available.keys())
    for i, code in enumerate(codes, start=1):
        print(f"  {i}. {code}")

    choice = input(f"\n{Colors.BOLD}Elige el número del idioma (o varios separados por coma):{Colors.RESET} ").strip()

    if not choice:
        return [], None

    selected = []
    for part in choice.split(","):
        part = part.strip()
        try:
            idx = int(part) - 1
            if 0 <= idx < len(codes):
                selected.append(codes[idx])
        except ValueError:
            continue

    if not selected:
        print(f"{Colors.YELLOW}[!] No se seleccionó ningún subtítulo válido.{Colors.RESET}")
        return [], None

    return selected, source


def main():
    print(f"""{Colors.MAGENTA}
        ╦  ╦╦╔╦╗╔═╗╔═╗  ╦ ╦╔═╗╦╔╗╔╦╔═╔═╗╦═╗
        ╚╗╔╝║ ║║║╣ ║ ║  ╚╦╝║ ║║║║║╠╩╗║╣ ╠╦╝
         ╚╝ ╩═╩╝╚═╝╚═╝   ╩ ╚═╝╩╝╚╝╩ ╩╚═╝╩╚═
    {Colors.RESET}""")
    print("=" * 51)
    print(f"{Colors.BOLD}   - Descargador YouTube: Audio y Subtítulos -{Colors.RESET}")
    print("=" * 51)

    url = input(f"\n{Colors.BOLD} URL del video de YouTube:{Colors.RESET} ").strip()

    if not url:
        print(f"{Colors.RED}[*] La URL no puede estar vacía.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD} Selecciona la calidad:{Colors.RESET}")
    print("  1. 1080p (Full HD)")
    print("  2. 720p (HD)")
    print("  3. 480p (SD)")
    print("  4. Mejor disponible")

    quality_option = input(f"\n{Colors.BOLD}Elige (1-4):{Colors.RESET} ").strip()

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

    # Pista de audio
    audio_lang, info = elegir_pista_audio(url)

    # Subtítulos (reutilizamos 'info' si ya lo obtuvimos)
    if info is None:
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception:
            info = {}

    sub_langs, sub_source = elegir_subtitulos(info)

    download_video(url, quality, audio_lang, sub_langs, sub_source)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!]  Operación cancelada por el usuario.{Colors.RESET}")
        exit(0)