# -*- coding: utf-8 -*-
"""Jmg SuiteMultimedia - lanzador (JMG, 13-11-2026): «en vez de anclar los dos programas por separado, Jmg SuiteMultimedia: al pulsarlo
sale una ventana para escoger uno u otro, con una pequeña descripción de lo que hace cada uno».
Instalado o portable: está en «Jmg Software\\Jmg SuiteMultimedia» y los programas en las carpetas de al lado. Desde el código fuente,
abre los main.pyw de «Jmg AudioProcesador 5.1» y «Jmg VideoEncoder». Los textos, en el idioma de Windows (los 9 de la ayuda)."""
import os, re, sys, subprocess, shutil
import tkinter as tk
from imagenes import LOGO, ICO_AP, ICO_VE

F_ = "#232323"; TARJ = "#2b2b2b"; BORDE = "#3c3c3c"; VERDE = "#34a853"; TXT = "#e0e0e0"; GRIS = "#969696"; DESC = "#c8c8c8"
TEXTOS = {
 "es": ("Elige un programa", "Abrir", "No instalado",
        "Procesa, convierte y ajusta las pistas de audio de tus películas: volumen, voces, graves, sincronía, Dolby Digital, DTS, FLAC… Para el 5.1 y el estéreo.",
        "Convierte y comprime vídeos (H.264, H.265, AV1…) con el procesador o la tarjeta gráfica, conservando audios y subtítulos. También DVD y Blu-ray."),
 "en": ("Choose a program", "Open", "Not installed",
        "Processes, converts and adjusts the audio tracks of your movies: volume, voices, bass, sync, Dolby Digital, DTS, FLAC… For 5.1 and stereo.",
        "Converts and compresses videos (H.264, H.265, AV1…) with the processor or the graphics card, keeping audio tracks and subtitles. Also DVD and Blu-ray."),
 "fr": ("Choisissez un programme", "Ouvrir", "Non installé",
        "Traite, convertit et ajuste les pistes audio de vos films : volume, voix, basses, synchro, Dolby Digital, DTS, FLAC… Pour le 5.1 et la stéréo.",
        "Convertit et compresse les vidéos (H.264, H.265, AV1…) avec le processeur ou la carte graphique, en gardant pistes audio et sous-titres. DVD et Blu-ray aussi."),
 "de": ("Programm wählen", "Öffnen", "Nicht installiert",
        "Bearbeitet, konvertiert und optimiert die Tonspuren Ihrer Filme: Lautstärke, Stimmen, Bass, Synchronität, Dolby Digital, DTS, FLAC… Für 5.1 und Stereo.",
        "Konvertiert und komprimiert Videos (H.264, H.265, AV1…) mit dem Prozessor oder der Grafikkarte und behält Tonspuren und Untertitel. Auch DVD und Blu-ray."),
 "pt": ("Escolha um programa", "Abrir", "Não instalado",
        "Processa, converte e ajusta as faixas de áudio dos seus filmes: volume, vozes, graves, sincronia, Dolby Digital, DTS, FLAC… Para 5.1 e estéreo.",
        "Converte e comprime vídeos (H.264, H.265, AV1…) com o processador ou a placa gráfica, mantendo faixas de áudio e legendas. Também DVD e Blu-ray."),
 "ru": ("Выберите программу", "Открыть", "Не установлена",
        "Обрабатывает, конвертирует и настраивает звуковые дорожки ваших фильмов: громкость, голоса, бас, синхронизация, Dolby Digital, DTS, FLAC… Для 5.1 и стерео.",
        "Конвертирует и сжимает видео (H.264, H.265, AV1…) процессором или видеокартой, сохраняя звуковые дорожки и субтитры. Также DVD и Blu-ray."),
 "hi": ("एक प्रोग्राम चुनें", "खोलें", "इंस्टॉल नहीं है",
        "आपकी फ़िल्मों के ऑडियो ट्रैक को प्रोसेस, कन्वर्ट और एडजस्ट करता है: वॉल्यूम, आवाज़ें, बेस, सिंक, Dolby Digital, DTS, FLAC… 5.1 और स्टीरियो के लिए।",
        "प्रोसेसर या ग्राफ़िक्स कार्ड से वीडियो (H.264, H.265, AV1…) कन्वर्ट और कंप्रेस करता है, ऑडियो ट्रैक और सबटाइटल बनाए रखते हुए। DVD और Blu-ray भी।"),
 "zh": ("选择一个程序", "打开", "未安装",
        "处理、转换和调整电影的音轨：音量、人声、低音、同步、Dolby Digital、DTS、FLAC…… 适用于 5.1 和立体声。",
        "使用处理器或显卡转换和压缩视频（H.264、H.265、AV1……），保留音轨和字幕。也支持 DVD 和蓝光。"),
 "ja": ("プログラムを選んでください", "開く", "インストールされていません",
        "映画の音声トラックを処理・変換・調整します：音量、声、低音、同期、Dolby Digital、DTS、FLAC… 5.1 とステレオに対応。",
        "プロセッサーまたはグラフィックカードで動画（H.264、H.265、AV1…）を変換・圧縮し、音声トラックと字幕はそのまま残します。DVD と Blu-ray にも対応。"),
}
FUENTES = {"zh": "Microsoft YaHei UI", "ja": "Yu Gothic UI", "hi": "Nirmala UI"}

def idioma():
    """el idioma de Windows (o de Linux) si es uno de los 9; si no, inglés"""
    try:
        if sys.platform == "win32":
            import ctypes
            n = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF
            c = {0x0A: "es", 0x09: "en", 0x0C: "fr", 0x07: "de", 0x16: "pt", 0x19: "ru", 0x39: "hi", 0x04: "zh", 0x11: "ja"}.get(n, "en")
        else:
            c = (os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or "en")[:2].lower()
        return c if c in TEXTOS else "en"
    except Exception:
        return "en"

def aqui():
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

def version_exe(p):
    """la versión de producto de un .exe (Windows), p. ej. «1.5»"""
    try:
        import ctypes, ctypes.wintypes as W
        v = ctypes.windll.version
        n = v.GetFileVersionInfoSizeW(p, None)
        if not n: return ""
        b = ctypes.create_string_buffer(n); v.GetFileVersionInfoW(p, 0, n, b)
        r = ctypes.c_void_p(); l = W.UINT()
        if v.VerQueryValueW(b, "\\VarFileInfo\\Translation", ctypes.byref(r), ctypes.byref(l)) and l.value >= 4:
            lg, cp = ctypes.cast(r, ctypes.POINTER(ctypes.c_ushort * 2)).contents
            q = f"\\StringFileInfo\\{lg:04X}{cp:04X}\\ProductVersion"
            if v.VerQueryValueW(b, q, ctypes.byref(r), ctypes.byref(l)) and l.value: return ctypes.wstring_at(r, l.value - 1)
    except Exception:
        pass
    return ""

def buscar(exe, carpeta_fuente, paquete_linux):
    """(orden para abrirlo, versión) o (None, "") si no está"""
    a = aqui()
    if getattr(sys, "frozen", False):
        p = os.path.join(os.path.dirname(a), exe, exe + (".exe" if sys.platform == "win32" else ""))
        if os.path.isfile(p): return [p], version_exe(p)
    else:
        m = os.path.join(os.path.dirname(os.path.dirname(a)), carpeta_fuente, "main.pyw")
        if os.path.isfile(m):
            ver = ""
            try: ver = re.search(r'^VERSION_PROG="([^"]+)"', open(m, encoding="utf-8").read(), re.M).group(1)
            except Exception: pass
            py = (shutil.which("pythonw") or sys.executable) if sys.platform == "win32" else sys.executable
            return [py, m], ver
    p = shutil.which(paquete_linux)
    if p: return [p], ""
    return None, ""

def version_suite():
    if getattr(sys, "frozen", False): return version_exe(sys.executable)
    try:
        t = open(os.path.join(os.path.dirname(aqui()), "suite.iss"), encoding="utf-8").read()
        return re.search(r'#define MyAppVersion "([^"]+)"', t).group(1)
    except Exception:
        return ""

def main():
    lg = idioma(); tit, abrir, falta, d_ap, d_ve = TEXTOS[lg]
    fam = FUENTES.get(lg, "Segoe UI" if sys.platform == "win32" else "")
    root = tk.Tk(); root.withdraw(); root.title("Jmg SuiteMultimedia")   # oculta hasta estar colocada (si no, asoma pequeña y negra)
    root.title("Jmg SuiteMultimedia"); root.configure(bg=F_); root.resizable(False, False)
    try:
        ico = os.path.join(getattr(sys, "_MEIPASS", aqui()), "JmgSuite.ico")
        if not os.path.isfile(ico): ico = os.path.join(os.path.dirname(aqui()), "JmgSuite.ico")
        if sys.platform == "win32" and os.path.isfile(ico): root.iconbitmap(ico)
    except Exception:
        pass
    imgs = {k: tk.PhotoImage(data=v) for k, v in (("logo", LOGO), ("ap", ICO_AP), ("ve", ICO_VE))}
    marco = tk.Frame(root, bg=F_, highlightthickness=1, highlightbackground="#2e7d32"); marco.pack(fill="both", expand=True)
    tk.Label(marco, image=imgs["logo"], bg=F_, bd=0).pack(pady=(22, 6))
    tk.Label(marco, text=tit, font=(fam, 13, "bold"), fg=TXT, bg=F_).pack(pady=(4, 14))
    fila = tk.Frame(marco, bg=F_); fila.pack(padx=22)
    tarjetas = []
    def tarjeta(col, img, nombre, desc, orden, ver):
        ok = orden is not None
        t = tk.Frame(fila, bg=TARJ, highlightthickness=2, highlightbackground=BORDE, highlightcolor=BORDE, cursor="hand2" if ok else "arrow", width=330, height=292)
        t.grid(row=0, column=col, padx=10, sticky="n"); t.grid_propagate(False); t.pack_propagate(False)
        tk.Label(t, image=img, bg=TARJ, bd=0).pack(pady=(18, 8))
        tk.Label(t, text=nombre, font=(fam, 13, "bold"), fg=TXT if ok else GRIS, bg=TARJ).pack()
        tk.Label(t, text=("v" + ver) if ver else "", font=(fam, 9), fg=GRIS, bg=TARJ).pack()
        tk.Label(t, text=desc, font=(fam, 9), fg=DESC if ok else GRIS, bg=TARJ, wraplength=290, justify="center").pack(padx=14, pady=(6, 8))
        bt = tk.Label(t, text=("▶  " + abrir) if ok else falta, font=(fam, 10, "bold"), fg=VERDE if ok else GRIS, bg=TARJ)
        bt.pack(side="bottom", pady=(0, 14))
        def ir(e=None):
            if not ok: return
            try:
                subprocess.Popen(orden, cwd=os.path.dirname(orden[-1]), close_fds=True)
            except Exception as ex:
                try:
                    from tkinter import messagebox
                    messagebox.showerror("Jmg SuiteMultimedia", str(ex)); return
                except Exception:
                    return
            root.after(300, root.destroy)
        def luz(on):
            if ok: t.configure(highlightbackground=VERDE if on else BORDE)
        for w in [t] + t.winfo_children():
            w.bind("<Button-1>", ir); w.bind("<Enter>", lambda e: luz(True)); w.bind("<Leave>", lambda e: luz(False))
        tarjetas.append(ir)
    o_ap, v_ap = buscar("Jmg AudioProcesador", "Jmg AudioProcesador 5.1", "jmg-audioprocesador")
    o_ve, v_ve = buscar("Jmg VideoEncoder", "Jmg VideoEncoder", "jmg-videoencoder")
    tarjeta(0, imgs["ap"], "Jmg AudioProcesador 5.1", d_ap, o_ap, v_ap)
    tarjeta(1, imgs["ve"], "Jmg VideoEncoder", d_ve, o_ve, v_ve)
    vs = version_suite()
    tk.Label(marco, text=("Jmg SuiteMultimedia " + vs).strip() + "  ·  Jmg Software", font=(fam, 8), fg=GRIS, bg=F_).pack(pady=(14, 14))
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("1", lambda e: tarjetas[0]()); root.bind("2", lambda e: tarjetas[1]())
    root.update_idletasks(); w, h = root.winfo_reqwidth(), root.winfo_reqheight()
    root.geometry(f"{w}x{h}+{(root.winfo_screenwidth() - w) // 2}+{(root.winfo_screenheight() - h) // 2}")
    root.deiconify(); root.lift(); root.focus_force()
    root.mainloop()

if __name__ == "__main__":
    main()
