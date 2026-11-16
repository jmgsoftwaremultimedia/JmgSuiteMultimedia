# -*- coding: utf-8 -*-
"""Jmg VideoEncoder - GUI v1.4 (ES/EN)"""
import os,sys,json,threading,subprocess,re,locale,time,base64,shutil,tempfile,math,tkinter as tk
from tkinter import ttk,filedialog,messagebox
try:
    from tkinterdnd2 import TkinterDnD,DND_FILES
    _HAY_DND=True
except Exception:          # sin tkinterdnd2: todo funciona salvo arrastrar y soltar
    _HAY_DND=False
    class TkinterDnD:
        Tk=tk.Tk
    DND_FILES=None
CNW=0x08000000 if sys.platform=="win32" else 0
def _find_bin(name):
    """Localiza ffmpeg/ffprobe: primero en bin/ junto al exe, si no en PATH"""
    ext=".exe" if sys.platform=="win32" else ""
    base=os.path.dirname(os.path.abspath(sys.executable if getattr(sys,"frozen",False) else __file__))
    for cand in (os.path.join(base,"bin",name+ext),os.path.join(base,name+ext),
                 os.path.join(os.path.dirname(base),"bin",name+ext)):   # Jmg SuiteMultimedia: un solo FFmpeg en el «bin» de la carpeta de arriba
        if os.path.isfile(cand):return cand
    return name+ext
FFMPEG=_find_bin("ffmpeg");FFPROBE=_find_bin("ffprobe");FFPLAY=_find_bin("ffplay")
def _aften_bin():
    """Aften (codificador AC3), en el bin; en Linux, el del sistema si está"""
    a=_find_bin("aften")
    if os.path.isfile(a):return a
    import shutil as _sh
    return _sh.which("aften")
AFTEN=_aften_bin()
# (JMG, 8-11) los ajustes de Aften por defecto (exps 32, ancho de banda adaptable variable, sin DRC, dialnorm 31) y (9-11) la
# información del flujo: Dolby Surround EX, Dolby Headphone, conversor A/D, downmix preferido y sus niveles
def _af_migrar(x):
    """(JMG, 15-11) ajustes de Aften guardados antes de que cambiaran los de fábrica: si tienen los de entonces (ancho adaptable
    variable, sin conmutación de bloques), pasan a los nuevos (ancho fijo completo, con conmutación); lo elegido a mano se respeta"""
    x=dict(x or {})
    try:v=int(x.get("v",1) or 1)
    except (TypeError,ValueError):v=1
    if v<2:
        if x.get("w",-2)==-2:x["w"]=60
        if not x.get("bs",0):x["bs"]=1
        x["v"]=2
    return x
AFTEN_DEF={"cod":"aften","modo":"cbr","q":240,"w":60,"exps":32,"drc":5,"dnorm":31,"bs":1,"v":2,"bwf":0,"dcf":0,"lfef":0,"dsur":0,"dsurex":0,"dhead":0,"adconv":0,
           "cmix":0,"smix":0,"dmix":0,"ltrtc":4,"ltrts":4,"loroc":4,"loros":4,"extra":""}
AFTEN_LOGO="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"   # logotipo de Aften (aften.sourceforge.net)
def _ff_ruta(p):
    """ruta de archivo dentro de un filtro de FFmpeg (C:/... con los dos puntos y las comillas escapados)"""
    return "'"+p.replace("\\","/").replace(":","\\:").replace("'","\\'")+"'"
def _app_dir():
    if getattr(sys,"frozen",False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))
_DATA_DIR=None
def _data_dir():
    global _DATA_DIR
    if _DATA_DIR is None:_DATA_DIR=_data_dir_calc()
    return _DATA_DIR
def _data_dir_calc():
    """carpeta de ajustes y presets: junto al programa si se puede escribir (portable),
    si no (instalado en Archivos de programa) en %APPDATA%\\Jmg VideoEncoder"""
    a=_app_dir()
    try:
        t=os.path.join(a,".jmg_escritura_test")
        with open(t,"w",encoding="utf-8") as f:f.write("ok")
        os.remove(t);return a
    except OSError:pass
    if sys.platform=="win32":
        d=os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"),"Jmg VideoEncoder")
    else:
        d=os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"),".config"),"jmg-videoencoder")
    try:os.makedirs(d,exist_ok=True)
    except OSError:pass
    return d
def _area_trabajo(root):
    """zona util de la pantalla SIN la barra de tareas: (x, y, ancho, alto)"""
    if sys.platform=="win32":
        try:
            import ctypes
            from ctypes import wintypes
            r=wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x30,0,ctypes.byref(r),0):   # SPI_GETWORKAREA
                return r.left,r.top,r.right-r.left,r.bottom-r.top
        except Exception:pass
    return 0,0,root.winfo_screenwidth(),root.winfo_screenheight()-60
_MARCO=40   # borde + barra de titulo de Windows (aprox.)
_PUERTO_UNICO=47392   # distinto del de Jmg AudioProcesador (47391): los dos programas pueden estar abiertos a la vez
def _instancia_unica(archivos):
    """Una sola ventana: la primera instancia escucha en 127.0.0.1; las siguientes le pasan sus archivos y se cierran.
    Devuelve el socket servidor, None si ya habia otra abierta, o False si no se pudo ni escuchar ni conectar"""
    import socket
    srv=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        srv.bind(("127.0.0.1",_PUERTO_UNICO));srv.listen(8);return srv
    except OSError:
        try:srv.close()
        except Exception:pass
    for _ in range(20):
        try:
            c=socket.create_connection(("127.0.0.1",_PUERTO_UNICO),timeout=1.5)
            c.sendall(json.dumps({"jmg":"jve","archivos":archivos}).encode("utf-8"));c.close();return None
        except OSError:time.sleep(0.15)
    return False
def _enviar_extraer(f):
    """(JMG, 15-11) si ya hay un Jmg VideoEncoder abierto, le pasa el vídeo para que abra su Extracción; True si lo ha recibido"""
    import socket
    try:
        c=socket.create_connection(("127.0.0.1",_PUERTO_UNICO),timeout=1.0)
        c.sendall(json.dumps({"jmg":"jve","extraer":f}).encode("utf-8"));c.close();return True
    except OSError:return False
def _enviar_orden(modo,arg):
    """(JMG, 16-11) si ya hay un Jmg VideoEncoder abierto, le pasa la orden del botón derecho (extraer / ripear / imagen); True si la ha recibido"""
    import socket
    try:
        c=socket.create_connection(("127.0.0.1",_PUERTO_UNICO),timeout=1.0)
        c.sendall(json.dumps({"jmg":"jve",modo:arg}).encode("utf-8"));c.close();return True
    except OSError:return False
def _escuchar_instancias(srv,app):
    while True:
        try:
            c,_=srv.accept();d=b""
            while True:
                x=c.recv(65536)
                if not x:break
                d+=x
            c.close();j=json.loads(d.decode("utf-8"))
            if j.get("jmg")=="jve" and j.get("extraer"):app._ui(app._ext_recibir,j["extraer"])   # (JMG, 15-11) botón derecho → Extracción
            elif j.get("jmg")=="jve" and j.get("ripear"):app._ui(app._disco_ripear,j["ripear"])   # (JMG, 16-11) botón derecho del lector
            elif j.get("jmg")=="jve" and j.get("imagen"):app._ui(app._disco_imagen,j["imagen"])
            elif j.get("jmg")=="jve":
                fs=[f for f in j.get("archivos",[]) if os.path.exists(f)]
                app._ui(lambda fs=fs:(setattr(app,"_ext_solo",False),setattr(app,"_isoc_solo",False),app._addl(fs) if fs else None,app.root.deiconify(),app.root.lift(),app.root.focus_force()))
        except Exception:time.sleep(0.2)
def rh(cmd,**k):
    k.setdefault("capture_output",True);k.setdefault("text",True)
    k.setdefault("encoding","utf-8");k.setdefault("errors","ignore")
    if sys.platform=="win32":k.setdefault("creationflags",CNW)
    return subprocess.run(cmd,**k)
IDIOMAS={"es":"Español","en":"English"}
TXT={
"es":{
"titulo":"Jmg VideoEncoder", "ayuda":"❓ Ayuda", "acerca":"ℹ Acerca de", "contribuir":"Contribuir al proyecto (GitHub)", "idioma":"🌐 ES",
"acerca_t":"Acerca de", "acerca_x":"Jmg VideoEncoder\nVersión {v}\n\nComprime y convierte vídeos con FFmpeg: H.264, H.265, H.266, AV1, VP9, Apple ProRes y Avid DNxHR, por procesador o por tarjeta gráfica (NVIDIA y AMD), con sus pistas de audio y subtítulos.\n\nAutor: JMG\nCorreo: jmgsoftwaremultimedia@gmail.com\n\nSi te resulta útil, puedes apoyar el proyecto con un donativo (botón de abajo). ¡Gracias y que lo disfrutes!\n\nSoftware libre bajo licencia GNU GPL v3.\nUsa FFmpeg (compilación de BtbN), licencia GNU GPL v3.\n«Jmg VideoEncoder» y el logo Jmg Software son de su autor: las versiones modificadas deben usar otro nombre.",
"cerrar":"Cerrar", "si":"Sí", "no":"No", "info_tit":"Información", "warn_tit":"Atención", "error_tit":"Error", "cancelado_tit":"Cancelado",
"sel":"📂 Seleccionar...", "add":"➕ Añadir...", "dvd":"📀 DVD/BD...", "quit":"➖ Quitar", "limp":"🗑 Limpiar",
"guardar_p":"💾 Guardar preset", "cargar_p":"📁 Cargar preset", "tema":"🎨 Tema", "tema_auto":"Auto", "tema_claro":"Claro", "tema_oscuro":"Oscuro",
"procesar":"▶ PROCESAR", "cancelar":"⏹ Cancelar", "resetear":"🔄 Resetear", "salir":"🚪 Salir",
"al_terminar":"Al terminar:", "al_nada":"No hacer nada", "al_salir":"Salir del programa", "al_apagar":"Apagar el PC", "al_suspender":"Suspender el PC",
"ayuda_titulo":"Ayuda — Jmg VideoEncoder", "ayuda_slider":"💡 Doble clic en un deslizador = valor inicial · También puedes escribir el valor a su derecha",
"t_video":"Vídeo", "t_audio":"Audio", "t_subs":"Subtítulos", "t_vis":"Visualización / Edición", "t_sal":"Salida", "t_log":"Edit/Log",
},
"en":{
"titulo":"Jmg VideoEncoder", "ayuda":"❓ Help", "acerca":"ℹ About", "contribuir":"Support the project (GitHub)", "idioma":"🌐 EN",
"acerca_t":"About", "acerca_x":"Jmg VideoEncoder\nVersion {v}\n\nCompresses and converts videos with FFmpeg: H.264, H.265, H.266, AV1, VP9, Apple ProRes and Avid DNxHR, on the processor or on the graphics card (NVIDIA and AMD), with their audio and subtitle tracks.\n\nAuthor: JMG\nE-mail: jmgsoftwaremultimedia@gmail.com\n\nIf you find it useful, you can support the project with a donation (button below). Thanks and enjoy!\n\nFree software under the GNU GPL v3 license.\nUses FFmpeg (BtbN build), GNU GPL v3 license.\n«Jmg VideoEncoder» and the Jmg Software logo belong to their author: modified versions must use another name.",
"cerrar":"Close", "si":"Yes", "no":"No", "info_tit":"Information", "warn_tit":"Warning", "error_tit":"Error", "cancelado_tit":"Cancelled",
"sel":"📂 Select...", "add":"➕ Add...", "dvd":"📀 DVD/BD...", "quit":"➖ Remove", "limp":"🗑 Clear",
"guardar_p":"💾 Save preset", "cargar_p":"📁 Load preset", "tema":"🎨 Theme", "tema_auto":"Auto", "tema_claro":"Light", "tema_oscuro":"Dark",
"procesar":"▶ PROCESS", "cancelar":"⏹ Cancel", "resetear":"🔄 Reset", "salir":"🚪 Exit",
"al_terminar":"When done:", "al_nada":"Do nothing", "al_salir":"Exit the program", "al_apagar":"Shut down the PC", "al_suspender":"Put the PC to sleep",
"ayuda_titulo":"Help — Jmg VideoEncoder", "ayuda_slider":"💡 Double-click a slider = initial value · You can also type the value on its right",
"t_video":"Video", "t_audio":"Audio", "t_subs":"Subtitles", "t_vis":"Visualization / Editing", "t_sal":"Output", "t_log":"Edit/Log",
}
}
IDIOMA="es"
def det_id():
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            loc=locale.getlocale()[0] or ""
        cod=loc.split("_")[0].lower()
        if cod in IDIOMAS:return cod
        if loc.lower().startswith("spanish"):return "es"
        if loc.lower().startswith("english"):return "en"
    except Exception:pass
    for v in ("LANG","LANGUAGE","LC_ALL"):
        try:
            cod=os.environ.get(v,"").split("_")[0].split(".")[0].lower()
            if cod in IDIOMAS:return cod
        except Exception:continue
    return "es"
def T(k,**kw):
    d=TXT.get(IDIOMA,{})
    t=d.get(k) or TXT.get("es",{}).get(k,k)
    if kw:
        try:t=t.format(**kw)
        except Exception:pass
    return t
def V(es,en):return es if IDIOMA=="es" else en
LOGO_B64="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"
WEB_URL="https://github.com/jmgsoftwaremultimedia"   # (JMG, 22-11) su espacio en GitHub, «como mi página web»: el logo de la ventana principal
DONAR_URL="https://github.com/jmgsoftwaremultimedia"  # el enlace de «Acerca de» y el del recordatorio (JMG, 13-11: su página de GitHub, donde pondrá el botón de contribuir; se cambia aquí)
APOYO_DIAS=45   # (JMG, 13-11) cada cuántos días sale el recordatorio de contribuir
def _apoyo_ruta():
    """(JMG, 13-11) el recordatorio de contribuir es de la suite: un solo archivo para los dos programas"""
    a=_app_dir()
    if _data_dir()==a:   # portable: en la carpeta «Jmg Software» (la de arriba, la que tiene el bin común); el programa suelto, junto a él
        s=os.path.dirname(a)
        return os.path.join(s if os.path.isdir(os.path.join(s,"bin")) else a,"apoyo.json")
    if sys.platform=="win32":c=os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"),"Jmg Software")
    else:c=os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"),".config"),"jmg-software")
    try:os.makedirs(c,exist_ok=True)
    except OSError:pass
    return os.path.join(c,"apoyo.json")
def _apoyo_leer():
    try:
        with open(_apoyo_ruta(),encoding="utf-8") as f:j=json.load(f)
        return j if isinstance(j,dict) else {}
    except Exception:return {}
def _apoyo_guardar(j):
    try:
        with open(_apoyo_ruta(),"w",encoding="utf-8") as f:json.dump(j,f)
    except Exception:pass
def _apoyo_hecho():
    """se ha abierto la página de contribuir: el recordatorio no vuelve a salir (en ninguno de los dos programas)"""
    j=_apoyo_leer();j["donado"]=True;j.setdefault("desde",time.strftime("%Y-%m-%d"));_apoyo_guardar(j)
def _apoyo_toca():
    """True si hoy toca el recordatorio: han pasado APOYO_DIAS desde la instalación (el primer arranque) o desde el último aviso"""
    import datetime
    j=_apoyo_leer()
    if j.get("donado"):return False
    hoy=datetime.date.today()
    try:d0=datetime.date.fromisoformat(str(j.get("desde")))
    except Exception:d0=None
    if d0 is None or d0>hoy:j["desde"]=hoy.isoformat();_apoyo_guardar(j);return False   # el primer arranque (o el reloj cambiado): empieza a contar
    return (hoy-d0).days>=APOYO_DIAS
CONTACTO_MAIL="jmgsoftwaremultimedia@gmail.com"   # el logotipo abre un correo nuevo a esta direccion
VERSION_PROG="1.4"   # la de construir.bat; el aviso de version nueva la compara con la ultima Release de GitHub
SUITE_VER="1.0"   # Jmg SuiteMultimedia (los dos programas en una sola instalación): el aviso de versión nueva compara esta
REPO_GH="jmgsoftwaremultimedia/JmgSuiteMultimedia"
_EXT_VID="*.mkv *.mp4 *.m4v *.avi *.mov *.m2ts *.mts *.ts *.webm *.wmv *.flv *.mpg *.mpeg *.vob *.ogv *.3gp *.mxf *.divx"
if sys.platform!="win32":_EXT_VID+=" "+_EXT_VID.upper()   # en Linux el filtro distingue mayusculas
PALETAS={
"claro":{"CF":"#f0f0f0","CT":"#202020","CSB":"#a0a0a0","CSK":"#c8c8c8","CA":"#666666","CDO":"#d4edda","CDN":"#ffffff","CAV":"#b84c4c","CID":"#3a6ea5","CPS":"#d0e4ff","CASB":"#3a3a3a","CASF":"#ffffff","CPB":"#4CAF50","CPT":"#d0d0d0"},
"oscuro":{"CF":"#2b2b2b","CT":"#e0e0e0","CSB":"#505050","CSK":"#383838","CA":"#b8b8b8","CDO":"#3a5a3a","CDN":"#2a2a2a","CAV":"#e08080","CID":"#7bb8e5","CPS":"#4a5a7a","CASB":"#404040","CASF":"#ffffff","CPB":"#4CAF50","CPT":"#454545"}
}
def _set_paleta(nombre):
    global CF,CT,CSB,CSK,CA,CDO,CDN,CAV,CID,CPS,CASB,CASF,CPB,CPT
    p=PALETAS.get(nombre,PALETAS["claro"])
    CF=p["CF"];CT=p["CT"];CSB=p["CSB"];CSK=p["CSK"];CA=p["CA"]
    CDO=p["CDO"];CDN=p["CDN"];CAV=p["CAV"];CID=p["CID"];CPS=p["CPS"]
    CASB=p["CASB"];CASF=p["CASF"];CPB=p["CPB"];CPT=p["CPT"]
def _win_dark():
    try:
        import winreg
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        v,_=winreg.QueryValueEx(k,"AppsUseLightTheme")
        winreg.CloseKey(k)
        return v==0
    except Exception:return False
_set_paleta("oscuro")
def _abrir_externo(destino):
    """abre una web, un mailto: o una carpeta con el programa del sistema; False si no hay con que abrirlo"""
    if sys.platform=="win32":
        os.startfile(destino);return True
    import webbrowser
    sin_salida=dict(stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    if shutil.which("xdg-open"):
        p=subprocess.Popen(["xdg-open",destino],**sin_salida)
        try:return p.wait(timeout=1.5)==0
        except subprocess.TimeoutExpired:return True
    if "://" in destino:return bool(webbrowser.open(destino))
    return False

# ---------- vídeo ----------
VCODECS=[("copy","Passthrough"),("h264","H.264 / AVC"),("hevc","H.265 / HEVC"),("vvc","H.266 / VVC"),("av1","AV1"),("vp9","VP9 (web)"),("prores","Apple ProRes 422 LT"),("dnxhr","Avid DNxHR HQ")]
INTRA=("prores","dnxhr")   # para editar: cada fotograma entero, sin calidad ni bitrate que elegir
VENC={("h264","cpu"):"libx264",("hevc","cpu"):"libx265",("vvc","cpu"):"libvvenc",("av1","cpu"):"libsvtav1",("prores","cpu"):"prores_ks",("vp9","cpu"):"libvpx-vp9",("dnxhr","cpu"):"dnxhd",
      ("h264","nvidia"):"h264_nvenc",("hevc","nvidia"):"hevc_nvenc",("av1","nvidia"):"av1_nvenc",
      ("h264","amd"):"h264_amf",("hevc","amd"):"hevc_amf",("av1","amd"):"av1_amf"}
GPU_ENC=("h264_nvenc","hevc_nvenc","av1_nvenc","h264_amf","hevc_amf","av1_amf")
_AMF_2P={}   # (22-11) la ayuda de «2 pasadas» que admite cada AMD de este PC (-preanalysis o -preencode); la rellena _detectar_gpu
KBPS_HEVC=((2160,16000),(1440,9000),(1080,6000),(720,3000),(480,1800),(0,1200))   # kbps de referencia en HEVC segun la altura
KBPS_FACTOR={"h264":1.6,"hevc":1.0,"vvc":0.65,"av1":0.75,"vp9":0.85}                         # los demas, respecto a HEVC
CRF_DEF={"h264":20,"hevc":22,"vvc":30,"av1":30,"vp9":31,"prores":0,"dnxhr":0}   # calidad constante: x264/x265 crf, vvenc qp, SVT-AV1 crf (menos = mejor)
RESOLUCIONES=["orig","2160","1440","1080","720","576","480"]
VIMG_KEYS=("brillo","contraste","satur","tono","nitidez","ruido")   # (JMG, 20-11) + tono   # correcciones de imagen (Visualizacion / Edicion)
def _vimg_filtro(v):
    """brillo / contraste / saturacion (eq), nitidez (unsharp) y quitar ruido (hqdn3d) de los deslizadores -> filtros"""
    f=[];b=v.get("brillo",0);c=v.get("contraste",0);s=v.get("satur",0);n=v.get("nitidez",0);r=v.get("ruido",0)
    if b or c or s:f.append(f"eq=brightness={b*0.02:.2f}:contrast={1+c*0.05:.2f}:saturation={1+s*0.08:.2f}")
    t=v.get("tono",0)
    if t:f.append(f"hue=h={t*3}")   # (JMG, 20-11) tono: 3 grados por paso (±30°)
    if r:f.append(f"hqdn3d={r*0.6:.1f}:{r*0.45:.1f}:{r*0.9:.1f}:{r*0.9:.1f}")
    if n:f.append(f"unsharp=5:5:{n*0.15:.2f}:5:5:0")
    return f
VELS=("lenta","media","rapida")
PRESET={"libx264":{"lenta":"slow","media":"medium","rapida":"veryfast"},"libx265":{"lenta":"slow","media":"medium","rapida":"fast"},
        "libvvenc":{"lenta":"medium","media":"fast","rapida":"faster"},"libvpx-vp9":{"lenta":"1","media":"2","rapida":"4"},"libsvtav1":{"lenta":"4","media":"6","rapida":"9"},
        "h264_nvenc":{"lenta":"p7","media":"p5","rapida":"p3"},"hevc_nvenc":{"lenta":"p7","media":"p5","rapida":"p3"},"av1_nvenc":{"lenta":"p7","media":"p5","rapida":"p3"},
        "h264_amf":{"lenta":"quality","media":"balanced","rapida":"speed"},"hevc_amf":{"lenta":"quality","media":"balanced","rapida":"speed"},"av1_amf":{"lenta":"quality","media":"balanced","rapida":"speed"}}
def _kbps_obj(codec,h,hdr=False):
    """kbps de vídeo que el Auto pone para ese codec y esa altura (HDR, un 20 % mas)"""
    b=next(k for hh,k in KBPS_HEVC if h>=hh)
    return int(round(b*KBPS_FACTOR.get(codec,1.0)*(1.2 if hdr else 1.0)/100.0)*100)

# ---------- audio ----------
ACODECS=[("copy","Passthrough"),("ac3","AC3 (Dolby Digital)"),("eac3","E-AC3 (Dolby Digital Plus)"),("truehd","Dolby TrueHD"),("dts","DTS"),("aac","AAC"),("mp3","MP3 (estéreo)"),("flac","FLAC"),("opus","Opus")]
AKBPS={"ac3":(96,112,128,160,192,224,256,320,384,448,512,576,640),"eac3":(64,96,128,160,192,224,256,320,384,448,512,576,640,768,1024,1536),"dts":(768,1536),"aac":(128,192,256,320,384,512),"mp3":(128,192,256,320),"opus":(96,128,192,256,320,384,512),"flac":(16,24),"truehd":(16,24),"copy":()}
ABITS=("flac","truehd")   # sin perdidas: en vez de kbps se elige 16 o 24 bits
def _akbps_def(cod,nch):
    """bitrate por defecto de cada codec de audio segun los canales"""
    if cod=="copy":return 0
    if cod in ABITS:return 24
    return {"ac3":640 if nch>2 else (192 if nch==2 else 128),"eac3":640 if nch>2 else (192 if nch==2 else 128),"dts":1536 if nch>2 else 768,"aac":384 if nch>2 else 192,"mp3":320 if nch>=2 else 128,"opus":384 if nch>2 else 128}[cod]
def _eac3_rango(nch):
    """(JMG, 16-11) E-AC3: admite cualquier bitrate (FFmpeg lo da exacto hasta 6144); desde 192 en 5.1 (JMG), 64 en estéreo y 48 en mono"""
    return (192 if nch>2 else (64 if nch==2 else 48)),6144
def _eac3_ok(kb,nch):
    lo,hi=_eac3_rango(nch)
    return isinstance(kb,int) and lo<=kb<=hi
def _akbps_lista(cod,nch):
    """(JMG, 16-11) los bitrates de la lista según los canales: el AC3 en 5.1 desde 224; el E-AC3 dentro de su margen"""
    l=list(AKBPS.get(cod,()))
    if cod=="ac3" and nch>2:l=[x for x in l if x>=224]
    if cod=="eac3":lo,hi=_eac3_rango(nch);l=[x for x in l if lo<=x<=hi]
    return l
ACOD_DE_ORIGEN={"ac3":"ac3","eac3":"eac3","dts":"dts","aac":"aac","flac":"flac","opus":"opus","truehd":"truehd","mp3":"mp3"}   # al aplicar efectos a una pista en Passthrough
IDIOMAS_PISTA=["spa","eng","cat","glg","eus","fre","ger","ita","por","jpn","chi","kor","rus","dut","pol","swe","und"]
# canales de cada disposicion de FFmpeg (los laterales usan los deslizadores de los traseros)
LAYCH={"mono":["FC"],"stereo":["FL","FR"],"2.1":["FL","FR","LFE"],"3.0":["FL","FR","FC"],"3.1":["FL","FR","FC","LFE"],"4.0":["FL","FR","FC","BC"],
       "quad":["FL","FR","BL","BR"],"4.1":["FL","FR","FC","LFE","BC"],"5.0":["FL","FR","FC","BL","BR"],"5.0(side)":["FL","FR","FC","SL","SR"],
       "5.1":["FL","FR","FC","LFE","BL","BR"],"5.1(side)":["FL","FR","FC","LFE","SL","SR"],"6.1":["FL","FR","FC","LFE","BC","SL","SR"],
       "7.1":["FL","FR","FC","LFE","BL","BR","SL","SR"]}
DEF_LAY={1:"mono",2:"stereo",3:"2.1",4:"quad",5:"5.0",6:"5.1",7:"6.1",8:"7.1"}
SLIDER_CH={"FL":"fl","FR":"fr","FC":"fc","LFE":"lfe","BL":"bl","BR":"br","SL":"bl","SR":"br","BC":"bl"}
SUAV_FC=(7500,6000,5000,4300,3600)   # corte del Suavizado 1-5 (los mismos que Jmg AudioProcesador)
EQ3_F=(100,1000,5000)
AEF_KEYS=("gama","gama_c","fl","fr","fc","lfe","bl","br","suav","eq_bass","eq_mids","eq_treble","db","voz","amb","efc","sub")
def _db_auto(f63,f1k,l63,tope,V):
    """«Auto» del Double Bass (igual en Jmg AudioProcesador y Jmg VideoEncoder): f63/f1k = graves profundos y 1 kHz de los
    altavoces delanteros, l63 = graves del subwoofer (None: vacío). -> (intensidad 0-tope, motivo)"""
    fino=(-3.0-(f63-f1k))/3.0                                  # altavoces flojos de graves profundos
    if l63 is not None and l63<-80:l63=None                   # subwoofer prácticamente vacío (doblajes sin LFE)
    sub=((f63-l63)-6.0)/5.0 if l63 is not None else 3.0        # subwoofer flojo respecto a los graves de los altavoces
    n=int(max(0,min(tope,math.floor(max(fino,sub)+0.5))))
    if not n:return 0,V("los graves de los altavoces y del subwoofer ya están equilibrados: no hace falta (0).","the bass of the speakers and the subwoofer is already balanced: not needed (0).")
    if l63 is None:return n,V("el subwoofer está casi vacío.","the subwoofer is almost empty.")
    if fino>=sub:return n,V(f"a los altavoces les faltan graves (63 Hz {f63-f1k:+.0f} dB respecto a 1 kHz).",f"the speakers lack bass (63 Hz {f63-f1k:+.0f} dB against 1 kHz).")
    return n,V(f"el subwoofer va flojo ({l63-f63:+.0f} dB respecto a los graves de los altavoces).",f"the subwoofer is weak ({l63-f63:+.0f} dB against the speakers' bass).")
IMG_SUB=("hdmv_pgs_subtitle","dvd_subtitle","dvb_subtitle","pgssub")   # subtitulos de imagen
def _arbol_pids(raices):
    """(JMG, 13-11) esos procesos y los que cuelgan de ellos (hijos, nietos...)"""
    raices=[int(x) for x in raices if x]
    if not raices:return []
    padre={}
    try:
        if sys.platform=="win32":
            import ctypes,ctypes.wintypes as W_
            class _PE(ctypes.Structure):
                _fields_=[("dwSize",W_.DWORD),("cntUsage",W_.DWORD),("th32ProcessID",W_.DWORD),("th32DefaultHeapID",ctypes.c_size_t),("th32ModuleID",W_.DWORD),
                          ("cntThreads",W_.DWORD),("th32ParentProcessID",W_.DWORD),("pcPriClassBase",ctypes.c_long),("dwFlags",W_.DWORD),("szExeFile",ctypes.c_char*260)]
            k=ctypes.windll.kernel32;k.CreateToolhelp32Snapshot.restype=W_.HANDLE;k.CloseHandle.argtypes=[W_.HANDLE]
            k.Process32First.argtypes=k.Process32Next.argtypes=[W_.HANDLE,ctypes.POINTER(_PE)]
            h=k.CreateToolhelp32Snapshot(2,0)
            if h and h!=W_.HANDLE(-1).value:
                e=_PE();e.dwSize=ctypes.sizeof(_PE);ok=k.Process32First(h,ctypes.byref(e))
                while ok:padre[int(e.th32ProcessID)]=int(e.th32ParentProcessID);ok=k.Process32Next(h,ctypes.byref(e))
                k.CloseHandle(h)
        else:
            for d_ in os.listdir("/proc"):
                if d_.isdigit():
                    try:
                        with open(f"/proc/{d_}/stat") as f_:padre[int(d_)]=int(f_.read().rsplit(")",1)[1].split()[1])
                    except Exception:pass
    except Exception:pass
    res=list(dict.fromkeys(raices));i=0
    while i<len(res):
        res+=[p for p,pp in padre.items() if pp==res[i] and p not in res];i+=1
    return res
def _pausar_pid(pid,on):
    """(JMG, 13-11) suspende (on=True) o deja seguir un proceso; True si se pudo"""
    try:
        if sys.platform=="win32":
            import ctypes,ctypes.wintypes as W_
            k=ctypes.windll.kernel32;n=ctypes.windll.ntdll
            k.OpenProcess.restype=W_.HANDLE;k.OpenProcess.argtypes=[W_.DWORD,W_.BOOL,W_.DWORD];k.CloseHandle.argtypes=[W_.HANDLE]
            n.NtSuspendProcess.argtypes=n.NtResumeProcess.argtypes=[W_.HANDLE]
            h=k.OpenProcess(0x0800,False,int(pid))   # PROCESS_SUSPEND_RESUME
            if not h:return False
            try:return (n.NtSuspendProcess(h) if on else n.NtResumeProcess(h))==0
            finally:k.CloseHandle(h)
        import signal
        os.kill(int(pid),signal.SIGSTOP if on else signal.SIGCONT);return True
    except Exception:return False
_BD_LISTA={}   # (JMG, 13-11) carpeta BDMV -> la lista de reproducción (.mpls) que _bd_titulo eligió como película
def _bd_idiomas(carpeta):
    """(JMG, 13-11) Blu-ray: {PID: idioma} de las pistas de audio y de subtítulos de la película, leídos de la tabla de pistas
    (STN) de su lista de reproducción, porque los .m2ts no traen el idioma. {} si no se puede leer"""
    b=carpeta if os.path.basename(carpeta.rstrip("\\/")).upper()=="BDMV" else os.path.join(carpeta,"BDMV")
    k_=os.path.normcase(b)
    if k_ not in _BD_LISTA:_bd_titulo(carpeta)
    res={}
    try:
        with open(_BD_LISTA[k_],"rb") as fh:d=fh.read()
        p=int.from_bytes(d[8:12],"big");q=p+10
        L=int.from_bytes(d[q:q+2],"big");it=d[q+2:q+2+L];i=32
        if (int.from_bytes(it[9:11],"big")>>4)&1:i+=2+(it[32]-1)*10   # con varios ángulos
        sl=int.from_bytes(it[i:i+2],"big");s=it[i+2:i+2+sl]
        nv,na,npg,npip=s[2],s[3],s[4],s[8];i=14
        for tipo,n_ in (("v",nv),("a",na),("s",npg+npip)):
            for _ in range(n_):
                el=s[i];e=s[i+1:i+1+el];i+=1+el
                al=s[i];a=s[i+1:i+1+al];i+=1+al
                if tipo=="v" or not e or not a:continue
                pid=int.from_bytes(e[1:3],"big") if e[0]==1 else int.from_bytes(e[3:5],"big") if e[0]==2 else int.from_bytes(e[2:4],"big")
                lg=(a[2:5] if (tipo=="a" or a[0]==0x92) else a[1:4]).decode("ascii","ignore").strip().lower()
                if len(lg)==3 and lg.isalpha() and lg!="und":res[pid]=lg
    except Exception:return {}
    return res
LOGO_INICIO_B64="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"   # (JMG, 13-11) el logo de la ventana de inicio, sin el fondo blanco (430x190)
_DESPIERTO={"on":False,"p":None}
def _no_dormir(on):
    """(JMG, 13-11) mientras trabaja, el PC no entra en suspensión por inactividad (la pantalla sí puede apagarse). Windows: lo pide
    el hilo de la ventana, que dura lo que el programa; Linux: systemd-inhibit, que se suelta solo si el programa se cierra"""
    on=bool(on)
    if _DESPIERTO["on"]==on:return
    _DESPIERTO["on"]=on
    try:
        if sys.platform=="win32":
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState.restype=ctypes.c_uint
            ctypes.windll.kernel32.SetThreadExecutionState(ctypes.c_uint(0x80000000|(0x00000001 if on else 0)))   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        elif on:
            import shutil as sh_
            exe=sh_.which("systemd-inhibit")
            if exe:_DESPIERTO["p"]=subprocess.Popen([exe,"--what=idle:sleep","--who=Jmg Software","--why=Procesando / Processing","--mode=block","cat"],
                                                    stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:
            p=_DESPIERTO["p"];_DESPIERTO["p"]=None
            if p is not None and p.poll() is None:
                try:p.stdin.close()
                except Exception:pass
                p.terminate()
    except Exception:pass
def _inicio_abrir(root,nombre,version):
    """(JMG, 13-11) la ventana de inicio: el logo de Jmg Software sobre fondo oscuro mientras el programa se prepara. Devuelve
    cerrar(despues): la barra llega al final, la ventana se va (como pronto 1,5 s después de abrirse) y se llama a despues()"""
    t0=time.time();F_="#232323"
    try:
        top=tk.Toplevel(root);top.withdraw();top.overrideredirect(True);top.configure(bg=F_)
        try:top.attributes("-topmost",True)
        except Exception:pass
        fr=tk.Frame(top,bg=F_,highlightthickness=1,highlightbackground="#2e7d32",highlightcolor="#2e7d32");fr.pack(fill="both",expand=True)
        img=tk.PhotoImage(data=LOGO_INICIO_B64);top._img=img
        tk.Label(fr,image=img,bg=F_,bd=0).pack(padx=34,pady=(26,12))
        fam="Segoe UI" if sys.platform=="win32" else ""
        tk.Label(fr,text=nombre,font=(fam,15,"bold"),fg="#e0e0e0",bg=F_).pack()
        tk.Label(fr,text=version,font=(fam,9),fg="#969696",bg=F_).pack(pady=(2,14))
        cv=tk.Canvas(fr,width=380,height=4,bg="#3c3c3c",highlightthickness=0,bd=0);cv.pack(pady=(0,22))
        barra=cv.create_rectangle(0,0,95,4,fill="#34a853",width=0)
        top.update_idletasks();w,h=top.winfo_reqwidth(),top.winfo_reqheight()
        top.geometry(f"{w}x{h}+{(top.winfo_screenwidth()-w)//2}+{(top.winfo_screenheight()-h)//2}")
        top.deiconify();top.update()
    except Exception:
        def cerrar(despues=None):
            if despues:root.after(150,despues)
        return cerrar
    def cerrar(despues=None):
        fin=max(0.5,1.5-(time.time()-t0));ini=time.time()
        def paso():
            try:
                x=min(1.0,(time.time()-ini)/fin)
                cv.coords(barra,0,0,95+285*x,4)
                if x<1.0:root.after(30,paso);return
                top.destroy()
            except Exception:pass
            if despues:despues()
        paso()
    return cerrar
def _lector_fisico(raiz):
    """(JMG, 13-11) True si raiz es la raíz de un lector óptico de verdad (leer de él «al vuelo» es lento); False si es una carpeta, otra
    unidad o una imagen .iso montada por Windows (su lector es un «Virtual DVD-ROM»)"""
    try:
        if sys.platform!="win32":return False
        p_=os.path.abspath(raiz);r_=os.path.splitdrive(p_)[0]
        if not r_ or p_.rstrip("\\/").upper()!=r_.upper():return False
        import ctypes,ctypes.wintypes as W_
        k=ctypes.windll.kernel32
        if k.GetDriveTypeW(r_+"\\")!=5:return False
        k.CreateFileW.restype=W_.HANDLE;k.CreateFileW.argtypes=[W_.LPCWSTR,W_.DWORD,W_.DWORD,ctypes.c_void_p,W_.DWORD,W_.DWORD,W_.HANDLE]
        k.DeviceIoControl.argtypes=[W_.HANDLE,W_.DWORD,ctypes.c_void_p,W_.DWORD,ctypes.c_void_p,W_.DWORD,ctypes.POINTER(W_.DWORD),ctypes.c_void_p]
        k.CloseHandle.argtypes=[W_.HANDLE]
        h=k.CreateFileW("\\\\.\\"+r_,0,3,None,3,0,None)
        if not h or h==W_.HANDLE(-1).value:return True
        q=(ctypes.c_ubyte*12)();o=(ctypes.c_ubyte*1024)();n=W_.DWORD()
        ok=k.DeviceIoControl(h,0x2D1400,q,12,o,1024,ctypes.byref(n),None);k.CloseHandle(h)   # IOCTL_STORAGE_QUERY_PROPERTY: el fabricante y el modelo
        if not ok:return True
        b=bytes(o)
        def cad(off):
            x=int.from_bytes(b[off:off+4],"little")
            return b[x:b.index(b"\0",x)].decode("ascii","ignore") if 0<x<len(b) else ""
        return "virtual" not in (cad(12)+" "+cad(16)).lower()
    except Exception:return False
def _carpeta_usuario(cual):
    """(JMG, 14-11) la carpeta «videos» o «music» del usuario: la de verdad, aunque Windows la tenga en otro disco o en OneDrive"""
    try:
        if sys.platform=="win32":
            import ctypes,uuid
            g={"videos":"{18989B1D-99B5-455B-841C-AB7C74E4DDFC}","music":"{4BD8D571-6D19-48D3-BE97-422220080E43}"}[cual]
            class _G(ctypes.Structure):_fields_=[("b",ctypes.c_ubyte*16)]
            u=_G();u.b[:]=list(uuid.UUID(g).bytes_le);p=ctypes.c_wchar_p()
            if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(u),0,None,ctypes.byref(p))==0:
                r=p.value;ctypes.windll.ole32.CoTaskMemFree(p)
                if r and os.path.isdir(r):return r
        else:
            r=subprocess.run(["xdg-user-dir",{"videos":"VIDEOS","music":"MUSIC"}[cual]],capture_output=True,text=True,timeout=5).stdout.strip()
            if r and os.path.isdir(r) and os.path.normpath(r)!=os.path.normpath(os.path.expanduser("~")):return r
    except Exception:pass
    p=os.path.join(os.path.expanduser("~"),{"videos":"Videos","music":"Music"}[cual])
    return p if os.path.isdir(p) else os.path.expanduser("~")
def _esperar_lectura(raiz,estable=5.0,maximo=40.0):
    """(JMG, 14-11) recién montada una imagen, Windows y los descifradores como AnyDVD la analizan y durante un instante no se deja leer
    («Invalid argument», «el dispositivo no está listo»): un ripeo que empieza justo entonces se corta a los pocos segundos (el «39 s»).
    Espera a que el archivo grande de la película se lea bien `estable` segundos seguidos (como mucho `maximo`)"""
    t0=time.time();bien=None;k=0
    while time.time()-t0<maximo:
        try:
            fs=[]
            for sub,ext in ((("BDMV","STREAM"),".m2ts"),(("VIDEO_TS",),".vob")):
                c=os.path.join(raiz,*sub)
                if os.path.isdir(c):fs+=[os.path.join(c,x) for x in os.listdir(c) if x.lower().endswith(ext)]
        except OSError:fs=None
        if not fs:   # recién montada, a veces aún no se ven sus carpetas
            if fs==[] and time.time()-t0>12:return False   # no es un DVD ni un Blu-ray: no hay nada que esperar
            bien=None;k+=1;time.sleep(0.25);continue
        try:
            f=max(fs,key=os.path.getsize);n=os.path.getsize(f)
            with open(f,"rb") as h:h.seek((k*7919*2048)%max(2048,n-65536)//2048*2048);h.read(65536)
            if bien is None:bien=time.time()
            if time.time()-bien>=estable:return True
        except Exception:bien=None
        k+=1;time.sleep(0.25)
    return False
TMDB_SERVICIO=""   # (JMG, 16-11) el servicio intermedio con la clave de JMG (Jmg SuiteMultimedia\servicio_portadas); vacío: solo con la clave propia
TMDB_API="https://api.themoviedb.org"
TMDB_IMG="https://image.tmdb.org/t/p/"
TMDB_AVISO="This program uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise approved by TMDB."   # (JMG, 19-11) la frase de las condiciones de TMDB (§3)
JMG_LOGO="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"   # (JMG, 19-11) el logo de Jmg Software (160 x 69) arriba en «Acerca de»
TMDB_LOGO="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"   # el logo oficial de TMDB (blue_short, 154x20): lo piden sus condiciones
def _tmdb_cfg_ruta():
    """la clave propia de TMDB del usuario (si la pone): una para los dos programas, junto a apoyo.json"""
    return os.path.join(os.path.dirname(_apoyo_ruta()),"tmdb.json")
def _tmdb_clave():
    try:
        with open(_tmdb_cfg_ruta(),encoding="utf-8") as f:return str(json.load(f).get("clave","")).strip()
    except Exception:return ""
def _tmdb_clave_poner(c):
    try:
        with open(_tmdb_cfg_ruta(),"w",encoding="utf-8") as f:json.dump({"clave":str(c).strip()},f)
    except Exception:pass
def _tmdb_hay():
    return bool(TMDB_SERVICIO or _tmdb_clave())
def _tmdb(ruta,params):
    """(JMG, 16-11) una consulta a TMDB: con la clave propia, directa; si no, por el servicio de Jmg Software"""
    import urllib.request,urllib.parse
    p=dict(params);hd={"User-Agent":"JmgSuiteMultimedia/"+str(SUITE_VER),"Accept":"application/json"};c=_tmdb_clave()
    if c:
        base=TMDB_API
        if c.startswith("eyJ"):hd["Authorization"]="Bearer "+c   # el «token de lectura» (v4)
        else:p["api_key"]=c                                       # la «clave de la API» (v3)
    elif TMDB_SERVICIO:base=TMDB_SERVICIO.rstrip("/")
    else:raise RuntimeError("TMDB")
    rq=urllib.request.Request(base+ruta+"?"+urllib.parse.urlencode(p),headers=hd)
    with urllib.request.urlopen(rq,timeout=15) as r:return json.loads(r.read().decode("utf-8"))
def _tmdb_buscar(q,anio="",idioma="es-ES"):
    """películas de TMDB -> [{id, titulo, original, anio, poster}]"""
    p={"query":q,"language":idioma,"include_adult":"false"}
    if str(anio).strip().isdigit():p["year"]=str(anio).strip()
    out=[]
    for x in (_tmdb("/3/search/movie",p).get("results") or [])[:20]:
        a=str(x.get("release_date") or "")[:4]
        out.append({"id":x.get("id"),"titulo":x.get("title") or x.get("original_title") or "","original":x.get("original_title") or "","anio":a if a.isdigit() else "","poster":x.get("poster_path") or ""})
    if not out and "year" in p:return _tmdb_buscar(q,"",idioma)   # el año puede estar mal: sin él
    return out
def _tmdb_posters(i,idioma="es"):
    """los pósters de una película: los del idioma primero, luego en inglés y sin texto (los mejor votados delante)"""
    ps=_tmdb(f"/3/movie/{int(i)}/images",{"include_image_language":f"{idioma},en,null"}).get("posters") or []
    orden={idioma:0,"en":1,None:2}
    ps=sorted(ps,key=lambda x:(orden.get(x.get("iso_639_1"),3),-float(x.get("vote_average") or 0)))
    return list(dict.fromkeys(x.get("file_path") for x in ps if x.get("file_path")))[:30]
def _tmdb_bajar(ruta,tam="w185",timeout=20):
    import urllib.request
    rq=urllib.request.Request(TMDB_IMG+tam+ruta,headers={"User-Agent":"JmgSuiteMultimedia/"+str(SUITE_VER)})
    with urllib.request.urlopen(rq,timeout=timeout) as r:return r.read()
def _png_de_jpg(datos,ancho=0):
    """JPG -> PNG con FFmpeg (Tk no enseña JPG), a un ancho si se pide"""
    c=[FFMPEG,"-v","error","-i","pipe:0"]+(["-vf",f"scale={int(ancho)}:-2"] if ancho else [])+["-frames:v","1","-f","image2pipe","-vcodec","png","-"]
    r=subprocess.run(c,input=datos,capture_output=True,timeout=30,creationflags=CNW)
    return r.stdout if r.returncode==0 else b""
def _adivinar_titulo(nombre):
    """(JMG, 16-11) título y año a partir del nombre: «MONSTERS_BALL», «Monsters.Ball.2001.1080p.BluRay.x264», «Monster's Ball (2001)»"""
    s=os.path.basename(str(nombre).rstrip("\\/"))
    s=re.sub(r"\.(mkv|mp4|m4v|avi|mov|m2ts|mts|ts|webm|wmv|mpg|mpeg|vob|iso|mka|ac3|dts|flac|wav)$","",s,flags=re.I)
    s=re.sub(r"\(\s*Jmg [^)]*\)","",s);s=re.sub(r"[._]+"," ",s)
    cs=list(re.finditer(r"(?:^|[\s(\[])((?:19|20)\d\d)(?=[\s)\]]|$)",s))
    pa=[c for c in cs if c.group(0)[:1] in "(["];cs=pa or [c for c in cs if c.start()>0]   # entre paréntesis; si no, el último que no abre el nombre
    m=cs[-1] if cs else None;anio=m.group(1) if m else ""
    if m:s=s[:m.start()]   # detrás del año suele ir la calidad, el códec...
    s=re.split(r"\b(?:2160p|1080p|1080i|720p|576p|480p|4k|uhd|bluray|blu ray|bdrip|brrip|bdremux|remux|web ?dl|webrip|hdtv|dvdrip|dvd|x264|x265|h264|h265|hevc|avc|dts|ac3|truehd|atmos|hdr|disc ?\d+|disco ?\d+)\b",s,flags=re.I)[0]
    s=re.sub(r"[\[\]()]"," ",s);s=re.sub(r"\s+"," ",s).strip(" -")
    if s and (s.isupper() or s.islower()):s=s.title()
    return s,anio
def _portada_junto(ruta):
    """(JMG, 16-11) la portada que ya está junto al vídeo: cover.jpg, folder.jpg o poster.jpg (las que dejan muchos programas de ripeo, Kodi, Plex...)"""
    try:
        if not os.path.isfile(ruta):return None
        d=os.path.dirname(os.path.abspath(ruta));ls={n.lower():n for n in os.listdir(d)}
        for n in ("cover","folder","poster"):
            for e in (".jpg",".jpeg",".png"):
                if n+e in ls:return os.path.join(d,ls[n+e])
    except Exception:pass
    return None
_PERFILES={"DTS-HD MA":"DTS-HD Master Audio","DTS-HD HRA":"DTS-HD High Resolution","DTS-HD MA + DTS:X":"DTS:X (DTS-HD MA)",
           "DTS-HD MA + DTS:X IMAX":"DTS:X IMAX (DTS-HD MA)","Dolby TrueHD + Dolby Atmos":"Dolby Atmos (TrueHD)","Dolby Digital Plus + Dolby Atmos":"Dolby Atmos (E-AC3)"}
def _nombre_codec(codec,perfil=""):
    """(JMG, 18-11) el nombre que se enseña de una pista de audio: el perfil cuando dice más que el códec («DTS» a secas parecía el núcleo
    de un DTS-HD Master Audio)"""
    c=str(codec or "?").upper();p=str(perfil or "").strip()
    if c in ("DTS","TRUEHD","EAC3") and p and p.lower() not in ("dts","unknown"):return _PERFILES.get(p,p)
    return c
_BD_FIRMAS={}
def _bd_firma(f):
    """(JMG, 15-11) el códec y los canales de cada pista de audio de un .m2ts (None si no se puede leer)"""
    try:k=(os.path.normcase(f),os.path.getsize(f))
    except OSError:return None
    if k not in _BD_FIRMAS:
        try:
            r=rh([FFPROBE,"-v","error","-select_streams","a","-show_entries","stream=codec_name,channels","-of","csv=p=0",f],timeout=60)
            _BD_FIRMAS[k]=tuple(l.strip() for l in (r.stdout or "").splitlines() if l.strip()) or None
        except Exception:_BD_FIRMAS[k]=None
    return _BD_FIRMAS[k]
def _bd_recortar(fs,dur,dd):
    """(JMG, 15-11, Monster's Ball) una entradilla corta al principio o al final de la lista con otro audio que la película (14 s en
    estéreo antes de una película 5.1): FFmpeg toma los canales del primer archivo y toda la película salía «estéreo». Fuera las de
    menos de 2 minutos cuyo audio no es como el del archivo grande -> (archivos, duración)"""
    try:
        if len(fs)<2:return fs,dur
        g=max(fs,key=os.path.getsize);fg=_bd_firma(g)
        if not fg:return fs,dur
        fs=list(fs)
        for lado in (0,-1):
            while len(fs)>1 and fs[lado]!=g and (dd.get(fs[lado],0.0)<60 or (dd.get(fs[lado],0.0)<120 and (lambda x:x is not None and x!=fg)(_bd_firma(fs[lado])))):   # (JMG, 17-11) y los logos (< 60 s): su salto de tiempo desincronizaba el Aften
                dur-=dd.get(fs[lado],0.0);fs.pop(lado)
        return fs,max(0.0,dur)
    except Exception:return fs,dur
def _bd_titulo(carpeta):
    """(JMG, 8-11) Blu-ray (carpeta con BDMV): los .m2ts de la lista de reproduccion (.mpls) mas larga, en orden, y su duracion (s).
    Sin listas legibles, el .m2ts mas grande. Los Blu-ray protegidos (AACS) no se pueden leer"""
    b=carpeta if os.path.basename(carpeta.rstrip("\\/")).upper()=="BDMV" else os.path.join(carpeta,"BDMV")
    st=os.path.join(b,"STREAM");pl=os.path.join(b,"PLAYLIST")
    if not os.path.isdir(st):return [],0.0
    mejor=([],0.0,{});mejor_k=(-1,-1.0)
    try:ls=os.listdir(pl)
    except OSError:ls=[]
    for n in ls:
        if not n.lower().endswith(".mpls"):continue
        try:
            with open(os.path.join(pl,n),"rb") as fh:d=fh.read()
            if d[:4]!=b"MPLS":continue
            p=int.from_bytes(d[8:12],"big");ni=int.from_bytes(d[p+6:p+8],"big");q=p+10;fs=[];dur=0.0;dd={}
            for _ in range(ni):
                L=int.from_bytes(d[q:q+2],"big");it=d[q+2:q+2+L]
                nom=it[0:5].decode("ascii","ignore");a=int.from_bytes(it[12:16],"big");z=int.from_bytes(it[16:20],"big")
                f=next((os.path.join(st,nom+e) for e in (".m2ts",".M2TS",".mts") if os.path.isfile(os.path.join(st,nom+e))),None)
                if f and f not in fs:fs.append(f)   # (revisión, 17-11) cada archivo una vez (las listas de menú repiten el mismo trozo cientos de veces)
                dur+=max(0,z-a)/45000.0;q+=2+L
                if f:dd[f]=dd.get(f,0.0)+max(0,z-a)/45000.0   # (JMG, 15-11) lo que dura cada archivo
            if fs:   # (revisión, 17-11) la película es la lista cuyos archivos pesan más, no la que «dura» más: un menú en bucle duraba 176 min
                k_=(sum(os.path.getsize(x) for x in fs),dur)
                if k_>mejor_k:mejor_k=k_;mejor=(fs,dur,dd);_BD_LISTA[os.path.normcase(b)]=os.path.join(pl,n)   # (JMG, 13-11) de ahí salen los idiomas
        except Exception:continue
    if mejor[0]:return _bd_recortar(*mejor)   # (JMG, 15-11) sin entradillas con otro audio
    _BD_LISTA.pop(os.path.normcase(b),None)
    try:m=[os.path.join(st,n) for n in os.listdir(st) if n.lower().endswith((".m2ts",".mts"))]
    except OSError:m=[]
    return ([max(m,key=os.path.getsize)],0.0) if m else ([],0.0)
def _disco_protegido(archivos):
    """(JMG, 8-11) «CSS» si los VOB de un DVD están cifrados, «AACS» si lo están los .m2ts de un Blu-ray, None si se pueden leer.
    Mira el archivo más grande por el medio: en un DVD, las marcas de cifrado de los paquetes de vídeo; en un Blu-ray, si los
    paquetes de 192 bytes conservan su byte de sincronía (0x47), que el cifrado AACS borra"""
    try:
        fs=[f for f in archivos if os.path.isfile(f)]
        if not fs:return None
        f=max(fs,key=os.path.getsize);n=os.path.getsize(f)
        if f.lower().endswith(".vob"):
            with open(f,"rb") as fh:fh.seek((n//2)//2048*2048);d=fh.read(4*1024*1024)
            tot=cif=0;i=d.find(b"\x00\x00\x01\xe0")
            while i>=0 and i+7<len(d):
                b6=d[i+6]
                if b6>>6==2:tot+=1;cif+=1 if (b6>>4)&3 else 0
                i=d.find(b"\x00\x00\x01\xe0",i+4)
            return "CSS" if tot>=5 and cif*2>tot else None
        with open(f,"rb") as fh:fh.seek((n//2)//6144*6144);d=fh.read(6144*16)
        pos=list(range(4,len(d),192))
        if len(pos)<64:return None
        return "AACS" if sum(1 for k in pos if d[k]==0x47)<0.5*len(pos) else None
    except Exception:return None
def _srt_leer(ruta):
    """[(ini, fin, texto)] de un SRT"""
    try:
        with open(ruta,encoding="utf-8",errors="replace") as fh:t=fh.read().replace("\r\n","\n")
    except OSError:return []
    ts=lambda h,m,s,ms:int(h)*3600+int(m)*60+int(s)+int(ms.ljust(3,"0")[:3])/1000.0
    out=[]
    for bl in re.split(r"\n\s*\n",t):
        m=re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)",bl)
        if not m:continue
        txt=bl[m.end():].strip("\n")
        if txt.strip():out.append((ts(*m.groups()[:4]),ts(*m.groups()[4:]),txt))
    return out
def _srt_escribir(cues,ruta):
    def f(s):
        ms=int(round(max(0.0,s)*1000));h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s_,ms=divmod(ms,1000)
        return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"
    with open(ruta,"w",encoding="utf-8") as fh:
        for k,(a,b,t) in enumerate(cues,1):fh.write(f"{k}\n{f(a)} --> {f(b)}\n{t}\n\n")
def _a_proc(t):
    """(JMG, 8-11) pista «procesada» (sale la primera, «Jmg procesada», con la original detrás) solo si lleva efectos;
    cambiar el códec o el bitrate (o el delay, los tramos o el framerate) la recomprime en su sitio, sin más"""
    return any((t.get("ef") or {}).get(k) for k in AEF_KEYS)
def _eff(v,top_pos,top_neg=None,expo=1.4):
    """Presencia (como en Jmg AudioProcesador): deslizador -10..10 -> dB reales, curva suave y con tope"""
    try:v=float(v)
    except Exception:return 0.0
    if abs(v)<0.05:return 0.0
    top=top_pos if v>0 else (top_neg if top_neg is not None else top_pos)
    return round((1 if v>0 else -1)*top*(min(abs(v),10.0)/10.0)**expo,2)
def _eff_inv(db,top_pos,top_neg,expo=1.4):
    """lo contrario de _eff: valor del deslizador que da mas o menos esos dB"""
    if abs(db)<0.05:return 0
    t=top_pos if db>0 else top_neg
    return int((1 if db>0 else -1)*round(10.0*(min(abs(db),t)/t)**(1.0/expo)))
DB_CORTE=90   # Double Bass: corte de los graves (Hz), como en Jmg AudioProcesador
def _gd_points(nivel):
    """Gama dinamica (EXPANSION, la de Jmg AudioProcesador) en el nivel 1-5: los sonidos flojos bajan, los fuertes se quedan"""
    vn=max(0.0,min(10.0,2.0*float(nivel)));v=vn/2.0
    P=-28+3.2*v;sd=1.0+0.45*v;xg=3.0*vn/10.0
    o=lambda x:P+sd*(x-P)-xg*min(1.0,(P-x)/6.0) if x<P else x
    xs=sorted(set(round(x,1) for x in [-90,-70,-55,-45,-35,-28,-20,P,-8,-3,0]))
    return "|".join(f"{x}/{round(max(-110.0,o(x)),1)}" for x in xs)
def _comp_points(nivel):
    """Compresion (la «Elevacion» del Procesado dinamico de Jmg AudioProcesador) en el nivel 1-5: suben los sonidos flojos"""
    vn=max(0,min(10,int(round(2*float(nivel)))))
    u=(vn-1)/9.0;L=lambda a,b:a+(b-a)*u;xtra=6.0*vn/10.0
    up55=L(2.5,13)+xtra;up40=L(2,9)+xtra;up30=L(1,4.5)+xtra;Pe=-25.0
    ex=[q for q in [(-90,-90),(-72,-72+up55*0.3),(-55,-55+up55),(-40,-40+up40),(-30,-30+up30)] if q[0]<Pe-1]+[(Pe,Pe),(0,0),(20,20)]
    for i in range(len(ex)-2,0,-1):
        (x0,y0),(x1,y1)=ex[i],ex[i+1]
        if y0>y1-0.25*(x1-x0):ex[i]=(x0,y1-0.25*(x1-x0))
    return "|".join(f"{a:g}/{b:.1f}" for a,b in ex)
def _compand(g):
    """g = deslizador -5..+5: a la izquierda gama dinamica (expansion), a la derecha compresion; 0 = apagado"""
    g=int(round(g or 0))   # (JMG, 9-11) deslizador -10..+10, más preciso: cada paso, medio nivel de antes (el 10 = el 5 de antes)
    if g<0:return f"compand=attacks=0.05:decays=0.4:points={_gd_points(-g/2.0)}:soft-knee=6:gain=0:volume=0"
    if g>0:return f"compand=attacks=0.008:decays=0.25:points={_comp_points(g/2.0)}:soft-knee=4:gain=0:volume=-30"
    return None

# ---------- información del archivo ----------
def _num(x,d=0.0):
    try:return float(x)
    except (TypeError,ValueError):return d
def _hms(s):
    s=max(0.0,float(s or 0));h=int(s//3600);m=int(s%3600//60);sg=s%60
    return f"{h}:{m:02d}:{sg:06.3f}"
def _seg(txt):
    """«1:02:03.5», «62:03» o «3723.5» -> segundos (None si no se entiende)"""
    t=str(txt or "").strip().replace(",",".")
    if not t:return 0.0
    try:
        p=[float(x) for x in t.split(":")]
        s=0.0
        for x in p:s=s*60+x
        return s
    except ValueError:return None
def _vstream(info):
    """el vídeo principal (no las portadas)"""
    for s in (info or {}).get("streams",[]):
        if s.get("codec_type")=="video" and not (s.get("disposition") or {}).get("attached_pic"):return s
    return None
def _portadas(info):
    return [s for s in (info or {}).get("streams",[]) if s.get("codec_type")=="video" and (s.get("disposition") or {}).get("attached_pic")]
def _hdr_tipo(vs):
    if not vs:return "SDR"
    if any("dovi" in str(sd.get("side_data_type","")).lower() or "dolby vision" in str(sd.get("side_data_type","")).lower() for sd in vs.get("side_data_list",[]) or []):return "Dolby Vision"
    t=vs.get("color_transfer","")
    if t=="smpte2084":return "HDR10"
    if t=="arib-std-b67":return "HLG"
    return "SDR"
def _bits(vs):
    pf=str((vs or {}).get("pix_fmt",""))
    m=re.search(r"p(\d\d)",pf)
    return int(m.group(1)) if m else 8
def _fps(vs):
    try:
        a,b=str((vs or {}).get("avg_frame_rate") or vs.get("r_frame_rate") or "0/1").split("/")
        return float(a)/float(b) if float(b) else 0.0
    except Exception:return 0.0
def _dur(info):
    d=_num((info or {}).get("format",{}).get("duration"))
    if d<=0:
        for s in (info or {}).get("streams",[]):
            d=max(d,_num(s.get("duration")),_seg(_tag(s,"duration").split(".")[0]) or 0.0)
    return d
def _tag(s,k):
    t=s.get("tags") or {}
    for kk,v in t.items():
        if kk.lower()==k:return v
    return ""
def _skbps(s):
    """kbps de una pista: bit_rate, o la etiqueta BPS de los MKV"""
    b=_num(s.get("bit_rate"))
    if b<=0:
        for k,v in (s.get("tags") or {}).items():
            if k.upper().startswith("BPS"):b=_num(v);break
    return int(b/1000) if b>0 else 0
def _vkbps(info):
    vs=_vstream(info)
    if not vs:return 0
    k=_skbps(vs)
    if k:return k
    tot=_num(info.get("format",{}).get("bit_rate"))/1000.0
    if tot<=0:return 0
    oth=sum(_skbps(s) or (640 if s.get("codec_type")=="audio" else 0) for s in info.get("streams",[]) if s is not vs)
    return int(max(0,tot-oth))
def _es_log(info):
    """video logaritmico de camara (S-Log, V-Log, C-Log...): por su curva o por lo que dicen sus etiquetas"""
    vs=_vstream(info) or {}
    if str(vs.get("color_transfer","")).startswith("log"):return True
    txt=" ".join(str(v) for d in (vs.get("tags") or {},(info or {}).get("format",{}).get("tags") or {}) for v in d.values()).lower()
    return any(k in txt for k in ("s-log","slog","v-log","vlog","c-log","log-c","logc","f-log","flog","n-log","nlog","d-log","dlog"))
def _entrelazado(vs):
    return str((vs or {}).get("field_order","")) in ("tt","bb","tb","bt")
def _lay(s):
    l=str(s.get("channel_layout") or "")
    n=int(_num(s.get("channels"),2))
    if l not in LAYCH:l=DEF_LAY.get(n,"")
    return l
# ---------- framerate de las pistas (la de Jmg AudioProcesador): 25 -> 23,976 y al reves ----------
FPS_OPS=[("23.976","23,976"),("24","24"),("25","25"),("29.97","29,97"),("30","30"),("50","50"),("59.94","59,94"),("60","60")]
def _fps_fr(v):
    """framerate exacto como fraccion (23,976 = 24000/1001) o None"""
    from fractions import Fraction
    s=str(v or "").strip().replace(",",".")
    if not s:return None
    N={"23.976":Fraction(24000,1001),"23.98":Fraction(24000,1001),"29.97":Fraction(30000,1001),"47.952":Fraction(48000,1001),"59.94":Fraction(60000,1001)}
    try:return N.get(s) or Fraction(s)
    except (ValueError,ZeroDivisionError):return None
def _fps_q(t):
    """velocidad de la pista convertida (fps_a / fps_de, fraccion exacta): 25 -> 23,976 = 960/1001 (va mas lenta). None = sin cambio"""
    a=_fps_fr(t.get("fps_de"));b=_fps_fr(t.get("fps_a"))
    return (b/a) if (a and b and a!=b) else None
def _fps_f(t):
    """segundo del archivo original por cada segundo de la salida (1.0 = sin cambio de framerate)"""
    q=_fps_q(t);return float(q) if q else 1.0
def _fps_cad(t):
    """filtros del cambio de framerate (los de Jmg AudioProcesador: exactos, sin deriva) o "" """
    fac=_fps_q(t)
    if not fac:return ""
    if t.get("fps_met","tono")=="atempo":return f"atempo={float(fac):.12f}"
    a_=48000*fac;b_=48000/fac
    if a_.denominator==1:return f"aresample=48000,asetrate={a_.numerator},aresample=48000"
    if b_.denominator==1:return f"aresample={b_.numerator},asetrate=48000"
    return f"aresample=48000,asetrate={int(round(float(a_)))},aresample=48000"
def _fps_cerca(v):
    """el framerate de la lista mas cercano a v (el del video), como codigo"""
    try:v=float(v)
    except (TypeError,ValueError):return "23.976"
    if v<=0:return "23.976"
    return min(FPS_OPS,key=lambda o:abs(float(_fps_fr(o[0]))-v))[0]
def _s_esc(s):
    """subtitulo: (escala de sus tiempos, delay en s). 25 -> 23,976 = 1,0427 (van mas tarde)"""
    q=_fps_q(s)
    return (float(1/q) if q else 1.0),(int(s.get("delay") or 0)/1000.0)
# ---------- FFmpeg de otra carpeta (Salida -> FFmpeg) y el otro programa de Jmg Software ----------
OTRO_NOMBRE="Jmg AudioProcesador";OTRO_PUERTO=47391;OTRO_CLAVE="ap51";OTRO_APPID="{8F3C2A51-6B7D-4E2A-9C1E-5A4D3B2F1E60}";OTRO_EXE="Jmg AudioProcesador.exe";OTRO_LINUX="jmg-audioprocesador"
def _ff_carpeta_ok(d):
    """la carpeta tiene ffmpeg y ffprobe -> (ffmpeg, ffprobe, ffplay o None); si no, None"""
    ext=".exe" if sys.platform=="win32" else ""
    try:
        f=[os.path.join(d,n+ext) for n in ("ffmpeg","ffprobe","ffplay")]
        if os.path.isfile(f[0]) and os.path.isfile(f[1]):return f[0],f[1],(f[2] if os.path.isfile(f[2]) else None)
    except Exception:pass
    return None
def _ff_aplicar(d):
    """usa el FFmpeg de la carpeta d ("" = el del programa, su carpeta «bin»). True si se ha podido"""
    global FFMPEG,FFPROBE,FFPLAY
    if not d:
        FFMPEG=_find_bin("ffmpeg");FFPROBE=_find_bin("ffprobe");FFPLAY=_find_bin("ffplay");return True
    r=_ff_carpeta_ok(d)
    if not r:return False
    FFMPEG,FFPROBE=r[0],r[1]
    if r[2]:FFPLAY=r[2]
    return True
def _ff_inicio():
    """al arrancar: el FFmpeg elegido en «Salida -> FFmpeg» (config.json), si sigue estando ahi"""
    try:
        with open(os.path.join(_data_dir(),"config.json"),encoding="utf-8") as f:d=json.load(f).get("ffmpeg_dir","")
        if d:_ff_aplicar(d)
    except Exception:pass
def _otro_enviar(archivos):
    """pasa los archivos a la ventana abierta del otro programa (por su puerto de «una sola ventana") -> True si estaba abierto"""
    import socket
    try:
        c=socket.create_connection(("127.0.0.1",OTRO_PUERTO),timeout=1.0)
        c.sendall(json.dumps({"jmg":OTRO_CLAVE,"archivos":archivos}).encode("utf-8"));c.close();return True
    except OSError:return False
def _otro_buscar(elegido=""):
    """el ejecutable del otro programa: el que se eligio, el instalado (registro de Windows), Archivos de programa,
    el portable junto a este, o en Linux el del paquete .deb"""
    import shutil
    c=[elegido] if elegido else []
    if sys.platform=="win32":
        try:
            import winreg
            for raiz in (winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER):
                for vista in (winreg.KEY_WOW64_64KEY,winreg.KEY_WOW64_32KEY):
                    try:
                        k=winreg.OpenKey(raiz,"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"+OTRO_APPID+"_is1",0,winreg.KEY_READ|vista)
                        d,_=winreg.QueryValueEx(k,"InstallLocation");c.append(os.path.join(d,OTRO_EXE))
                    except OSError:pass
        except Exception:pass
        for pf in (os.environ.get("ProgramFiles"),os.environ.get("ProgramFiles(x86)")):
            if pf:c.append(os.path.join(pf,OTRO_NOMBRE,OTRO_EXE))
        c.append(os.path.join(os.path.dirname(_app_dir()),OTRO_NOMBRE,OTRO_EXE))
    else:
        w=shutil.which(OTRO_LINUX)
        if w:c.append(w)
    return next((x for x in c if x and os.path.isfile(x)),None)
# ---------- escucha (los reproductores de Jmg AudioProcesador) ----------
# ---------- (JMG, 10-11) icono en la bandeja del sistema (Windows), como los programas de siempre: al minimizar, la ventana
# se esconde y queda el icono; clic izquierdo = vuelve; clic derecho = menú. Con las funciones de Windows (ctypes), sin nada que instalar
class _Bandeja:
    WM_ICONO=0x8000+77
    def __init__(self,ico,tip,izq,der):
        import ctypes
        from ctypes import wintypes as W
        self.ok=False;self.visible=False;self._ct=ctypes;self._W=W;self.pend=[]   # (clics apuntados: los atiende el programa desde Tk)
        u=ctypes.windll.user32;s=ctypes.windll.shell32;k=ctypes.windll.kernel32
        self.u,self.s=u,s;self._izq,self._der=izq,der
        LRESULT=ctypes.c_ssize_t
        u.DefWindowProcW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM];u.DefWindowProcW.restype=LRESULT
        u.CreateWindowExW.argtypes=[W.DWORD,W.LPCWSTR,W.LPCWSTR,W.DWORD,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,W.HWND,W.HMENU,W.HINSTANCE,W.LPVOID]
        u.CreateWindowExW.restype=W.HWND
        u.LoadImageW.argtypes=[W.HINSTANCE,W.LPCWSTR,W.UINT,ctypes.c_int,ctypes.c_int,W.UINT];u.LoadImageW.restype=W.HANDLE
        u.LoadIconW.argtypes=[W.HINSTANCE,W.LPVOID];u.LoadIconW.restype=W.HICON
        u.TrackPopupMenu.argtypes=[W.HMENU,W.UINT,ctypes.c_int,ctypes.c_int,ctypes.c_int,W.HWND,W.LPVOID];u.TrackPopupMenu.restype=ctypes.c_int
        u.AppendMenuW.argtypes=[W.HMENU,W.UINT,ctypes.c_size_t,W.LPCWSTR]
        u.SetMenuDefaultItem.argtypes=[W.HMENU,W.UINT,W.UINT]
        u.DestroyMenu.argtypes=[W.HMENU];u.CreatePopupMenu.restype=W.HMENU
        u.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
        u.SetForegroundWindow.argtypes=[W.HWND];u.DestroyWindow.argtypes=[W.HWND]
        WNDPROC=ctypes.WINFUNCTYPE(LRESULT,W.HWND,W.UINT,W.WPARAM,W.LPARAM)
        class WNDCLASSW(ctypes.Structure):
            _fields_=[("style",W.UINT),("lpfnWndProc",WNDPROC),("cbClsExtra",ctypes.c_int),("cbWndExtra",ctypes.c_int),("hInstance",W.HINSTANCE),
                      ("hIcon",W.HICON),("hCursor",W.HANDLE),("hbrBackground",W.HBRUSH),("lpszMenuName",W.LPCWSTR),("lpszClassName",W.LPCWSTR)]
        class NID(ctypes.Structure):
            _fields_=[("cbSize",W.DWORD),("hWnd",W.HWND),("uID",W.UINT),("uFlags",W.UINT),("uCallbackMessage",W.UINT),("hIcon",W.HICON),
                      ("szTip",W.WCHAR*128),("dwState",W.DWORD),("dwStateMask",W.DWORD),("szInfo",W.WCHAR*256),("uVersion",W.UINT),
                      ("szInfoTitle",W.WCHAR*64),("dwInfoFlags",W.DWORD),("guidItem",ctypes.c_byte*16),("hBalloonIcon",W.HICON)]
        self._NID=NID
        s.Shell_NotifyIconW.argtypes=[W.DWORD,ctypes.POINTER(NID)]
        def proc(h,msg,wp,lp):
            try:
                if msg==self.WM_ICONO:
                    ev=lp&0xFFFF
                    # (JMG, 11-11) aquí NO se puede llamar a Tk (se cerraba el programa): solo se apunta
                    if ev in (0x0202,0x0203):self.pend.append("izq")   # clic izquierdo (o doble clic): la ventana vuelve
                    elif ev==0x0205:self.pend.append("der")          # clic derecho: el menú
                    return 0
            except Exception:pass
            return u.DefWindowProcW(h,msg,wp,lp)
        self._proc=WNDPROC(proc)   # (la referencia se guarda: si no, Python la libera y Windows llama a la nada)
        hinst=k.GetModuleHandleW(None);cls="JmgBandeja%d"%id(self)
        wc=WNDCLASSW();wc.lpfnWndProc=self._proc;wc.hInstance=hinst;wc.lpszClassName=cls
        if not u.RegisterClassW(ctypes.byref(wc)):return
        self.hwnd=u.CreateWindowExW(0,cls,cls,0,0,0,0,0,None,None,hinst,None)
        if not self.hwnd:return
        hi=None
        if ico and os.path.isfile(ico):hi=u.LoadImageW(None,ico,1,16,16,0x10)   # IMAGE_ICON, LR_LOADFROMFILE
        self.hicon=hi or u.LoadIconW(None,ctypes.c_void_p(32512))
        self.tip=tip;self.ok=True
        import atexit;atexit.register(self.quitar)
    def _nid(self,tip=None):
        n=self._NID();n.cbSize=self._ct.sizeof(n);n.hWnd=self.hwnd;n.uID=1;n.uFlags=0x1|0x2|0x4   # NIF_MESSAGE|NIF_ICON|NIF_TIP
        n.uCallbackMessage=self.WM_ICONO;n.hIcon=self.hicon;n.szTip=(tip or self.tip)[:127];return n
    def poner(self,tip=None):
        if not self.ok:return False
        n=self._nid(tip)
        if self.visible:return bool(self.s.Shell_NotifyIconW(1,self._ct.byref(n)))   # NIM_MODIFY
        self.visible=bool(self.s.Shell_NotifyIconW(0,self._ct.byref(n)));return self.visible   # NIM_ADD
    def texto(self,tip):
        if self.ok and self.visible:
            n=self._nid(tip);self.s.Shell_NotifyIconW(1,self._ct.byref(n))
    def quitar(self):
        if self.ok and self.visible:
            n=self._nid();self.s.Shell_NotifyIconW(2,self._ct.byref(n));self.visible=False   # NIM_DELETE
    def menu(self,ops):
        """menú de Windows junto al ratón: ops = [(texto, función) o None (raya)]; el primero va en negrita"""
        if not self.ok:return
        u=self.u;m=u.CreatePopupMenu();W=self._W
        for i,o in enumerate(ops):
            if o is None:u.AppendMenuW(m,0x800,0,None)   # MF_SEPARATOR
            else:u.AppendMenuW(m,(o[2] if len(o)>2 else 0),i+1,o[0])   # (MF_CHECKED 0x8, MF_GRAYED 0x1)
        u.SetMenuDefaultItem(m,1,0)
        p=W.POINT();u.GetCursorPos(self._ct.byref(p));u.SetForegroundWindow(self.hwnd)
        r=u.TrackPopupMenu(m,0x0100|0x0080|0x0008,p.x,p.y,0,self.hwnd,None)   # TPM_RETURNCMD|TPM_NONOTIFY|TPM_BOTTOMALIGN
        u.PostMessageW(self.hwnd,0,0,0);u.DestroyMenu(m)
        if r and 0<r<=len(ops) and ops[r-1] and ops[r-1][1]:ops[r-1][1]()

# ---------- (JMG, 12-11) opciones avanzadas de los códecs (las más importantes): cod -> título, nota, opciones y argumentos propios.
# Cada opción: (clave, etiqueta es, en, [(valor, es, en)...] (el primero = automático, no se manda nada), descripción es, en)
_AUTO_=("Automático","Automatic")
def _o_auto(v=""):return (v,)+_AUTO_
def _o_gop():return ("gop","Fotograma clave cada:","Keyframe every:",[(0,)+_AUTO_,(1,"1 s","1 s"),(2,"2 s","2 s"),(4,"4 s","4 s"),(10,"10 s","10 s")],
                     "Distancia máxima entre fotogramas completos (clave); en los cambios de plano se pone uno también. Más a menudo = se salta mejor por el vídeo, pero ocupa algo más.","Maximum distance between full (key) frames; scene cuts get one too. More often = better seeking, but a little bigger.")
def _o_bf():return ("bf","Fotogramas B:","B-frames:",[(-1,)+_AUTO_]+[(n,str(n),str(n)) for n in (0,1,2,3,4,6,8)],
                    "Fotogramas que se predicen de los de antes y de después: más = archivo más pequeño, codifica algo más lento.","Frames predicted from the ones before and after: more = smaller file, slightly slower encoding.")
def _o_refs():return ("refs","Fotogramas de referencia:","Reference frames:",[(-1,)+_AUTO_]+[(n,str(n),str(n)) for n in (1,2,3,4,5,6,8)],
                      "Cuántos fotogramas anteriores puede mirar para comprimir: más = algo mejor y más lento (los aparatos antiguos admiten hasta 4).","How many earlier frames it can look at: more = slightly better and slower (old devices take up to 4).")
_NV_COM=[("multipass","Dos pasadas (NVIDIA):","Two passes (NVIDIA):",[_o_auto(),("disabled","No","No"),("qres","Sí, rápida (1/4 de resolución)","Yes, fast (1/4 resolution)"),("fullres","Sí, completa","Yes, full")],
          "Analiza cada trozo antes de codificarlo: reparte mejor la calidad. «Completa» es la mejor.","Analyses each piece before encoding it: spreads the quality better. «Full» is the best."),
         ("saq","AQ espacial:","Spatial AQ:",[(0,)+_AUTO_,(1,"Sí","Yes")],"Más bits en las zonas lisas (cielos, paredes): menos bloques.","More bits for flat areas (skies, walls): fewer blocks."),
         ("taq","AQ temporal:","Temporal AQ:",[(0,)+_AUTO_,(1,"Sí","Yes")],"Más bits en lo que está quieto mucho rato: mejor nitidez en escenas tranquilas.","More bits for what stays still a long time: sharper calm scenes."),
         ("look","Mirar adelante (fotogramas):","Look-ahead (frames):",[(-1,)+_AUTO_]+[(n,str(n),str(n)) for n in (0,8,16,32)],
          "Cuántos fotogramas mira por adelantado para repartir el bitrate: más = mejor reparto, algo más lento.","How many frames it looks ahead to spread the bitrate: more = better spread, a little slower.")]
OPC={
 "libx264":{"tit":"H.264 (x264)","nota":("Lo que no toques queda en automático (lo que elige x264 con la velocidad elegida).","Whatever you do not touch stays automatic (what x264 chooses for the chosen speed)."),
   "ops":[("tune","Ajuste (tune):","Tune:",[_o_auto(),("film","Cine (imagen real)","Film (live action)"),("animation","Animación","Animation"),("grain","Grano de película","Film grain"),("stillimage","Imagen casi fija","Still image"),("fastdecode","Decodificación fácil","Fast decode")],
           "Afina x264 para el tipo de imagen: «Grano de película» conserva el grano de las películas antiguas; «Animación», los dibujos.","Tunes x264 for the kind of picture: «Film grain» keeps the grain of old films; «Animation», cartoons."),
          ("perfil","Perfil:","Profile:",[_o_auto(),("baseline","Baseline (aparatos muy antiguos)","Baseline (very old devices)"),("main","Main","Main"),("high","High","High")],
           "Limita las herramientas para aparatos antiguos. Con 10 bits no se aplica (x264 usa High 10).","Limits the tools for old devices. With 10 bits it does not apply (x264 uses High 10)."),
          ("nivel","Nivel:","Level:",[_o_auto()]+[(x,x,x) for x in ("4.0","4.1","4.2","5.0","5.1","5.2")],"Límite de resolución y bitrate que exige algún aparato (4.1 = Blu-ray y muchas teles).","Resolution and bitrate limit some devices require (4.1 = Blu-ray and many TVs)."),
          _o_gop(),_o_bf(),_o_refs(),
          ("aq","Cuantización adaptativa:","Adaptive quantization:",[(-1,)+_AUTO_,(0,"No","Off"),(1,"Varianza","Variance"),(2,"Autovarianza","Auto-variance"),(3,"Autovarianza con sesgo oscuro","Auto-variance, dark bias")],
           "Reparte los bits según la zona; «con sesgo oscuro» cuida las escenas oscuras.","Spreads the bits by area; «dark bias» looks after dark scenes.")],
   "extra":("Parámetros de x264 (x264-params):","x264 parameters (x264-params):")},
 "libx265":{"tit":"H.265 (x265)","nota":("Lo que no toques queda en automático (lo que elige x265 con la velocidad elegida).","Whatever you do not touch stays automatic (what x265 chooses for the chosen speed)."),
   "ops":[("tune","Ajuste (tune):","Tune:",[_o_auto(),("grain","Grano de película","Film grain"),("animation","Animación","Animation"),("fastdecode","Decodificación fácil","Fast decode")],
           "Afina x265 para el tipo de imagen: «Grano de película» conserva el grano (archivo más grande).","Tunes x265 for the kind of picture: «Film grain» keeps the grain (bigger file)."),
          _o_gop(),_o_bf(),_o_refs(),
          ("aqs","Fuerza de la AQ:","AQ strength:",[_o_auto()]+[(x,x,x) for x in ("0.5","0.8","1.0","1.2","1.5")],"Más = más bits a las zonas lisas y oscuras (menos bloques en cielos y sombras).","More = more bits to flat and dark areas (fewer blocks in skies and shadows)."),
          ("psy","Psicovisual (psy-rd):","Psycho-visual (psy-rd):",[_o_auto()]+[(x,x,x) for x in ("0","1.0","2.0","3.0")],"Más = conserva más textura y detalle aparente; 0 = imagen más suave.","More = keeps more texture and apparent detail; 0 = smoother picture.")],
   "extra":("Parámetros de x265 (x265-params):","x265 parameters (x265-params):")},
 "libsvtav1":{"tit":"AV1 (SVT-AV1)","nota":("Lo que no toques queda en automático.","Whatever you do not touch stays automatic."),
   "ops":[("grano","Grano de película sintético:","Synthetic film grain:",[(0,"No","Off")]+[(n,str(n),str(n)) for n in (4,8,12,16,25)],
           "Quita el grano al comprimir y lo vuelve a poner al reproducir: películas con grano en mucho menos tamaño.","Removes the grain when compressing and adds it back on playback: grainy films in far less size."),
          ("tune","Ajuste (tune):","Tune:",[(-1,)+_AUTO_,(0,"Visual (subjetivo)","Visual (subjective)"),(1,"PSNR","PSNR"),(2,"SSIM","SSIM")],"«Visual» busca lo que mejor se ve; PSNR y SSIM, lo que mejor mide.","«Visual» aims at what looks best; PSNR and SSIM, at what measures best."),
          _o_gop()],
   "extra":("Parámetros de SVT-AV1 (svtav1-params):","SVT-AV1 parameters (svtav1-params):")},
 "libvvenc":{"tit":"H.266 (VVenC)","nota":("Lo que no toques queda en automático.","Whatever you do not touch stays automatic."),
   "ops":[("gop","Fotograma clave cada:","Keyframe every:",[(0,)+_AUTO_,(1,"1 s","1 s"),(2,"2 s","2 s"),(4,"4 s","4 s"),(10,"10 s","10 s")],"Distancia máxima entre fotogramas completos (clave).","Maximum distance between full (key) frames."),
          ("qpa","Optimización subjetiva:","Subjective optimization:",[(-1,)+_AUTO_,(1,"Sí","Yes"),(0,"No","No")],"Reparte los bits según lo que mejor ve el ojo.","Spreads the bits by what the eye sees best.")],
   "extra":("Parámetros de VVenC (vvenc-params):","VVenC parameters (vvenc-params):")},
 "libvpx-vp9":{"tit":"VP9 (libvpx)","nota":("Lo que no toques queda en automático.","Whatever you do not touch stays automatic."),
   "ops":[("tiles","Columnas de tiles:","Tile columns:",[(-1,)+_AUTO_]+[(n,str(2**n),str(2**n)) for n in (0,1,2,3,4)],"Trozos en paralelo: más = codifica y decodifica más rápido, un poco menos eficiente.","Parallel pieces: more = faster encoding and decoding, slightly less efficient."),
          ("lag","Mirar adelante (fotogramas):","Look-ahead (frames):",[(-1,)+_AUTO_]+[(n,str(n),str(n)) for n in (0,16,25)],"Más = mejor reparto de la calidad (más memoria).","More = better spread of quality (more memory)."),
          ("aq","Cuantización adaptativa:","Adaptive quantization:",[(-1,)+_AUTO_,(0,"No","Off"),(1,"Varianza","Variance"),(2,"Complejidad","Complexity"),(3,"Cíclica","Cyclic")],"Reparte los bits según la zona.","Spreads the bits by area."),
          ("cont","Tipo de imagen:","Content type:",[(-1,)+_AUTO_,(0,"Normal","Default"),(1,"Pantalla (capturas)","Screen"),(2,"Cine (grano)","Film")],"Afina VP9 para el tipo de imagen.","Tunes VP9 for the kind of picture."),
          _o_gop()],
   "extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")},
 "prores_ks":{"tit":"Apple ProRes","nota":("Para editar: cada fotograma entero. El perfil fija la calidad y el tamaño.","For editing: each frame whole. The profile sets the quality and the size."),
   "ops":[("perfil","Perfil:","Profile:",[(1,"422 LT (por defecto)","422 LT (default)"),(0,"422 Proxy","422 Proxy"),(2,"422","422"),(3,"422 HQ","422 HQ"),(4,"4444","4444"),(5,"4444 XQ","4444 XQ")],
           "Proxy y LT: ligeros; 422 y HQ: para editar con calidad; 4444 y XQ: máxima calidad (color 4:4:4).","Proxy and LT: light; 422 and HQ: for quality editing; 4444 and XQ: top quality (4:4:4 colour).")],"extra":None},
 "dnxhd":{"tit":"Avid DNxHR","nota":("Para editar: cada fotograma entero. El perfil fija la calidad y el tamaño.","For editing: each frame whole. The profile sets the quality and the size."),
   "ops":[("perfil","Perfil:","Profile:",[("dnxhr_hq","HQ (por defecto)","HQ (default)"),("dnxhr_lb","LB (ligero)","LB (light)"),("dnxhr_sq","SQ","SQ"),("dnxhr_hqx","HQX (10 bits)","HQX (10-bit)"),("dnxhr_444","444 (10 bits, 4:4:4)","444 (10-bit, 4:4:4)")],
           "LB y SQ: ligeros; HQ: el habitual; HQX y 444: 10 bits para color y efectos.","LB and SQ: light; HQ: the usual one; HQX and 444: 10-bit for grading and effects.")],"extra":None},
 # --- audio
 "ac3":{"tit":"AC3 (Dolby Digital) · FFmpeg","nota":("La información del flujo que lee el amplificador (como en Aften) y el corte de agudos.","The bitstream information the amplifier reads (as in Aften) and the treble cut-off."),"ops":None,"extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")},
 "aac":{"tit":"AAC · FFmpeg","nota":("Lo que no toques queda en automático.","Whatever you do not touch stays automatic."),
   "ops":[("coder","Método de codificación:","Coding method:",[_o_auto(),("twoloop","Dos bucles (más lento, mejor)","Two loops (slower, better)"),("fast","Rápido","Fast")],"El método con el que reparte los bits.","How it spreads the bits."),
          ("cutoff","Corte de agudos:","Treble cut-off:",[(0,)+_AUTO_,(15000,"15 kHz","15 kHz"),(18000,"18 kHz","18 kHz"),(20000,"20 kHz (todo)","20 kHz (all)")],"Hasta qué frecuencia guarda los agudos: más alto = más agudos, más bits.","Up to which frequency the treble is kept: higher = more treble, more bits.")],
   "extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")},
 "mp3":{"tit":"MP3 (LAME)","nota":("Con VBR manda la calidad elegida aquí, no el bitrate.","With VBR the quality chosen here rules, not the bitrate."),
   "ops":[("vbr","Modo:","Mode:",[(-1,"CBR (el bitrate elegido)","CBR (the chosen bitrate)"),(0,"VBR, calidad máxima (V0)","VBR, top quality (V0)"),(2,"VBR, muy alta (V2)","VBR, very high (V2)"),(4,"VBR, alta (V4)","VBR, high (V4)")],"VBR: el bitrate cambia según lo que suena; mejor calidad por tamaño.","VBR: the bitrate changes with the sound; better quality for its size."),
          ("joint","Estéreo conjunto:","Joint stereo:",[(1,"Sí (por defecto)","Yes (default)"),(0,"No (estéreo separado)","No (separate stereo)")],"Aprovecha lo que tienen en común los dos canales: mejor calidad por tamaño.","Uses what both channels share: better quality for its size.")],
   "extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")},
 "opus":{"tit":"Opus","nota":("Lo que no toques queda en automático.","Whatever you do not touch stays automatic."),
   "ops":[("vbr","Bitrate:","Bitrate:",[("on","Variable (por defecto)","Variable (default)"),("constrained","Variable limitado","Constrained variable"),("off","Fijo (CBR)","Constant (CBR)")],"Variable: mejor calidad por tamaño; fijo: tamaño exacto.","Variable: better quality for its size; constant: exact size."),
          ("app","Uso:","Use:",[("audio","Música y cine (por defecto)","Music and film (default)"),("voip","Voz","Speech"),("lowdelay","Poco retardo","Low delay")],"Para qué se afina el códec.","What the codec is tuned for."),
          ("trama","Duración de la trama:","Frame duration:",[(20,"20 ms (por defecto)","20 ms (default)"),(10,"10 ms","10 ms"),(40,"40 ms","40 ms"),(60,"60 ms","60 ms")],"Tramas más largas: algo más eficientes; más cortas: menos retardo.","Longer frames: slightly more efficient; shorter: less delay.")],
   "extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")},
 "flac":{"tit":"FLAC","nota":("Sin pérdidas: la compresión solo cambia el tamaño y el tiempo, nunca el sonido.","Lossless: compression only changes size and time, never the sound."),
   "ops":[("comp","Compresión:","Compression:",[(5,"5 (por defecto)","5 (default)"),(0,"0 (la más rápida)","0 (fastest)"),(8,"8 (la más pequeña)","8 (smallest)"),(12,"12 (máxima, muy lenta)","12 (maximum, very slow)")],"Más = archivo algo más pequeño y más lento de hacer; el sonido es idéntico.","More = slightly smaller file, slower to make; the sound is identical.")],
   "extra":None},
}
_DD_OPS=[("dialnorm","Nivel de diálogo:","Dialogue level:",[(-31,"-31 dB (sin bajar nada, por defecto)","-31 dB (no lowering, default)"),(-27,"-27 dB","-27 dB"),(-24,"-24 dB","-24 dB"),(-20,"-20 dB","-20 dB")],
          "El dialnorm: cuánto baja el amplificador el volumen para igualar los diálogos. -31 = nada.","The dialnorm: how much the amplifier lowers the volume to even out dialogue. -31 = nothing."),
         ("dsur","Dolby Surround (estéreo):","Dolby Surround (stereo):",[_o_auto(),("on","Sí","Yes"),("off","No","No")],"En estéreo: avisa de que lleva Dolby Surround (Pro Logic).","In stereo: tells it carries Dolby Surround (Pro Logic)."),
         ("dsurex","Dolby Surround EX:","Dolby Surround EX:",[_o_auto(),("on","Sí","Yes"),("off","No","No"),("dpliiz","Pro Logic IIz","Pro Logic IIz")],"Avisa de que los traseros llevan un trasero central (6.1).","Tells the surrounds carry a back centre channel (6.1)."),
         ("dhead","Dolby Headphone:","Dolby Headphone:",[_o_auto(),("on","Sí","Yes"),("off","No","No")],"Avisa de que está preparado para auriculares Dolby Headphone.","Tells it is prepared for Dolby Headphone."),
         ("adconv","Conversor A/D:","A/D converter:",[_o_auto(),("standard","Estándar","Standard"),("hdcd","HDCD","HDCD")],"Cómo se grabó el original.","How the original was recorded."),
         ("dmix","Downmix preferido:","Preferred downmix:",[_o_auto(),("ltrt","Lt/Rt (Pro Logic)","Lt/Rt (Pro Logic)"),("loro","Lo/Ro (estéreo normal)","Lo/Ro (normal stereo)"),("dplii","Pro Logic II","Pro Logic II")],"El estéreo que debe hacer el amplificador si solo hay dos altavoces.","The stereo the amplifier should make with only two speakers."),
         ("sala","Tipo de sala:","Room type:",[_o_auto(),("large","Grande (cine)","Large (cinema)"),("small","Pequeña (casa)","Small (home)")],
          "La sala donde se mezcló: grande (cine) o pequeña (casa). El amplificador puede ajustar el sonido a la tuya. Va con el nivel de mezcla (si no lo eliges, 105 dB).","The room it was mixed in: large (cinema) or small (home). The amplifier may adapt the sound to yours. It goes with the mixing level (105 dB if you do not choose one)."),
         ("mezcla","Nivel de mezcla:","Mixing level:",[(-1,)+_AUTO_]+[(n,f"{n} dB SPL",f"{n} dB SPL") for n in (80,85,95,100,105,111)],
          "El volumen máximo (dB SPL) al que se mezcló; en cine suele ser 105.","The peak volume (dB SPL) it was mixed at; in cinemas it is usually 105."),
         ("cutoff","Corte de agudos:","Treble cut-off:",[(0,)+_AUTO_,(16000,"16 kHz","16 kHz"),(18000,"18 kHz","18 kHz"),(20000,"20 kHz (todo)","20 kHz (all)")],"Hasta qué frecuencia guarda los agudos (automático: según el bitrate).","Up to which frequency the treble is kept (automatic: by bitrate).")]
OPC["ac3"]["ops"]=_DD_OPS
OPC["eac3"]=dict(OPC["ac3"],tit="E-AC3 (Dolby Digital Plus) · FFmpeg",ops=[o for o in _DD_OPS if o[0]!="adconv"])   # (el E-AC3 de FFmpeg no admite el conversor A/D)
OPC["dts"]={"tit":"DTS · FFmpeg","nota":("El DTS de FFmpeg es siempre de bitrate fijo (el elegido): 768 o 1536 kbps, los estándar del DTS (con menos, los reproductores y amplificadores solo dan ruido). El de bitrate variable es el DTS-HD Master Audio, sin pérdidas, que FFmpeg no sabe hacer.",
                                          "FFmpeg's DTS is always constant bitrate (the chosen one): 768 or 1536 kbps, the DTS standard ones (with less, players and amplifiers only give noise). The variable one is the lossless DTS-HD Master Audio, which FFmpeg cannot make."),
            "ops":[("adpcm","Predicción ADPCM:","ADPCM prediction:",[(0,"No (por defecto)","No (default)"),(1,"Sí","Yes")],
                    "Predice la onda de las subbandas: puede mejorar los sonidos tonales (música, voces sostenidas) con el mismo bitrate; codifica más despacio.","Predicts the waveform of the sub-bands: may improve tonal sounds (music, sustained voices) at the same bitrate; slower to encode.")],
            "extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")}
for _e,_t,_u in (("h264_nvenc","H.264 · NVIDIA (NVENC)",False),("hevc_nvenc","H.265 · NVIDIA (NVENC)",True),("av1_nvenc","AV1 · NVIDIA (NVENC)",True)):
    OPC[_e]={"tit":_t,"nota":("Lo que no toques queda en automático.","Whatever you do not touch stays automatic."),
             "ops":[("tune","Ajuste (tune):","Tune:",[_o_auto(),("hq","Alta calidad","High quality")]+([("uhq","Calidad ultra alta","Ultra high quality")] if _u else [])+[("ll","Poco retardo","Low latency")],
                     "«Calidad ultra alta» es la mejor (más lenta); «Poco retardo», para emitir en directo.","«Ultra high quality» is the best (slower); «Low latency», for live streaming.")]+_NV_COM+[_o_gop()],
             "extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")}
for _e,_t,_b,_va in (("h264_amf","H.264 · AMD (AMF)",True,True),("hevc_amf","H.265 · AMD (AMF)",False,True),("av1_amf","AV1 · AMD (AMF)",True,False)):
    OPC[_e]={"tit":_t,"nota":("Lo que no toques queda en automático.","Whatever you do not touch stays automatic."),
             "ops":[("hq","Calidad máxima:","Highest quality:",[(0,)+_AUTO_,(1,"Sí (más lento)","Yes (slower)")],"Usa el modo de máxima calidad de AMD, por encima de la velocidad elegida.","Uses AMD's highest-quality mode, above the chosen speed."),
                    ("pre","Preanálisis:","Pre-analysis:",[(-1,)+_AUTO_,(1,"Sí","Yes"),(0,"No","No")],"Analiza el vídeo antes: reparte mejor la calidad.","Analyses the video first: spreads the quality better.")]+
                   ([("vbaq","VBAQ:","VBAQ:",[(-1,)+_AUTO_,(1,"Sí","Yes"),(0,"No","No")],"Más bits a las zonas lisas: menos bloques.","More bits to flat areas: fewer blocks.")] if _va else [])+
                   ([("bf","Fotogramas B:","B-frames:",[(-1,)+_AUTO_]+[(n,str(n),str(n)) for n in (0,1,2,3)],"Fotogramas que se predicen de los de antes y de después.","Frames predicted from the ones before and after.")] if _b else [])+[_o_gop()],
             "extra":("Argumentos propios de FFmpeg:","Own FFmpeg arguments:")}

class _ReproMC:
    """Reproductor multicanal (5.1 / 7.1) con waveOut de Windows.
    FFmpeg decodifica desde la posicion pedida y escribe un WAV por la tuberia: de su cabecera se toma el formato
    EXACTO (WAVE_FORMAT_EXTENSIBLE con el mapa de altavoces correcto: 5.1, 5.1(side), 7.1...) y el resto es audio.
    Con ich se oye SOLO ese canal, pero por SU altavoz (p. ej. el LFE por el subwoofer)."""
    def __init__(self,src,pos,nch,ich=None,arg=None):
        import ctypes
        from ctypes import wintypes
        self.ct=ctypes;self.parar=False;self.err=None;self.hwo=None
        w=ctypes.windll.winmm
        class WAVEHDR(ctypes.Structure):
            _fields_=[("lpData",ctypes.c_void_p),("dwBufferLength",wintypes.DWORD),("dwBytesRecorded",wintypes.DWORD),
                      ("dwUser",ctypes.c_size_t),("dwFlags",wintypes.DWORD),("dwLoops",wintypes.DWORD),
                      ("lpNext",ctypes.c_void_p),("reserved",ctypes.c_size_t)]
        self.WAVEHDR=WAVEHDR
        w.waveOutOpen.argtypes=[ctypes.POINTER(ctypes.c_void_p),ctypes.c_uint,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint]
        for fn in ("waveOutPrepareHeader","waveOutUnprepareHeader","waveOutWrite"):
            getattr(w,fn).argtypes=[ctypes.c_void_p,ctypes.POINTER(WAVEHDR),ctypes.c_uint]
        w.waveOutReset.argtypes=[ctypes.c_void_p];w.waveOutClose.argtypes=[ctypes.c_void_p]
        self.w=w
        af=[]
        if ich is not None:   # solo un canal, por su altavoz: los demas a cero, la disposicion se conserva
            af=["-af","aeval=exprs='"+"|".join(("val(%d)"%i if i==ich else "0") for i in range(nch))+"':c=same"]
        cmd=[FFMPEG,"-v","error","-ss","%.3f"%max(0.0,pos),"-i",src]+(arg or af)+["-c:a","pcm_s16le","-f","wav","-"]
        self.pr=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,creationflags=CNW)
        self.th=threading.Thread(target=self._bucle,daemon=True);self.th.start()
    def _leer(self,n):
        b=b""
        while len(b)<n:
            c=self.pr.stdout.read(n-len(b))
            if not c:break
            b+=c
        return b
    def _bucle(self):
        ct=self.ct;w=self.w
        try:
            # --- cabecera WAV de FFmpeg: RIFF....WAVE, luego trozos hasta "data"
            h=self._leer(12)
            if len(h)<12 or h[:4]!=b"RIFF" or h[8:12]!=b"WAVE":raise RuntimeError("cabecera WAV no valida")
            fmt=None
            while True:
                ck=self._leer(8)
                if len(ck)<8:raise RuntimeError("WAV sin datos")
                cid=ck[:4];sz=int.from_bytes(ck[4:8],"little")
                if cid==b"data":break
                body=self._leer(sz+(sz&1))
                if cid==b"fmt ":fmt=body[:sz]
            if not fmt:raise RuntimeError("WAV sin formato")
            nch=int.from_bytes(fmt[2:4],"little");sr=int.from_bytes(fmt[4:8],"little");blk=int.from_bytes(fmt[12:14],"little")
            if len(fmt)<18:fmt=fmt+b"\x00\x00"          # cbSize=0 para PCM simple
            self._fmt=ct.create_string_buffer(fmt,len(fmt))
            hwo=ct.c_void_p()
            # Si la salida aun esta ocupada (la escucha anterior todavia se esta cerrando: algunas tarjetas HDMI hacia
            # un amplificador tardan en soltar el multicanal), se reintenta hasta 2 s en vez de quedarse sin sonido.
            for _int in range(21):
                r=w.waveOutOpen(ct.byref(hwo),0xFFFFFFFF,ct.cast(self._fmt,ct.c_void_p),0,0,0)
                if r==0 or self.parar or r==32:break      # 32 = WAVERR_BADFORMAT: formato no admitido, no sirve reintentar
                time.sleep(0.1)
            if self.parar and r==0:
                w.waveOutClose(hwo);return
            if r:raise RuntimeError("waveOutOpen %d (%d canales, %d Hz)"%(r,nch,sr))
            self.hwo=hwo
            try:   # al 100 %: el volumen de esta aplicacion en el mezclador de Windows puede haberse quedado bajo
                w.waveOutSetVolume.argtypes=[ct.c_void_p,ct.c_uint];w.waveOutSetVolume(hwo,0xFFFFFFFF)
            except Exception:pass
            tam=max(blk,(sr//10)*blk)                      # bloques de 100 ms
            nb=6;bufs=[ct.create_string_buffer(tam) for _ in range(nb)];hdrs=[self.WAVEHDR() for _ in range(nb)]
            enuso=[False]*nb;fin=False;i=0
            while not self.parar:
                if not enuso[i]:
                    if fin:
                        if not any(enuso):break
                    else:
                        d=self._leer(tam)
                        if not d:fin=True
                        else:
                            d=d[:len(d)-len(d)%blk]
                            ct.memmove(bufs[i],d,len(d))
                            hd=hdrs[i];hd.lpData=ct.cast(bufs[i],ct.c_void_p);hd.dwBufferLength=len(d);hd.dwFlags=0
                            w.waveOutPrepareHeader(hwo,ct.byref(hd),ct.sizeof(hd));w.waveOutWrite(hwo,ct.byref(hd),ct.sizeof(hd))
                            enuso[i]=True
                    i=(i+1)%nb;continue
                if hdrs[i].dwFlags & 1:                    # WHDR_DONE: bloque ya sonado -> se reutiliza
                    w.waveOutUnprepareHeader(hwo,ct.byref(hdrs[i]),ct.sizeof(hdrs[i]));enuso[i]=False
                    continue
                time.sleep(0.01)
            w.waveOutReset(hwo)
            for k in range(nb):
                if enuso[k]:w.waveOutUnprepareHeader(hwo,ct.byref(hdrs[k]),ct.sizeof(hdrs[k]))
            w.waveOutClose(hwo);self.hwo=None
        except Exception as e:
            self.err=str(e)
        finally:
            try:self.pr.kill()
            except Exception:pass
    def stop(self):
        self.parar=True
        try:self.pr.kill()
        except Exception:pass
        try:self.th.join(timeout=1.5)
        except Exception:pass
class _ReproFF:
    """Reproductor para Linux/macOS con ffplay (sin ventana). Estereo o multicanal (PulseAudio/PipeWire reparten
    los canales); con ich suena solo ese canal por su altavoz; con estereo=True se mezcla a 2 canales."""
    def __init__(self,src,pos,nch=2,ich=None,estereo=False,arg=None):
        self.err=None;self.p0=None
        if arg:   # con filtros propios: FFmpeg los aplica y ffplay reproduce lo que sale
            self.p0=subprocess.Popen([FFMPEG,"-v","error","-ss","%.3f"%max(0.0,pos),"-i",src]+arg+["-c:a","pcm_s16le","-f","wav","-"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        af=[]
        if ich is not None and nch>1:
            af.append("aeval=exprs='"+"|".join(("val(%d)"%i if i==ich else "0") for i in range(nch))+"':c=same")
        if estereo:af.append("aformat=channel_layouts=stereo")
        cmd=[FFPLAY,"-nodisp","-autoexit","-hide_banner","-loglevel","error"]+(["-i","-"] if arg else ["-ss","%.3f"%max(0.0,pos)]+(["-af",",".join(af)] if af else [])+[src])
        try:
            self.pr=subprocess.Popen(cmd,stdin=self.p0.stdout if arg else subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        except FileNotFoundError:
            self.pr=None;self.err="ffplay no encontrado (instala el paquete ffmpeg)"
            return
        def vig():
            try:
                e=self.pr.stderr.read().decode("utf-8","ignore").strip()
                if self.pr.wait()!=0 and e and not getattr(self,"_parado",False):self.err=e.splitlines()[-1][:160]
            except Exception:pass
        threading.Thread(target=vig,daemon=True).start()
    def stop(self):
        self._parado=True
        try:
            if self.p0 and self.p0.poll() is None:self.p0.terminate()
            if self.pr and self.pr.poll() is None:
                self.pr.terminate()
                try:self.pr.wait(timeout=1)
                except Exception:self.pr.kill()
        except Exception:pass
class VideoEncoderGUI:
    def __init__(self,root):
        global IDIOMA
        self.root=root
        IDIOMA=det_id()
        _cfg_tema="oscuro"   # por defecto: oscuro, como Jmg AudioProcesador
        self._cfg={}
        try:
            p_cfg=os.path.join(_data_dir(),"config.json")
            if os.path.exists(p_cfg):
                with open(p_cfg,"r",encoding="utf-8") as f:self._cfg=json.load(f)
                if self._cfg.get("idioma") in IDIOMAS:IDIOMA=self._cfg["idioma"]
                if self._cfg.get("tema") in ("auto","claro","oscuro"):_cfg_tema=self._cfg["tema"]
        except Exception:self._cfg={}
        self.var_tema=tk.StringVar(value=_cfg_tema)
        self._aplicar_tema()
        self.root.title(T("titulo"))
        try:
            base=sys._MEIPASS if getattr(sys,"frozen",False) else os.path.dirname(os.path.abspath(__file__))
            ico=os.path.join(base,"VideoEncoder.ico")
            if sys.platform=="win32" and os.path.exists(ico):self.root.iconbitmap(ico);self.root.iconbitmap(default=ico)
            else:
                self._ico_img=tk.PhotoImage(data=LOGO_B64);self.root.iconphoto(True,self._ico_img)
        except Exception:pass
        try:
            ax,ay,aw,ah=_area_trabajo(self.root)
            w=min(1300,aw-20);h=min(950,ah-_MARCO-10)
            self.root.geometry("%dx%d+%d+%d"%(w,h,ax+max(0,(aw-w)//2),ay+max(0,(ah-h-_MARCO)//2)))
            self._geo_ini=(w,h,ay+max(0,(ah-h-_MARCO)//2))
        except Exception:self.root.geometry("1300x950")
        self.root.minsize(1000,min(700,max(500,self.root.winfo_screenheight()-140)))
        self.root.configure(bg=CF)
        self.root.protocol("WM_DELETE_WINDOW",self._on_close);self.root.after(900,self._extras_10_11)   # (JMG, 10-11) bandeja y descripciones
        import queue as _q
        self._uiq=_q.Queue()
        # datos
        self.files=[]          # rutas (vídeos o carpetas de DVD)
        self.info={}           # ruta -> lo que dice ffprobe
        self.jobs={}           # ruta -> trabajo (ajustes de vídeo, pistas de audio y subtítulos, recorte) tras «Agregar»
        self.actual=None       # ruta del trabajo que se ve en las pestañas
        self.procesando=False;self._proc=None;self._cancelar=threading.Event()
        self._gpu=set();self._gpu_listo=False
        self._auto_hecho={}    # (ruta, pista, efecto) -> lo que puso el «Auto» (segunda pulsacion sin tocar nada: lo quita)
        self._muestras={}      # (ruta, pista) -> WAV de muestra para los «Auto» de audio
        self._ext_info={}      # archivo de una pista de audio añadida -> lo que dice ffprobe
        self._repro=None       # escucha en marcha
        self._tmp=tempfile.mkdtemp(prefix="jmg_ve_")
        self._cargando=False   # mientras se pasan los ajustes de un trabajo a la pantalla: las trazas no guardan
        self._escaneando=False
        self.var_al_terminar=tk.StringVar(value="nada");self.var_reset_all=tk.BooleanVar(value=False)
        self._ud_pila=[];self._ud_re=[];self._ud_act=None;self._ud_pend=None   # Deshacer / Rehacer (las ultimas 5 acciones)
        self.var_progreso=tk.StringVar(value="")
        # salida (para todos los trabajos)
        o=self._cfg.get("salida",{})
        self.var_cont=tk.StringVar(value=o.get("cont","mkv"))
        self.var_dest_modo=tk.StringVar(value=o.get("dest_modo","original"))
        self.var_dest=tk.StringVar(value=o.get("dest",""))
        self.var_sufijo=tk.StringVar(value=" (Jmg VideoEncoder)")   # (JMG, 9-11) fijo: el nombre de cada vídeo se cambia en «Nombre de este vídeo»
        self.var_dup=tk.StringVar(value=o.get("dup","rename"))
        self.var_caps=tk.BooleanVar(value=o.get("caps",True))
        self.var_meta=tk.BooleanVar(value=o.get("meta",True))
        self.var_adj=tk.BooleanVar(value=o.get("adj",True))
        self.var_abrir=tk.BooleanVar(value=o.get("abrir",True));self.var_bandeja=tk.BooleanVar(value=o.get("bandeja",True))   # (JMG, 8-11) al terminar se abre la carpeta (salvo si se apaga el PC)
        self.var_nom=tk.StringVar(value="")   # nombre del archivo del vídeo de las pestañas
        self._aften=dict(AFTEN_DEF);self._aften.update({k:v for k,v in _af_migrar(o.get("aften")).items() if k in AFTEN_DEF})   # (JMG, 8-11)
        self._vars_video();self._vars_audio();self._vars_subs()
        self._estilo();self._build()
        self.root.after(40,self._ui_poll)
        self.root.bind_class('TCombobox','<<ComboboxSelected>>',self._cmb_sin_foco,add='+')
        def _enter_fija(e):
            try:e.widget.winfo_toplevel().focus_set()
            except Exception:pass
        for _k in ('<Return>','<KP_Enter>'):self.root.bind_class('Entry',_k,_enter_fija,add='+')
        self._chk_ff();self._refrescar_estado()
        threading.Thread(target=self._detectar_gpu,daemon=True).start()
        self.root.after(60,self._forzar_colores)

    # ---------- tema, estilo y ayudas comunes (igual que Jmg AudioProcesador) ----------
    def _aplicar_tema(self):
        t=self.var_tema.get()
        _set_paleta(("oscuro" if _win_dark() else "claro") if t=="auto" else t)
    def _vt(self,es,en):return es if IDIOMA=="es" else en
    def _estilo(self):
        s=ttk.Style()
        try:s.theme_use("clam")
        except tk.TclError:pass
        s.configure(".",background=CF,foreground=CT,fieldbackground=CDN,borderwidth=0)
        s.configure("TEntry",fieldbackground=CDN,foreground=CT,background=CDN,bordercolor=CSB,lightcolor=CSB,darkcolor=CSB,borderwidth=1,relief="solid",padding=2,insertcolor=CT)
        s.configure("TCombobox",fieldbackground=CDN,foreground=CT,background=CDN,arrowcolor=CT,bordercolor=CSB,lightcolor=CSB,darkcolor=CSB,borderwidth=1,relief="solid",padding=2)
        try:
            self.root.option_add("*TCombobox*Listbox.background",CDN);self.root.option_add("*TCombobox*Listbox.foreground",CT)
            self.root.option_add("*TCombobox*Listbox.selectBackground",CID);self.root.option_add("*TCombobox*Listbox.selectForeground",CASF)
        except Exception:pass
        s.map("TCombobox",fieldbackground=[("readonly",CDN),("disabled",CDN)],foreground=[("readonly",CT),("disabled",CA)],background=[("readonly",CDN),("active",CDN)],bordercolor=[("focus",CID)])
        s.configure("H.TScale",background=CF,troughcolor=CSB,bordercolor=CF,lightcolor=CSB,darkcolor=CSB,borderwidth=0,sliderrelief="flat",sliderlength=14)
        s.configure("Horizontal.TScale",arrowsize=11,sliderlength=14,lightcolor="#7d7d7d",darkcolor="#5a5a5a",bordercolor="#454545")   # (JMG, 8-11) pequeños y,
        s.map("Horizontal.TScale",lightcolor=[("disabled","#eeebe7")],darkcolor=[("disabled","#cfcdc8")],bordercolor=[("disabled","#9e9a91")])   # activos, tirador oscuro
        s.map("H.TScale",background=[("active",CF),("!active",CF)],troughcolor=[("active",CSB),("!active",CSB)])
        s.configure("V.Horizontal.TProgressbar",troughcolor=CPT,background=CPB,bordercolor=CPT,lightcolor=CPB,darkcolor=CPB,borderwidth=0,thickness=14)
        s.configure("TNotebook",background=CF,borderwidth=0,tabmargins=[0,0,0,0],relief="flat")
        try:s.layout("TNotebook",[("Notebook.client",{"sticky":"nswe"})])
        except Exception:pass
        s.configure("TNotebook",borderwidth=0,lightcolor=CSB,darkcolor=CSB,bordercolor=CSB,background=CF)
        s.configure("TNotebook.Tab",padding=[6,2],font=("",9),background=CSB,foreground=CT,borderwidth=0,focuscolor=CF,lightcolor=CSB,darkcolor=CSB,bordercolor=CSB)
        s.map("TNotebook.Tab",background=[("selected",CF),("active",CSK),("!active",CSB)],foreground=[("selected",CT),("active",CT),("!active",CT)],
              expand=[("selected",(0,0,0,0)),("active",(0,0,0,0)),("!active",(0,0,0,0))])
        s.configure("TFrame",background=CF,borderwidth=0,relief="flat")
        s.configure("NbBorder.TFrame",background=CSB,borderwidth=1,relief="flat")
        s.configure("TLabel",background=CF,foreground=CT)
        s.configure("TButton",padding=4,borderwidth=1,relief="solid",background=CF,foreground=CT,bordercolor=CSB,lightcolor=CF,darkcolor=CF)
        s.map("TButton",background=[("active",CSB),("pressed",CSK),("disabled",CF)],foreground=[("active",CT),("pressed",CT),("disabled",CA)])
        s.configure("G.TCheckbutton",font=("",10),padding=6,background=CF,foreground=CT,focuscolor=CF,borderwidth=0)
        s.map("G.TCheckbutton",background=[("active",CF),("!active",CF)],foreground=[("active",CT),("disabled",CA),("!active",CT)])
        s.configure("G.TRadiobutton",font=("",10),padding=4,background=CF,foreground=CT,focuscolor=CF,borderwidth=0)
        s.map("G.TRadiobutton",background=[("active",CF),("!active",CF)],foreground=[("active",CT),("disabled",CA),("!active",CT)])
        for st_ in ("TCheckbutton","TRadiobutton"):   # (JMG, 11-11) los que no llevan estilo propio: con el ratón encima no se ponen blancos
            s.configure(st_,background=CF,foreground=CT,focuscolor=CF)
            s.map(st_,background=[("active",CF),("!active",CF)],foreground=[("active",CT),("disabled",CA),("!active",CT)])
        for st_,col in (("Nv","#76b900"),("Amd","#e8323c"),("Cpu",CT)):   # (JMG, 8-11) como sus logos: NVIDIA verde, AMD rojo; (15-11) el procesador, en el color normal (en plata parecía desactivado)
            s.configure(st_+".G.TRadiobutton",font=("",10,"bold"),padding=4,background=CF,foreground=col,focuscolor=CF,borderwidth=0)
            s.map(st_+".G.TRadiobutton",background=[("active",CF),("!active",CF)],foreground=[("disabled",CA),("selected",col),("!selected",CT)])   # (JMG, 8-11) color solo el marcado
        s.configure("Auto.TButton",padding=0,anchor="center",font=("",8))   # (JMG, 14-11) «Auto»: del tamaño de las casillas de valor (_caja_auto), centrado
        s.configure("AutoOn.TButton",padding=0,anchor="center",font=("",8,"bold"),foreground="#3cb95a")   # puesto: la palabra en verde
        s.map("AutoOn.TButton",foreground=[("disabled",CA),("pressed","#3cb95a"),("active","#3cb95a"),("!active","#3cb95a")])
        s.configure("Vertical.TScrollbar",background=CSB,troughcolor=CF,bordercolor=CF,arrowcolor=CT,borderwidth=0,arrowsize=12)
        s.map("Vertical.TScrollbar",background=[("active",CSK)])
        s.configure("Horizontal.TScrollbar",background=CSB,troughcolor=CF,bordercolor=CF,arrowcolor=CT,borderwidth=0,arrowsize=12)
        s.configure("Treeview",background=CDN,fieldbackground=CDN,foreground=CT,bordercolor=CSB,borderwidth=1,rowheight=22)
        s.map("Treeview",background=[("selected",CPS)],foreground=[("selected",CT)])
        s.configure("Treeview.Heading",background=CSB,foreground=CT,relief="flat",borderwidth=0,font=("",9,"bold"))
        s.map("Treeview.Heading",background=[("active",CSK)])
        try:
            for k,v in (("background",CDN),("foreground",CT),("selectBackground",CASB),("selectForeground",CASF),("highlightBackground",CSB),("highlightColor",CID)):
                self.root.option_add("*Listbox."+k,v)
        except Exception:pass
    def _forzar_colores(self):
        def todos(p):
            for w in p.winfo_children():
                yield w;yield from todos(w)
        for w in todos(self.root):
            try:
                c=w.winfo_class()
                if c=="Entry":w.configure(bg=CDN,fg=CT,insertbackground=CT,highlightbackground=CSB,highlightcolor=CID,highlightthickness=1,borderwidth=0,relief="flat",disabledbackground=CDN,disabledforeground=CA,readonlybackground=CDN)
                elif c=="Listbox":w.configure(bg=CDN,fg=CT)
                elif c=="Canvas":w.configure(bg=CF,highlightthickness=0)
            except Exception:pass
    def _ui(self,fn,*args):
        """pide al hilo principal que ejecute fn(*args). Seguro desde cualquier hilo"""
        try:self._uiq.put((fn,args))
        except AttributeError:
            try:self.root.after_idle(fn,*args)
            except Exception:pass
    def _ui_poll(self):
        try:
            for _ in range(200):
                fn,args=self._uiq.get_nowait()
                try:fn(*args)
                except Exception as e:
                    try:self._log("[UI] %s"%e)
                    except Exception:pass
        except Exception:pass
        try:self.root.after(40,self._ui_poll)
        except Exception:pass
    def _cmb_sin_foco(self,e=None):
        try:
            w=e.widget;w.selection_clear();w.icursor("end")
            self.root.after_idle(self.root.focus_set)
        except Exception:pass
    def _tra(self,var,cb,w):
        """trace_add que se elimina sola al destruir el widget (cambio de tema o de idioma)"""
        tid=var.trace_add("write",cb)
        def _rm(ev,v=var,t=tid):
            if ev.widget is w:
                try:v.trace_remove("write",t)
                except Exception:pass
        w.bind("<Destroy>",_rm,add="+")
        return tid
    def _raw(self,var):
        try:return float(self.root.globalgetvar(str(var)))
        except Exception:
            try:return float(var.get())
            except Exception:return 0.0
    def _fv(self,v):
        try:
            f=float(v)
            return str(int(f)) if abs(f-int(f))<1e-9 else f"{f:.1f}"
        except (TypeError,ValueError):return str(v)
    def _sl(self,p,lbl,var,a,b,r,d=0,cl=0,cs=1,cv=2,sl=200,step=1):
        """deslizador con su casilla para escribir el valor (doble clic = valor inicial)"""
        if lbl:ttk.Label(p,text=lbl).grid(row=r,column=cl,sticky="w",padx=5,pady=3)
        e=ttk.Scale(p,from_=a,to=b,variable=var,orient="horizontal",length=int(sl*0.75))
        e.grid(row=r,column=cs,padx=(5,1),pady=3)
        ve=tk.StringVar(value=self._fv(var.get()))
        en=tk.Entry(p,textvariable=ve,width=6,justify="center",bg=CDN,fg=CT,insertbackground=CT,relief="flat",highlightthickness=1,highlightbackground=CSB,highlightcolor=CID,borderwidth=0,disabledbackground=CDN)
        en.grid(row=r,column=cv,padx=(1,5),pady=3)
        rv=lambda:max(a,min(b,int(round(self._raw(var)/float(step))*step)))
        def oc(*_):
            x=rv()
            try:ac=float(ve.get().replace(",","."))
            except ValueError:ac=None
            if ac is None or abs(ac-x)>0.001:ve.set(self._fv(x))
        self._tra(var,oc,e)
        def ap(e_=None):
            try:v=float(ve.get().replace(",","."))
            except ValueError:ve.set(self._fv(rv()));return
            v=max(a,min(b,int(round(v/float(step))*step)));var.set(v);ve.set(self._fv(v))
        en.bind("<Return>",ap);en.bind("<FocusOut>",ap);en.bind("<KP_Enter>",ap)
        def dbl(ev=None):var.set(d);ve.set(self._fv(d))
        e.bind("<Double-Button-1>",dbl)
        _g=[False]
        def snap(*_):
            if _g[0]:return
            x=self._raw(var);sv=max(a,min(b,int(round(x/float(step))*step)))
            if abs(sv-x)>1e-6:
                _g[0]=True
                try:var.set(sv)
                finally:_g[0]=False
        self._tra(var,snap,e)
        def soltar(ev=None):
            try:
                sv=rv()
                if abs(float(e.get())-sv)>1e-6:e.set(sv)
            except Exception:pass
        e.bind("<ButtonRelease-1>",soltar,add="+")
        self._flechas(e,var,a,b,step)
        e.configure(cursor="hand2");return e,en
    def _flechas(self,e,var,a,b,step=1,al_mover=None):
        """el deslizador se mueve con las flechas del teclado (clic en el para elegirlo): un paso por pulsacion"""
        e.configure(takefocus=1)
        e.bind("<Button-1>",lambda ev:e.focus_set(),add="+")
        def mv(ev,s):
            try:
                if str(e.cget("state"))=="disabled" or "disabled" in e.state():return "break"
            except Exception:pass
            v=max(a,min(b,round(self._raw(var)/step)*step+s*step))
            var.set(int(v) if float(step).is_integer() else v)
            if al_mover:al_mover()
            return "break"
        for k,s in (("<Left>",-1),("<Down>",-1),("<Right>",1),("<Up>",1)):e.bind(k,lambda ev,s=s:mv(ev,s))
    # ---------- (JMG, 10-11) icono en la bandeja del sistema y descripciones al pasar el ratón (los dos programas igual) ----------
    def _extras_10_11(self):
        """se llama una vez al abrir: la bandeja (solo Windows) y las descripciones"""
        try:self._tips_iniciar()
        except Exception as e:self._log(f"[TIPS] {e}")
        try:self._bandeja_iniciar()
        except Exception as e:self._log(f"[BANDEJA] {e}")
    def _bandeja_iniciar(self):
        if getattr(self,"_bandeja",None) is not None or sys.platform!="win32":return
        ico=None
        for b_ in (getattr(sys,"_MEIPASS",""),os.path.dirname(os.path.abspath(sys.argv[0] or ".")),os.path.dirname(os.path.abspath(__file__))):
            if b_ and os.path.isfile(os.path.join(b_,self._ICO_NOMBRE)):ico=os.path.join(b_,self._ICO_NOMBRE);break
        self._bandeja=_Bandeja(ico,T("titulo"),lambda:self.root.after(0,self._bandeja_volver),lambda:self.root.after(0,self._bandeja_menu))
        if not self._bandeja.ok:self._bandeja=None;return
        self.root.bind("<Unmap>",self._bandeja_unmap,add="+")
        self.root.after(300,self._bandeja_poll)
    def _bandeja_poll(self):
        """los clics en el icono, desde Tk (no desde la función de Windows, que cerraba el programa)"""
        b_=getattr(self,"_bandeja",None)
        if b_ is None:return
        try:
            while b_.pend:
                ev=b_.pend.pop(0)
                if ev=="izq":self._bandeja_volver()
                elif ev=="der":self._bandeja_menu()
        except Exception:pass
        try:self.root.after(150,self._bandeja_poll)
        except Exception:pass
    def _bandeja_unmap(self,e=None):
        """al minimizar: la ventana se esconde (fuera de la barra de tareas) y queda el icono junto al reloj"""
        try:
            if e is not None and e.widget is not self.root:return
            if self._bandeja is None or self.root.state()!="iconic":return
            vb=getattr(self,"var_bandeja",None)
            if vb is not None and not vb.get():return   # (JMG, 11-11) opción de la Salida: a la barra de tareas, como siempre
            if self._bandeja.poner(self._bandeja_tip()):
                self.root.withdraw();self._bandeja_tick()
        except Exception:pass
    def _bandeja_tip(self):
        t=T("titulo")
        try:
            if getattr(self,"procesando",False):t+=f" · {int(float(self.prog['value']))} %"
        except Exception:pass
        return t
    def _bandeja_tick(self):
        """mientras está en la bandeja, el texto del icono dice cómo va el proceso"""
        b_=getattr(self,"_bandeja",None)
        if b_ is None or not b_.visible:return
        try:b_.texto(self._bandeja_tip())
        except Exception:pass
        self.root.after(1000,self._bandeja_tick)
    def _fin_poner(self,k):
        """«Al terminar» desde el menú de la bandeja (el desplegable de abajo también cambia)"""
        self.var_al_terminar.set(k)
        try:self.cmb_fin.current(["nada","salir","apagar","suspender"].index(k))
        except Exception:pass
    def _bandeja_volver(self):
        try:
            if self._bandeja is not None:self._bandeja.quitar()
            self.root.deiconify();self.root.state("normal");self.root.lift()
            self.root.attributes("-topmost",True);self.root.after(300,lambda:self.root.attributes("-topmost",False))
            self.root.focus_force()
        except Exception:pass
    def _bandeja_menu(self):
        """(JMG, 11-11) clic derecho: si se ha minimizado es que se está procesando; lo que hace falta: cancelar y qué hacer al terminar"""
        V=self._vt;G,C=0x1,0x8   # apagada, con ✓
        ops=[(V("Mostrar ","Show ")+T("titulo"),self._bandeja_volver),(V("📤 Extracción...","📤 Extraction..."),self._ext_elegir,G if getattr(self,"procesando",False) else 0)]   # (JMG, 15-11)
        try:   # (JMG, 16-11) con un disco en el lector: ripearlo (DVD o Blu-ray de vídeo) y crear su imagen ISO
            for r_,et,video,datos in self._discos():
                n_=f"«{et or r_[:2]}» ({r_[:2]})";gr=G if getattr(self,"procesando",False) else 0
                if video:ops.append((V("💿 Ripear ","💿 Rip ")+n_,lambda r_=r_:self._disco_ripear(r_),gr))
                if datos:ops.append((V("💿 Crear imagen ISO de ","💿 Create ISO image of ")+n_,lambda r_=r_:self._disco_imagen(r_),gr))
        except Exception:pass
        if getattr(self,"procesando",False):
            ops+=[None,(V("Procesando: ","Processing: ")+f"{int(float(self.prog['value']))} %",None,G),(V("⏹ Cancelar el proceso","⏹ Cancel the process"),self._cancel)]
        ops+=[None,(V("Al terminar:","When done:"),None,G)]
        a=self.var_al_terminar.get()
        for k,t in (("nada",T("al_nada")),("salir",T("al_salir")),("apagar",T("al_apagar")),("suspender",T("al_suspender"))):ops.append(("      "+t,lambda k=k:self._fin_poner(k),C if a==k else 0))
        ab=getattr(self,"var_abrir",None) or getattr(self,"var_abrir_dest",None)
        if ab is not None:ops+=[None,(V("Abrir la carpeta al terminar","Open the folder when done"),lambda:(ab.set(not ab.get()),self._save_cfg()),C if ab.get() else 0)]
        ops+=[None,(V("Salir","Exit"),lambda:(self._bandeja_volver(),self.root.after(150,self._bandeja_salir)))]
        try:self._bandeja.menu(ops)
        except Exception:pass
    # --- descripciones al pasar el ratón: salen al medio segundo y se van solas a los 6 segundos (o al moverse / hacer clic) ---
    _TIP_RETRASO=600;_TIP_DURA=6000
    def _tips_iniciar(self):
        if getattr(self,"_tips_on",False):return
        self._tips_on=True;self._tip_top=None;self._tip_id=None;self._tip_fin=None
        if not hasattr(self,"_tip_fijo"):self._tip_fijo={}
        for ev,f in (("<Enter>",self._tip_entrar),("<Leave>",self._tip_quitar),("<ButtonPress>",self._tip_quitar),("<KeyPress>",self._tip_quitar)):
            self.root.bind_all(ev,f,add="+")
    def _tip_entrar(self,e):
        self._tip_quitar()
        try:
            w=e.widget
            if isinstance(w,str):return
            txt=self._tip_texto(w)
        except Exception:return
        if txt:self._tip_id=self.root.after(self._TIP_RETRASO,lambda:self._tip_mostrar(w,txt))
    def _tip_mostrar(self,w,txt):
        self._tip_id=None
        try:
            if not w.winfo_ismapped():return
            x,y=self.root.winfo_pointerxy()
            if self.root.winfo_containing(x,y) is not w:return
            t=tk.Toplevel(self.root);t.overrideredirect(True);t.attributes("-topmost",True)
            tk.Label(t,text=txt,bg=CDN,fg=CT,relief="solid",borderwidth=1,padx=8,pady=4,font=("",9),justify="left",wraplength=380).pack()
            t.update_idletasks();tw,th=t.winfo_width(),t.winfo_height()
            sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight()
            px=min(x+16,sw-tw-4);py=y+20 if y+20+th<sh-40 else y-th-12
            t.geometry(f"+{max(0,px)}+{max(0,py)}");self._tip_top=t
            self._tip_fin=self.root.after(self._TIP_DURA,self._tip_quitar)
        except Exception:pass
    def _tip_quitar(self,e=None):
        for k in ("_tip_id","_tip_fin"):
            i=getattr(self,k,None)
            if i:
                try:self.root.after_cancel(i)
                except Exception:pass
            setattr(self,k,None)
        t=getattr(self,"_tip_top",None)
        if t is not None:
            try:t.destroy()
            except Exception:pass
            self._tip_top=None
    @staticmethod
    def _tip_norm(t):
        t=str(t).replace("«","").replace("»","").replace("\n"," ").strip()
        i=0
        while i<len(t) and not (t[i].isalnum() and ord(t[i])<0x2000):i+=1   # (los símbolos como ℹ cuentan como letras)
        return t[i:].lower() if i<len(t) else t.lower()
    def _tip_vecino(self,w):
        """el texto de la etiqueta de un deslizador, casilla de número o desplegable: la de su misma fila, o la de antes"""
        p=w.master
        try:
            gi=w.grid_info()
            if gi:
                r=int(gi.get("row",-1));c0=int(gi.get("column",0))
                cand=[(int(x.grid_info().get("column",0)),x) for x in p.grid_slaves(row=r) if x is not w and x.winfo_class() in ("TLabel","Label")]
                cand=[cx for cx in cand if cx[0]<c0] or cand
                if cand:return str(sorted(cand,key=lambda a:a[0])[-1 if cand[0][0]<c0 else 0][1].cget("text"))
        except Exception:pass
        try:
            hs=p.winfo_children();i=hs.index(w)
            for x in reversed(hs[:i]):
                if x.winfo_class() in ("TLabel","Label"):
                    t=str(x.cget("text")).strip()
                    if t:return t
        except Exception:pass
        return ""
    def _tip_texto(self,w):
        k=str(w)
        if k in getattr(self,"_tip_fijo",{}):return self._tip_fijo[k]
        cls=w.winfo_class()
        if cls in ("TButton","Button","TLabel","Label","TCheckbutton","Checkbutton","TRadiobutton","Radiobutton","TMenubutton"):
            try:t=str(w.cget("text"))
            except Exception:t=""
            if len(t)>70:return None   # las notas largas ya se explican solas
        elif cls in ("TScale","Scale","Entry","TEntry","TCombobox","TSpinbox","Spinbox"):t=self._tip_vecino(w)
        else:return None
        n=self._tip_norm(t)
        if not n:return None
        es=IDIOMA=="es"
        for pats,a,b in self._TIPS:
            for p in pats:
                if p.startswith("@"):
                    c_,p=p[1:].split("@",1)
                    if c_!=cls:continue
                if (n==p[1:]) if p.startswith("=") else n.startswith(p):return a if es else b
        return None
    _TIPS=[
        # --- abajo ---
        (("=procesar","=process"),"Empieza a procesar todo lo que está en la lista, con los ajustes de cada archivo o pista.","Starts processing everything in the list, with the settings of each file or track."),
        (("=cancelar","=cancel"),"Para el proceso en marcha. Lo que se estaba haciendo no se guarda a medias.","Stops the running process. What was being made is not left half-saved."),
        (("resetear","reset"),"Vuelve a los valores de fábrica los ajustes del archivo o pista seleccionados (con «Todo», los de todo el programa).","Puts the selected file or track settings back to the factory values (with «All», the whole program)."),
        (("=todo","=all"),"Marcado, «Resetear» lo deja todo como recién instalado: todos los archivos, la salida y las opciones.","Ticked, «Reset» leaves everything as just installed: all files, the output and the options."),
        (("deshacer","undo"),"Deshace la última acción (hasta 5).","Undoes the last action (up to 5)."),
        (("rehacer","redo"),"Vuelve a hacer lo que se ha deshecho.","Redoes what was undone."),
        (("al terminar","when done"),"Qué hacer cuando acabe el proceso: nada, apagar el PC, suspenderlo...","What to do when the process ends: nothing, shut down the PC, sleep..."),
        (("salir","exit"),"Cierra el programa (si hay un proceso en marcha, pregunta antes).","Closes the program (if a process is running, it asks first)."),
        # --- ventana de Aften ---
        (("cbr","cbr"),"Bitrate fijo: el elegido en el desplegable. Lo leen todos los aparatos.","Fixed bitrate: the one chosen in the list. Every device reads it."),
        (("vbr","vbr"),"Bitrate variable según la calidad (0-1023). Mejor sonido por tamaño, pero no todos los aparatos lo leen.","Variable bitrate by quality (0-1023). Better sound for its size, but not every device reads it."),
        (("ancho de banda","bandwidth"),"Hasta qué frecuencia se guardan los agudos. «Adaptable variable» lo ajusta en cada momento.","Up to which frequency the treble is kept. «Variable adaptive» adjusts it at every moment."),
        (("precisión","accuracy"),"Cuánto busca Aften la mejor forma de codificar: 32 es la máxima calidad.","How hard Aften looks for the best encoding: 32 is the highest quality."),
        (("conmutación de bloques","block switching"),"Golpes más nítidos (bloques cortos en los transitorios).","Crisper hits (short blocks on transients)."),
        (("filtro del ancho","bandwidth filter"),"Filtro paso bajo al ancho de banda elegido.","Low-pass filter at the chosen bandwidth."),
        (("filtro de continua","dc filter"),"Quita la corriente continua (un desplazamiento de la onda).","Removes DC offset."),
        (("filtro del subwoofer","lfe filter"),"Filtro paso bajo de 120 Hz en el subwoofer.","120 Hz low-pass filter on the subwoofer."),
        (("compresión (drc)","compression (drc)"),"La compresión que puede aplicar el amplificador en modo nocturno. «Ninguna» = toda la gama dinámica.","The compression the amplifier may apply in night mode. «None» = full dynamic range."),
        (("nivel de diálogo","dialogue level"),"El dialnorm: -31 dB = el amplificador no baja nada el volumen.","The dialnorm: -31 dB = the amplifier does not lower the volume at all."),
        (("dolby surround ex","dolby surround ex"),"Avisa al amplificador de que los traseros llevan un canal trasero central (6.1).","Tells the amplifier the surrounds carry a back center channel (6.1)."),
        (("dolby headphone","dolby headphone"),"Avisa de que el sonido está preparado para auriculares Dolby Headphone.","Tells the sound is prepared for Dolby Headphone."),
        (("dolby surround (","dolby surround ("),"En estéreo: avisa de que lleva Dolby Surround (Pro Logic).","In stereo: tells it carries Dolby Surround (Pro Logic)."),
        (("conversor a/d","a/d converter"),"Cómo se grabó el original: Estándar o HDCD.","How the original was recorded: Standard or HDCD."),
        (("central en el downmix","center in the downmix"),"Cuánto central entra al pasar a estéreo.","How much center goes in when downmixing to stereo."),
        (("surround en el downmix","surround in the downmix"),"Cuánto de los traseros entra al pasar a estéreo.","How much of the surrounds goes in when downmixing to stereo."),
        (("downmix preferido","preferred downmix"),"El tipo de estéreo que debe hacer el amplificador: Lt/Rt (Pro Logic) o Lo/Ro (normal).","The stereo the amplifier should make: Lt/Rt (Pro Logic) or Lo/Ro (normal)."),
        (("lt/rt","lo/ro"),"Nivel de este canal en ese tipo de downmix.","Level of this channel in that kind of downmix."),
        (("argumentos propios","own arguments"),"Opciones de Aften escritas a mano (para expertos).","Aften options typed by hand (for experts)."),
        # --- arriba ---
        (("seleccionar...","select..."),"Elige los archivos con los que trabajar (sustituye la lista).","Chooses the files to work with (replaces the list)."),
        (("añadir...","add..."),"Añade más archivos a la lista sin quitar los que hay. También puedes arrastrarlos a la ventana.","Adds more files to the list without removing the ones there. You can also drag them onto the window."),
        (("dvd/bd","dvd/bd"),"Abre un DVD o un Blu-ray (el disco, su carpeta o su imagen ISO) para codificar su película.","Opens a DVD or a Blu-ray (the disc, its folder or its ISO image) to encode its movie."),
        (("crear iso","create iso"),"Hace una imagen ISO de un disco o de una carpeta (copia exacta; los discos protegidos, con aviso).","Makes an ISO image of a disc or a folder (exact copy; protected discs, with a warning)."),
        (("=quitar","=remove"),"Quita de la lista lo seleccionado (el archivo no se borra).","Removes the selection from the list (the file is not deleted)."),
        (("limpiar","clear"),"Vacía la lista entera.","Empties the whole list."),
        (("a audioprocesador","to audioprocesador"),"Pasa los archivos seleccionados a Jmg AudioProcesador (si está abierto, a su lista; si no, lo abre con ellos).","Sends the selected files to Jmg AudioProcesador (if it is open, to its list; if not, it opens with them)."),
        (("a videoencoder","to videoencoder"),"Pasa los archivos seleccionados a Jmg VideoEncoder (si está abierto, a su lista; si no, lo abre con ellos).","Sends the selected files to Jmg VideoEncoder (if it is open, to its list; if not, it opens with them)."),
        (("guardar preset","save preset"),"Guarda todos los ajustes actuales con un nombre, para usarlos otra vez.","Saves all the current settings under a name, to use them again."),
        (("cargar preset","load preset"),"Pone unos ajustes guardados antes con «Guardar preset».","Applies settings saved before with «Save preset»."),
        (("ayuda","help"),"La ayuda completa del programa, en 9 idiomas.","The full help of the program, in 9 languages."),
        (("acerca de","about"),"Versión, autor, licencias y cómo apoyar el proyecto.","Version, author, licences and how to support the project."),
        (("tema","theme"),"Cambia entre el tema oscuro y el claro.","Switches between the dark and the light theme."),
        (("=es","=en"),"Idioma de la ventana: español o inglés.","Window language: Spanish or English."),
        (("=⬆","=↑"),"Sube la pista seleccionada: el orden en el archivo final.","Moves the selected track up: the order in the final file."),
        (("=⬇","=↓"),"Baja la pista seleccionada.","Moves the selected track down."),
        (("=↺",),"Vuelve a lo que había al principio.","Goes back to what there was at first."),
        (("=◀",),"Hacia atrás.","Backwards."),
        (("=▶",),"Hacia adelante.","Forwards."),
        (("=✖",),"Quita lo seleccionado.","Removes the selection."),
        (("=procesador","=processor","=cpu"),"Codifica con el procesador: la mejor calidad para el tamaño, pero más lento.","Encodes with the processor: the best quality for its size, but slower."),
        (("=nvidia",),"Codifica con la tarjeta gráfica NVIDIA (NVENC): mucho más rápido.","Encodes with the NVIDIA graphics card (NVENC): much faster."),
        (("=amd",),"Codifica con la tarjeta gráfica AMD (AMF): mucho más rápido.","Encodes with the AMD graphics card (AMF): much faster."),
        (("dos pasadas","two passes","2 pasadas","2 passes"),"Analiza el vídeo una vez antes de codificarlo: reparte mejor el bitrate (tarda el doble).","Analyses the video once before encoding it: spreads the bitrate better (takes twice as long)."),
        (("=mov",),"MOV: el de Apple, para editar.","MOV: Apple's, for editing."),
        (("=avi",),"AVI: para aparatos antiguos (sin subtítulos; audio AC3, MP3 o DTS).","AVI: for old devices (no subtitles; AC3, MP3 or DTS audio)."),
        (("=webm",),"WebM: para la web (VP9 o AV1 con Opus).","WebM: for the web (VP9 or AV1 with Opus)."),
        (("pausa","pause"),"Pausa la escucha (otra vez, sigue).","Pauses playback (again, it goes on)."),
        (("parar","stop"),"Para la escucha y vuelve al principio.","Stops playback and goes back to the start."),
        (("editar el archivo","edit the file"),"Edita a mano el archivo WAV o FLAC: marca un trozo y cambia su volumen.","Edits the WAV or FLAC file by hand: mark a piece and change its volume."),
        (("=aplicar","=apply"),"Aplica el cambio de volumen al trozo marcado.","Applies the volume change to the marked piece."),
        (("oír la selección","hear the selection"),"Escucha solo el trozo marcado.","Plays only the marked piece."),
        (("=guardar","=save"),"Guarda los cambios en el archivo.","Saves the changes to the file."),
        (("al minimizar","when minimized"),"Marcado: al minimizar, el programa se esconde y queda como icono junto al reloj (clic izquierdo = vuelve; clic derecho = cancelar, al terminar...). Sin marcar: a la barra de tareas, como siempre.","Ticked: when minimized, the program hides and stays as an icon next to the clock (left click = back; right click = cancel, when done...). Unticked: to the taskbar, as usual."),
        (("grabar en la imagen","burn into"),"Dibuja este subtítulo en el vídeo: se ve en cualquier aparato, pero ya no se puede quitar. Solo uno; hay que recomprimir el vídeo.","Draws this subtitle into the video: it shows on any device, but it can no longer be removed. Only one; the video must be re-encoded."),
        # --- lista (VideoEncoder) ---
        (("agregar","add to queue"),"Mete el vídeo seleccionado en la cola de trabajo, con sus ajustes.","Puts the selected video in the work queue, with its settings."),
        (("no procesar","do not process"),"Saca el vídeo de la cola (sigue en la lista, sin procesar).","Takes the video out of the queue (it stays in the list, unprocessed)."),
        (("combinar vídeos","combine videos"),"Une varios vídeos en uno o corta uno en trozos, con todas sus pistas.","Joins several videos into one or cuts one into pieces, with all their tracks."),
        # --- Vídeo ---
        (("=auto",),"Mide y lo pone solo según la película. Pulsado otra vez sin tocar nada, lo quita. En verde mientras sigue lo que puso.","Measures and sets it by itself for the movie. Pressed again without touching anything, it removes it. Green while what it set is still in place."),
        (("códec de vídeo","video codec"),"Con qué se comprime la imagen: H.265 (pequeño y bueno), H.264 (lo lee todo), AV1 (lo más moderno) o Passthrough (sin tocar).","How the picture is compressed: H.265 (small and good), H.264 (plays everywhere), AV1 (the newest) or Passthrough (untouched)."),
        (("codificar con","encode with"),"Procesador (la mejor calidad por tamaño) o la tarjeta gráfica NVIDIA / AMD (mucho más rápido).","Processor (the best quality for its size) or the NVIDIA / AMD graphics card (much faster)."),
        (("calidad constante","constant quality"),"La misma calidad en toda la película; el tamaño final depende de la película.","The same quality throughout the movie; the final size depends on the movie."),
        (("bitrate (tamaño fijo)","bitrate (fixed size)"),"Un tamaño final conocido de antemano (con 2 pasadas, mejor repartido).","A final size known in advance (with 2 passes, better spread)."),
        (("calidad (menos","quality (lower"),"Número de calidad: más bajo = mejor imagen y archivo más grande.","Quality number: lower = better picture and bigger file."),
        (("bitrate (kbps)","bitrate (kbps)"),"Kilobits por segundo del vídeo: más = mejor imagen y archivo más grande.","Video kilobits per second: more = better picture and bigger file."),
        (("velocidad","speed"),"Más lento = un poco más de calidad para el mismo tamaño.","Slower = a little more quality for the same size."),
        (("resolución","resolution"),"El tamaño de la imagen de salida (sin cambiar, 1080p, 720p...).","The size of the output picture (unchanged, 1080p, 720p...)."),
        (("profundidad","bit depth"),"8 o 10 bits de color: 10 bits evita bandas en cielos y sombras.","8 or 10 bits of colour: 10 bits avoids banding in skies and shadows."),
        (("desentrelazar","deinterlace"),"Quita las rayas de los vídeos entrelazados (televisión, DVD antiguos).","Removes the combing lines of interlaced videos (TV, old DVDs)."),
        (("más opciones","more options","opciones avanzadas","advanced options"),"Antes y después de la imagen, recorte por tramos, brillo, contraste, nitidez, bandas negras y reproducir.","Picture before and after, trimming by parts, brightness, contrast, sharpness, black bars and playback."),
        (("color de salida","output color"),"El color del vídeo final: igual que el original, o HDR pasado a SDR para pantallas normales.","The colour of the final video: the same as the original, or HDR turned into SDR for normal screens."),
        (("es un vídeo logarítmico","it is a log video"),"Márcalo con vídeos de cámara grabados en Log: se les aplica su LUT para el color normal.","Tick it for camera videos shot in Log: their LUT is applied for normal colour."),
        (("lut","lut"),"Archivo .cube con la conversión de color de tu cámara.","A .cube file with your camera's colour conversion."),
        # --- Audio (pistas) ---
        (("idioma:","language:"),"Idioma de la pista (lo que enseñan los reproductores).","Track language (what players show)."),
        (("título:","title:"),"Nombre de la pista que enseñan los reproductores.","Track name that players show."),
        (("códec:","codec:"),"Con qué se comprime: en Vídeo, la imagen; en Audio, la pista (Passthrough = sin tocar; Aften Dolby Digital, AC3 de FFmpeg, E-AC3, DTS, FLAC...).","What it is compressed with: in Video, the picture; in Audio, the track (Passthrough = untouched; Aften Dolby Digital, FFmpeg's AC3, E-AC3, DTS, FLAC...)."),
        (("kbps","bits:"),"Calidad de la pista comprimida: más kbps = mejor sonido y más tamaño. Con Aften VBR manda la calidad de su ventana.","Compressed track quality: more kbps = better sound and more size. With Aften VBR its window's quality rules."),
        (("@TButton@por defecto","@TButton@default"),"Vuelve a los ajustes de fábrica de esta ventana.","Goes back to this window's factory settings."),
        (("por defecto","default"),"La pista que los reproductores ponen al empezar.","The track players choose when starting."),
        (("añadir pista","add track"),"Añade una pista de audio de otro archivo (un doblaje, un comentario...).","Adds an audio track from another file (a dub, a commentary...)."),
        (("eliminar pista","delete track","remove track"),"Quita la pista seleccionada del resultado.","Removes the selected track from the result."),
        (("eliminar original","remove original"),"De una pista procesada, no guarda también la original.","Of a processed track, the original is not kept as well."),
        (("visual / ondas","visual / waves"),"Ver y escuchar las ondas de cada canal, antes y después de los efectos.","See and hear the waves of each channel, before and after the effects."),
        # --- volúmenes ---
        (("frontal izq","front left"),"Volumen del altavoz delantero izquierdo, en dB.","Volume of the front left speaker, in dB."),
        (("frontal der","front right"),"Volumen del altavoz delantero derecho, en dB.","Volume of the front right speaker, in dB."),
        (("central (fc):","center (fc):"),"Gama dinámica del central (los diálogos): más contraste entre lo flojo y lo fuerte.","Dynamic range of the center (dialogue): more contrast between quiet and loud."),
        (("central (fc)","center (fc)"),"Volumen del canal central (los diálogos), en dB.","Volume of the center channel (dialogue), in dB."),
        (("subwoofer (lfe)","subwoofer (lfe)"),"Volumen del subwoofer, en dB.","Subwoofer volume, in dB."),
        (("trasero izq","surround left","surround izq"),"Volumen del altavoz trasero izquierdo, en dB.","Volume of the left surround speaker, in dB."),
        (("trasero der","surround right","surround der"),"Volumen del altavoz trasero derecho, en dB.","Volume of the right surround speaker, in dB."),
        (("volumen por canal","volume per channel"),"El volumen de cada altavoz por separado. «Auto» los equilibra como en el cine (el central no se toca).","The volume of each speaker separately. «Auto» balances them as in the cinema (the center is not touched)."),
        # --- sincronización ---
        (("sincronización del subtítulo","sincronización","synchronization"),"Para que la pista vaya a la vez que la imagen: framerate y delay.","So the track goes with the picture: framerate and delay."),
        (("framerate","de:","from:","=a:","=to:"),"Cambia la velocidad de la pista (por ejemplo de 25 a 23,976 fps) para una edición de otro país.","Changes the track speed (for example from 25 to 23.976 fps) for an edition from another country."),
        (("con cambio de tono","with pitch change"),"Como en el cine: el tono cambia un poco y es lo más limpio.","As in the cinema: the pitch changes slightly and it is the cleanest."),
        (("sin cambio de tono","without pitch change"),"Mantiene el tono original al cambiar la velocidad.","Keeps the original pitch when changing the speed."),
        (("delay automático","automatic delay"),"Calcula el delay solo comparando con otra pista.","Works out the delay by itself comparing with another track."),
        (("delay por canal","delay per channel"),"Retrasa un canal para compensar un altavoz más cercano (5 ms ≈ 1,7 m).","Delays one channel to make up for a closer speaker (5 ms ≈ 1.7 m)."),
        (("delay","delay inicial","initial delay"),"Adelanta (-) o retrasa (+) toda la pista respecto al vídeo, en milisegundos.","Moves the whole track earlier (-) or later (+) against the video, in milliseconds."),
        (("comparar con","compare with"),"La pista bien sincronizada (normalmente la del idioma original) con la que se compara.","The well-synchronized track (normally the original-language one) to compare with."),
        (("calcular delay","calculate delay"),"Calcula solo el delay comparando la música y los efectos con la otra pista.","Works out the delay by itself, comparing music and effects with the other track."),
        (("corregir por tramos","fix by parts"),"Para las pistas que se desincronizan a ratos (cortes de otra edición): corrige cada trozo.","For tracks that drift at times (cuts from another edition): fixes each piece."),
        (("quitar tramos","=quitar tramos"),"Quita la corrección por tramos.","Removes the fix by parts."),
        (("revisar sincronización","check synchronization"),"Escucha un momento de las dos pistas a la vez para comprobar que van juntas.","Listen to a moment of both tracks at once to check they go together."),
        # --- efectos de audio ---
        (("suavizado digital","digital smoothing"),"Quita el exceso de agudos (eses y brillo metálico) de muchas películas y doblajes de los 80 y 90. No va junto con el ecualizador.","Removes the excess treble (harsh S sounds, metallic shine) of many 80s and 90s movies and dubs. It does not go with the equalizer."),
        (("intensidad","amount","strength"),"Cuánto actúa el efecto: 0 = apagado.","How much the effect acts: 0 = off."),
        (("ecualizador de 3 bandas","eq 3 bandas","eq 3 bands","3-band equalizer"),"Graves, medios y agudos de los altavoces (el subwoofer no). No va junto con el Suavizado.","Bass, mids and treble of the speakers (not the subwoofer). It does not go with Smoothing."),
        (("graves","bass ("),"Sube o baja los graves (alrededor de 100 Hz).","Raises or lowers the bass (around 100 Hz)."),
        (("medios","mids"),"Sube o baja los medios (alrededor de 1 kHz), donde están las voces.","Raises or lowers the mids (around 1 kHz), where the voices are."),
        (("agudos","treble"),"Sube o baja los agudos (alrededor de 5 kHz).","Raises or lowers the treble (around 5 kHz)."),
        (("double bass","double bass"),"Copia los graves del subwoofer a los altavoces, y los de los altavoces al subwoofer, sin quitarlos de donde están.","Copies the subwoofer's bass to the speakers, and the speakers' to the subwoofer, without removing them."),
        (("presencia central","center presence"),"Upmix: cuánto sonido común va al canal central.","Upmix: how much common sound goes to the center channel."),
        (("presencia","presence"),"Realza o baja las voces, el ambiente, los efectos y el subwoofer.","Raises or lowers the voices, ambience, effects and subwoofer."),
        (("voz (solo","voice (center"),"Sube o baja los diálogos (solo el canal central).","Raises or lowers the dialogue (center channel only)."),
        (("música","music"),"Sube o baja la música y el ambiente de los demás altavoces.","Raises or lowers the music and ambience of the other speakers."),
        (("efectos (no","effects (no","effects (not"),"Sube o baja los efectos (golpes, explosiones) de los demás altavoces.","Raises or lowers the effects (hits, explosions) of the other speakers."),
        (("subwoofer 0-10",),"Intensidad para el subwoofer (0 = sin efecto; mejor a 0 con Bass Management o Double Bass).","Strength for the subwoofer (0 = no effect; better 0 with Bass Management or Double Bass)."),
        (("=subwoofer",),"Sube o baja el subwoofer respecto a los diálogos.","Raises or lowers the subwoofer against the dialogue."),
        (("techo limitador","limiter ceiling"),"Hasta dónde pueden llegar los picos: evita que el sonido se sature.","How high peaks may go: keeps the sound from clipping."),
        (("gama dinámica / compresión","dynamic range / compression"),"A la izquierda, más contraste entre lo flojo y lo fuerte; a la derecha, compresión: suben los sonidos flojos (de noche).","To the left, more contrast between quiet and loud; to the right, compression: quiet sounds go up (at night)."),
        (("delanteros y traseros","fronts and surrounds"),"Gama dinámica o compresión de todos los altavoces menos el central.","Dynamic range or compression of all speakers except the center."),
        (("frontales (fl/fr)","front (fl/fr)"),"Gama dinámica de los delanteros: más contraste.","Dynamic range of the fronts: more contrast."),
        (("traseros (bl/br)","surround (bl/br)"),"Gama dinámica de los traseros: más contraste.","Dynamic range of the surrounds: more contrast."),
        (("gama dinámica","dynamic range"),"Aumenta el contraste: los sonidos flojos bajan y los fuertes se quedan igual. Esconde ruidos y eco.","Increases the contrast: quiet sounds go down and loud ones stay. Hides noise and echo."),
        (("procesado dinámico","dynamic processing"),"Elevación (sube lo flojo), Impacto (lo fuerte destaca) o las dos cosas, por grupos de altavoces.","Elevation (raises the quiet), Impact (the loud stands out) or both, per speaker group."),
        (("modo:","mode:"),"0 = apagado · 1 Elevación: sube lo flojo · 2 Impacto: lo fuerte destaca · 3 las dos cosas.","0 = off · 1 Elevation: raises the quiet · 2 Impact: the loud stands out · 3 both."),
        (("front./traseros","front/rear"),"Intensidad para los delanteros y traseros (0 = sin efecto).","Strength for the fronts and surrounds (0 = no effect)."),
        (("central 0-10","center 0-10"),"Intensidad para el central (0 = sin efecto).","Strength for the center (0 = no effect)."),
        (("=central","=center"),"Solo el canal central, el de los diálogos.","Only the center channel, the dialogue one."),
        (("=frontales","=front"),"El grupo de los altavoces delanteros.","The front speakers group."),
        (("=traseros","=surround"),"El grupo de los altavoces traseros.","The surround speakers group."),
        # --- AudioProcesador: volumen y normalización ---
        (("master","master"),"Volumen general de la pista, en dB.","Overall track volume, in dB."),
        (("normalizar el volumen","normalize the volume"),"Deja la pista al volumen objetivo midiéndolo (Loudnorm), sin comprimir.","Brings the track to the target loudness by measuring it (Loudnorm), without compressing."),
        (("normalizar","normalize"),"Mide ya el volumen de la pista (si no, se mide al PROCESAR).","Measures the track loudness now (otherwise it is measured on PROCESS)."),
        (("ajustar master","set master"),"Mide el volumen y pone el Master exacto para llegar al objetivo.","Measures the loudness and sets the exact Master to reach the target."),
        (("objetivo","target"),"El volumen al que se quiere llegar (LUFS): cine, televisión, música...","The loudness to reach (LUFS): cinema, TV, music..."),
        (("atenuación","attenuation"),"Baja un poco el resultado para dejar margen a los picos.","Lowers the result a little to leave room for peaks."),
        (("otras normalizaciones","other normalizations"),"Normalizaciones que comprimen: igualan lo flojo y lo fuerte.","Normalizations that compress: they even out quiet and loud."),
        (("dynaudnorm","dynaudnorm"),"Sube lo flojo y baja lo fuerte poco a poco, sin que se note.","Raises the quiet and lowers the loud gradually, unnoticed."),
        (("speechnorm","speechnorm"),"Iguala el volumen de los diálogos.","Evens out the dialogue loudness."),
        (("canales:","channels:"),"Los canales de la pista seleccionada.","The channels of the selected track."),
        (("título pista procesada","processed track title"),"Nombre que llevará la pista procesada.","Name the processed track will carry."),
        (("seleccionar todas","select all"),"Selecciona todas las pistas del archivo.","Selects all the tracks of the file."),
        (("aplicar a todas","apply to all"),"Copia los ajustes de esta pista a todas las seleccionadas.","Copies this track's settings to all the selected ones."),
        (("combinar","combine"),"Une pistas de varios archivos en una o mezcla canales a mano.","Joins tracks from several files into one or mixes channels by hand."),
        (("método","method"),"Cómo se cambia la velocidad del audio.","How the audio speed is changed."),
        (("tiempo de la pista","track timing"),"El inicio y la duración exactos de la pista, al milisegundo.","The exact start and length of the track, to the millisecond."),
        (("eq avanzado","advanced eq"),"Tres bandas con su frecuencia, por grupo de altavoces.","Three bands with their frequency, per speaker group."),
        (("banda ","band "),"Ganancia de esta banda en dB (a la derecha, su frecuencia).","Gain of this band in dB (on the right, its frequency)."),
        (("freq","freq"),"Frecuencia central de la banda, en Hz.","Center frequency of the band, in Hz."),
        (("fl:","fr:","fc:","bl:","br:"),"Retraso de este canal, en milisegundos.","Delay of this channel, in milliseconds."),
        (("limpieza de audio","audio cleanup"),"Para grabaciones antiguas o con ruido de fondo.","For old recordings or with background noise."),
        (("reducir ruido","noise reduction"),"Quita el soplido o siseo de fondo: 0 = apagado.","Removes the background hiss: 0 = off."),
        (("quitar clics","remove clicks"),"Quita los clics y crujidos (discos de vinilo, grabaciones viejas).","Removes clicks and crackles (vinyl, old recordings)."),
        (("reparar saturación","repair clipping"),"Reconstruye los picos recortados de un audio saturado.","Rebuilds the clipped peaks of a saturated audio."),
        (("bass management","bass management"),"Pasa al subwoofer los graves de los demás altavoces.","Sends the other speakers' bass to the subwoofer."),
        (("corte de graves","crossover"),"Frecuencia por debajo de la cual los graves van al subwoofer.","Frequency below which the bass goes to the subwoofer."),
        # --- AudioProcesador: salida ---
        (("carpeta de destino","output folder","destination folder"),"Dónde se guarda el resultado.","Where the result is saved."),
        (("junto al original","next to"),"El resultado se guarda en la misma carpeta que el original; de un disco o una imagen ISO, en Vídeos.","The result is saved in the same folder as the original; from a disc or an ISO image, in Videos."),
        (("carpeta personalizada","carpeta elegida","custom folder"),"El resultado se guarda en la carpeta que elijas.","The result is saved in the folder you choose."),
        (("elegir imagen","choose image"),"Pone tu propia portada.","Sets your own cover."),
        (("elegir carpeta","elegir...","choose"),"Elige la carpeta.","Chooses the folder."),
        (("abrir la carpeta","open the"),"Al terminar se abre la carpeta del resultado (no si el PC se apaga).","When done, the result folder opens (not if the PC shuts down)."),
        (("si el archivo","if file","if the file"),"Qué hacer si ya hay un archivo con ese nombre.","What to do if a file with that name already exists."),
        (("sobrescribir","overwrite"),"Reemplaza el archivo que ya existe.","Replaces the existing file."),
        (("renombrar","rename"),"Guarda con otro nombre (_1, _2...) y no toca el que ya existe.","Saves under another name (_1, _2...) and leaves the existing one."),
        (("upmix","upmix"),"Convierte una pista estéreo en 5.1.","Turns a stereo track into 5.1."),
        (("quitar voz","remove voice"),"Upmix: cuánto se quita la voz de los delanteros y traseros (queda en el central).","Upmix: how much voice is removed from fronts and surrounds (it stays in the center)."),
        (("downmix","downmix"),"Convierte una pista 5.1 o 7.1 en estéreo (Dolby: los traseros quedan codificados para Pro Logic).","Turns a 5.1 or 7.1 track into stereo (Dolby: the surrounds stay encoded for Pro Logic)."),
        (("incluir subwoofer","include subwoofer"),"En el downmix, el subwoofer también se suma (-10 dB).","In the downmix, the subwoofer is added too (-10 dB)."),
        (("canales de salida","output channels"),"Cuántos canales tendrá el resultado; los que sobran se suman a los demás.","How many channels the result has; the extra ones are added to the others."),
        (("formato de salida","output format"),"Formato del resultado: Aften Dolby Digital, AC3, E-AC3, DTS, AAC, FLAC, WAV...","Result format: Aften Dolby Digital, AC3, E-AC3, DTS, AAC, FLAC, WAV..."),
        (("bitrate / modo","bitrate / mode"),"Calidad del formato elegido. Con Aften en VBR manda la calidad de su ventana.","Quality of the chosen format. With Aften in VBR its window's quality rules."),
        (("aften","aften"),"Ajustes de Aften de esta pista: CBR o VBR, ancho de banda, gama dinámica e información del flujo.","This track's Aften settings: CBR or VBR, bandwidth, dynamic range and bitstream information."),
        (("modo de salida","output mode"),"Solo el audio, o un MKV con el vídeo copiado y las pistas procesadas.","Audio only, or an MKV with the video copied and the processed tracks."),
        (("solo audio","audio only"),"Guarda solo las pistas de audio.","Saves only the audio tracks."),
        (("mkv con vídeo","mkv with video"),"Un MKV con el vídeo original (sin recodificar) y las pistas procesadas.","An MKV with the original video (not re-encoded) and the processed tracks."),
        (("copiar también","also copy"),"Lo que se copia también del original.","What is also copied from the original."),
        (("=subtítulos","=subtitles"),"Copia los subtítulos del original.","Copies the original's subtitles."),
        (("capítulos","chapters"),"Copia los capítulos del original.","Copies the original's chapters."),
        (("adjuntos","attachments"),"Copia las portadas y las fuentes de los subtítulos ASS.","Copies the covers and the ASS subtitle fonts."),
        (("metadatos","metadata"),"Copia el título, el año y demás datos del original.","Copies the title, year and other data of the original."),
        (("=añadir","=add","cargado","loaded"),"Pone una portada tuya (JPG o PNG) en el MKV.","Puts your own cover (JPG or PNG) in the MKV."),
        # --- VideoEncoder: subtítulos y salida ---
        (("forzado","forced"),"Subtítulo que sale solo (los carteles y frases en otro idioma).","A subtitle that shows by itself (signs and lines in another language)."),
        (("añadir subtítulo","add external subtitle"),"Añade un subtítulo de un archivo (SRT, ASS...).","Adds a subtitle from a file (SRT, ASS...)."),
        (("quitar el externo","remove the external"),"Quita el subtítulo externo seleccionado.","Removes the selected external subtitle."),
        (("contenedor","container"),"El tipo de archivo final: MKV (lo admite todo), MP4 (más aparatos), MOV, AVI o WebM.","The final file type: MKV (takes everything), MP4 (more devices), MOV, AVI or WebM."),
        (("=mkv",),"MKV: admite todas las pistas, subtítulos y capítulos.","MKV: takes all tracks, subtitles and chapters."),
        (("=mp4",),"MP4: se ve en más aparatos (móviles, teles).","MP4: plays on more devices (phones, TVs)."),
        (("portada","cover"),"La imagen que enseñan los reproductores y el explorador.","The picture players and the file browser show."),
        (("la original","the original"),"Vuelve a la portada del original.","Goes back to the original's cover."),
        (("sin portada","no cover"),"El resultado sale sin portada.","The result has no cover."),
        (("extracción","extraction"),"Saca todo lo que lleva el vídeo (vídeo, audios, subtítulos, portadas, adjuntos y capítulos), cada cosa en su formato original y sin recomprimir, a una carpeta «(extracción)».",
         "Takes everything the video carries (video, audio tracks, subtitles, covers, attachments and chapters) out, each in its original format and without re-encoding, to an «(extraction)» folder."),
        (("nombre de este vídeo","nombre","name"),"Nombre del archivo de salida (por defecto, el original con « (Jmg VideoEncoder)»).","Output file name (by default, the original with « (Jmg VideoEncoder)»)."),
        (("copiar todo el log","copy the whole log"),"Copia el registro entero para pegarlo donde quieras.","Copies the whole log to paste it anywhere."),
        (("ver el comando","show the ffmpeg"),"Enseña la orden de FFmpeg que se va a usar.","Shows the FFmpeg command that will be used."),
        (("vaciar","clear log"),"Borra el registro.","Clears the log."),
        (("volver","back"),"Vuelve a la ventana normal.","Goes back to the normal window."),
        (("recorte por tramos","trimming by parts"),"Elige los trozos del vídeo que quieres (se unen en orden).","Chooses the parts of the video you want (joined in order)."),
        (("aquí","here"),"Pone el momento de la barra.","Sets the moment of the bar."),
        (("añadir tramo","add part"),"Añade el trozo de Inicio a Fin.","Adds the part from Start to End."),
        (("sin recorte","no trim"),"Quita todos los tramos: el vídeo entero.","Removes all parts: the whole video."),
        (("brillo","brightness"),"Más claro u oscuro.","Lighter or darker."),
        (("contraste","contrast"),"Más o menos diferencia entre lo claro y lo oscuro.","More or less difference between light and dark."),
        (("saturación","saturation"),"Colores más vivos o más apagados.","More vivid or duller colours."),
        (("nitidez","sharpness"),"Imagen más definida o más suave.","Sharper or softer picture."),
        (("quitar ruido","denoise"),"Quita el grano y el ruido de la imagen.","Removes grain and noise from the picture."),
        (("bandas negras","black bars"),"Las franjas negras de arriba y abajo (o los lados).","The black bars at the top and bottom (or the sides)."),
        (("quitarlas","remove them"),"Recorta las bandas negras.","Crops the black bars."),
        (("detectar","detect"),"Busca otra vez las bandas negras.","Looks for the black bars again."),
        (("tramo:","segment:"),"Qué parte del archivo se dibuja: los primeros minutos o todo.","Which part of the file is drawn: the first minutes or all of it."),
        (("generar visualización","generate visualization"),"Dibuja las ondas de cada canal, antes y después de los efectos.","Draws the waves of each channel, before and after the effects."),
        (("zoom","zoom"),"Amplía la altura de las ondas.","Enlarges the height of the waves."),
        (("detalle","detail"),"Más resolución en el tiempo (la rueda o la barra para moverse).","More time resolution (wheel or bar to move)."),
        (("=antes","=before","escuchar antes","play before"),"Escucha el original desde donde está la marca.","Plays the original from the mark."),
        (("=después","=after","escuchar después","play after"),"Escucha con los efectos desde donde está la marca.","Plays with the effects from the mark."),
        (("reproducir","play"),"Reproduce el vídeo en una ventana aparte.","Plays the video in a separate window."),
        (("con los ajustes","with the settings"),"Reproduce con los ajustes de imagen aplicados.","Plays with the picture settings applied."),
        (("=original",),"Reproduce el original.","Plays the original."),
    ]
    _ICO_NOMBRE="VideoEncoder.ico"
    def _bandeja_salir(self):self._on_close()
    # ---------- (JMG, 12-11) opciones avanzadas de los códecs: una ventana para todos (como la de Aften) ----------
    @staticmethod
    def _opc_norm(cod,o=None):
        """los ajustes de un códec con lo de fábrica en lo que no se ha tocado"""
        sp=OPC.get(cod) or {};x={k:ops[0][0] for k,_,_,ops,_,_ in (sp.get("ops") or [])}
        if sp.get("extra"):x["extra"]=""
        for k,v in (o or {}).items():
            if k in x:x[k]=v
        return x
    @classmethod
    def _opc_cambiadas(cls,cod,o):
        """lo que se ha tocado: [(etiqueta, valor)] en el idioma de la ventana"""
        sp=OPC.get(cod) or {};x=cls._opc_norm(cod,o);d=cls._opc_norm(cod);r=[]
        es=IDIOMA=="es"
        for k,a_,b_,ops,_,_ in (sp.get("ops") or []):
            if x[k]!=d[k]:r.append(((a_ if es else b_).rstrip(":"),next(((e_ if es else n_) for v_,e_,n_ in ops if v_==x[k]),str(x[k]))))
        if x.get("extra"):r.append(("+",x["extra"]))
        return r
    def _opc_resumen(self,cod,o):
        r=self._opc_cambiadas(cod,o)
        return ", ".join(f"{a} {b}" for a,b in r)
    @staticmethod
    def _opc_v_args(enc,o,fps,bits):
        """argumentos de FFmpeg de las opciones avanzadas de vídeo (los de -x265-params, -svtav1-params y -vvenc-params van aparte)"""
        x=o;s=":v:0";a=[]
        g=x.get("gop",0)
        if g and enc not in ("libvvenc","prores_ks","dnxhd"):a+=["-g"+s,str(max(1,int(round((fps or 25.0)*g))))]
        if enc=="libvvenc" and g:a+=["-period"+s,str(int(g))]
        if enc in ("libx264","libx265") and x.get("tune"):a+=["-tune"+s,x["tune"]]
        if enc in ("libx264","libx265","h264_amf","av1_amf") and x.get("bf",-1)>=0:a+=["-bf"+s,str(x["bf"])]
        if enc=="libx264":
            if x.get("perfil") and bits==8:a+=["-profile"+s,x["perfil"]]
            if x.get("nivel"):a+=["-level"+s,x["nivel"]]
            if x.get("refs",-1)>0:a+=["-refs"+s,str(x["refs"])]
            if x.get("aq",-1)>=0:a+=["-aq-mode"+s,str(x["aq"])]
            if x.get("extra"):a+=["-x264-params"+s,x["extra"]]
        elif enc=="libvpx-vp9":
            for k,f in (("tiles","-tile-columns"),("lag","-lag-in-frames"),("aq","-aq-mode"),("cont","-tune-content")):
                if x.get(k,-1)>=0:a+=[f+s,str(x[k])]
        elif enc.endswith("_nvenc"):
            if x.get("tune"):a+=["-tune"+s,x["tune"]]
            if x.get("multipass"):a+=["-multipass"+s,x["multipass"]]
            if x.get("saq"):a+=["-spatial-aq"+s,"1"]
            if x.get("taq"):a+=["-temporal-aq"+s,"1"]
            if x.get("look",-1)>=0:a+=["-rc-lookahead"+s,str(x["look"])]
        elif enc.endswith("_amf"):
            if x.get("hq"):a+=["-quality"+s,"high_quality"]
            if x.get("pre",-1)>=0 and (x["pre"]==0 or (_AMF_2P.get(enc) or [""])[0]=="-preanalysis"):a+=["-preanalysis"+s,str(x["pre"])]   # (22-11) si la tarjeta lo admite
            if x.get("vbaq",-1)>=0:a+=["-vbaq"+s,str(x["vbaq"])]
        elif enc=="libvvenc" and x.get("qpa",-1)>=0:a+=["-qpa"+s,str(x["qpa"])]
        if enc not in ("libx264","libx265","libsvtav1","libvvenc") and x.get("extra"):
            try:
                import shlex;a+=shlex.split(x["extra"],posix=False)
            except ValueError:pass
        return a
    @staticmethod
    def _opc_params(enc,o):
        """lo que va dentro de -x265-params / -svtav1-params / -vvenc-params (lista de clave=valor)"""
        x=o;p=[]
        if enc=="libx265":
            if x.get("refs",-1)>0:p.append(f"ref={x['refs']}")
            if x.get("aqs"):p.append(f"aq-strength={x['aqs']}")
            if x.get("psy"):p.append(f"psy-rd={x['psy']}")
        elif enc=="libsvtav1":
            if x.get("grano",0):p.append(f"film-grain={x['grano']}")
            if x.get("tune",-1)>=0:p.append(f"tune={x['tune']}")
        if enc in ("libx265","libsvtav1","libvvenc") and x.get("extra"):p+=[q for q in str(x["extra"]).split(":") if q.strip()]
        return p
    @staticmethod
    def _opc_a_args(cod,o,s):
        """argumentos de FFmpeg de las opciones avanzadas de audio; s = el especificador de la pista (":a:3", o ":a")"""
        x=o;a=[]
        if cod in ("ac3","eac3"):
            if x.get("dialnorm",-31)!=-31:a+=["-dialnorm"+s,str(x["dialnorm"])]
            for k,f in (("dsur","dsur_mode"),("dsurex","dsurex_mode"),("dhead","dheadphone_mode"),("adconv","ad_conv_type"),("dmix","dmix_mode")):
                if x.get(k):a+=["-"+f+s,x[k]]
            if x.get("sala"):a+=["-room_type"+s,x["sala"],"-mixing_level"+s,str(x["mezcla"] if x.get("mezcla",-1)>=0 else 105)]   # (FFmpeg exige el nivel de mezcla con la sala)
            elif x.get("mezcla",-1)>=0:a+=["-mixing_level"+s,str(x["mezcla"])]
        if cod=="dts" and x.get("adpcm"):a+=["-dca_adpcm"+s,"1"]
        if cod in ("ac3","eac3","aac") and x.get("cutoff"):a+=["-cutoff"+s,str(x["cutoff"])]
        if cod=="aac" and x.get("coder"):a+=["-aac_coder"+s,x["coder"]]
        if cod=="mp3":
            if x.get("vbr",-1)>=0:a+=["-q"+s,str(x["vbr"])]
            if x.get("joint",1)==0:a+=["-joint_stereo"+s,"0"]
        if cod=="opus":
            if x.get("vbr","on")!="on":a+=["-vbr"+s,x["vbr"]]
            if x.get("app","audio")!="audio":a+=["-application"+s,x["app"]]
            if x.get("trama",20)!=20:a+=["-frame_duration"+s,str(x["trama"])]
        if cod=="flac" and x.get("comp",5)!=5:a+=["-compression_level"+s,str(x["comp"])]
        if x.get("extra"):
            try:
                import shlex;a+=shlex.split(x["extra"],posix=False)
            except ValueError:pass
        return a
    def _opc_ventana(self,cod,actual,titulo,guardar):
        """la ventana de las opciones avanzadas de un códec (modal, como la de Aften): «Aceptar» llama a guardar(ajustes)"""
        V=self._vt;sp=OPC.get(cod)
        if not sp:return
        if getattr(self,"_opc_top",None) is not None:
            try:self._opc_top.lift();return
            except Exception:self._opc_top=None
        a=self._opc_norm(cod,actual)
        top=tk.Toplevel(self.root);self._opc_top=top;top.title(V("Opciones avanzadas","Advanced options")+" · "+sp["tit"]+titulo);top.configure(bg=CF);top.transient(self.root)
        f=ttk.Frame(top);f.pack(fill="both",expand=True,padx=16,pady=12)
        ttk.Label(f,text="⚙ "+sp["tit"],font=("",11,"bold")).grid(row=0,column=0,columnspan=2,sticky="w")
        ttk.Label(f,text=V(*sp["nota"]),foreground=CA,font=("",8,"italic"),wraplength=560,justify="left").grid(row=1,column=0,columnspan=2,sticky="w",pady=(2,8))
        cbs={};r=2
        for k,es,en,ops,te,tn in sp["ops"]:
            lb=ttk.Label(f,text=V(es,en));lb.grid(row=r,column=0,sticky="w",pady=(4,0))
            vals=[V(x,y) for _,x,y in ops]
            cb=ttk.Combobox(f,values=vals,width=max(12,max(len(v) for v in vals)+1),state="readonly");cb.grid(row=r,column=1,sticky="w",padx=8,pady=(4,0))
            cb.current(next((n for n,(v_,_,_) in enumerate(ops) if v_==a.get(k)),0));cbs[k]=(cb,ops)
            for w_ in (lb,cb):self._ayuda_flotante(w_,V(te,tn))
            r+=1
        vex=tk.StringVar(value=a.get("extra",""))
        if sp.get("extra"):
            lb=ttk.Label(f,text=V(*sp["extra"]));lb.grid(row=r,column=0,sticky="w",pady=(12,0))
            en_=tk.Entry(f,textvariable=vex,width=48,bg=CDN,fg=CT,insertbackground=CT,relief="flat",highlightthickness=1,highlightbackground=CSB,highlightcolor=CID)
            en_.grid(row=r,column=1,sticky="w",padx=8,pady=(12,0),ipady=3);r+=1
            for w_ in (lb,en_):self._ayuda_flotante(w_,V("Para expertos: se añaden tal cual a la orden de FFmpeg de este códec.","For experts: added as they are to this codec's FFmpeg command."))
        def leer():
            x={}
            for k,(cb,ops) in cbs.items():
                i=cb.current();x[k]=ops[i][0] if 0<=i<len(ops) else ops[0][0]
            if sp.get("extra"):x["extra"]=vex.get().strip()
            return x
        def poner(x):
            x=self._opc_norm(cod,x)
            for k,(cb,ops) in cbs.items():cb.current(next((n for n,(v_,_,_) in enumerate(ops) if v_==x.get(k)),0))
            vex.set(x.get("extra",""))
        def cerrar():
            try:top.grab_release();top.destroy()
            except Exception:pass
            if self._opc_top is not None:
                self._opc_top=None
                try:self._af_modal(False)
                except Exception:pass
        def aceptar():
            x=leer();cerrar();guardar(x)
        bf=ttk.Frame(f);bf.grid(row=r,column=0,columnspan=2,sticky="ew",pady=(16,0))
        ttk.Button(bf,text="↺ "+V("Por defecto","Default"),command=lambda:poner({})).pack(side="left")
        ttk.Button(bf,text=V("Cancelar","Cancel"),command=cerrar).pack(side="right")
        ttk.Button(bf,text=V("Aceptar","OK"),command=aceptar).pack(side="right",padx=6)
        top.protocol("WM_DELETE_WINDOW",cerrar)
        try:self._af_modal(True)
        except Exception:pass
        try:top.update_idletasks();top.geometry(f"+{self.root.winfo_rootx()+120}+{self.root.winfo_rooty()+80}");top.grab_set()
        except Exception:pass
        self._opc_leer=leer;self._opc_poner=poner;self._opc_aceptar=aceptar;self._opc_cerrar=cerrar   # (para las pruebas)
    def _ayuda_flotante(self,w,texto):
        """(JMG, 10-11) texto al pasar el ratón: con las demás descripciones (sale al medio segundo y se va solo)"""
        if not hasattr(self,"_tip_fijo"):self._tip_fijo={}
        self._tip_fijo[str(w)]=texto
    def _toast(self,titulo,mensaje,tipo="info",seg=5):
        """ventana emergente con el tema del programa, se cierra sola"""
        if threading.current_thread()!=threading.main_thread():
            self._ui(self._toast,titulo,mensaje,tipo,seg);return
        top=tk.Toplevel(self.root);top.title(titulo)
        top.configure(bg=CF);top.transient(self.root);top.resizable(False,False);top.attributes("-topmost",True)
        icono={"info":"ℹ","warning":"⚠","error":"✖"}.get(tipo,"ℹ");color={"info":CID,"warning":CAV,"error":CAV}.get(tipo,CID)
        ttk.Label(top,text=f"{icono}  {titulo}",font=("",11,"bold"),foreground=color,background=CF).pack(pady=(20,8),padx=25,anchor="w")
        ttk.Label(top,text=mensaje,font=("",10),background=CF,foreground=CT,justify="left",wraplength=720).pack(pady=(0,15),padx=25,anchor="w")
        bf=tk.Frame(top,bg=CF);bf.pack(side="bottom",fill="x",pady=(10,20))
        ttk.Button(bf,text=T("cerrar"),command=top.destroy).pack(ipadx=15,ipady=3)
        try:
            top.update_idletasks();self.root.update_idletasks()
            w=max(460,top.winfo_reqwidth()+24);h=max(190,top.winfo_reqheight()+10)
            x=self.root.winfo_rootx()+(self.root.winfo_width()-w)//2;y=self.root.winfo_rooty()+(self.root.winfo_height()-h)//2
            top.geometry(f"{w}x{h}+{max(0,x)}+{max(0,y)}")
        except Exception:pass
        try:top.after(seg*1000,lambda:top.winfo_exists() and top.destroy())
        except Exception:pass
    def _confirm(self,titulo,mensaje,detalle=None):
        res={"v":False}
        top=tk.Toplevel(self.root);top.title(titulo)
        top.configure(bg=CF);top.transient(self.root);top.attributes("-topmost",True)
        ttk.Label(top,text=f"?  {titulo}",font=("",11,"bold"),foreground=CID).pack(fill="x",padx=20,pady=(16,8))
        ttk.Label(top,text=mensaje,font=("",10),wraplength=620,justify="left").pack(fill="x",padx=20,pady=(0,12))
        bf=tk.Frame(top,bg=CF);bf.pack(side="bottom",pady=(8,18))
        def si():res["v"]=True;top.destroy()
        def no():res["v"]=False;top.destroy()
        ttk.Button(bf,text=T("si"),command=si).pack(side="left",padx=10,ipadx=12,ipady=3)
        ttk.Button(bf,text=T("no"),command=no).pack(side="left",padx=10,ipadx=12,ipady=3)
        if detalle:self._boton_detalle(bf,top,titulo,detalle)
        try:
            top.update_idletasks();w=max(480,top.winfo_reqwidth()+20);h=top.winfo_reqheight()+10
            top.geometry(f"{w}x{h}+{self.root.winfo_rootx()+(self.root.winfo_width()-w)//2}+{self.root.winfo_rooty()+(self.root.winfo_height()-h)//2}")
            top.grab_set()
        except Exception:pass
        try:top.wait_window()
        except Exception:pass
        return res["v"]
    def _ver_detalle(self,titulo,texto,padre=None):
        """toda la información en una ventana: se puede seleccionar y copiar (no se puede escribir)"""
        V=self._vt;padre=padre or self.root
        w=tk.Toplevel(padre);w.title(titulo);w.configure(bg=CF);w.transient(padre)
        try:w.attributes("-topmost",True)
        except Exception:pass
        f=tk.Frame(w,bg=CF);f.pack(fill="both",expand=True,padx=12,pady=(12,0))
        fam="Consolas" if sys.platform=="win32" else "Monospace"
        tx=tk.Text(f,wrap="word",font=(fam,9),bg=CDN,fg=CT,insertbackground=CT,relief="flat",borderwidth=0,highlightthickness=1,
                   highlightbackground=CSB,padx=8,pady=6,width=110,height=30)
        sy=ttk.Scrollbar(f,orient="vertical",command=tx.yview)
        tx.configure(yscrollcommand=sy.set)
        sy.pack(side="right",fill="y");tx.pack(side="left",fill="both",expand=True)
        # (JMG, 9-11) sin barra horizontal: una línea larga (las órdenes de FFmpeg) sigue debajo, alineada un poco más adentro que su principio
        try:
            import tkinter.font as tkf;esp=tkf.Font(family=fam,size=9).measure(" ")
        except Exception:esp=7
        lns=texto.split("\n")
        for n_,l_ in enumerate(lns):
            s_=len(l_)-len(l_.lstrip(" "));tg=f"sangria{s_}"
            tx.tag_configure(tg,lmargin1=0,lmargin2=esp*(s_+4))
            tx.insert("end",l_+("\n" if n_<len(lns)-1 else ""),tg)
        def tecla(e):
            if e.state&4 and e.keysym.lower()=="a":tx.tag_add("sel","1.0","end");return "break"
            if (e.state&4 and e.keysym.lower()=="c") or e.keysym in ("Left","Right","Up","Down","Prior","Next","Home","End"):return None
            return "break"   # solo leer
        tx.bind("<Key>",tecla);self._menu_copiar(tx)
        def copiar():
            w.clipboard_clear();w.clipboard_append(texto);self._toast(T("info_tit"),V("Copiado: ya lo puedes pegar donde quieras.","Copied: you can paste it anywhere."),seg=3)
        bf=tk.Frame(w,bg=CF);bf.pack(fill="x",pady=10,padx=12)
        ttk.Button(bf,text="📋 "+V("Copiar todo","Copy all"),command=copiar).pack(side="left")
        ttk.Button(bf,text=V("Cerrar","Close"),command=w.destroy).pack(side="right")
        try:
            w.update_idletasks();w.geometry(f"+{padre.winfo_rootx()+30}+{padre.winfo_rooty()+30}");w.grab_set()
        except Exception:pass
        return w
    def _boton_detalle(self,bf,top,titulo,detalle):
        """botón «🔍 Ver todo» en una ventana de Confirmar: abre el detalle y, al cerrarlo, Confirmar sigue siendo la activa"""
        def ver():
            try:top.grab_release()
            except Exception:pass
            d=self._ver_detalle(titulo,detalle,top)
            def fin(e):
                if e.widget is d:
                    try:
                        if top.winfo_exists():top.grab_set()
                    except Exception:pass
            d.bind("<Destroy>",fin)
        ttk.Button(bf,text="🔍 "+self._vt("Ver todo","See everything"),command=ver).pack(side="left",padx=10,ipadx=6,ipady=3)
    def _ancho_min(self,bt):
        """(JMG, 8-11) la ventana, como poco, tan ancha como la fila de botones de arriba (que se vea el del idioma), sin pasar de la pantalla"""
        try:
            self.root.update_idletasks()
            ax,ay,aw,ah=_area_trabajo(self.root)
            need=min(bt.winfo_reqwidth()+50,aw-20)
            self.root.minsize(max(1000,need),self.root.minsize()[1])
            g=re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)",self.root.geometry())   # lo pedido: al arrancar, la ventana aun no tiene su tamaño
            w,h,_,y=[int(v) for v in g.groups()] if g else (self.root.winfo_width(),self.root.winfo_height(),0,self.root.winfo_y())
            if (w<300 or h<300) and getattr(self,"_geo_ini",None):w,h,y=self._geo_ini   # aun oculta (Tk la da como 1x1): el tamaño pedido al abrir
            if w<need:self.root.geometry(f"{need}x{h}+{ax+max(0,(aw-need)//2)}+{max(ay,y)}")
        except Exception:pass
    def _menu_copiar(self,tx):
        """botón derecho en un texto: Copiar (lo seleccionado, o todo si no hay nada) y Seleccionar todo"""
        V=self._vt
        def copiar():
            try:s=tx.get("sel.first","sel.last")
            except tk.TclError:s=tx.get("1.0","end-1c")
            self.root.clipboard_clear();self.root.clipboard_append(s)
        def todo():tx.tag_add("sel","1.0","end");tx.focus_set()
        def menu(e):
            m=tk.Menu(self.root,tearoff=0)
            m.add_command(label=V("Copiar","Copy"),command=copiar)
            m.add_command(label=V("Seleccionar todo","Select all"),command=todo)
            try:m.tk_popup(e.x_root,e.y_root)
            finally:m.grab_release()
        tx.bind("<Button-3>",menu,add="+");tx._jmg_copiar=copiar
    def _log(self,m):
        if hasattr(self,"txt_log"):
            try:self.txt_log.insert("end",m+"\n");self.txt_log.see("end")
            except Exception:pass
    def _ls(self,m):self._ui(self._log,m)
    def _st(self,m):self._ui(self.var_progreso.set,m)
    def _set_prog(self,v):self._ui(lambda v=v:self.prog.configure(value=v))
    def _mt(self):
        m=tk.Menu(self.root,tearoff=0)
        for cod,et in (("auto",T("tema_auto")),("claro",T("tema_claro")),("oscuro",T("tema_oscuro"))):
            m.add_command(label=("✓ " if self.var_tema.get()==cod else "   ")+et,command=lambda c=cod:self._ct(c))
        try:m.tk_popup(self.btn_tema.winfo_rootx(),self.btn_tema.winfo_rooty()+self.btn_tema.winfo_height())
        finally:m.grab_release()
    def _ct(self,cod):
        self.var_tema.set(cod);self._aplicar_tema();self._reconstruir()
    def _mi(self):
        m=tk.Menu(self.root,tearoff=0)
        for cod,n in IDIOMAS.items():
            m.add_command(label=("✓ " if cod==IDIOMA else "   ")+n,command=lambda c=cod:self._ci(c))
        try:m.tk_popup(self.btn_idioma.winfo_rootx(),self.btn_idioma.winfo_rooty()+self.btn_idioma.winfo_height())
        finally:m.grab_release()
    def _ci(self,cod):
        global IDIOMA
        if cod in IDIOMAS:IDIOMA=cod;self._reconstruir()
    def _reconstruir(self):
        """cambio de tema o de idioma: se vuelve a dibujar la ventana con los mismos datos"""
        self._guardar_trabajo()
        try:self._sash_rest=int(self.vpan.sash_coord(0)[1]) if (hasattr(self,"vpan") and self.vpan.winfo_ismapped()) else None   # (JMG, 10-11)
        except Exception:self._sash_rest=None
        tab=self.nb.index(self.nb.select()) if hasattr(self,"nb") else 0
        sel=list(self.la.curselection()) if hasattr(self,"la") else []
        try:self._log_txt=self.txt_log.get("1.0","end-1c")
        except Exception:pass
        for w in self.root.winfo_children():w.destroy()
        self.root.configure(bg=CF);self._estilo();self._build()
        self._pintar_lista()
        for i in sel:
            try:self.la.selection_set(i)
            except Exception:pass
        self._sarch()
        try:self.nb.select(tab)
        except Exception:pass
        self._forzar_colores();self._save_cfg()
    @staticmethod
    def _mailto_registrado():
        if sys.platform!="win32":return True
        try:
            import winreg
            for raiz,ruta,val in ((winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\mailto\UserChoice","ProgId"),
                                  (winreg.HKEY_CLASSES_ROOT,r"mailto\shell\open\command","")):
                try:
                    with winreg.OpenKey(raiz,ruta) as k:
                        if str(winreg.QueryValueEx(k,val)[0]).strip():return True
                except OSError:continue
        except Exception:pass
        return False
    def _web(self):
        """(JMG, 22-11) clic en el logo de la ventana principal: su espacio en GitHub («como mi página web»)"""
        try:
            if not _abrir_externo(WEB_URL):raise OSError(self._vt("no hay navegador","no web browser found"))
            self._log("[i] "+self._vt("Abriendo ","Opening ")+WEB_URL)
        except Exception as e:self._toast(T("info_tit"),WEB_URL+f"\n\n{e}",tipo="info",seg=8)
    def _contactar(self):
        """clic en el logotipo: correo nuevo al autor con el programa de correo; si no hay, Gmail en el navegador"""
        from urllib.parse import quote
        asunto="Jmg VideoEncoder"
        try:
            if self._mailto_registrado() and _abrir_externo("mailto:%s?subject=%s"%(CONTACTO_MAIL,quote(asunto))):return
        except Exception:pass
        try:
            if not _abrir_externo("https://mail.google.com/mail/?view=cm&fs=1&to=%s&su=%s"%(quote(CONTACTO_MAIL),quote(asunto))):raise OSError()
        except Exception:
            self._toast(T("info_tit"),self._vt("Puedes escribir a: ","You can write to: ")+CONTACTO_MAIL,tipo="info",seg=8)
    def _tmdb_entrada(self,p,var,ancho,**k):
        return tk.Entry(p,textvariable=var,width=ancho,bg=CDN,fg=CT,insertbackground=CT,relief="flat",highlightthickness=1,highlightbackground=CSB,highlightcolor=CID,**k)
    def _tmdb_clave_dialogo(self,despues=None):
        """(JMG, 16-11) la clave propia de TMDB (opcional si está el servicio de Jmg Software)"""
        V_=self._vt
        top=tk.Toplevel(self.root);top.title(V_("Portadas de TMDB","TMDB covers"));top.configure(bg=CF);top.transient(self.root);top.resizable(False,False)
        if TMDB_SERVICIO:t=V_("Las portadas, los títulos y los años vienen de TMDB (themoviedb.org). El programa ya los busca por el servicio de Jmg Software; si quieres, puedes usar tu propia clave de TMDB (déjala vacía para usar el servicio).",
                              "Covers, titles and years come from TMDB (themoviedb.org). The program already looks them up through the Jmg Software service; if you want, you can use your own TMDB key (leave it empty to use the service).")
        else:t=V_("Las portadas, los títulos y los años vienen de TMDB (themoviedb.org). Para buscarlos hace falta una clave de TMDB: es gratis (crea una cuenta en themoviedb.org → Ajustes → API) y se pega aquí. TMDB pide rellenar un formulario corto (para qué la vas a usar, etc.) y la clave sale al momento. Se guarda solo en este PC.",
                  "Covers, titles and years come from TMDB (themoviedb.org). Looking them up needs a TMDB key: it is free (create an account at themoviedb.org → Settings → API) and you paste it here. TMDB asks you to fill in a short form (what you will use it for, etc.) and the key is issued straight away. It is only saved on this PC.")
        ttk.Label(top,text=t,wraplength=460,justify="left").pack(padx=18,pady=(16,8),anchor="w")
        v=tk.StringVar(value=_tmdb_clave());e=self._tmdb_entrada(top,v,56,show="•");e.pack(padx=18,anchor="w",ipady=3)
        bf=ttk.Frame(top);bf.pack(fill="x",padx=18,pady=(12,16))
        def ok():
            _tmdb_clave_poner(v.get())
            try:top.grab_release();top.destroy()
            except Exception:pass
            if despues and _tmdb_hay():despues()
        lk=tk.Label(bf,text="themoviedb.org",fg=CID,bg=CF,cursor="hand2",font=("",9,"underline"));lk.pack(side="left")
        lk.bind("<Button-1>",lambda e_:_abrir_externo("https://www.themoviedb.org/settings/api"))
        ttk.Button(bf,text=V_("Guardar","Save"),command=ok).pack(side="right")
        ttk.Button(bf,text=V_("Cancelar","Cancel"),command=top.destroy).pack(side="right",padx=6)
        e.focus_set();e.bind("<Return>",lambda e_:ok())
        try:top.update_idletasks();top.geometry(f"+{self.root.winfo_rootx()+120}+{self.root.winfo_rooty()+120}");top.grab_set()
        except Exception:pass
        self._tmdb_dlg=top
    def _portada_web(self,nombre,al_elegir):
        """(JMG, 16-11) «🔍 Buscar»: la película en TMDB (título y año) y sus pósters para elegir uno -> al_elegir(jpg, título, año)"""
        V_=self._vt
        if not _tmdb_hay():self._tmdb_clave_dialogo(lambda:self._portada_web(nombre,al_elegir));return
        t0,a0=_adivinar_titulo(nombre);idioma="es-ES" if IDIOMA=="es" else "en-US"
        top=tk.Toplevel(self.root);top.title(V_("Buscar portada en internet (TMDB)","Find a cover online (TMDB)"));top.configure(bg=CF);top.transient(self.root)
        self._tmdb_top=top
        cab=ttk.Frame(top);cab.pack(fill="x",padx=12,pady=(12,6))
        vt=tk.StringVar(value=t0);va=tk.StringVar(value=a0)
        ttk.Label(cab,text=V_("Película:","Movie:")).pack(side="left")
        e1=self._tmdb_entrada(cab,vt,38);e1.pack(side="left",padx=6,ipady=3)
        ttk.Label(cab,text=V_("Año:","Year:")).pack(side="left",padx=(8,0))
        e2=self._tmdb_entrada(cab,va,6);e2.pack(side="left",padx=6,ipady=3)
        bb=ttk.Button(cab,text="🔍 "+V_("Buscar","Search"));bb.pack(side="left",padx=6)
        pie=ttk.Frame(top);pie.pack(side="bottom",fill="x",padx=12,pady=(6,12))
        try:
            lg=tk.PhotoImage(data=TMDB_LOGO);top._logo=lg;tk.Label(pie,image=lg,bg=CF).pack(side="left")
        except Exception:pass
        ttk.Label(pie,text=V_("Datos de TMDB (The Movie Database), que no colabora con este programa ni lo respalda.","Data from TMDB (The Movie Database).")+"\n"+TMDB_AVISO,foreground=CA,font=("",8,"italic"),justify="left",wraplength=430).pack(side="left",padx=8)
        bu=ttk.Button(pie,text="✔ "+V_("Usar esta portada","Use this cover"),state="disabled");bu.pack(side="right")
        ttk.Button(pie,text="⚙ "+V_("Clave de TMDB...","TMDB key..."),command=lambda:self._tmdb_clave_dialogo(None)).pack(side="right",padx=6)
        est=tk.StringVar(value="");ttk.Label(top,textvariable=est,foreground=CID).pack(side="bottom",anchor="w",padx=12)
        cuerpo=ttk.Frame(top);cuerpo.pack(fill="both",expand=True,padx=12)
        lb=tk.Listbox(cuerpo,width=40,bg=CDN,fg=CT,relief="flat",highlightthickness=1,highlightbackground=CSB,activestyle="none",exportselection=False,
                      selectbackground=CASB,selectforeground=CASF)
        lb.pack(side="left",fill="y")
        cv=tk.Canvas(cuerpo,bg=CF,highlightthickness=0);sb=ttk.Scrollbar(cuerpo,orient="vertical",command=cv.yview);cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y");cv.pack(side="left",fill="both",expand=True,padx=(10,0))
        gal=ttk.Frame(cv);cv.create_window((0,0),window=gal,anchor="nw");gal.bind("<Configure>",lambda e_:cv.configure(scrollregion=cv.bbox("all")))
        def rueda(e_):
            try:cv.yview_scroll(int(-e_.delta/120) or (-1 if e_.delta>0 else 1),"units")
            except Exception:pass
        cv.bind("<Enter>",lambda e_:cv.bind_all("<MouseWheel>",rueda));cv.bind("<Leave>",lambda e_:cv.unbind_all("<MouseWheel>"))
        res=[];sel={"p":None,"w":None};fotos=[];gen=[0]
        def hilo(f,ok):
            def run():
                try:r=f();self._ui(ok,r,None)
                except Exception as ex:self._ui(ok,None,ex)
            threading.Thread(target=run,daemon=True).start()
        def vivo():
            try:return bool(top.winfo_exists())
            except Exception:return False
        def limpiar():
            for w in gal.winfo_children():w.destroy()
            fotos.clear();sel["p"]=None;sel["w"]=None;bu.state(["disabled"])
        def buscar(*_):
            q=vt.get().strip()
            if not q:return
            est.set(V_("Buscando...","Searching..."));lb.delete(0,"end");res.clear();limpiar();gen[0]+=1
            a_=va.get().strip();hilo(lambda:_tmdb_buscar(q,a_,idioma),fin_buscar)   # (las casillas, desde aquí: no desde el hilo)
        def fin_buscar(r,ex):
            if not vivo():return
            if ex is not None:est.set(V_("No se ha podido buscar (¿hay conexión a internet?): ","Could not search (is there an internet connection?): ")+str(ex)[:120]);return
            res[:]=r
            for x in r:lb.insert("end",f"{x['titulo']} ({x['anio'] or '?'})"+(f" · {x['original']}" if x["original"] and x["original"]!=x["titulo"] else ""))
            if r:lb.selection_set(0);elegir_peli()
            else:est.set(V_("No se ha encontrado nada: prueba con otro título (o sin el año).","Nothing found: try another title (or without the year)."))
        def elegir_peli(*_):
            s=lb.curselection()
            if not s:return
            x=res[s[0]];limpiar();gen[0]+=1;g=gen[0];est.set(V_("Cargando los pósters...","Loading the posters..."))
            def todo():
                ps=_tmdb_posters(x["id"],idioma[:2])
                return ps or ([x["poster"]] if x["poster"] else [])
            hilo(todo,lambda ps,ex:fin_posters(ps,ex,g))
        def fin_posters(ps,ex,g):
            if g!=gen[0] or not vivo():return
            if ex is not None:est.set(V_("No se han podido cargar los pósters: ","Could not load the posters: ")+str(ex)[:120]);return
            if not ps:est.set(V_("Esta película no tiene pósters en TMDB.","This movie has no posters on TMDB."));return
            est.set(V_(f"{len(ps)} póster(es): haz clic en uno y pulsa «Usar esta portada» (o doble clic).",f"{len(ps)} poster(s): click one and press «Use this cover» (or double-click)."))
            for k,p in enumerate(ps):hilo(lambda p=p:_png_de_jpg(_tmdb_bajar(p,"w185"),130),lambda d,ex,p=p,k=k:poner(d,ex,p,k,g))
        def poner(d,ex,p,k,g):
            if g!=gen[0] or not vivo() or ex is not None or not d:return
            import base64
            try:im=tk.PhotoImage(data=base64.b64encode(d).decode())
            except Exception:return
            fotos.append(im)
            b=tk.Label(gal,image=im,bg=CF,bd=0,highlightthickness=3,highlightbackground=CF,cursor="hand2");b.grid(row=k//4,column=k%4,padx=4,pady=4)
            b.bind("<Button-1>",lambda e_,p=p,b=b:marcar(p,b));b.bind("<Double-Button-1>",lambda e_,p=p,b=b:(marcar(p,b),usar()))
        def marcar(p,b):
            if sel["w"] is not None:
                try:sel["w"].configure(highlightbackground=CF)
                except Exception:pass
            sel["p"]=p;sel["w"]=b;b.configure(highlightbackground=CID);bu.state(["!disabled"])
        def usar(*_):
            s=lb.curselection()
            if not sel["p"] or not s:return
            x=res[s[0]];p=sel["p"];est.set(V_("Descargando la portada...","Downloading the cover..."));bu.state(["disabled"])
            def bajar():
                import tempfile
                d=_tmdb_bajar(p,"w780",30);f=os.path.join(tempfile.gettempdir(),f"jmg_portada_{x['id']}_{os.path.basename(p)}")
                with open(f,"wb") as fh:fh.write(d)
                return f
            hilo(bajar,lambda f,ex:fin_usar(f,ex,x))
        def fin_usar(f,ex,x):
            if ex is not None:
                if vivo():est.set(V_("No se ha podido descargar: ","Could not download: ")+str(ex)[:120]);bu.state(["!disabled"])
                return
            try:top.destroy()
            except Exception:pass
            al_elegir(f,x["titulo"],x["anio"])
        bb.configure(command=buscar);bu.configure(command=usar);e1.bind("<Return>",buscar);e2.bind("<Return>",buscar);lb.bind("<<ListboxSelect>>",elegir_peli)
        try:
            top.geometry(f"900x620+{max(0,self.root.winfo_rootx()+60)}+{max(0,self.root.winfo_rooty()+40)}")
        except Exception:pass
        buscar()
    def _acv(self):
        top=tk.Toplevel(self.root);top.title(T("acerca_t"));top.geometry("560x665");top.configure(bg=CF)   # (JMG, 19-11) +85 de alto: el logo de Jmg Software
        top.transient(self.root);top.resizable(False,False)
        f=ttk.Frame(top);f.pack(fill="both",expand=True,padx=20,pady=(20,10))
        try:   # (JMG, 19-11) arriba, el logo de Jmg Software: el programa es de su autor (el de TMDB va abajo y más pequeño)
            _jl=tk.PhotoImage(data=JMG_LOGO);top._jmg_logo=_jl;_jw=tk.Label(f,image=_jl,bg=CF,cursor="hand2");_jw.pack(anchor="w",pady=(0,12))
            _jw.bind("<Button-1>",lambda e:self._contactar());self._ayuda_flotante(_jw,self._vt("Escríbeme: ","Write to me: ")+CONTACTO_MAIL)   # (JMG, 22-11) aquí, el correo
        except Exception:pass
        txt=tk.Text(f,wrap="word",font=("",10),bg=CF,fg=CT,relief="flat",highlightthickness=0,borderwidth=0,height=18,spacing3=2)
        txt.insert("1.0",T("acerca_x",v=VERSION_PROG));txt.pack(fill="both",expand=True)
        txt.bind("<Key>",lambda e:"break" if e.keysym not in ("c","C","a","A") else None)
        bf=ttk.Frame(top);bf.pack(side="bottom",fill="x",pady=(10,15))
        ft=ttk.Frame(top);ft.pack(side="bottom",fill="x",padx=20)   # (JMG, 16-11) lo que piden las condiciones de TMDB
        try:
            _lg=tk.PhotoImage(data=TMDB_LOGO);top._tmdb_logo=_lg;tk.Label(ft,image=_lg,bg=CF).pack(side="left",padx=(0,10))
        except Exception:pass
        ttk.Label(ft,text=self._vt("Portadas, títulos y años: TMDB (The Movie Database), que no colabora con este programa ni lo respalda.","Covers, titles and years: TMDB (The Movie Database).")+"\n"+TMDB_AVISO,foreground=CA,font=("",8),justify="left",wraplength=320).pack(side="left")
        def contribuir():
            _apoyo_hecho()   # (JMG, 13-11) quien abre la página de contribuir ya no ve el recordatorio
            try:
                if not _abrir_externo(DONAR_URL):self._toast(T("info_tit"),self._vt("Abre esta dirección:\n","Open this address:\n")+DONAR_URL,tipo="info",seg=8)
            except Exception as e:self._toast(T("error_tit"),str(e),tipo="error")
        lk=tk.Label(bf,text="❤ "+T("contribuir"),fg=CID,bg=CF,cursor="hand2",font=("",10,"underline"))   # (JMG, 13-11) un enlace normal, no un botón
        lk.pack(side="left",padx=20);lk.bind("<Button-1>",lambda e:contribuir())
        ttk.Button(bf,text=T("cerrar"),command=top.destroy,width=12).pack(side="right",padx=20)
    def _ayuda_linea(self,txt,cod,l,tag):
        """(JMG, 13-11) una línea de la ayuda; en hindi, por trozos (ver _trozos_txt)"""
        if cod!="hi":txt.insert("end",l+"\n",tag);return
        for k_,p_ in enumerate(_trozos_txt(l)):txt.insert("end",p_,((tag,) if tag else ())+("h%d"%(k_%2),))
        txt.insert("end","\n",tag)
    def _av(self):
        """Ayuda en 9 idiomas: selector arriba, texto con titulos en negrita y enlaces clicables"""
        top=tk.Toplevel(self.root);top.title(T("ayuda_titulo"));top.geometry("820x740");top.configure(bg=CF);top.transient(self.root)
        cab=ttk.Frame(top);cab.pack(fill="x",padx=14,pady=(12,6))
        ttk.Label(cab,text="🌐 "+self._vt("Idioma de la ayuda:","Help language:")).pack(side="left",padx=(0,8))
        nombres=[n for _,n in AYUDA_IDIOMAS];cods=[c for c,_ in AYUDA_IDIOMAS]
        si_=_idioma_sistema()   # (JMG, 13-11) con la interfaz en inglés, la ayuda en el idioma de Windows si lo tiene (ruso, hindi...)
        lg=getattr(self,"_ayuda_lg",None) or ("es" if IDIOMA=="es" else (si_ if (si_ in cods and si_ not in ("es","en")) else (IDIOMA if IDIOMA in cods else "es")))
        cmb=ttk.Combobox(cab,values=nombres,state="readonly",width=16);cmb.current(cods.index(lg));cmb.pack(side="left")
        f=ttk.Frame(top);f.pack(fill="both",expand=True,padx=14,pady=(0,8))
        fam="Segoe UI" if sys.platform=="win32" else ""
        txt=tk.Text(f,wrap="word",font=(fam,10),bg=CDN,fg=CT,relief="flat",borderwidth=0,highlightthickness=1,highlightbackground=CSB,padx=16,pady=12,spacing1=2,spacing3=2,cursor="arrow")
        sb=ttk.Scrollbar(f,orient="vertical",command=txt.yview);txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y");txt.pack(side="left",fill="both",expand=True)
        txt.tag_configure("link",foreground=CID,underline=True)
        txt.tag_bind("link","<Enter>",lambda e:txt.configure(cursor="hand2"));txt.tag_bind("link","<Leave>",lambda e:txt.configure(cursor="arrow"))
        def abrir(e):
            try:
                i=txt.index(f"@{e.x},{e.y}");r=txt.tag_prevrange("link",i+"+1c")
                if r:_abrir_externo(txt.get(*r))
            except Exception:pass
        txt.tag_bind("link","<Button-1>",abrir)
        FCJK={"zh":"Microsoft YaHei UI","ja":"Yu Gothic UI","hi":"Nirmala UI"} if sys.platform=="win32" else {"zh":"Noto Sans CJK SC","ja":"Noto Sans CJK JP","hi":"Noto Sans Devanagari"}   # (JMG, 13-11) hindi
        def pintar(cod):
            self._ayuda_lg=cod;fm=FCJK.get(cod,fam)
            txt.configure(font=(fm,10))
            txt.tag_configure("tit",font=(fm,14,"bold"),foreground=CID,spacing3=8);txt.tag_configure("sec",font=(fm,11,"bold"),foreground=CID,spacing1=12,spacing3=4)
            txt.configure(state="normal");txt.delete("1.0","end")
            for k,l in enumerate(AYUDA.get(cod,AYUDA["es"]).splitlines()):
                st=l.strip()
                if k==0:tag="tit"
                elif st and st==st.upper() and not st.startswith("•") and len(st)<60 and any(c.isalpha() for c in st):tag="sec"
                else:tag=None
                ini=txt.index("end-1c");self._ayuda_linea(txt,cod,l,tag)
                for m in re.finditer(r"https?://\S+",l):txt.tag_add("link",f"{ini}+{m.start()}c",f"{ini}+{m.end()}c")
            txt.configure(state="disabled");txt.yview_moveto(0)
        cmb.bind("<<ComboboxSelected>>",lambda e:(pintar(cods[cmb.current()]),self._cmb_sin_foco(e)))
        pintar(lg)
        ttk.Button(top,text=T("cerrar"),command=top.destroy).pack(pady=(0,12))
    def _apoyo_aviso(self):
        """(JMG, 13-11) cada 45 días desde la instalación, al abrir cualquiera de los dos programas: «si te gusta, puedes contribuir».
        Se quita solo a los 5 segundos y no bloquea nada; con el enlace pulsado no vuelve a salir"""
        try:
            if not _apoyo_toca():return
            if self.procesando or self.root.grab_current() is not None or not self.root.winfo_viewable():   # ni en medio de un proceso ni sobre otra ventana
                self.root.after(60000,self._apoyo_aviso);return
            j=_apoyo_leer();j["desde"]=time.strftime("%Y-%m-%d");_apoyo_guardar(j)   # el siguiente, dentro de otros 45 días
            V=self._vt
            top=tk.Toplevel(self.root);top.title("Jmg SuiteMultimedia");top.configure(bg=CF);top.transient(self.root);top.resizable(False,False)
            self._apoyo_top=top
            tk.Label(top,text="❤  "+V("¿Te gusta el programa?","Do you like the program?"),font=("",11,"bold"),fg=CID,bg=CF).pack(pady=(20,6),padx=28,anchor="w")
            tk.Label(top,text=V("Jmg SuiteMultimedia es gratis y lo seguirá siendo.\nSi te resulta útil, puedes contribuir con el proyecto:","Jmg SuiteMultimedia is free and will stay free.\nIf you find it useful, you can support the project:"),font=("",10),fg=CT,bg=CF,justify="left").pack(padx=28,anchor="w")
            def ir(e=None):
                _apoyo_hecho()
                try:top.destroy()
                except Exception:pass
                try:
                    if not _abrir_externo(DONAR_URL):self._toast(T("info_tit"),V("No se encontró un navegador. Abre esta dirección:\n","No web browser found. Open this address:\n")+DONAR_URL,tipo="info",seg=8)
                except Exception as e_:self._ls(f"[APOYO] {e_}")
            lk=tk.Label(top,text=T("contribuir"),fg=CID,bg=CF,cursor="hand2",font=("",10,"underline"));lk.pack(pady=(8,4),padx=28,anchor="w");lk.bind("<Button-1>",ir)
            tk.Label(top,text=V("Este mensaje se cierra solo.","This message closes by itself."),font=("",8,"italic"),fg=CA,bg=CF).pack(pady=(6,16),padx=28,anchor="w")
            try:
                top.update_idletasks();w=max(440,top.winfo_reqwidth()+20);h=top.winfo_reqheight()
                x=self.root.winfo_rootx()+(self.root.winfo_width()-w)//2;y=self.root.winfo_rooty()+(self.root.winfo_height()-h)//2
                top.geometry(f"{w}x{h}+{max(0,x)}+{max(0,y)}")
            except Exception:pass
            top.after(5000,lambda:top.winfo_exists() and top.destroy())
        except Exception as e:
            try:self._ls(f"[APOYO] {e}")
            except Exception:pass
    def _ver_nueva(self):
        """una vez al dia, al arrancar: mira en GitHub la ultima version publicada. Sin internet o sin Releases no hace nada"""
        hoy=time.strftime("%Y-%m-%d")
        if self._cfg.get("ver_comprobada")==hoy:return
        self._cfg["ver_comprobada"]=hoy
        def hilo():
            try:
                import urllib.request
                rq=urllib.request.Request(f"https://api.github.com/repos/{REPO_GH}/releases/latest",headers={"Accept":"application/vnd.github+json","User-Agent":f"JmgVideoEncoder/{VERSION_PROG}"})
                with urllib.request.urlopen(rq,timeout=8) as r:j=json.loads(r.read().decode("utf-8"))
                tag=str(j.get("tag_name","")).strip();url=j.get("html_url") or f"https://github.com/{REPO_GH}/releases/latest"
                na=[int(x) for x in re.findall(r"\d+",tag)];nb=[int(x) for x in re.findall(r"\d+",SUITE_VER)]
                n=max(len(na),len(nb))
                if na and na+[0]*(n-len(na))>nb+[0]*(n-len(nb)):
                    self._ui(self._ver_aviso,tag.lstrip("vV"),url)
            except Exception as e:self._ls(f"[VERSIÓN] {e}")
        threading.Thread(target=hilo,daemon=True).start()
    def _ver_aviso(self,ver,url):
        if self.procesando:self.root.after(60000,self._ver_aviso,ver,url);return
        if self._confirm(self._vt("Versión nueva","New version"),self._vt(f"Hay una versión nueva de Jmg SuiteMultimedia: la {ver} (tienes la {SUITE_VER}).\n\n¿Abrir la página de descarga?",f"A new version of Jmg SuiteMultimedia is available: {ver} (you have {SUITE_VER}).\n\nOpen the download page?")):
            try:_abrir_externo(url)
            except Exception:pass
    # ---------- variables de las pestañas ----------
    def _vars_video(self):
        self.var_vcodec=tk.StringVar(value="copy");self.var_vmotor=tk.StringVar(value="cpu");self.var_vmodo=tk.StringVar(value="b")
        self.var_crf=tk.IntVar(value=22);self.var_kbps=tk.IntVar(value=6000);self.var_2pass=tk.BooleanVar(value=True)
        self.var_vel=tk.StringVar(value="media");self.var_res=tk.StringVar(value="orig");self.var_bits=tk.StringVar(value="auto")
        self.var_color=tk.StringVar(value="auto");self.var_lut=tk.StringVar(value="");self.var_deint=tk.StringVar(value="auto")
        self.var_ini=tk.StringVar(value="");self.var_fin=tk.StringVar(value="");self.var_log=tk.BooleanVar(value=False)
        for k in VIMG_KEYS:setattr(self,"var_"+k,tk.IntVar(value=0))
        self.var_crop_on=tk.BooleanVar(value=False)
    def _vars_audio(self):
        self.var_a_lang=tk.StringVar(value="");self.var_a_tit=tk.StringVar(value="");self.var_a_cod=tk.StringVar(value="copy")
        self.var_a_kbps=tk.StringVar(value="");self.var_a_def=tk.BooleanVar(value=False);self.var_a_incl=tk.BooleanVar(value=True)
        self.var_a_delay=tk.IntVar(value=0);self.var_a_fps_de=tk.StringVar(value="");self.var_a_fps_a=tk.StringVar(value="");self.var_a_fps_met=tk.StringVar(value="tono");self.var_a_orig=tk.BooleanVar(value=False)
        self.var_oir_sal=tk.StringVar(value=self._cfg.get("oir_sal","mc"))
        for k in AEF_KEYS:setattr(self,"var_"+k,tk.IntVar(value=0))
    def _vars_subs(self):
        self.var_s_lang=tk.StringVar(value="");self.var_s_tit=tk.StringVar(value="")
        self.var_s_fps_de=tk.StringVar(value="");self.var_s_fps_a=tk.StringVar(value="");self.var_s_delay=tk.IntVar(value=0)
        self.var_s_def=tk.BooleanVar(value=False);self.var_s_forz=tk.BooleanVar(value=False);self.var_s_burn=tk.BooleanVar(value=False);self.var_s_incl=tk.BooleanVar(value=True)

    # ---------- ventana ----------
    def _scroll(self,padre):
        """marco con barra de desplazamiento (pestañas largas en pantallas bajas)"""
        cv=tk.Canvas(padre,bg=CF,highlightthickness=0,borderwidth=0)
        sb=ttk.Scrollbar(padre,orient="vertical",command=cv.yview);cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y");cv.pack(side="left",fill="both",expand=True)
        f=ttk.Frame(cv);wid=cv.create_window((0,0),window=f,anchor="nw")
        f.bind("<Configure>",lambda e:cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",lambda e:cv.itemconfigure(wid,width=e.width))
        def rueda(e):
            try:
                if cv.winfo_exists() and f.winfo_height()>cv.winfo_height():cv.yview_scroll(int(-e.delta/120) or (-1 if e.delta>0 else 1),"units")
            except Exception:pass
        def dentro(e):cv.bind_all("<MouseWheel>",rueda)
        def fuera(e):cv.unbind_all("<MouseWheel>")
        cv.bind("<Enter>",dentro);cv.bind("<Leave>",fuera)
        self._tab_in[str(padre)]=f
        return f
    def _dos_cols(self,f):
        """columna izquierda | raya vertical | columna derecha (igual en todas las pestañas)"""
        f.columnconfigure(0,weight=0);f.columnconfigure(1,weight=0,minsize=30);f.columnconfigure(2,weight=1)
        L=ttk.Frame(f);L.grid(row=0,column=0,sticky="nw",padx=(6,0),pady=(4,6))
        ttk.Separator(f,orient="vertical").grid(row=0,column=1,sticky="ns",pady=8)
        R=ttk.Frame(f);R.grid(row=0,column=2,sticky="nw",padx=(4,12),pady=(4,6))
        return L,R
    def _caja_auto(self,p,cmd):
        """(JMG, 14-11) «Auto» del mismo ancho y alto que las casillas de valor (una tk.Entry de 6): un marco de ese tamaño exacto con el
        botón dentro, sea cual sea la escala de la pantalla -> (marco para colocar, botón)"""
        ref=tk.Entry(p,width=6,relief="flat",highlightthickness=1,borderwidth=0);w_,h_=ref.winfo_reqwidth(),ref.winfo_reqheight();ref.destroy()
        fr=ttk.Frame(p,width=w_,height=h_);fr.pack_propagate(False)
        b=ttk.Button(fr,text="Auto",style="Auto.TButton",command=cmd);b.pack(fill="both",expand=True)
        return fr,b
    def _sec(self,p,row,txt,ef=None,cols=3):
        """titulo de seccion (con su «Auto» a la derecha si lo tiene) y raya debajo"""
        fr=ttk.Frame(p);fr.grid(row=row,column=0,columnspan=cols,sticky="ew",pady=(10,2))
        ttk.Label(fr,text=txt,font=("",10,"bold")).pack(side="left",padx=5)
        if ef:
            # (JMG, 8-11) en la columna de las casillas de valor, centrado sobre ellas: todos alineados
            fr_,b=self._caja_auto(p,lambda:self._auto(ef));fr_.grid(row=row,column=cols-1,padx=(1,5),pady=(10,2))   # (JMG, 14-11) del tamaño de las casillas, alineado con ellas
            self._auto_bts[ef]=b
        return fr
    def _nota(self,p,row,txt,cols=3,wrap=560):
        l=ttk.Label(p,text=txt,foreground=CA,font=("",8,"italic"),wraplength=wrap,justify="left");l.grid(row=row,column=0,columnspan=cols,sticky="w",padx=6,pady=(0,4))
        return l
    def _build(self):
        self._auto_bts={};self._cols_hecho=False;self._tab_in={}
        top=ttk.Frame(self.root)
        ttk.Label(top,text=" Archivos / Files ",font=("",10,"bold")).pack(anchor="w",padx=5,pady=(0,4))
        ttk.Separator(top,orient="horizontal").pack(fill="x",pady=(0,6))
        bt=ttk.Frame(top);bt.pack(fill="x",pady=(0,6));self._fr_sup=bt
        ttk.Button(bt,text=T("sel"),command=self._sel).pack(side="left",padx=2)
        ttk.Button(bt,text=T("add"),command=self._add).pack(side="left",padx=2)
        b_dvd=ttk.Button(bt,text=T("dvd"));b_dvd.configure(command=lambda b=b_dvd:self._dvd_menu(b));b_dvd.pack(side="left",padx=2)   # (JMG, 8-11) carpeta o imagen .iso
        b_iso=ttk.Button(bt,text="💿 "+self._vt("Crear ISO...","Create ISO..."),command=self._isoc_ventana);b_iso.pack(side="left",padx=2)   # (JMG, 8-11)
        self._ayuda_flotante(b_iso,self._vt("Imagen .iso de una carpeta de DVD o Blu-ray (VIDEO_TS o BDMV)\no copia exacta del disco del lector.","An .iso image of a DVD or Blu-ray folder (VIDEO_TS or BDMV)\nor an exact copy of the disc in the drive."))
        self.btn_quit=ttk.Button(bt,text=T("quit"),command=self._del);self.btn_quit.pack(side="left",padx=2)
        self.btn_limp=ttk.Button(bt,text=T("limp"),command=self._clr);self.btn_limp.pack(side="left",padx=2)
        # (JMG, 17-11) Seleccionar, Añadir, Quitar y Limpiar juntos; luego DVD/BD e Imagen (igual en los dos programas)
        b_dvd.pack_forget();b_iso.pack_forget();b_dvd.pack(side="left",padx=(10,2),after=self.btn_limp);b_iso.pack(side="left",padx=2,after=b_dvd)
        self.btn_otro=ttk.Button(bt,text="🎵 "+self._vt("A AudioProcesador","To AudioProcesador"),command=self._pasar_otro);self.btn_otro.pack(side="left",padx=(10,2))
        self._ayuda_flotante(self.btn_otro,self._vt("Pasa los vídeos seleccionados (o todos) a Jmg AudioProcesador:\nsi está abierto, a su lista; si no, lo abre con ellos.",
                                                    "Sends the selected videos (or all of them) to Jmg AudioProcesador:\nif it is open, to its list; if not, it opens it with them."))
        self.btn_gp=ttk.Button(bt,text=T("guardar_p"),command=self._gp);self.btn_gp.pack(side="left",padx=(16,2))
        self.btn_cp=ttk.Button(bt,text=T("cargar_p"),command=self._mp);self.btn_cp.pack(side="left",padx=2)
        ttk.Button(bt,text=T("ayuda"),command=self._av).pack(side="left",padx=(16,2))
        ttk.Button(bt,text=T("acerca"),command=self._acv).pack(side="left",padx=2)
        self.btn_tema=ttk.Button(bt,text=T("tema"),command=self._mt);self.btn_tema.pack(side="left",padx=2)
        self.btn_idioma=ttk.Button(bt,text=T("idioma"),command=self._mi);self.btn_idioma.pack(side="left",padx=2)
        self.root.after(150,lambda b_=bt:self._ancho_min(b_))
        cols=tk.PanedWindow(top,orient=tk.HORIZONTAL,sashrelief="flat",sashwidth=12,bg=CF,borderwidth=0,sashcursor="sb_h_double_arrow")
        cols.pack(fill="both",expand=True,pady=(0,5))
        ci=ttk.Frame(cols,cursor="arrow");cols.add(ci,minsize=220,stretch="always")
        hc=ttk.Frame(ci);hc.pack(fill="x",pady=(6,4))
        ttk.Label(hc,text=self._vt("Vídeos (clic para ver su información)","Videos (click to see their information)"),font=("",9,"bold")).pack(side="left")
        self.lbl_f=ttk.Label(hc,text="",foreground=CID,font=("",9));self.lbl_f.pack(side="right",padx=4)
        lf=ttk.Frame(ci);lf.pack(fill="both",expand=True)
        self.la=tk.Listbox(lf,selectmode="extended",height=8,bg=CDN,fg=CT,selectbackground=CASB,selectforeground=CASF,relief="flat",borderwidth=0,highlightthickness=1,highlightbackground=CSB,highlightcolor=CID,activestyle="none",exportselection=False)
        self.la.pack(side="left",fill="both",expand=True);self.la.bind("<<ListboxSelect>>",self._sarch)
        self.la.bind("<Double-Button-1>",lambda e:self._agregar())
        sc=ttk.Scrollbar(lf,orient="vertical",command=self.la.yview);sc.pack(side="right",fill="y");self.la.configure(yscrollcommand=sc.set)
        if _HAY_DND:
            try:
                self.la.drop_target_register(DND_FILES);self.la.dnd_bind("<<Drop>>",self._drop)
                self.la.dnd_bind("<<DropEnter>>",lambda e:self.la.configure(bg=CDO));self.la.dnd_bind("<<DropLeave>>",lambda e:self.la.configure(bg=CDN))
            except Exception:pass
        cd=ttk.Frame(cols,cursor="arrow");cols.add(cd,minsize=420,stretch="always")
        ttk.Label(cd,text=self._vt("Información","Information"),font=("",9,"bold")).pack(anchor="w",pady=(6,4))
        tf=ttk.Frame(cd);tf.pack(fill="both",expand=True)
        self.txt_info=tk.Text(tf,height=8,wrap="none",font=("Consolas",9),bg=CDN,fg=CT,relief="flat",borderwidth=0,highlightthickness=1,highlightbackground=CSB,padx=6,pady=4,cursor="arrow")
        isb=ttk.Scrollbar(tf,orient="vertical",command=self.txt_info.yview);self.txt_info.configure(yscrollcommand=isb.set)
        isb.pack(side="right",fill="y");self.txt_info.pack(side="left",fill="both",expand=True)
        self.txt_info.bind("<Key>",lambda e:None if (e.state & 4 and e.keysym.lower() in ("c","a")) else "break");self._menu_copiar(self.txt_info)
        row=ttk.Frame(cd);row.pack(fill="x",pady=(6,0));self._fr_fila=row
        self.btn_agr=ttk.Button(row,text="➕ "+self._vt("Agregar","Add to queue"),command=self._agregar);self.btn_agr.pack(side="left",padx=(0,4))
        self.btn_noagr=ttk.Button(row,text="✖ "+self._vt("No procesar","Do not process"),command=self._quitar_trabajo);self.btn_noagr.pack(side="left",padx=4)
        self._ayuda_flotante(self.btn_agr,self._vt("Pasa los vídeos seleccionados a las pestañas (Vídeo, Audio, Subtítulos...)\ncon los ajustes automáticos. Los vídeos agregados llevan ✔ y son los que se procesan.","Loads the selected videos into the tabs (Video, Audio, Subtitles...)\nwith the automatic settings. Added videos show ✔ and are the ones processed."))
        self._ayuda_flotante(self.btn_noagr,self._vt("El vídeo sigue en la lista, pero no se procesa.","The video stays in the list, but it is not processed."))
        self.btn_comb=ttk.Button(row,text="🎬 "+self._vt("Combinar vídeos","Combine videos"),command=self._combinar);self.btn_comb.pack(side="left",padx=(12,4))
        self._ayuda_flotante(self.btn_comb,self._vt("Une trozos de varios vídeos en uno solo (con «Igualar color y brillo»).","Joins parts of several videos into a single one (with «Match color and brightness»)."))
        self.lbl_act=ttk.Label(row,text="",foreground=CID,font=("",9,"italic"));self.lbl_act.pack(side="left",padx=12)
        cols.bind("<Configure>",lambda e:self.root.after_idle(lambda:self._cols_aj(cols)),add="+")
        bot=ttk.Frame(self.root);bot.pack(side="bottom",fill="x",padx=10,pady=(5,10));self._fr_inf=bot
        self.btn_p=ttk.Button(bot,text=T("procesar"),command=self._conf);self.btn_p.pack(side="left",padx=4)
        self.btn_pausa=ttk.Button(bot,text="⏸ "+self._vt("Pausa","Pause"),command=self._pausa_pulsar,state="disabled");self.btn_pausa.pack(side="left",padx=4)   # (JMG, 13-11)
        self._ayuda_flotante(self.btn_pausa,self._vt("Para el procesado sin perder nada;\n«▶ Continuar» lo sigue donde estaba.","Pauses the processing without losing anything;\n«▶ Resume» carries on where it was."))
        if not getattr(self,"_pausa_tick_on",False):self._pausa_tick_on=True;self.root.after(500,self._pausa_tick)
        self.btn_c=ttk.Button(bot,text=T("cancelar"),command=self._cancel,state="disabled");self.btn_c.pack(side="left",padx=4)
        self.btn_rst=ttk.Button(bot,text=T("resetear"),command=self._rst);self.btn_rst.pack(side="left",padx=4)
        self.chk_rst_all=ttk.Checkbutton(bot,text=self._vt("Todo","All"),variable=self.var_reset_all,style="G.TCheckbutton",command=lambda:self._refrescar_estado());self.chk_rst_all.pack(side="left",padx=(0,4))
        self._ayuda_flotante(self.btn_rst,self._vt("Vuelve a poner los ajustes automáticos del vídeo activo;\ncon «Todo», todo de cero: la lista de vídeos, sus ajustes y la Salida\n(«↶ Deshacer» lo recupera).","Puts back the automatic settings of the active video;\nwith «All», everything from scratch: the video list, its settings and the Output\n(«↶ Undo» brings it back)."))
        self.btn_ud=ttk.Button(bot,text="↶ "+self._vt("Deshacer","Undo"),command=lambda:self._ud_mover(-1),state="disabled");self.btn_ud.pack(side="left",padx=(8,2))
        self.btn_ur=ttk.Button(bot,text="↷ "+self._vt("Rehacer","Redo"),command=lambda:self._ud_mover(1),state="disabled");self.btn_ur.pack(side="left",padx=(2,4))
        for w_,t_ in ((self.btn_ud,self._vt("Deshace la última acción (hasta 5). También Ctrl+Z.","Undoes the last action (up to 5). Also Ctrl+Z.")),(self.btn_ur,self._vt("Rehace lo deshecho. También Ctrl+Y.","Redoes what was undone. Also Ctrl+Y."))):self._ayuda_flotante(w_,t_)
        if not getattr(self,"_ud_on",False):   # una sola vez (la ventana se rehace al cambiar de tema o de idioma)
            self._ud_on=True;self.root.after(800,self._ud_tick)
            for _t,_s in (("<Control-z>",-1),("<Control-Z>",-1),("<Control-y>",1),("<Control-Y>",1)):self.root.bind(_t,lambda e,s=_s:self._ud_tecla(e,s),add="+")
        ttk.Label(bot,text=T("al_terminar"),font=("",10)).pack(side="left",padx=(12,2))
        fin=[("nada",T("al_nada")),("salir",T("al_salir")),("apagar",T("al_apagar")),("suspender",T("al_suspender"))]
        self.cmb_fin=ttk.Combobox(bot,values=[b for _,b in fin],width=16,state="readonly");self.cmb_fin.pack(side="left",padx=(0,8))
        self.cmb_fin.current([a for a,_ in fin].index(self.var_al_terminar.get()))
        self.cmb_fin.bind("<<ComboboxSelected>>",lambda e:self.var_al_terminar.set(fin[self.cmb_fin.current()][0]))
        ttk.Button(bot,text=T("salir"),command=self._on_close).pack(side="right",padx=4)
        try:
            self._logo_img=tk.PhotoImage(data=LOGO_B64)
            lg=ttk.Label(bot,image=self._logo_img,cursor="hand2");lg.pack(side="right",padx=(0,14))
            lg.bind("<Button-1>",lambda e:self._web());self._ayuda_flotante(lg,self._vt("Mi página: ","My page: ")+WEB_URL.replace("https://",""))   # (JMG, 22-11) su GitHub; el correo, en «Acerca de»
        except Exception:pass
        pf=ttk.Frame(self.root);pf.pack(side="bottom",fill="x",padx=10,pady=(0,8))
        self.prog=ttk.Progressbar(pf,mode="determinate",style="V.Horizontal.TProgressbar",maximum=100);self.prog.pack(fill="x")
        ttk.Label(pf,textvariable=self.var_progreso,font=("",9,"italic")).pack(anchor="w",pady=(2,0))
        nbo=ttk.Frame(self.root,style="NbBorder.TFrame")
        self.nb=ttk.Notebook(nbo);self.nb.pack(fill="both",expand=True,padx=1,pady=1)
        self.vpan=tk.PanedWindow(self.root,orient=tk.VERTICAL,sashrelief="flat",sashwidth=10,bg=CF,borderwidth=0,sashcursor="sb_v_double_arrow")
        self.vpan.pack(side="top",fill="both",expand=True)
        self.vpan.add(top,minsize=120,stretch="never",padx=10,pady=4,height=320)
        self.vpan.add(nbo,minsize=250,stretch="always",padx=10,pady=4)
        self.vpan.lower();top.lift();nbo.lift();self._vp_top=top;self._vp_nb=nbo
        self.root.after(300,self._alto_inicio);self.root.after(600,self._auto_bucle)
        self._tvideo();self._taudio();self._tsubs();self._tsal();self._tlog()
        self._tab_log_w=self.nb.tabs()[-1]
        self._avz=None;self._av_video();self._av_audio()   # «Opciones avanzadas»: se abren en lugar de la lista y las pestañas
        self.nb.bind("<<NotebookTabChanged>>",self._tab_cambio,add="+")
        self._pintar_trabajo()
    def _ajustar_alto(self):
        """(JMG, 7-11-2026: «déjala como estaba en un principio») la parte de arriba (lista de vídeos y botones) no cambia de alto
        sola: la pestaña larga lleva su barra de desplazamiento, y la raya entre las dos se puede arrastrar"""
        return
    def _cols_aj(self,cols):
        try:
            w=cols.winfo_width()
            if w>300 and not getattr(self,"_cols_hecho",False):cols.sash_place(0,int((w-12)*0.38),1);self._cols_hecho=True
        except Exception:pass
    # ---------- pestañas ----------
    def _combo(self,p,ops,var,width=24):
        """desplegable que enseña textos y guarda codigos: ops = [(codigo, texto)]"""
        cb=ttk.Combobox(p,values=[t for _,t in ops],width=width,state="readonly")
        def pon(*_):
            c=var.get()
            for i,(k,_) in enumerate(ops):
                if k==c:
                    if cb.current()!=i:cb.current(i)
                    return
            cb.set("")
        def sel(e=None):
            i=cb.current()
            if 0<=i<len(ops) and var.get()!=ops[i][0]:var.set(ops[i][0])
        cb.bind("<<ComboboxSelected>>",sel,add="+");self._tra(var,pon,cb);pon()
        cb._ops=ops
        return cb
    def _fila(self,p,row,txt,lw=14):
        """fila «Texto: control»: el control pegado a su texto (no a la columna de los deslizadores)"""
        fr=ttk.Frame(p);fr.grid(row=row,column=0,columnspan=3,sticky="w",padx=5,pady=3)
        ttk.Label(fr,text=txt,width=lw,anchor="w").pack(side="left")
        return fr
    def _entry(self,p,var,width):
        return tk.Entry(p,textvariable=var,width=width,bg=CDN,fg=CT,insertbackground=CT,relief="flat",highlightthickness=1,highlightbackground=CSB,highlightcolor=CID,disabledbackground=CDN)
    def _tvideo(self):
        o=ttk.Frame(self.nb);self.nb.add(o,text=T("t_video"))
        f=self._scroll(o);L,R=self._dos_cols(f);V_=self._vt
        self._sec(L,0,V_("Códec de vídeo","Video codec"),"video")
        self.cb_vcod=self._combo(self._fila(L,1,V_("Códec:","Codec:")),VCODECS,self.var_vcodec,28);self.cb_vcod.pack(side="left")
        self.btn_vopc=ttk.Button(self.cb_vcod.master,text="⚙",width=3,command=self._opc_video);self.btn_vopc.pack(side="left",padx=(4,0))   # (JMG, 12-11)
        self._ayuda_flotante(self.btn_vopc,V_("Opciones avanzadas del códec (lo más importante: ajuste, perfil, fotogramas clave...)","Advanced codec options (the most important: tune, profile, keyframes...)"))
        for v_ in (self.var_vcodec,self.var_vmotor):self._tra(v_,lambda *a:self._opc_v_estado(),self.btn_vopc)
        self._tra(self.var_vcodec,self._vvc_def,self.cb_vcod)   # (JMG, 23-11) VVC: una pasada y «Rápida» por defecto
        fm=self._fila(L,2,V_("Codificar con:","Encode with:"))
        self.rb_motor={}
        for k,t in (("cpu",V_("Procesador","Processor")),("nvidia","NVIDIA"),("amd","AMD")):
            self.rb_motor[k]=ttk.Radiobutton(fm,text=t,variable=self.var_vmotor,value=k,command=lambda k=k:self._motor_elegido(k),style={"nvidia":"Nv.G.TRadiobutton","amd":"Amd.G.TRadiobutton","cpu":"Cpu.G.TRadiobutton"}.get(k,"G.TRadiobutton"));self.rb_motor[k].pack(side="left",padx=(0,6))
        self.lbl_gpu=ttk.Label(L,text="",foreground=CA,font=("",8,"italic"));self.lbl_gpu.grid(row=3,column=0,columnspan=3,sticky="w",padx=6)
        self._sec(L,4,V_("Compresión","Compression"))
        fq=ttk.Frame(L);fq.grid(row=5,column=0,columnspan=3,sticky="w",padx=2)
        self.rb_q=ttk.Radiobutton(fq,text=V_("Calidad constante","Constant quality"),variable=self.var_vmodo,value="q",style="G.TRadiobutton");self.rb_q.pack(side="left",padx=(0,10))
        self.rb_b=ttk.Radiobutton(fq,text=V_("Bitrate (tamaño fijo)","Bitrate (fixed size)"),variable=self.var_vmodo,value="b",style="G.TRadiobutton");self.rb_b.pack(side="left")
        self.sl_crf=self._sl(L,V_("Calidad (menos = mejor)","Quality (lower = better)"),self.var_crf,0,51,6,d=22)
        self.sl_kbps=self._sl(L,V_("Bitrate (kbps)","Bitrate (kbps)"),self.var_kbps,300,60000,7,d=6000,step=100)
        self.chk_2p=ttk.Checkbutton(L,text=self._vt("Dos pasadas (más lento, reparte mejor el bitrate)","Two passes (slower, spreads the bitrate better)"),variable=self.var_2pass,style="G.TCheckbutton");self.chk_2p.grid(row=8,column=0,columnspan=3,sticky="w")
        self.cb_vel=self._combo(self._fila(L,9,V_("Velocidad:","Speed:")),[("lenta",V_("Lenta (mejor calidad)","Slow (best quality)")),("media",V_("Media","Medium")),("rapida",V_("Rápida","Fast"))],self.var_vel,24);self.cb_vel.pack(side="left")
        self.lbl_vest=ttk.Label(L,text="",foreground=CID,font=("",9),wraplength=520,justify="left");self.lbl_vest.grid(row=10,column=0,columnspan=3,sticky="w",padx=6,pady=(6,2))
        self._nota(L,11,V_("«Auto» elige el códec, el bitrate y la resolución según el vídeo (si ya está bien comprimido, lo deja en Passthrough). Pulsado otra vez sin tocar nada, vuelve a Passthrough. Todo se puede cambiar a mano.",
                          "«Auto» picks the codec, bitrate and resolution for the video (if it is already well compressed, it leaves Passthrough). Pressed again without touching anything, it goes back to Passthrough. Everything can be changed by hand."),wrap=520)
        self._sec(R,0,V_("Imagen","Picture"))
        self.cb_res=self._combo(self._fila(R,1,V_("Resolución:","Resolution:")),[("orig",V_("Igual que el original","Same as the original")),("2160","2160p (4K)"),("1440","1440p"),("1080","1080p (Full HD)"),("720","720p (HD)"),("576","576p (PAL)"),("480","480p (NTSC)")],self.var_res,24);self.cb_res.pack(side="left")
        self.cb_bits=self._combo(self._fila(R,2,V_("Profundidad:","Bit depth:")),[("auto","Auto"),("8","8 bits"),("10","10 bits")],self.var_bits,24);self.cb_bits.pack(side="left")
        self.cb_deint=self._combo(self._fila(R,3,V_("Desentrelazar:","Deinterlace:")),[("auto",V_("Auto (si el vídeo lo necesita)","Auto (if the video needs it)")),("si",V_("Sí","Yes")),("no","No")],self.var_deint,24);self.cb_deint.pack(side="left")
        fa=ttk.Frame(R);fa.grid(row=4,column=0,columnspan=3,sticky="w",padx=5,pady=(4,0))
        ttk.Button(fa,text="🔧 "+V_("Más opciones","More options"),command=lambda:self._avz_mostrar("v")).pack(side="left")
        ttk.Label(fa,text=V_("antes / después, recorte, brillo, nitidez, bandas negras y reproducir","before / after, trimming, brightness, sharpness, black bars and play"),foreground=CA,font=("",8,"italic")).pack(side="left",padx=8)
        self._sec(R,5,V_("Color","Color"))
        self.lbl_csrc=ttk.Label(R,text="",foreground=CID);self.lbl_csrc.grid(row=6,column=0,columnspan=3,sticky="w",padx=6,pady=(0,2))
        self.cb_color=self._combo(self._fila(R,7,V_("Color de salida:","Output color:")),[("auto",V_("Igual que el original","Same as the original")),("sdr",V_("SDR (BT.709): convierte HDR a SDR","SDR (BT.709): converts HDR to SDR"))],self.var_color,30);self.cb_color.pack(side="left")
        self.chk_log=ttk.Checkbutton(R,text=V_("Es un vídeo logarítmico (S-Log, V-Log, C-Log...)","It is a log video (S-Log, V-Log, C-Log...)"),variable=self.var_log,style="G.TCheckbutton");self.chk_log.grid(row=8,column=0,columnspan=3,sticky="w")
        fl=self._fila(R,9,"LUT (.cube):")
        self.en_lut=self._entry(fl,self.var_lut,24);self.en_lut.pack(side="left",ipady=2)
        self.bt_lut=ttk.Button(fl,text=V_("Elegir...","Choose..."),command=self._elegir_lut);self.bt_lut.pack(side="left",padx=4)
        self.bt_lutx=ttk.Button(fl,text="✖",width=3,command=lambda:self.var_lut.set(""));self.bt_lutx.pack(side="left")
        self._nota(R,10,V_("El color solo se activa si hace falta: con HDR, para pasarlo a SDR; con vídeo logarítmico de cámara, para su LUT (si el programa no lo detecta, marca la casilla). Dolby Vision: se conserva la capa HDR10.",
                           "Color is only enabled when needed: with HDR, to turn it into SDR; with camera log video, for its LUT (if the program does not detect it, tick the box). Dolby Vision: the HDR10 layer is kept."),wrap=440)
        for v in (self.var_vcodec,self.var_vmotor,self.var_vmodo,self.var_crf,self.var_kbps,self.var_2pass,self.var_vel,self.var_res,self.var_bits,self.var_color,self.var_lut,self.var_deint,self.var_log):
            self._tra(v,lambda *a:self._cambio(),o)
    def _taudio(self):
        o=ttk.Frame(self.nb);self.nb.add(o,text=T("t_audio"))
        f=self._scroll(o);V_=self._vt
        top=ttk.Frame(f);top.grid(row=0,column=0,columnspan=3,sticky="ew",padx=6,pady=(6,2))
        ttk.Label(top,text=V_("Pistas de audio (doble clic = incluir o no)","Audio tracks (double-click = include or not)"),font=("",10,"bold")).pack(anchor="w",pady=(0,4))
        tw=ttk.Frame(top);tw.pack(fill="x")
        cols=("incl","n","lang","tit","orig","ch","sal")
        self.tv_a=ttk.Treeview(tw,columns=cols,show="headings",height=4,selectmode="browse")
        for c,t,w in zip(cols,("✔","#",V_("Idioma","Language"),V_("Título","Title"),V_("Original","Original"),V_("Canales","Channels"),V_("Salida","Output")),(30,40,70,230,180,80,230)):
            self.tv_a.heading(c,text=t);self.tv_a.column(c,width=w,minwidth=min(w,60),anchor="w" if c in ("tit","orig","sal") else "center",stretch=c not in ("incl","n"))   # (JMG, 8-11) al ensanchar una, las de la derecha ceden sitio
        self.tv_a.pack(side="left",fill="x",expand=True)
        self._tv_caber(self.tv_a,("tit","orig","sal"))
        self.tv_a.bind("<<TreeviewSelect>>",lambda e:self._a_sel_cambio());self.tv_a.bind("<Double-Button-1>",lambda e:self._a_incl())
        bb=ttk.Frame(tw);bb.pack(side="left",padx=6,anchor="n")
        ttk.Button(bb,text="⬆",width=3,command=lambda:self._mover("a",-1)).pack(pady=1)
        ttk.Button(bb,text="⬇",width=3,command=lambda:self._mover("a",1)).pack(pady=1)
        ed=ttk.Frame(top);ed.pack(fill="x",pady=(6,0))
        ttk.Label(ed,text=V_("Idioma:","Language:")).pack(side="left")
        ttk.Combobox(ed,textvariable=self.var_a_lang,values=IDIOMAS_PISTA,width=6).pack(side="left",padx=(2,10))
        ttk.Label(ed,text=V_("Título:","Title:")).pack(side="left")
        self._entry(ed,self.var_a_tit,24).pack(side="left",padx=(2,10),ipady=2)
        ttk.Label(ed,text=V_("Códec:","Codec:")).pack(side="left")
        ops_a=[]   # (JMG, 9-11) «Aften Dolby Digital» (por defecto) y el AC3 de FFmpeg
        for k_,t_ in ACODECS:ops_a+=([("aften","Aften Dolby Digital (AC3)"),("ac3","AC3 (Dolby Digital) · FFmpeg")] if k_=="ac3" else [(k_,t_)])
        self.cb_acod=self._combo(ed,ops_a,self.var_a_cod,26);self.cb_acod.pack(side="left",padx=(2,2))
        # (JMG, 15-11) al elegir Aften ya no se abre su ventana: va con «⚙», como las opciones de los demás
        self.btn_af=ttk.Button(ed,text="⚙",width=3,command=self._opc_audio);self.btn_af.pack(side="left",padx=(0,10))
        self._ayuda_flotante(self.btn_af,V_("Opciones avanzadas del códec de la pista (con Aften, sus ajustes)","Advanced options of the track's codec (with Aften, its settings)"));self._tra(self.var_a_cod,lambda *a:self._aften_estado(),o)
        self.lbl_akbps=ttk.Label(ed,text="kbps:");self.lbl_akbps.pack(side="left")
        self.cb_akbps=ttk.Combobox(ed,textvariable=self.var_a_kbps,width=6,state="readonly");self.cb_akbps.pack(side="left",padx=(2,4))
        self.cb_akbps.bind("<Return>",lambda e:self._akbps_escrito());self.cb_akbps.bind("<FocusOut>",lambda e:self._akbps_escrito(),add="+")   # (JMG, 16-11) E-AC3 a mano
        self.lbl_afvbr=ttk.Label(ed,text="",foreground=CID,font=("",9,"bold"));self.lbl_afvbr.pack(side="left",padx=(0,10))   # (JMG, 10-11) «VBR 240» con Aften en VBR
        ttk.Checkbutton(ed,text=V_("Por defecto","Default"),variable=self.var_a_def,style="G.TCheckbutton").pack(side="left")
        ex=ttk.Frame(top);ex.pack(fill="x",pady=(4,0))
        ttk.Button(ex,text="➕ "+V_("Añadir pista","Add track"),command=self._a_externa).pack(side="left")
        ttk.Button(ex,text="➖ "+V_("Eliminar pista","Delete track"),command=self._a_quitar_ext).pack(side="left",padx=(6,6))
        self.btn_elim_orig=ttk.Button(ex,text="🚫 "+V_("Eliminar original","Remove original"),command=self._a_elim_orig);self.btn_elim_orig.pack(side="left",padx=(0,6))
        self._ayuda_flotante(self.btn_elim_orig,V_("Como en Jmg AudioProcesador: la pista procesada (con efectos) sale la primera y por defecto («Jmg procesada»)\ny la original se conserva detrás. Esto la quita (la fila se pone en rojo suave). Otra vez: vuelve.",
                                                   "As in Jmg AudioProcesador: the processed track (with effects) comes first and by default («Jmg procesada»)\nand the original is kept after it. This removes it (the row turns soft red). Again: it comes back."))
        b_nuc=ttk.Button(ex,text="➕ "+V_("Núcleo DTS","DTS core"),command=self._a_nucleo);b_nuc.pack(side="left",padx=(0,6))   # (JMG, 15-11; vuelve el 17-11)
        self._ayuda_flotante(b_nuc,V_("Una pista DTS-HD (Master Audio o High Resolution) lleva dentro un DTS normal para los aparatos que no entienden el HD.\nEsto lo saca también como pista aparte (en MKV), sin recomprimir. Otra vez: se quita.",
                                      "A DTS-HD track (Master Audio or High Resolution) carries a regular DTS inside for devices that do not understand HD.\nThis also takes it out as a separate track (in MKV), not re-encoded. Again: it is removed."))
        ttk.Button(ex,text="〰 "+V_("Visual / Ondas","Visual / Waves"),command=lambda:self._avz_mostrar("a")).pack(side="left",padx=(0,16))   # (JMG, 9-11)
        ttk.Label(ex,text=V_("Para escuchar y ver las ondas, «Visual / Ondas».","To listen and see the waves, «Visual / Waves»."),foreground=CA,font=("",8,"italic")).pack(side="left")
        g=ttk.Frame(f);g.grid(row=1,column=0,sticky="nw")
        L,R=self._dos_cols(g)
        self._sec(L,4,V_("Volumen por canal (dB)","Volume per channel (dB)"),"vol")
        for i,(k,t) in enumerate((("fl",V_("Frontal izq. (FL)","Front left (FL)")),("fr",V_("Frontal der. (FR)","Front right (FR)")),("fc",V_("Central (FC)","Center (FC)")),("lfe","Subwoofer (LFE)"),("bl",V_("Trasero izq. (BL/SL)","Surround left (BL/SL)")),("br",V_("Trasero der. (BR/SR)","Surround right (BR/SR)")))):
            self._sl(L,t,getattr(self,"var_"+k),-12,12,5+i)
        self._sec(L,11,V_("Sincronización","Synchronization"))
        self._fps_fila(L,12,self.var_a_fps_de,self.var_a_fps_a,self.var_a_fps_met)
        self._sl(L,V_("Delay (ms)","Delay (ms)"),self.var_a_delay,-6000,6000,13)
        fr=self._fila(L,14,V_("Comparar con:","Compare with:"))
        self.cb_aref=ttk.Combobox(fr,width=34,state="readonly");self.cb_aref.pack(side="left")
        fb=ttk.Frame(L);fb.grid(row=15,column=0,columnspan=3,sticky="w",padx=5,pady=2)
        self.bt_sinc=ttk.Button(fb,text="🎯 "+V_("Calcular delay","Calculate delay"),command=self._sinc_calc);self.bt_sinc.pack(side="left")
        self.bt_tramos=ttk.Button(fb,text="✂ "+V_("Corregir por tramos","Fix by parts"),command=self._sinc_tramos);self.bt_tramos.pack(side="left",padx=6)
        ttk.Button(fb,text="✖ "+V_("Quitar tramos","Remove parts"),command=self._sinc_quitar_tramos).pack(side="left")
        fq=ttk.Frame(L);fq.grid(row=16,column=0,columnspan=3,sticky="w",padx=5)
        self.bt_revisar=ttk.Button(fq,text="▶ "+V_("Revisar sincronización","Check synchronization"),command=self._sinc_revisar);self.bt_revisar.pack(anchor="w",pady=(2,2))
        self.lbl_sinc=ttk.Label(fq,text="",foreground=CID,wraplength=520,justify="left");self.lbl_sinc.pack(anchor="w",padx=1)
        self._nota(L,17,V_("Compara la pista con otra, normalmente la del idioma original, por su música y sus efectos. «Calcular delay» pone un desfase para toda la película; «Corregir por tramos» arregla los doblajes que van desfasados por partes.",
                           "Compares the track with another one, normally the original-language one, by its music and effects. «Calculate delay» sets one offset for the whole movie; «Fix by parts» fixes dubs that are out of sync in parts."),wrap=520)
        self._sec(R,8,V_("Suavizado digital","Digital smoothing"),"suav")
        self._w_suav=list(self._sl(R,V_("Intensidad (0-5)","Amount (0-5)"),self.var_suav,0,5,9))+[self._auto_bts["suav"]]   # (JMG, 9-11) no va con el EQ
        self._nota(R,10,V_("Quita el exceso de agudos (eses y brillo metálico) de muchas películas y doblajes de los 80 y 90. No toca el subwoofer.","Removes the excess treble (harsh S sounds and metallic shine) of many movies and dubs from the 80s and 90s. The subwoofer is not touched."),wrap=420)
        self._sec(R,3,V_("Ecualizador de 3 bandas","3-band equalizer"),"eq3")
        self._nota(R,4,V_("Delanteros, central y traseros (el subwoofer no).","Fronts, center and surrounds (not the subwoofer)."),wrap=420)
        self._w_eq3=list(self._sl(R,V_("Graves (100 Hz)","Bass (100 Hz)"),self.var_eq_bass,-10,10,5))+list(self._sl(R,V_("Medios (1 kHz)","Mids (1 kHz)"),self.var_eq_mids,-10,10,6))+\
                    list(self._sl(R,V_("Agudos (5 kHz)","Treble (5 kHz)"),self.var_eq_treble,-10,10,7))+[self._auto_bts["eq3"]]
        for v_ in (self.var_suav,self.var_eq_bass,self.var_eq_mids,self.var_eq_treble):self._tra(v_,lambda *a:self._ex_suav_eq(),o)
        self._sec(R,0,V_("Double Bass (más graves en todos)","Double Bass (more bass everywhere)"),"db")
        self._sl(R,V_("Intensidad (0-5)","Amount (0-5)"),self.var_db,0,5,1)
        self._nota(R,2,V_("Copia los graves del subwoofer a los altavoces, y los de los altavoces al subwoofer, sin quitarlos de donde están. Solo en pistas con subwoofer.","Copies the subwoofer bass to the speakers, and the speakers' bass to the subwoofer, without removing it from where it is. Only on tracks with a subwoofer."),wrap=420)
        self._nota(R,11,V_("Los efectos son de la pista seleccionada arriba. Con Passthrough el audio no se toca: al poner un efecto o un delay, la pista pasa a comprimirse con su mismo códec (o E-AC3 si ese no se puede). Cada «Auto» mide la pista con los demás efectos ya puestos; pulsado otra vez sin tocar nada, lo quita.",
                           "The effects belong to the track selected above. With Passthrough the audio is not touched: when you set an effect or a delay, the track is compressed again with its own codec (or E-AC3 if that one is not possible). Each «Auto» measures the track with the other effects already applied; pressed again without touching anything, it removes them."),wrap=420)
        for v in [self.var_a_lang,self.var_a_tit,self.var_a_cod,self.var_a_kbps,self.var_a_def,self.var_a_delay,self.var_a_fps_de,self.var_a_fps_a,self.var_a_fps_met]+[getattr(self,"var_"+k) for k in AEF_KEYS]:
            self._tra(v,lambda *a:self._cambio_a(),o)
    def _tsubs(self):
        o=ttk.Frame(self.nb);self.nb.add(o,text=T("t_subs"))
        f=self._scroll(o);V_=self._vt
        top=ttk.Frame(f);top.pack(fill="x",padx=6,pady=(6,8))
        ttk.Label(top,text=V_("Subtítulos (doble clic = incluir o no)","Subtitles (double-click = include or not)"),font=("",10,"bold")).pack(anchor="w",pady=(0,4))
        tw=ttk.Frame(top);tw.pack(fill="x")
        cols=("incl","n","lang","tit","fmt","def","forz")
        self.tv_s=ttk.Treeview(tw,columns=cols,show="headings",height=7,selectmode="browse")
        for c,t,w in zip(cols,("✔","#",V_("Idioma","Language"),V_("Título","Title"),V_("Formato","Format"),V_("Por defecto","Default"),V_("Forzado","Forced")),(30,40,70,300,150,90,80)):
            self.tv_s.heading(c,text=t);self.tv_s.column(c,width=w,minwidth=min(w,60),anchor="w" if c in ("tit","fmt") else "center",stretch=c not in ("incl","n"))
        self.tv_s.pack(side="left",fill="x",expand=True)
        self._tv_caber(self.tv_s,("tit","fmt"))
        self.tv_s.bind("<<TreeviewSelect>>",lambda e:self._s_sel_cambio());self.tv_s.bind("<Double-Button-1>",lambda e:self._s_incl())
        bb=ttk.Frame(tw);bb.pack(side="left",padx=6,anchor="n")
        ttk.Button(bb,text="⬆",width=3,command=lambda:self._mover("s",-1)).pack(pady=1)
        ttk.Button(bb,text="⬇",width=3,command=lambda:self._mover("s",1)).pack(pady=1)
        ed=ttk.Frame(top);ed.pack(fill="x",pady=(6,0))
        ttk.Label(ed,text=V_("Idioma:","Language:")).pack(side="left")
        ttk.Combobox(ed,textvariable=self.var_s_lang,values=IDIOMAS_PISTA,width=6).pack(side="left",padx=(2,10))
        ttk.Label(ed,text=V_("Título:","Title:")).pack(side="left")
        self._entry(ed,self.var_s_tit,30).pack(side="left",padx=(2,10),ipady=2)
        ttk.Checkbutton(ed,text=V_("Por defecto","Default"),variable=self.var_s_def,style="G.TCheckbutton").pack(side="left")
        ttk.Checkbutton(ed,text=V_("Forzado","Forced"),variable=self.var_s_forz,style="G.TCheckbutton").pack(side="left")
        ttk.Checkbutton(ed,text=V_("Grabar en la imagen","Burn into the picture"),variable=self.var_s_burn,style="G.TCheckbutton").pack(side="left",padx=(10,0))   # (JMG, 11-11)
        sy=ttk.Frame(top);sy.pack(fill="x",pady=(8,0))
        ttk.Label(sy,text=V_("Sincronización del subtítulo seleccionado","Synchronization of the selected subtitle"),font=("",9,"bold")).grid(row=0,column=0,columnspan=3,sticky="w",padx=5)
        self._fps_fila(sy,1,self.var_s_fps_de,self.var_s_fps_a,None)
        self._sl(sy,V_("Delay (ms)","Delay (ms)"),self.var_s_delay,-6000,6000,2)
        ex=ttk.Frame(top);ex.pack(fill="x",pady=(8,0))
        ttk.Button(ex,text="➕ "+V_("Añadir subtítulo externo...","Add external subtitle..."),command=self._s_externo).pack(side="left")
        ttk.Button(ex,text="➖ "+V_("Eliminar subtítulo","Delete subtitle"),command=self._s_quitar_ext).pack(side="left",padx=6)   # (JMG, 13-11) cualquiera
        ttk.Label(top,text=V_("Framerate y Delay: para los subtítulos de una edición de 25 fps en una película de 23,976 (o al revés), como el audio. "
                              "Se aplican al procesar, también a los de imagen (PGS, DVD).",
                              "Framerate and Delay: for the subtitles of a 25 fps edition in a 23.976 movie (or the other way round), like the audio. "
                              "They are applied when processing, also to the image ones (PGS, DVD)."),
                  foreground=CA,font=("",8,"italic"),wraplength=900,justify="left").pack(anchor="w",pady=(8,0))
        ttk.Label(top,text=V_("En MKV van todos tal cual. En MP4 y MOV los de texto (SRT, ASS...) se convierten a su formato y los de imagen (PGS, DVD) no caben: se dejan fuera y se avisa.",
                              "In MKV they all go as they are. In MP4 and MOV the text ones (SRT, ASS...) are converted to their format and the image ones (PGS, DVD) do not fit: they are left out with a notice."),
                  foreground=CA,font=("",8,"italic"),wraplength=900,justify="left").pack(anchor="w",pady=(8,0))
        for v in (self.var_s_lang,self.var_s_tit,self.var_s_def,self.var_s_forz,self.var_s_burn,self.var_s_fps_de,self.var_s_fps_a,self.var_s_delay):self._tra(v,lambda *a:self._cambio_s(),o)
    def _tsal(self):
        o=ttk.Frame(self.nb);self.nb.add(o,text=T("t_sal"))
        f=self._scroll(o);L,R=self._dos_cols(f);V_=self._vt
        self._sec(L,0,V_("Contenedor","Container"))
        fc=ttk.Frame(L);fc.grid(row=1,column=0,columnspan=3,sticky="w")
        for k,t in (("mkv","MKV"),("mp4","MP4"),("mov","MOV"),("avi","AVI"),("webm","WebM")):ttk.Radiobutton(fc,text=t,variable=self.var_cont,value=k,style="G.TRadiobutton").pack(side="left",padx=(0,12))
        self._nota(L,2,V_("MKV admite todo (todas las pistas y subtítulos). MP4 se ve en más aparatos (móviles, teles). MOV es el de Apple, el habitual para ProRes.","MKV takes everything (all tracks and subtitles). MP4 plays on more devices (phones, TVs). MOV is Apple's, the usual one for ProRes."),wrap=440)
        self._sec(L,3,V_("Carpeta de destino","Destination folder"))
        ttk.Radiobutton(L,text=V_("Junto al original","Next to the original"),variable=self.var_dest_modo,value="original",command=lambda:self._dest_disco_aviso(True),style="G.TRadiobutton").grid(row=4,column=0,columnspan=3,sticky="w")
        ttk.Radiobutton(L,text=V_("Carpeta elegida:","Chosen folder:"),variable=self.var_dest_modo,value="carpeta",style="G.TRadiobutton").grid(row=5,column=0,columnspan=3,sticky="w")
        fd=ttk.Frame(L);fd.grid(row=6,column=0,columnspan=3,sticky="w",padx=6)
        self._entry(fd,self.var_dest,40).pack(side="left",ipady=2)
        ttk.Button(fd,text="📁 "+V_("Elegir...","Choose..."),command=self._elegir_dest).pack(side="left",padx=4)
        fk=ttk.Frame(L);fk.grid(row=7,column=0,columnspan=3,sticky="w")
        ttk.Checkbutton(fk,text=V_("Abrir la carpeta al terminar","Open the folder when done"),variable=self.var_abrir,style="G.TCheckbutton").pack(anchor="w")
        ttk.Checkbutton(fk,text=V_("Al minimizar, a la bandeja del sistema (junto al reloj)","When minimized, to the system tray (next to the clock)"),variable=self.var_bandeja,style="G.TCheckbutton").pack(anchor="w")   # (JMG, 11-11)
        self._sec(L,8,V_("Portada","Cover"))
        self.lbl_portada=ttk.Label(L,text="",foreground=CID,wraplength=440,justify="left");self.lbl_portada.grid(row=9,column=0,columnspan=3,sticky="w",padx=6)
        fp=ttk.Frame(L);fp.grid(row=10,column=0,columnspan=3,sticky="w",padx=5,pady=2)
        ttk.Button(fp,text="🖼 "+V_("Elegir imagen...","Choose image..."),command=self._portada_elegir).pack(side="left")
        ttk.Button(fp,text="↺ "+V_("La original","The original"),command=lambda:self._portada_poner(None)).pack(side="left",padx=4)
        ttk.Button(fp,text="✖ "+V_("Sin portada","No cover"),command=lambda:self._portada_poner("")).pack(side="left")
        ttk.Button(fp,text="🔍 "+V_("Buscar en internet...","Search online..."),command=self._portada_buscar).pack(side="left",padx=(4,0))   # (JMG, 16-11) TMDB
        self._sec(R,0,V_("Nombre","Name"))
        fn=ttk.Frame(R);fn.grid(row=1,column=0,columnspan=3,sticky="w",padx=5)
        f1=ttk.Frame(fn);f1.pack(anchor="w")   # (JMG, 8-11) el nombre de cada vídeo se puede cambiar
        ttk.Label(f1,text=V_("Nombre de este vídeo:","Name of this video:"),width=20).pack(side="left")
        self._entry(f1,self.var_nom,40).pack(side="left",padx=6,ipady=2)
        ttk.Button(f1,text="↺",width=3,command=self._nom_def).pack(side="left")
        self.btn_ext=ttk.Button(f1,text="📤 "+V_("Extracción...","Extraction..."),command=self._ext_ventana);self.btn_ext.pack(side="left",padx=(16,0))   # (JMG, 15-11)
        self._tra(self.var_nom,lambda *a:self._nom_cambio(),o)   # (JMG, 9-11) sin «Añadir al nombre»: el sufijo es « (Jmg VideoEncoder)»
        ttk.Label(R,text=V_("Si el archivo ya existe:","If the file already exists:")).grid(row=2,column=0,columnspan=3,sticky="w",padx=5,pady=(6,0))
        fx=ttk.Frame(R);fx.grid(row=3,column=0,columnspan=3,sticky="w")
        ttk.Radiobutton(fx,text=V_("Renombrar (_1, _2...)","Rename (_1, _2...)"),variable=self.var_dup,value="rename",style="G.TRadiobutton").pack(side="left",padx=(0,10))
        ttk.Radiobutton(fx,text=V_("Sobrescribir","Overwrite"),variable=self.var_dup,value="sobre",style="G.TRadiobutton").pack(side="left")
        self._sec(R,4,V_("Copiar también","Also copy"))
        for i,(t,v) in enumerate(((V_("Capítulos","Chapters"),self.var_caps),(V_("Metadatos (título, año...)","Metadata (title, year...)"),self.var_meta),(V_("Adjuntos y portada (fuentes de los ASS, carátula)","Attachments and cover (ASS fonts, cover art)"),self.var_adj)),start=5):
            ttk.Checkbutton(R,text=t,variable=v,style="G.TCheckbutton").grid(row=i,column=0,columnspan=3,sticky="w")
        self.lbl_sal=ttk.Label(R,text="",foreground=CID,wraplength=440,justify="left");self.lbl_sal.grid(row=9,column=0,columnspan=3,sticky="w",padx=6,pady=(10,0))
        for v in (self.var_cont,self.var_dest_modo,self.var_dest,self.var_sufijo,self.var_dup,self.var_caps,self.var_meta,self.var_adj,self.var_abrir,self.var_bandeja):
            self._tra(v,lambda *a:(self._save_cfg(),self._refrescar_estado()),o)
    def _tlog(self):
        o=ttk.Frame(self.nb);self.nb.add(o,text=T("t_log"))
        bf=ttk.Frame(o);bf.pack(fill="x",padx=6,pady=(6,2))
        ttk.Button(bf,text="📋 "+self._vt("Copiar todo el log","Copy the whole log"),command=self._copiar_log).pack(side="left")
        ttk.Button(bf,text="⌨ "+self._vt("Ver el comando de FFmpeg","Show the FFmpeg command"),command=self._ver_cmd).pack(side="left",padx=6)
        ttk.Button(bf,text="🗑 "+self._vt("Vaciar","Clear"),command=lambda:self.txt_log.delete("1.0","end")).pack(side="left")
        tf=ttk.Frame(o);tf.pack(fill="both",expand=True,padx=6,pady=(2,6))
        viejo=getattr(self,"_log_txt","");self._log_txt=""   # el log sigue al cambiar de tema o de idioma
        self.txt_log=tk.Text(tf,wrap="word",font=("Consolas",9),bg=CDN,fg=CT,insertbackground=CT,relief="flat",highlightthickness=1,highlightbackground=CSB)
        self._menu_copiar(self.txt_log)
        sb=ttk.Scrollbar(tf,orient="vertical",command=self.txt_log.yview);self.txt_log.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y");self.txt_log.pack(side="left",fill="both",expand=True)
        if viejo:self.txt_log.insert("end",viejo+"\n")
    # ---------- archivos ----------
    def _chk_ff(self):
        try:
            if rh([FFMPEG,"-version"]).returncode!=0:raise FileNotFoundError
        except (FileNotFoundError,OSError):
            messagebox.showerror("Error",self._vt("No se encuentra FFmpeg. Comprueba que ffmpeg.exe y ffprobe.exe están en la carpeta «bin».","FFmpeg not found. Check that ffmpeg.exe and ffprobe.exe are in the «bin» folder."))
    def _detectar_gpu(self):
        """que codificadores de tarjeta grafica funcionan de verdad en este PC (se prueba codificando 3 fotogramas)"""
        ok=set()
        for e in GPU_ENC:
            try:
                r=rh([FFMPEG,"-hide_banner","-v","error","-f","lavfi","-i","nullsrc=s=256x256:d=0.2","-frames:v","3","-c:v",e,"-f","null","-"],timeout=25)
                if r.returncode==0:ok.add(e)
            except Exception:pass
        for e in sorted(x for x in ok if x.endswith("_amf")):   # (22-11) no todas las AMD admiten -preanalysis: con él, FFmpeg no codificaba nada
            for o_ in (["-preanalysis","1"],["-preencode","1"]):
                try:
                    r=rh([FFMPEG,"-hide_banner","-v","error","-f","lavfi","-i","nullsrc=s=256x256:d=0.2","-frames:v","3","-c:v",e,"-b:v","2M"]+o_+["-f","null","-"],timeout=25)
                    if r.returncode==0:_AMF_2P[e]=o_;break
                except Exception:pass
        self._gpu=ok;self._gpu_listo=True
        self._ls("[GPU] "+(", ".join(sorted(ok)) if ok else self._vt("ninguna","none")))
        self._ui(self._estado_video)
    def _sel(self):
        fs=filedialog.askopenfilenames(title=T("sel"),filetypes=[(self._vt("Vídeos","Videos"),_EXT_VID),(self._vt("Todos los archivos","All files"),"*.*")])
        if fs:self._clr(sin_preguntar=True);self._addl(list(fs))
    def _add(self):
        fs=filedialog.askopenfilenames(title=T("add"),filetypes=[(self._vt("Vídeos","Videos"),_EXT_VID),(self._vt("Todos los archivos","All files"),"*.*")])
        if fs:self._addl(list(fs))
    def _add_dvd(self):
        try:ds=[x[0] for x in self._discos() if x[2]]   # (JMG, 19-11) con un DVD o un Blu-ray en el lector, se abre ya en él
        except Exception:ds=[]
        d=filedialog.askdirectory(title=self._vt("Carpeta del DVD o del Blu-ray (la que tiene VIDEO_TS o BDMV)","DVD or Blu-ray folder (the one with VIDEO_TS or BDMV)"),initialdir=ds[0] if ds else None)
        if d:self._addl([d])
    def _drop(self,e):
        try:fs=list(self.root.tk.splitlist(e.data))
        except Exception:fs=[]
        try:self.la.configure(bg=CDN)
        except Exception:pass
        if self.procesando:return   # (JMG, 14-11) codificando: no se añade nada
        self._addl(fs)
    @staticmethod
    def _vobs(carpeta):
        """VOB del titulo principal de un DVD (el VTS que mas ocupa), en orden; de un Blu-ray, sus .m2ts"""
        if not os.path.isdir(os.path.join(carpeta,"VIDEO_TS")) and (os.path.isdir(os.path.join(carpeta,"BDMV")) or os.path.basename(carpeta.rstrip("\\/")).upper()=="BDMV"):
            return _bd_titulo(carpeta)[0]   # (JMG, 8-11) Blu-ray: la lista de reproducción más larga (la película)
        d=os.path.join(carpeta,"VIDEO_TS") if os.path.isdir(os.path.join(carpeta,"VIDEO_TS")) else carpeta
        g={}
        try:
            for n in os.listdir(d):
                m=re.match(r"VTS_(\d\d)_([1-9])\.VOB$",n,re.I)
                if m:g.setdefault(m.group(1),[]).append((int(m.group(2)),os.path.join(d,n)))
        except OSError:return []
        if not g:return []
        best=max(g.values(),key=lambda l:sum(os.path.getsize(p) for _,p in l))
        return [p for _,p in sorted(best)]
    def _addl(self,rutas):
        nuevos=[]
        for r in rutas:
            r=os.path.normpath(r)
            if r.lower().endswith(".iso") and os.path.isfile(r):self._iso_abrir(r);continue   # (JMG, 8-11) imagen de disco: se monta
            if os.path.isdir(r):
                if not self._vobs(r):continue
            elif not os.path.isfile(r):continue
            if r in self.files:continue
            self.files.append(r);nuevos.append(r)
        if not nuevos:return
        self._pintar_lista()
        if not self.la.curselection():
            self.la.selection_set(self.files.index(nuevos[0]))
        self._refrescar_estado()
        def hilo():
            for r in nuevos:
                inf=self._probe(r)
                self._ui(self._probe_fin,r,inf)
        threading.Thread(target=hilo,daemon=True).start()
    def _probe(self,ruta):
        dvd=os.path.isdir(ruta)
        ent="concat:"+"|".join(self._vobs(ruta)) if dvd else ruta
        cmd=[FFPROBE,"-v","error"]+(["-analyzeduration","100M","-probesize","100M"] if dvd else [])+["-show_format","-show_streams","-show_chapters","-of","json",ent]
        try:
            r=rh(cmd,timeout=120);j=json.loads(r.stdout or "{}")
        except Exception as e:j={"error":str(e)}
        j["entrada"]=ent;j["dvd"]=dvd
        if dvd:j["protegido"]=_disco_protegido(self._vobs(ruta))   # (JMG, 8-11) DVD (CSS) o Blu-ray (AACS) con protección anticopia
        if dvd and not os.path.isdir(os.path.join(ruta,"VIDEO_TS")):
            bd=_bd_titulo(ruta)
            if bd[1]>0:j.setdefault("format",{})["duration"]=str(bd[1])   # Blu-ray: la duración de su lista de reproducción
            try:   # (JMG, 13-11) los .m2ts no traen el idioma de sus pistas: se lee de la lista de reproducción
                lg=_bd_idiomas(ruta)
                for s_ in j.get("streams",[]):
                    try:pid=int(str(s_.get("id")),16)
                    except ValueError:continue
                    tg=s_.setdefault("tags",{})
                    if lg.get(pid) and str(tg.get("language") or "und").lower() in ("","und"):tg["language"]=lg[pid]
            except Exception:pass
        if dvd and _dur(j)<=0:
            try:j.setdefault("format",{})["duration"]=str(sum(os.path.getsize(p) for p in self._vobs(ruta))*8/max(1.0,_num(j.get("format",{}).get("bit_rate"),6e6)))
            except Exception:pass
        return j
    def _probe_fin(self,ruta,inf):
        if ruta not in self.files:return
        if inf.get("protegido"):   # (JMG, 8-11) disco con protección anticopia: aviso y fuera de la lista
            V_=self._vt;q=inf["protegido"];tipo="DVD" if q=="CSS" else "Blu-ray";nom=os.path.basename(ruta.rstrip("\\/"))
            msg=V_(f"{nom}: este {tipo} está protegido contra copia ({q}).\n\nFFmpeg no puede leerlo y el programa no quita esa protección: usa una copia sin protección o ya descifrada, si la ley de tu país te lo permite.",
                   f"{nom}: this {tipo} is copy-protected ({q}).\n\nFFmpeg cannot read it and the program does not remove that protection: use an unprotected or already decrypted copy, if the law of your country allows it.")
            self._log("[!] "+msg.replace("\n\n"," "));self.files.remove(ruta);self._pintar_lista();self._refrescar_estado()
            self._toast(T("warn_tit"),msg,tipo="warning",seg=15);return
        if not _vstream(inf):
            self._log(f"[!] {os.path.basename(ruta)}: "+self._vt("no tiene vídeo, se quita de la lista.","it has no video, it is removed from the list."))
            self.files.remove(ruta);self._pintar_lista();self._refrescar_estado();return
        self.info[ruta]=inf
        self._pintar_lista();self._sarch()
        if inf.get("dvd") and os.path.normcase(ruta)!=os.path.normcase(str(getattr(self,"_pel_pend",None) or "")) and _lector_fisico(ruta) \
           and not any(str(k)[:2].upper()==ruta[:2].upper() for k in getattr(self,"_isos",{})):   # (JMG, 13-11) «Ripear» ya trae su aviso
            V_=self._vt
            self._toast(T("warn_tit"),V_("Estás leyendo el disco directamente del lector: es lento y puede ser inestable para el programa.\n\nSe aconseja hacer antes una imagen ISO («💿 Crear ISO...») y abrirla con «📀 DVD/BD».",
                                         "You are reading the disc straight from the drive: it is slow and can make the program unstable.\n\nIt is better to make an ISO image first («💿 Create ISO...») and open it with «📀 DVD/BD»."),tipo="warning",seg=12)
    def _nombre(self,ruta):
        return ("📀 "+self._base(ruta)) if os.path.isdir(ruta) else os.path.basename(ruta.rstrip("\\/"))
    def _pintar_lista(self):
        sel=list(self.la.curselection())
        self.la.delete(0,"end")
        for f in self.files:
            self.la.insert("end",("✔ " if f in self.jobs else "    ")+self._nombre(f)+("" if f in self.info else "   ("+self._vt("analizando...","analyzing...")+")"))
            if f==self.actual:self.la.itemconfigure("end",fg=CID)
        for i in sel:
            if i<len(self.files):self.la.selection_set(i)
    def _del(self):
        for i in sorted(self.la.curselection(),reverse=True):
            f=self.files.pop(i);self.jobs.pop(f,None)   # su informacion se queda: Deshacer puede devolverlo
            if f==self.actual:self.actual=None
        if self.actual is None and self.jobs:self.actual=next(f for f in self.files if f in self.jobs)
        self._pintar_lista();self._sarch();self._pintar_trabajo();self._refrescar_estado()
    def _clr(self,sin_preguntar=False):
        if self.procesando:return
        self.files=[];self.jobs={};self.actual=None
        for r_ in list(getattr(self,"_isos",{})):self._iso_soltar(r_)   # las imágenes de disco montadas, fuera
        self._pintar_lista();self._sarch();self._pintar_trabajo();self._refrescar_estado()
    def _sarch(self,e=None):
        """clic en la lista: la informacion completa de un video, o un resumen de cada uno si hay varios"""
        sel=[self.files[i] for i in self.la.curselection() if i<len(self.files)]
        t=self.txt_info;t.configure(state="normal");t.delete("1.0","end")
        if len(sel)==1:t.insert("end",self._info_txt(sel[0]))
        else:
            for f in sel:t.insert("end",self._info_corta(f)+"\n")
        if len(sel)==1 and sel[0] in self.jobs and sel[0]!=self.actual:
            self._guardar_trabajo();self.actual=sel[0];self._pintar_trabajo();self._pintar_lista()
    def _info_corta(self,f):
        inf=self.info.get(f)
        if not inf:return self._nombre(f)+" · "+self._vt("analizando...","analyzing...")
        vs=_vstream(inf) or {}
        na=sum(1 for s in inf.get("streams",[]) if s.get("codec_type")=="audio");ns=sum(1 for s in inf.get("streams",[]) if s.get("codec_type")=="subtitle")
        h=_hdr_tipo(vs)
        return f"{'✔ ' if f in self.jobs else ''}{self._nombre(f)} · {vs.get('width','?')}x{vs.get('height','?')} {str(vs.get('codec_name','?')).upper()} {_bits(vs)} bits{' '+h if h!='SDR' else ''} · {_hms(_dur(inf)).split('.')[0]} · {na} audio · {ns} {self._vt('subs','subs')}"
    def _info_txt(self,f):
        inf=self.info.get(f)
        V_=self._vt
        if not inf:return self._nombre(f)+"\n"+V_("Analizando...","Analyzing...")
        fm=inf.get("format",{});L=[]
        L.append(V_("Archivo:   ","File:      ")+self._nombre(f))
        L.append(V_("Carpeta:   ","Folder:    ")+os.path.dirname(f.rstrip("\\/")))
        tam=sum(os.path.getsize(p) for p in self._vobs(f)) if os.path.isdir(f) else (os.path.getsize(f) if os.path.isfile(f) else 0)
        L.append(V_("Formato:   ","Format:    ")+f"{fm.get('format_long_name') or fm.get('format_name','?')} · {_hms(_dur(inf)).split('.')[0]} · {tam/1e9:.2f} GB · {int(_num(fm.get('bit_rate'))/1000)} kbps")
        vs=_vstream(inf)
        L.append("");L.append(V_("VÍDEO","VIDEO"))
        if vs:
            fps=_fps(vs);sar=vs.get("sample_aspect_ratio","1:1")
            L.append(f"  #{vs['index']} {str(vs.get('codec_name','?')).upper()}{' ('+vs['profile']+')' if vs.get('profile') else ''} · {vs.get('width')}x{vs.get('height')}{' (SAR '+sar+')' if sar not in ('1:1','0:1','N/A') else ''} · {fps:.3f} fps · {_bits(vs)} bits")
            L.append(f"     {_hdr_tipo(vs)} · {vs.get('color_primaries','?')}/{vs.get('color_transfer','?')} · {_vkbps(inf) or '?'} kbps · {V_('entrelazado','interlaced') if _entrelazado(vs) else V_('progresivo','progressive')}")
        for p in _portadas(inf):L.append(f"  #{p['index']} "+V_("portada","cover")+f" {str(p.get('codec_name','')).upper()} {p.get('width')}x{p.get('height')}")
        a=[s for s in inf.get("streams",[]) if s.get("codec_type")=="audio"]
        L.append("");L.append(f"AUDIO ({len(a)})")
        for s in a:
            d=s.get("disposition") or {}
            _kb=_skbps(s);_sp=s.get("profile")=="DTS-HD MA" or str(s.get("codec_name","")) in ("truehd","mlp","flac","alac") or str(s.get("codec_name","")).startswith("pcm")
            _kbt=f"{_kb} kbps" if _kb else (V_("sin pérdida","lossless") if _sp else "? kbps")   # (JMG, 15-11) DTS-HD MA, TrueHD...: sin bitrate fijo
            L.append(f"  #{s['index']} [{_tag(s,'language') or 'und'}] {_nombre_codec(s.get('codec_name'),s.get('profile'))} · {s.get('channel_layout') or str(s.get('channels','?'))+' ch'} · {_kbt} · {s.get('sample_rate','?')} Hz{' · «'+_tag(s,'title')+'»' if _tag(s,'title') else ''}{V_(' · por defecto',' · default') if d.get('default') else ''}")
        su=[s for s in inf.get("streams",[]) if s.get("codec_type")=="subtitle"]
        L.append("");L.append(V_("SUBTÍTULOS","SUBTITLES")+f" ({len(su)})")
        for s in su:
            d=s.get("disposition") or {}
            L.append(f"  #{s['index']} [{_tag(s,'language') or 'und'}] {str(s.get('codec_name','?')).upper()}{' · «'+_tag(s,'title')+'»' if _tag(s,'title') else ''}{V_(' · forzado',' · forced') if d.get('forced') else ''}{V_(' · por defecto',' · default') if d.get('default') else ''}")
        L.append("");L.append(V_("Capítulos: ","Chapters: ")+str(len(inf.get("chapters",[]))))
        if f in self.jobs:L.append("");L.append("✔ "+V_("Agregado: sus ajustes están en las pestañas.","Added: its settings are in the tabs."))
        return "\n".join(L)

    # ---------- trabajos ----------
    def _agregar(self):
        sel=[self.files[i] for i in self.la.curselection() if i<len(self.files)]
        if not sel:self._toast(T("info_tit"),self._vt("Selecciona antes uno o varios vídeos de la lista.","First select one or more videos in the list."),seg=4);return
        falta=[f for f in sel if f not in self.info]
        if falta:self._toast(T("info_tit"),self._vt("Espera un momento: aún se está analizando ","Wait a moment: still analyzing ")+self._nombre(falta[0]),seg=4);return
        self._guardar_trabajo()
        for f in sel:
            if f not in self.jobs:self.jobs[f]=self._nuevo_trabajo(f);self._crop_detectar(f,callado=True);self._medir_kbps_pedir(f)   # las bandas negras se buscan solas; (17-11) y el bitrate se mide
        self.actual=sel[0]
        self._pintar_lista();self._pintar_trabajo();self._sarch();self._refrescar_estado()
        self._log("[+] "+", ".join(self._nombre(f) for f in sel))
    def _quitar_trabajo(self):
        for i in self.la.curselection():
            f=self.files[i];self.jobs.pop(f,None)
            if f==self.actual:self.actual=None
        if self.actual is None:self.actual=next((f for f in self.files if f in self.jobs),None)
        self._pintar_lista();self._pintar_trabajo();self._sarch();self._refrescar_estado()
    def _pista_a(self,s,ext=""):
        """una pista de audio del trabajo (ext = archivo de donde viene si no es el video)"""
        n=int(_num(s.get("channels"),2))
        bits=24 if (str(s.get("sample_fmt","")).startswith("s32") or int(_num(s.get("bits_per_raw_sample"),0))>16) else 16
        return {"idx":s["index"],"ext":ext,"incl":True,"lang":_tag(s,"language") or "und","tit":_tag(s,"title") or (os.path.splitext(os.path.basename(ext))[0] if ext else ""),
                "codec_in":s.get("codec_name",""),"perfil":s.get("profile") or "","nch":n,"lay":_lay(s),"bits_in":bits,"start":_num(s.get("start_time")),
                "orig":(f"{os.path.basename(ext)} · " if ext else "")+f"{_nombre_codec(s.get('codec_name'),s.get('profile'))} {_skbps(s) or ''}{' kbps' if _skbps(s) else ''}".strip(),"kbps_in":_skbps(s),
                "cod":"copy","kbps":0,"def":False,"ef":{k:0 for k in AEF_KEYS},"delay":0,"tramos":None,"fps_de":"","fps_a":"","fps_met":"tono","conservar":True,"tit_proc":"Jmg procesada"}
    def _nuevo_trabajo(self,ruta):
        inf=self.info[ruta]
        a=[self._pista_a(s) for s in inf.get("streams",[]) if s.get("codec_type")=="audio"]
        # (JMG, 7-11) ninguna pista de audio sale marcada «Por defecto»: la marca quien codifica
        su=[]
        for s in inf.get("streams",[]):
            if s.get("codec_type")!="subtitle":continue
            d=s.get("disposition") or {}
            su.append({"idx":s["index"],"ext":"","incl":True,"lang":_tag(s,"language") or "und","tit":_tag(s,"title"),"fmt":s.get("codec_name",""),
                       "def":bool(d.get("default")),"forz":bool(d.get("forced"))})
        for s_ in su:s_["def"]=False   # (JMG, 8-11) por defecto, el forzado; si no hay, el primero de la lista
        if su:next((s_ for s_ in su if s_["forz"]),su[0])["def"]=True
        v,_=self._auto_video(ruta)
        return {"v":v,"a":a,"s":su,"rec":{"ini":"","fin":"","tramos":[]},"portada":None if _portadas(inf) else _portada_junto(ruta)}   # (JMG, 16-11) o el cover.jpg de su carpeta
    def _auto_video(self,ruta):
        """el códec, el bitrate y la resolución que mejor le van al vídeo -> (ajustes, explicacion)"""
        inf=self.info[ruta];vs=_vstream(inf) or {};h=int(_num(vs.get("height"),1080));V_=self._vt
        hdr=_hdr_tipo(vs)!="SDR";src=_vkbps(inf);cin=str(vs.get("codec_name",""))
        codec="h264" if h<=576 and not hdr else "hevc"
        kb=_kbps_obj(codec,h,hdr)
        v={"codec":codec,"motor":"cpu","modo":"b","crf":CRF_DEF[codec],"kbps":kb,"pasadas2":True,"vel":"media","res":"orig","bits":"auto","color":"auto","lut":"","deint":"auto",
           "log":_es_log(inf),"crop_on":False,"crop":""}
        v.update({k:0 for k in VIMG_KEYS})
        if cin in ("hevc","av1","vvc") and src and src<=kb*1.1:
            v["codec"]="copy";v["kbps"]=min(kb,max(300,int(round(src/100.0))*100))
            return v,V_(f"ya está bien comprimido ({cin.upper()}, {src} kbps): se deja el vídeo como está (Passthrough).",f"it is already well compressed ({cin.upper()}, {src} kbps): the video is left as it is (Passthrough).")
        if src:kb=min(kb,max(500,int(round(src*0.8/100.0))*100));v["kbps"]=kb
        txt=V_(f"{dict(VCODECS)[codec]} a {kb} kbps en dos pasadas, {h}p","{0} at {1} kbps in two passes, {2}p".format(dict(VCODECS)[codec],kb,h))
        if hdr:txt+=V_(", 10 bits con su HDR",", 10 bits keeping its HDR")
        if _entrelazado(vs):txt+=V_(", desentrelazado",", deinterlaced")
        return v,txt+"."
    def _job(self):return self.jobs.get(self.actual) if self.actual else None
    _VVARS=(("codec","vcodec"),("motor","vmotor"),("modo","vmodo"),("crf","crf"),("kbps","kbps"),("pasadas2","2pass"),("vel","vel"),("res","res"),("bits","bits"),
            ("color","color"),("lut","lut"),("deint","deint"),("log","log"),("crop_on","crop_on"))+tuple((k,k) for k in VIMG_KEYS)
    def _pintar_trabajo(self):
        """pasa los ajustes del trabajo activo a las pestañas"""
        j=self._job()
        if not j and getattr(self,"_avz",None):self._avz_volver(pintar=False)
        self._cargando=True
        try:
            if j:
                v=j["v"]
                for k,n in self._VVARS:getattr(self,"var_"+n).set(v.get(k,0))
                self.var_ini.set(j["rec"]["ini"]);self.var_fin.set(j["rec"]["fin"])
                inf=self.info.get(self.actual,{});vs=_vstream(inf) or {}
                self.lbl_act.configure(text=self._vt("En las pestañas: ","In the tabs: ")+self._nombre(self.actual))
                self.lbl_csrc.configure(text=self._vt("Original: ","Original: ")+f"{_hdr_tipo(vs)} · {_bits(vs)} bits · {vs.get('color_primaries','?')}/{vs.get('color_transfer','?')}"+(self._vt(" · logarítmico"," · log") if _es_log(inf) else ""))
                try:
                    self.sc_pos.configure(to=max(1.0,_dur(inf)))
                    if not (0<self.var_pos.get()<=_dur(inf)) or getattr(self,"_pos_de",None)!=self.actual:self.var_pos.set(round(_dur(inf)*0.25,3))
                    self._pos_de=self.actual
                except Exception:pass
            else:
                self.lbl_act.configure(text=self._vt("Selecciona un vídeo y pulsa «Agregar».","Select a video and press «Add to queue»."))
                self.lbl_csrc.configure(text="")
            self._pintar_a();self._pintar_s();self._pintar_tramos();self._pintar_crop();self._pintar_portada();self._nom_pintar()
        finally:self._cargando=False
        self._estado_general();self._estado_video();self._refrescar_estado()
        for i in (0,1):
            try:getattr(self,"lbl_img%d"%i).configure(image="");setattr(self,"_img%d"%i,None)
            except Exception:pass
        self._prev_de=None
        if j and self._tab_vis():self._prev_pronto(200)
        self.root.after_idle(self._ajustar_alto)
    def _motor_elegido(self,k):
        """(JMG, 16-11) el motor que elige quien codifica: se recuerda aunque un códec obligue a pasar por el procesador"""
        j=self._job()
        if j:j["v"]["motor_pref"]=k
    _PERDIDA=("ac3","eac3","dts","aac","mp3","opus")
    def _nucleo_dts(self,j,ext=None):
        """(JMG, 16-11) decodificar solo el núcleo DTS de las DTS-HD de esta entrada (más rápido): si todas las que se recomprimen van a un
        formato con pérdida (las que van tal cual no se decodifican)"""
        try:
            hd=[t for t in j["a"] if t["incl"] and (t["ext"] or None)==ext and str(t.get("codec_in"))=="dts" and "DTS-HD" in str(t.get("perfil",""))]
            cs=[(ACOD_DE_ORIGEN.get(t["codec_in"],"eac3") if (t["cod"]=="copy" and self._a_recodificar(t)) else t["cod"]) for t in hd]
            cs=[x for x in cs if x!="copy"]
            return bool(cs) and all(x in self._PERDIDA for x in cs)
        except Exception:return False
    def _es_disco(self,ruta):
        """un disco en el lector o una imagen .iso (no se puede guardar «junto al original»)"""
        return bool((getattr(self,"_isos",{}) or {}).get(ruta)) or not os.path.basename(str(ruta or "x").rstrip("\\/"))
    def _dest_disco_aviso(self,toast=False):
        """(JMG, 16-11) con un disco o una imagen y «Junto al original»: se guarda en Vídeos (dicho bien claro) -> el texto o «»"""
        r_=self.actual;V_=self._vt
        if not r_ or self.var_dest_modo.get()=="carpeta" or not self._es_disco(r_):return ""
        t=V_(f"«{self._nombre(r_)}» es un disco o una imagen: «Junto al original» no se puede (el disco no se puede escribir). Se guarda en tu carpeta Vídeos: {self._dir_orig(r_)}\n\nSi lo quieres en otro sitio, elige «Carpeta elegida» en Salida.",
             f"«{self._nombre(r_)}» is a disc or an image: «Next to the original» is not possible (the disc cannot be written). It is saved in your Videos folder: {self._dir_orig(r_)}\n\nIf you want it elsewhere, choose «Chosen folder» in Output.")
        if toast:self._toast(T("info_tit"),t,seg=12)
        return t
    _KB_FAC={"h264":1.0,"hevc":0.65,"av1":0.55,"vp9":0.65,"vvc":0.5}
    def _medir_kbps_pedir(self,ruta):
        """(JMG, 17-11) el bitrate del «Auto» según la película, no solo su resolución: se mide en segundo plano, de una en una"""
        j=self.jobs.get(ruta)
        if not j:return
        j["_kb_auto"]=j["v"].get("kbps")
        self._med_cola=[x for x in getattr(self,"_med_cola",[]) if x!=ruta]+[ruta]
        if getattr(self,"_med_corriendo",False):return
        self._med_corriendo=True;threading.Thread(target=self._medir_kbps_hilo,daemon=True).start()
    def _medir_kbps_hilo(self):
        if not hasattr(self,"_med_ref"):self._med_ref={}
        while True:
            try:ruta=self._med_cola.pop(0)
            except IndexError:break
            if ruta not in self.jobs or ruta not in self.info:continue
            ref=self._med_ref.get(ruta)
            if ref is None:
                try:ref=self._medir_ref(ruta)
                except Exception as e:ref=0;self._ls(f"[AUTO] {e}")
                self._med_ref[ruta]=ref
            self._ui(self._medir_kbps_fin,ruta,ref)
        self._med_corriendo=False
    def _medir_ref(self,ruta):
        """kbps a calidad fija (x264 veryfast CRF 19) de 5 trozos de 6 s repartidos por la película, a su altura"""
        inf=self.info[ruta];vs=_vstream(inf) or {};d=_dur(inf) or 0
        if not vs or d<60:return 0
        ent=inf.get("entrada",ruta);dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        tot=seg=0
        for p_ in (0.1,0.3,0.5,0.7,0.9):
            c=[FFMPEG,"-hide_banner","-v","error","-nostdin"]+dvd+["-ss",f"{d*p_:.1f}","-i",ent,"-map",f"0:{vs['index']}","-t","6","-an","-sn","-dn",
               "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-f","matroska","-"]
            r=subprocess.run(c,capture_output=True,timeout=180,creationflags=CNW)
            if r.returncode==0 and r.stdout:tot+=len(r.stdout);seg+=6
        return int(tot*8/seg/1000) if seg else 0
    def _medir_kbps_fin(self,ruta,ref):
        j=self.jobs.get(ruta)
        if j and not ref:self._log(f"[AUTO] {self._nombre(ruta)}: "+self._vt("no se ha podido medir la película: se queda el bitrate de su resolución.","the movie could not be measured: the bitrate for its resolution stays."))
        if not j or not ref or self.procesando:return
        v=j["v"];c=v.get("codec")
        if c=="copy" or c in INTRA or v.get("modo")!="b" or str(v.get("res","orig"))!="orig":return
        if v.get("kbps")!=j.get("_kb_auto"):return   # quien codifica ha cambiado el bitrate: no se toca
        inf=self.info.get(ruta,{});vs=_vstream(inf) or {};h=int(_num(vs.get("height"),1080));hdr=_hdr_tipo(vs)!="SDR"
        tabla=_kbps_obj(c,h,hdr);src=_vkbps(inf)
        kb=ref*self._KB_FAC.get(c,0.65)*(1.2 if hdr else 1.0)*(1.15 if v.get("motor","cpu")!="cpu" else 1.0)
        hi=tabla*1.5
        if src:hi=min(hi,src*0.8)
        kb=int(round(max(tabla*0.25,min(hi,kb))/100.0)*100)
        if kb<=0 or kb==v.get("kbps"):return
        v["kbps"]=kb;j["_kb_auto"]=kb
        h_=self._auto_hecho.get((ruta,"v","video"))
        if h_:h_["kbps"]=kb
        if ruta==self.actual:
            self._cargando=True
            try:self.var_kbps.set(kb)
            finally:self._cargando=False
        self._log(f"[AUTO] {self._nombre(ruta)}: "+self._vt(f"medida la película ({ref} kbps a calidad fija con H.264): {dict(VCODECS).get(c,c)} a {kb} kbps (por su resolución serían {tabla}).",
                                                             f"movie measured ({ref} kbps at fixed quality with H.264): {dict(VCODECS).get(c,c)} at {kb} kbps (its resolution alone would give {tabla})."))
        try:self._estado_video();self._refrescar_estado()
        except Exception:pass
    def _guardar_trabajo(self):
        j=self._job()
        if self._cargando or not j:return
        v=j["v"]
        for k,n in self._VVARS:
            try:v[k]=getattr(self,"var_"+n).get()
            except (tk.TclError,ValueError):pass
        j["rec"]["ini"]=self.var_ini.get().strip();j["rec"]["fin"]=self.var_fin.get().strip()
    def _cambio(self):
        if self._cargando:return
        self._guardar_trabajo()
        j=self._job()
        if j and j["v"]["codec"]=="copy" and (j["v"].get("crop_on") or any(j["v"].get(k) for k in VIMG_KEYS) or (j["v"].get("lut") and j["v"].get("log"))):
            # retocar la imagen obliga a recomprimir el video: el codec del Auto (o HEVC)
            nv,_=self._auto_video(self.actual);c=nv["codec"] if nv["codec"]!="copy" else "hevc"
            j["v"]["codec"]=c;self._cargando=True
            try:self.var_vcodec.set(c)
            finally:self._cargando=False
            self._log("[i] "+self._vt(f"Para retocar la imagen hay que recomprimir el vídeo: pasa a {dict(VCODECS)[c]}.",f"To touch up the picture the video must be re-encoded: it becomes {dict(VCODECS)[c]}."))
        self._estado_video();self._refrescar_estado()
    def _vvc_def(self,*_):
        """(JMG, 23-11) «en el VVC, la opción por defecto: una pasada y rápida» (es muy lento): al pasar a VVC desde otro códec.
        Al cargar un vídeo o deshacer (_cargando) solo se apunta el códec, y se respeta lo que tenía"""
        c=self.var_vcodec.get();ant=getattr(self,"_vcod_ult",None);self._vcod_ult=c
        if self._cargando or c!="vvc" or ant in (None,"vvc") or not self._job():return
        if self.var_2pass.get():self.var_2pass.set(False)
        if self.var_vel.get()!="rapida":self.var_vel.set("rapida")
        self._log("[i] "+self._vt("H.266 / VVC es muy lento: una pasada y velocidad «Rápida» (puedes cambiarlo).","H.266 / VVC is very slow: one pass and «Fast» speed (you can change it)."))
    def _estado_general(self):
        """sin ningun video agregado, las pestañas (menos Edit/Log) quedan desactivadas"""
        hay=bool(self._job()) and not self.procesando
        if getattr(self,"_hay_previo",None)==hay:return
        self._hay_previo=hay
        def todos(p):
            for w in p.winfo_children():
                yield w;yield from todos(w)
        for i,tab in enumerate(self.nb.tabs()):
            if tab==getattr(self,"_tab_log_w",None):continue
            for w in todos(self.nb.nametowidget(tab)):
                try:
                    c=w.winfo_class()
                    if c in ("TButton","TCheckbutton","TRadiobutton","TScale","TCombobox","Treeview"):w.state(["!disabled"] if hay else ["disabled"])
                    elif c in ("Entry","Listbox"):w.configure(state="normal" if hay else "disabled")
                except Exception:pass
        if hay:   # (JMG, 14-11) al volver, lo que depende del códec, del motor o de otro ajuste se apaga otra vez (antes quedaba todo encendido)
            for f in ("_estado_video","_opc_v_estado","_ex_suav_eq","_aften_estado"):
                try:getattr(self,f)()
                except Exception:pass
    def _estado_video(self):
        """activa o desactiva lo que no se puede usar con el códec y el motor elegidos"""
        if not hasattr(self,"cb_vcod") or not self._job():return
        j=self._job();c=self.var_vcodec.get();m=self.var_vmotor.get();V_=self._vt
        def st(w,on):
            try:
                if isinstance(w,tuple):
                    w[0].state(["!disabled"] if on else ["disabled"]);w[1].configure(state="normal" if on else "disabled")
                elif isinstance(w,ttk.Combobox):   # (JMG, 13-11) un desplegable es también un tk.Entry: se enciende de solo elegir, no escribible
                    q_="readonly" if on else "disabled"
                    if str(w.cget("state"))!=q_:w.configure(state=q_)
                elif isinstance(w,tk.Entry):w.configure(state="normal" if on else "disabled")
                else:w.state(["!disabled"] if on else ["disabled"])
            except Exception:pass
        rec=c!="copy"
        for k,rb in self.rb_motor.items():
            st(rb,rec and (k=="cpu" or (c not in INTRA and VENC.get((c,k)) in self._gpu)))
        pref=(j["v"].get("motor_pref") if j else None) or "cpu"
        if rec and m=="cpu" and pref!="cpu" and self._gpu_listo and c not in INTRA and VENC.get((c,pref)) in self._gpu:   # (JMG, 16-11) vuelve a la tarjeta elegida
            j["v"]["motor"]=pref;self.var_vmotor.set(pref);return
        if rec and m!="cpu" and VENC.get((c,m)) not in self._gpu:
            self.var_vmotor.set("cpu")
            if j is not None:j["v"]["motor"]="cpu"
            if self._gpu_listo and j is not None:
                g_={"nvidia":"NVIDIA","amd":"AMD"}.get(m,m);n_=dict(VCODECS).get(c,c)
                self._toast(T("info_tit"),V_(f"Con {n_}, {g_} no puede codificar en este PC: pasa a Procesador. Al volver a un códec que sí puede, vuelve a {g_}.",
                                             f"With {n_}, {g_} cannot encode on this PC: it switches to Processor. When you go back to a codec it can do, it returns to {g_}."),seg=7)
            return
        tasa=rec and c not in INTRA
        st(self.rb_q,tasa);st(self.rb_b,tasa)
        q=self.var_vmodo.get()=="q"
        st(self.sl_crf,tasa and q);st(self.sl_kbps,tasa and not q);st(self.chk_2p,tasa and not q);st(self.cb_vel,tasa)
        self.chk_2p.configure(text=V_("Dos pasadas (más lento, reparte mejor el bitrate)","Two passes (slower, spreads the bitrate better)") if m=="cpu" or not rec else
                              V_("Dos pasadas (en la tarjeta gráfica: analiza cada fotograma antes de codificarlo)","Two passes (on the graphics card: it analyzes each frame before encoding it)"))
        for w in (self.cb_res,self.cb_bits,self.cb_deint):st(w,rec)
        inf=self.info.get(self.actual,{});hdr=_hdr_tipo(_vstream(inf))!="SDR"
        st(self.cb_color,rec and hdr)
        lg=rec and bool(self.var_log.get())
        st(self.chk_log,rec)
        for w in (self.en_lut,self.bt_lut,self.bt_lutx):st(w,lg)
        if not self._gpu_listo:g=V_("Buscando la tarjeta gráfica...","Looking for the graphics card...")
        elif not self._gpu:g=V_("No hay codificación por tarjeta gráfica en este PC: solo procesador.","No graphics card encoding on this PC: processor only.")
        else:
            nv=[x.split("_")[0].upper().replace("H264","H.264") for x in sorted(self._gpu) if "nvenc" in x];am=[x.split("_")[0].upper().replace("H264","H.264") for x in sorted(self._gpu) if "amf" in x]
            g=" · ".join(p for p in (("NVIDIA: "+", ".join(nv)) if nv else "",("AMD: "+", ".join(am)) if am else "") if p)
            if c in ("vvc","vp9")+INTRA:g+=V_("  (H.266, VP9, ProRes y DNxHR: solo procesador)","  (H.266, VP9, ProRes and DNxHR: processor only)")
        self.lbl_gpu.configure(text=g)
        self.lbl_vest.configure(text=self._estimacion(j))
    def _akbps_total(self,j):
        t=0
        for a in j["a"]:
            if not a["incl"]:continue
            if a["cod"]=="copy":t+=a.get("kbps_in") or 640
            elif a["cod"] in ABITS:t+=int((330 if (a["kbps"] or 24)>16 else 250)*a["nch"])
            else:t+=a["kbps"] or _akbps_def(a["cod"],a["nch"])
        return t
    def _tramos_job(self,j,ruta=None):
        """tramos [(ini, fin)] en segundos del video; [] = entero"""
        tr=[tuple(x) for x in j["rec"].get("tramos") or []]
        if tr:return tr
        ini=_seg(j["rec"]["ini"]) or 0.0;fin=_seg(j["rec"]["fin"]) or 0.0
        if ini or fin:
            d=_dur(self.info.get(ruta or self.actual,{}))
            return [(ini,fin if fin>ini else (d or ini))]
        return []
    def _dur_trabajo(self,j,ruta=None):
        tr=self._tramos_job(j,ruta)
        return sum(max(0.0,b-a) for a,b in tr) if tr else _dur(self.info.get(ruta or self.actual,{}))
    def _estimacion(self,j):
        V_=self._vt;v=j["v"];d=self._dur_trabajo(j)
        if v["codec"]=="copy":
            kb=_vkbps(self.info.get(self.actual,{}))
            return V_(f"Vídeo sin recomprimir. Tamaño aproximado: {(kb+self._akbps_total(j))*d/8e6:.2f} GB",f"Video not re-encoded. Approximate size: {(kb+self._akbps_total(j))*d/8e6:.2f} GB") if kb else V_("Vídeo sin recomprimir (Passthrough).","Video not re-encoded (Passthrough).")
        if v["codec"]=="dnxhr":
            vs=_vstream(self.info.get(self.actual,{})) or {};px=_num(vs.get("width"),1920)*_num(vs.get("height"),1080);kb=int(145000*px/(1920*1080)*_fps(vs)/23.976) if _fps(vs) else 145000
            return V_(f"DNxHR HQ: unos {kb//1000} Mbps, {(kb+self._akbps_total(j))*d/8e6:.1f} GB (es para editar, ocupa mucho)",f"DNxHR HQ: about {kb//1000} Mbps, {(kb+self._akbps_total(j))*d/8e6:.1f} GB (it is for editing, it takes a lot of space)")
        if v["codec"]=="prores":
            vs=_vstream(self.info.get(self.actual,{})) or {};px=_num(vs.get("width"),1920)*_num(vs.get("height"),1080);kb=int(102000*px/(1920*1080)*_fps(vs)/29.97) if _fps(vs) else 102000
            return V_(f"ProRes 422 LT: unos {kb//1000} Mbps, {(kb+self._akbps_total(j))*d/8e6:.1f} GB (es para editar, ocupa mucho)",f"ProRes 422 LT: about {kb//1000} Mbps, {(kb+self._akbps_total(j))*d/8e6:.1f} GB (it is for editing, it is big)")
        if v["modo"]=="q":return V_("Calidad constante: el tamaño depende de la película (no se sabe antes).","Constant quality: the size depends on the movie (it cannot be known beforehand).")
        return V_(f"Tamaño aproximado: {(v['kbps']+self._akbps_total(j))*d/8e6:.2f} GB ({v['kbps']} kbps de vídeo + {self._akbps_total(j)} de audio)",f"Approximate size: {(v['kbps']+self._akbps_total(j))*d/8e6:.2f} GB ({v['kbps']} kbps video + {self._akbps_total(j)} audio)")
    def _refrescar_estado(self):
        if getattr(self,"_bloq_n",0):return   # (JMG, 8-11) con una ventana emergente abierta, la principal queda bloqueada
        try:
            n=len(self.files);m=sum(1 for f in self.files if f in self.jobs)
            self.lbl_f.configure(text=self._vt(f"{n} vídeo{'s' if n!=1 else ''} · {m} agregado{'s' if m!=1 else ''}",f"{n} video{'s' if n!=1 else ''} · {m} added"))
            for b in (self.btn_quit,self.btn_limp,self.btn_agr,self.btn_noagr):b.state(["!disabled"] if n and not self.procesando else ["disabled"])
            self.btn_p.state(["!disabled"] if m and not self.procesando else ["disabled"])
            for b in (self.btn_gp,self.btn_cp):b.state(["!disabled"] if self._job() and not self.procesando else ["disabled"])
            self.btn_rst.state(["!disabled"] if (self._job() or (self.files and self.var_reset_all.get())) and not self.procesando else ["disabled"])
            j=self._job()
            if j:
                sal,avisos=self._salida(self.actual,j,probar=True)
                self.lbl_sal.configure(text=self._vt("Se guardará como:\n","It will be saved as:\n")+sal+("\n\n⚠ "+"\n⚠ ".join(avisos) if avisos else ""))
            else:self.lbl_sal.configure(text="")
        except Exception:pass
    def _tab_vis(self):return getattr(self,"_avz",None)=="v"
    def _tab_cambio(self,e=None):self._ajustar_alto()
    def _rst(self):
        """Resetear (JMG, 22-11): los ajustes automáticos de la PESTAÑA ABIERTA del vídeo activo (Vídeo con «Más opciones», Audio,
        Subtítulos, Salida o Edit/Log); con «Todo», todo de cero (JMG, 8-11): la lista de vídeos, la información, sus ajustes, los trozos
        de Combinar y la Salida por defecto. «↶ Deshacer» lo recupera"""
        if self.procesando:return
        V_=self._vt;todo=bool(self.var_reset_all.get())
        SAL=((self.var_cont,"mkv"),(self.var_dest_modo,"original"),(self.var_sufijo," (Jmg VideoEncoder)"),(self.var_dup,"rename"),(self.var_caps,True),(self.var_meta,True),(self.var_adj,True),(self.var_abrir,True))
        if todo:
            for f in list(self.jobs):self.jobs[f]=self._nuevo_trabajo(f)
            for var,v in SAL:var.set(v)
            self.var_al_terminar.set("nada");self.cmb_fin.current(0)
            self._clr(sin_preguntar=True);self._clips=[];self._auto_hecho={};self.var_reset_all.set(False)
            self._pintar_trabajo()
            self._toast(T("info_tit"),V_("Todo de cero: la lista de vídeos, sus ajustes y la Salida por defecto. «↶ Deshacer» lo recupera.","Everything from scratch: the video list, its settings and the default Output. «↶ Undo» brings it back."),seg=3);return
        try:nom=self.nb.tab(self.nb.select(),"text")
        except Exception:nom=T("t_video")
        if nom==T("t_log"):
            try:self.txt_log.delete("1.0","end")
            except Exception:pass
            return
        f=self.actual;j=self._job()
        if nom==T("t_sal"):
            for var,v in SAL:var.set(v)
            if j:j["portada"]=self._nuevo_trabajo(f)["portada"];j["nombre"]=None
            self._pintar_trabajo()
            self._toast(T("info_tit"),V_("La Salida vuelve a la de fábrica. «↶ Deshacer» la recupera.","The Output is back to its defaults. «↶ Undo» brings it back."),seg=3);return
        if not j:return
        n_=self._nuevo_trabajo(f)
        if nom==T("t_audio"):
            j["a"]=n_["a"];que=V_("del audio","for the audio")
            for k in [k for k in self._auto_hecho if k[0]==f and k[1]!="v"]:self._auto_hecho.pop(k,None)
        elif nom==T("t_subs"):j["s"]=n_["s"];que=V_("de los subtítulos","for the subtitles")
        else:   # Vídeo, con «Más opciones»: recorte por tramos, imagen y bandas negras
            j["v"]=n_["v"];j["rec"]=n_["rec"];que=V_("del vídeo","for the video")
            for k in [k for k in self._auto_hecho if k[0]==f and k[1]=="v"]:self._auto_hecho.pop(k,None)
            try:self._crop_detectar(f,callado=True);self._medir_kbps_pedir(f)   # como al agregarlo: las bandas negras y el bitrate
            except Exception:pass
        self._pintar_trabajo()
        self._toast(T("info_tit"),V_(f"Vuelven los ajustes automáticos {que} de ",f"The automatic settings are back {que} of ")+self._nombre(f)+V_(". «↶ Deshacer» los recupera.",". «↶ Undo» brings them back."),seg=3)

    # ---------- pistas de audio y subtítulos ----------
    def _a_texto(self,t):
        if t["cod"]=="copy":s="Passthrough"
        else:
            k=t['kbps'] or _akbps_def(t['cod'],t['nch'])
            af_=t["cod"]=="ac3" and t.get("aften",True) and AFTEN;a_=self._af_de(t) if af_ else {}
            if af_ and a_.get("modo")=="vbr":s=f"Aften AC3 VBR {int(a_.get('q',240))}"   # (JMG, 10-11) lo que se ha puesto en la ventana de Aften
            else:s=("Aften AC3" if af_ else dict(ACODECS)[t["cod"]].split(" (")[0])+(f" {k} bits" if t["cod"] in ABITS else f" {k}k")
        if t["cod"] in OPC and not (t["cod"]=="ac3" and t.get("aften",True) and AFTEN) and self._opc_cambiadas(t["cod"],(t.get("opc") or {}).get(t["cod"])):s+=" · ⚙"   # (JMG, 12-11) con opciones avanzadas
        if _fps_q(t):s+=f" · {t['fps_de'].replace('.',',')}→{t['fps_a'].replace('.',',')} fps"
        if t.get("delay"):s+=f" · {t['delay']:+d} ms"
        if t.get("tramos"):s+=self._vt(" · por tramos"," · by parts")
        if _a_proc(t):s+=self._vt(" · efectos"," · effects")
        if t.get("nucleo"):s+=self._vt(" · + núcleo DTS"," · + DTS core")   # (JMG, 15-11)
        if _a_proc(t):s+=self._vt(" · la primera"," · first")+(self._vt(" · + la original"," · + the original") if t.get("conservar",True) else self._vt(" · sin la original"," · without the original"))
        return s
    def _a_fila(self,k,t):
        return ("✔" if t["incl"] else "✖",(self._vt("ext.","ext.") if t["ext"] else t["idx"]),t["lang"],t["tit"],t["orig"],t["lay"] or f"{t['nch']} ch",self._a_texto(t))
    def _pintar_a(self,sel=None):
        tv=self.tv_a;tv.delete(*tv.get_children());j=self._job()
        if not j:self._a_i=None;return
        tv.tag_configure("elim",foreground=CAV)   # original eliminada o pista fuera: rojo suave, como en Jmg AudioProcesador
        for k,t in enumerate(j["a"]):tv.insert("","end",iid=str(k),values=self._a_fila(k,t),tags=self._a_tags(t))
        if j["a"]:
            i=sel if sel is not None else (getattr(self,"_a_i",0) or 0)
            i=max(0,min(i,len(j["a"])-1));tv.selection_set(str(i));self._a_i=i;self._a_cargar()
        else:self._a_i=None
        self._aref_vals()
    def _aref_vals(self):
        """«Comparar con»: las demas pistas (la del idioma original suele ser la primera)"""
        j=self._job();ops=[]
        if j and self._a_i is not None:
            ops=[(k,f"#{t['idx'] if not t['ext'] else 'ext.'} [{t['lang']}] {t['tit'] or t['codec_in'].upper()}") for k,t in enumerate(j["a"]) if k!=self._a_i]
        self._aref_ops=ops
        try:
            self.cb_aref.configure(values=[x for _,x in ops])
            if ops:self.cb_aref.current(0)
            else:self.cb_aref.set("")
        except Exception:pass
    def _a_sel_cambio(self):
        s=self.tv_a.selection()
        if not s:return
        i=int(s[0])
        if i!=getattr(self,"_a_i",None):self._a_i=i;self._a_cargar();self._aref_vals()
    def _a_cargar(self):
        j=self._job()
        if not j or self._a_i is None:return
        t=j["a"][self._a_i];prev=self._cargando;self._cargando=True
        try:
            self.var_a_lang.set(t["lang"]);self.var_a_tit.set(t["tit"]);self.var_a_cod.set("aften" if (t["cod"]=="ac3" and t.get("aften",True) and AFTEN) else t["cod"]);self.var_a_def.set(t["def"]);self.var_a_delay.set(t.get("delay",0))
            vf=self._fps_video();self.var_a_fps_de.set(t.get("fps_de") or vf);self.var_a_fps_a.set(t.get("fps_a") or vf);self.var_a_fps_met.set(t.get("fps_met") or "tono")
            if _a_proc(t):self.var_a_tit.set(t.get("tit_proc") or "Jmg procesada")   # procesada (con efectos): su título
            self._akbps_vals(t)
            for k in AEF_KEYS:getattr(self,"var_"+k).set(t["ef"].get(k,0))
            self.lbl_sinc.configure(text=self._sinc_txt(t))
        finally:self._cargando=prev
        self._aften_estado()
    def _akbps_vals(self,t):
        vals=[str(x) for x in _akbps_lista(t["cod"],t["nch"])]
        libre=t["cod"]=="eac3"   # (JMG, 16-11) el E-AC3 admite cualquier bitrate: se puede escribir
        self.cb_akbps.configure(values=vals,state=("normal" if libre else "readonly") if vals else "disabled")
        try:self.lbl_akbps.configure(text="bits:" if t["cod"] in ABITS else "kbps:")
        except Exception:pass
        if vals:
            vale=lambda k:str(k) in vals or (libre and _eac3_ok(k,t["nch"]))
            if not t["kbps"] or not vale(t["kbps"]):t["kbps"]=(t.get("bits_in",24) if t["cod"] in ABITS else _akbps_def(t["cod"],t["nch"]))
            if not vale(t["kbps"]):t["kbps"]=int(vals[-1])
            self.var_a_kbps.set(str(t["kbps"]))
        else:self.var_a_kbps.set("")
    def _akbps_escrito(self):
        """(JMG, 16-11) E-AC3: el bitrate escrito a mano, dentro de lo que admite según los canales (si no, al borde, y lo dice)"""
        j=self._job();i=getattr(self,"_a_i",None)
        if not j or i is None or i>=len(j["a"]):return
        t=j["a"][i]
        if t["cod"]!="eac3":return
        lo,hi=_eac3_rango(t["nch"]);V_=self._vt
        try:k=int(float((re.sub(r"[^0-9.,]","",self.var_a_kbps.get()) or "0").replace(",",".")))
        except ValueError:k=0
        k2=min(hi,max(lo,k)) if k else _akbps_def("eac3",t["nch"])
        if k and k2!=k:self._toast(T("info_tit"),V_(f"E-AC3: de {lo} a {hi} kbps con {t['nch']} canales.",f"E-AC3: {lo} to {hi} kbps with {t['nch']} channels."),seg=4)
        if str(k2)!=self.var_a_kbps.get():self.var_a_kbps.set(str(k2))
    def _a_recodificar(self,t):
        """efectos, delay o tramos necesitan recomprimir la pista: con su mismo códec (o E-AC3)"""
        return any(t["ef"].values()) or t.get("delay") or t.get("tramos") or _fps_q(t)
    def _cambio_a(self):
        j=self._job()
        if self._cargando or not j or getattr(self,"_a_i",None) is None:return
        t=j["a"][self._a_i];V_=self._vt
        t["lang"]=self.var_a_lang.get().strip() or "und"
        p0=_a_proc(t)
        if p0:t["tit_proc"]=self.var_a_tit.get()   # procesada: el título es el suyo («Jmg procesada»); la original conserva el suyo
        else:t["tit"]=self.var_a_tit.get()
        cod=self.var_a_cod.get()
        if cod=="aften":cod="ac3";t["aften"]=True   # (JMG, 9-11) «Aften Dolby Digital» = AC3 hecho por Aften
        elif cod=="ac3":t["aften"]=False             # «AC3 · FFmpeg»
        for k in AEF_KEYS:
            try:t["ef"][k]=int(round(self._raw(getattr(self,"var_"+k))))
            except Exception:pass
        try:t["delay"]=int(round(self._raw(self.var_a_delay)))
        except Exception:pass
        de,a_=self.var_a_fps_de.get(),self.var_a_fps_a.get()
        if de and a_ and de!=a_:t["fps_de"],t["fps_a"]=de,a_
        else:t["fps_de"]=t["fps_a"]=""
        t["fps_met"]=self.var_a_fps_met.get() or "tono"
        if cod=="copy" and self._a_recodificar(t):
            cod=ACOD_DE_ORIGEN.get(t["codec_in"],"eac3")
            self._log("[i] "+V_(f"Pista #{t['idx']}: para aplicar los efectos o el delay se comprime en {dict(ACODECS)[cod]}.",f"Track #{t['idx']}: to apply the effects or the delay it is compressed as {dict(ACODECS)[cod]}."))
        if cod!=t["cod"]:
            t["cod"]=cod;t["kbps"]=0;self._cargando=True
            try:self.var_a_cod.set("aften" if (cod=="ac3" and t.get("aften",True) and AFTEN) else cod);self._akbps_vals(t)
            finally:self._cargando=False
        else:
            try:t["kbps"]=int(self.var_a_kbps.get() or 0)
            except ValueError:pass
        if _a_proc(t)!=p0:   # al poner o quitar el último efecto cambia el título que se edita
            self._cargando=True
            try:self.var_a_tit.set((t.get("tit_proc") or "Jmg procesada") if _a_proc(t) else t["tit"])
            finally:self._cargando=False
        if self.var_a_def.get() and not t["def"]:
            for x in j["a"]:x["def"]=False
        t["def"]=bool(self.var_a_def.get())
        self.tv_a.item(str(self._a_i),values=self._a_fila(self._a_i,t),tags=self._a_tags(t))
        self._estado_video();self._refrescar_estado()
    def _a_incl(self):
        j=self._job()
        if not j or self._a_i is None:return
        j["a"][self._a_i]["incl"]=not j["a"][self._a_i]["incl"];self._pintar_a(self._a_i);self._estado_video()
    def _mover(self,tipo,d):
        j=self._job()
        if not j:return
        L=j[tipo];i=self._a_i if tipo=="a" else self._s_i
        if i is None or not (0<=i+d<len(L)):return
        L[i],L[i+d]=L[i+d],L[i]
        if tipo=="a":self._a_i=i+d;self._pintar_a(i+d)
        else:self._s_i=i+d;self._pintar_s(i+d)
    def _pintar_s(self,sel=None):
        tv=self.tv_s;tv.delete(*tv.get_children());j=self._job();V_=self._vt
        if not j:self._s_i=None;return
        for k,s in enumerate(j["s"]):
            tv.insert("","end",iid=str(k),values=("✔" if s["incl"] else "✖",s["idx"] if s["idx"] is not None else V_("ext.","ext."),s["lang"],s["tit"] or (os.path.basename(s["ext"]) if s["ext"] else ""),self._s_fmt_txt(s)+(V_(" · en la imagen"," · burned in") if s.get("burn") else ""),"✔" if s["def"] else "","✔" if s["forz"] else ""))
        if j["s"]:
            i=sel if sel is not None else (getattr(self,"_s_i",0) or 0)
            i=max(0,min(i,len(j["s"])-1));tv.selection_set(str(i));self._s_i=i;self._s_cargar()
        else:self._s_i=None
    def _s_sel_cambio(self):
        s=self.tv_s.selection()
        if s and int(s[0])!=getattr(self,"_s_i",None):self._s_i=int(s[0]);self._s_cargar()
    def _s_cargar(self):
        j=self._job()
        if not j or self._s_i is None:return
        s=j["s"][self._s_i];prev=self._cargando;self._cargando=True
        try:
            self.var_s_lang.set(s["lang"]);self.var_s_tit.set(s["tit"]);self.var_s_def.set(s["def"]);self.var_s_forz.set(s["forz"]);self.var_s_burn.set(bool(s.get("burn")))
            vf=self._fps_video();self.var_s_fps_de.set(s.get("fps_de") or vf);self.var_s_fps_a.set(s.get("fps_a") or vf);self.var_s_delay.set(int(s.get("delay") or 0))
        finally:self._cargando=prev
    def _cambio_s(self):
        j=self._job()
        if self._cargando or not j or getattr(self,"_s_i",None) is None:return
        s=j["s"][self._s_i]
        s["lang"]=self.var_s_lang.get().strip() or "und";s["tit"]=self.var_s_tit.get();s["forz"]=bool(self.var_s_forz.get())
        de,a_=self.var_s_fps_de.get(),self.var_s_fps_a.get()
        if de and a_ and de!=a_:s["fps_de"],s["fps_a"]=de,a_
        else:s["fps_de"]=s["fps_a"]=""
        try:s["delay"]=int(round(self._raw(self.var_s_delay)))
        except Exception:pass
        if self.var_s_def.get() and not s["def"]:
            for x in j["s"]:x["def"]=False
        s["def"]=bool(self.var_s_def.get())
        b_=bool(self.var_s_burn.get())
        if b_ and not s.get("burn"):   # (JMG, 11-11) solo uno grabado en la imagen; va incluido y el vídeo se recomprime
            for x in j["s"]:x["burn"]=False
            s["incl"]=True
            if j["v"].get("codec")=="copy":
                j["v"]["codec"]="hevc";self.root.after_idle(self._pintar_trabajo)
                self._toast(T("info_tit"),self._vt("Para grabar el subtítulo en la imagen hay que recomprimir el vídeo: en «Vídeo», el códec pasa a H.265.","To burn the subtitle into the picture the video must be re-encoded: in «Video», the codec becomes H.265."),seg=6)
        s["burn"]=b_
        self._pintar_s(self._s_i)
    def _s_incl(self):
        j=self._job()
        if not j or self._s_i is None:return
        j["s"][self._s_i]["incl"]=not j["s"][self._s_i]["incl"];self._pintar_s(self._s_i)
    def _s_externo(self):
        j=self._job()
        if not j:return
        f=filedialog.askopenfilename(title=self._vt("Subtítulo","Subtitle"),filetypes=[(self._vt("Subtítulos","Subtitles"),"*.srt *.ass *.ssa *.vtt *.sup"),(self._vt("Todos los archivos","All files"),"*.*")])
        if not f:return
        m=re.search(r"\.([a-z]{2,3})\.[^.]+$",os.path.basename(f).lower())
        fmt={".srt":"subrip",".ass":"ass",".ssa":"ass",".vtt":"webvtt",".sup":"hdmv_pgs_subtitle"}.get(os.path.splitext(f)[1].lower(),"subrip")
        j["s"].append({"idx":None,"ext":f,"incl":True,"lang":m.group(1) if m else "und","tit":"","fmt":fmt,"def":False,"forz":False})
        self._pintar_s(len(j["s"])-1)
    def _s_quitar_ext(self):
        """(JMG, 13-11) «Eliminar subtítulo»: el añadido o uno del vídeo (no sale en el archivo procesado; el original no se toca)"""
        j=self._job()
        if not j or self._s_i is None or not (0<=self._s_i<len(j["s"])):return
        j["s"].pop(self._s_i);self._pintar_s(max(0,self._s_i-1));self._refrescar_estado()
    def _elegir_lut(self):
        f=filedialog.askopenfilename(title="LUT",filetypes=[("LUT 3D","*.cube *.3dl *.dat *.m3d"),(self._vt("Todos los archivos","All files"),"*.*")])
        if f:self.var_lut.set(f)
    def _elegir_dest(self):
        d=filedialog.askdirectory(title=self._vt("Carpeta de destino","Destination folder"))
        if d:self.var_dest.set(os.path.normpath(d));self.var_dest_modo.set("carpeta")
    # ---------- comando de FFmpeg ----------
    def _enc(self,v):
        if v["codec"]=="copy":return None
        return VENC.get((v["codec"],v["motor"])) or VENC[(v["codec"],"cpu")]
    def _hdr_keep(self,ruta,j):
        return _hdr_tipo(_vstream(self.info[ruta]))!="SDR" and j["v"]["color"]!="sdr" and not j["v"]["lut"]
    def _bits_sal(self,ruta,j):
        v=j["v"];enc=self._enc(v)
        if v["codec"]=="prores":return 10
        if v["codec"]=="dnxhr":return 8
        if enc in ("h264_nvenc","h264_amf"):return 8
        if v["bits"] in ("8","10"):return int(v["bits"])
        if (v["color"]=="sdr" and _hdr_tipo(_vstream(self.info[ruta]))!="SDR") or v["lut"]:return 8   # pasado a SDR: 8 bits, como cualquier video normal
        if self._hdr_keep(ruta,j):return 10
        return 10 if (_bits(_vstream(self.info[ruta]))>=10 and v["codec"] in ("hevc","av1","vvc","vp9")) else 8
    def _pasadas(self,j):
        v=j["v"]
        return 2 if (v["codec"] not in ("copy",)+INTRA and v["modo"]=="b" and v["pasadas2"] and self._enc(v) in ("libx264","libx265","libsvtav1","libvvenc","libvpx-vp9")) else 1
    def _vfiltros(self,ruta,j,vista=False):
        """filtros de imagen: desentrelazar, bandas negras, color (LUT o HDR a SDR), brillo/contraste/nitidez/ruido y resolucion"""
        v=j["v"];vs=_vstream(self.info[ruta]) or {};f=[]
        if v["deint"]=="si" or (v["deint"]=="auto" and _entrelazado(vs)):f.append("bwdif=mode=send_frame:parity=auto:deint=all")
        if v.get("crop_on") and v.get("crop") not in ("","no",None):f.append("crop="+v["crop"])
        if v["lut"] and v.get("log"):f.append("lut3d=file="+_ff_ruta(v["lut"]))
        elif v["color"]=="sdr" and _hdr_tipo(vs)!="SDR":
            f.append("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv")
        f+=_vimg_filtro(v)
        if v["res"]!="orig" and not vista:
            H=int(v["res"])
            if H<int(_num(vs.get("height"),0)):f.append(f"scale=-2:{H}:flags=lanczos")
        return f
    def _venc(self,ruta,j,pase=None,log2=None):
        v=j["v"];enc=self._enc(v)
        if not enc:return ["-c:v:0","copy"]
        vs=_vstream(self.info[ruta]) or {};a=["-c:v:0",enc];bits=self._bits_sal(ruta,j);hk=self._hdr_keep(ruta,j);x265=["log-level=error"]
        trc="arib-std-b67" if _hdr_tipo(vs)=="HLG" else "smpte2084"
        col=(["-color_primaries","bt2020","-color_trc",trc,"-colorspace","bt2020nc"] if hk else
             (["-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709"] if (v["lut"] or (v["color"]=="sdr" and _hdr_tipo(vs)!="SDR") or vs.get("color_primaries")=="bt709") else []))
        o=self._opc_norm(enc,(v.get("opc") or {}).get(enc));fps=_fps(vs) or 25.0   # (JMG, 12-11) opciones avanzadas del códec
        if enc=="prores_ks":
            p=int(o.get("perfil",1));return a+["-profile:v:0",str(p),"-vendor","apl0","-pix_fmt","yuv444p10le" if p>=4 else "yuv422p10le"]+col
        if enc=="dnxhd":
            p=o.get("perfil","dnxhr_hq");return a+["-profile:v:0",p,"-pix_fmt",{"dnxhr_hqx":"yuv422p10le","dnxhr_444":"yuv444p10le"}.get(p,"yuv422p")]+col
        if enc=="libvpx-vp9":   # VP9 (el de YouTube): calidad constante con -b:v 0, o bitrate con dos pasadas
            a+=["-deadline","good","-cpu-used",PRESET[enc][v["vel"]],"-row-mt","1","-pix_fmt","yuv420p10le" if bits==10 else "yuv420p"]+(["-profile:v:0","2"] if bits==10 else [])
            if v["modo"]=="q":a+=["-crf",str(int(v["crf"])),"-b:v","0"]
            else:
                a+=["-b:v",f"{int(v['kbps'])}k"]
                if v["pasadas2"] and pase:a+=["-pass",str(pase),"-passlogfile",log2]
            return a+col+self._opc_v_args(enc,o,fps,bits)
        pr=PRESET[enc][v["vel"]]
        a+=(["-quality",pr] if enc.endswith("_amf") else ["-preset",pr])
        if enc.endswith("_nvenc"):a+=["-tune","hq"]
        gpu=enc.endswith("_nvenc") or enc.endswith("_amf")
        a+=["-pix_fmt",("p010le" if gpu else "yuv420p10le") if bits==10 else "yuv420p"]
        if v["modo"]=="q":
            q=str(int(v["crf"]))
            if enc in ("libx264","libx265","libsvtav1"):a+=["-crf",q]
            elif enc=="libvvenc":a+=["-qp",q]
            elif enc.endswith("_nvenc"):a+=["-rc","vbr","-cq",q,"-b:v","0"]
            else:a+=["-rc","cqp","-qp_i",q,"-qp_p",q]+(["-qp_b",q] if enc=="h264_amf" else [])
        else:
            k=int(v["kbps"]);a+=["-b:v",f"{k}k"]
            if enc.endswith("_nvenc"):a+=["-rc","vbr","-maxrate",f"{int(k*1.5)}k","-bufsize",f"{k*2}k"]
            elif enc.endswith("_amf"):a+=["-rc","vbr_peak","-maxrate",f"{int(k*1.5)}k"]
            if v["pasadas2"]:
                if enc in ("libx264","libsvtav1","libvvenc") and pase:a+=["-pass",str(pase),"-passlogfile",log2]
                elif enc=="libx265" and pase:x265+=[f"pass={pase}","stats="+log2.replace("\\","/").replace(":","\\:")+".log"]
                elif enc.endswith("_nvenc"):a+=["-multipass","fullres"]
                elif enc.endswith("_amf"):a+=list(_AMF_2P.get(enc,[]))   # (22-11) la que admita esta tarjeta (o ninguna)
        if hk and enc=="libx265":x265+=(["hdr10=1"] if trc=="smpte2084" else [])+["repeat-headers=1","colorprim=bt2020","transfer="+trc,"colormatrix=bt2020nc"]
        x265+=self._opc_params(enc,o) if enc=="libx265" else []
        if enc=="libx265":a+=["-x265-params",":".join(x265)]
        if enc=="libsvtav1":a+=["-svtav1-params",":".join(["enable-hdr=1" if hk else "enable-hdr=0"]+self._opc_params(enc,o))]
        if enc=="libvvenc" and self._opc_params(enc,o):a+=["-vvenc-params",":".join(self._opc_params(enc,o))]
        if enc=="libvvenc":a+=["-threads",str(max(2,min(64,os.cpu_count() or 8)))]   # (JMG, 22-11) solo usaba la mitad del procesador
        return a+col+self._opc_v_args(enc,o,fps,bits)
    def _a_pre(self,t,ent,lbl,off=0.0):
        """framerate, delay y tramos de sincronizacion de la pista: subgrafo que sale por [lbl], o None si no hace falta.
        El cambio de framerate va lo primero (como en Jmg AudioProcesador): el delay y los tramos ya cuentan con la velocidad nueva"""
        cv=_fps_cad(t)
        if cv:ent=f"{ent}{cv},"
        if t.get("tramos"):return self._tramos_grafo(t,ent,lbl,off)
        d=int(t.get("delay") or 0)
        if d>0:return f"{ent}adelay=delays={d}:all=1[{lbl}]"
        if d<0:return f"{ent}atrim=start={-d/1000.0:.3f},asetpts=PTS-STARTPTS[{lbl}]"
        return f"{ent}anull[{lbl}]" if cv else None
    def _a_grafo(self,t,ent,sal,sin=None,post=None,off=0.0):
        """filtros de una pista de audio: sincronizacion, y canal a canal volumen, gama dinamica / compresion, suavizado, EQ y
        Double Bass. None = no hace falta"""
        ef=dict(t["ef"])
        for k in {"gama":("gama","gama_c"),"vol":("fl","fr","fc","lfe","bl","br"),"suav":("suav",),"eq3":("eq_bass","eq_mids","eq_treble"),"db":("db",),"pres":("voz","amb","efc","sub")}.get(sin,()):ef[k]=0
        p=sal.strip("[]")
        pre=self._a_pre(t,ent,p+"pre",off)
        if pre:pre+=";";ent=f"[{p}pre]"
        else:pre=""
        eqs=[f"equalizer=f={f}:t=o:w=1:g={ef[k]}" for f,k in zip(EQ3_F,("eq_bass","eq_mids","eq_treble")) if ef.get(k)]
        lp=f"lowpass=f={SUAV_FC[ef['suav']-1]}:poles=2" if 1<=ef.get("suav",0)<=5 else None
        chans=LAYCH.get(t["lay"])
        if not any(ef.values()):
            if post:return f"{pre}{ent}{post}{sal}"
            return f"{pre}{ent}anull{sal}" if pre else None
        if not chans:   # disposicion rara: los efectos a toda la pista
            c=[x for x in (_compand(ef["gama"]),lp)+tuple(eqs) if x]
            return f"{pre}{ent}{','.join(c+([post] if post else [])) or 'anull'}{sal}"
        g=pre+f"{ent}channelsplit=channel_layout={t['lay']}"+"".join(f"[{p}s{c}]" for c in chans)
        # Presencia (la de Jmg AudioProcesador): voz solo en el central; ambiente y efectos en frontales y traseros; subwoofer
        pv=_eff(ef.get("voz"),8,24) if "FC" in chans else 0.0;pa=_eff(ef.get("amb"),7,14);pe=_eff(ef.get("efc"),7,14);ps=_eff(ef.get("sub"),9,20)
        peq=lambda fr,gg,q:f"equalizer=f={fr}:width_type=q:width={q}:g={gg}"
        b_voz=[peq(300,round(pv*0.7,2),0.9),peq(1000,round(pv*0.8,2),0.8),peq(2800,round(pv*0.7,2),0.9)] if pv else []
        b_ae=([peq(1000,pa,0.5),peq(4000,pa,0.5)] if pa else [])+([peq(2000,pe,0.6),peq(6000,pe,0.6)] if pe else [])
        for c in chans:
            ch=[];db=ef.get(SLIDER_CH.get(c,""),0)
            if db:ch.append(f"volume={db}dB")
            if c=="FC":ch+=b_voz
            elif c=="LFE":
                if ps:ch.append(f"volume={ps}dB")
            else:ch+=b_ae
            if c!="LFE":
                cp=_compand(ef["gama_c"] if c=="FC" else ef["gama"])
                if cp:ch.append(cp)
                if lp:ch.append(lp)
                ch+=eqs
            g+=f";[{p}s{c}]{','.join(ch) or 'anull'}[{p}d{c}]"
        fin={c:f"[{p}d{c}]" for c in chans}
        n=int(ef.get("db") or 0)
        if n and "LFE" in chans:   # Double Bass (el de Jmg AudioProcesador): graves del sub a los altavoces y de los altavoces al sub
            ip=lambda a,b:a+(b-a)*(n-1)/4.0
            dg=round(ip(0.12,0.6),3);dk=round(ip(0.4,1.6),3);ds=[c for c in chans if c!="LFE"]
            g+=f";[{p}dLFE]asplit=2[{p}L0][{p}L1];[{p}L1]lowpass=f={DB_CORTE}:poles=2,volume={dg},asplit={len(ds)}"+"".join(f"[{p}q{c}]" for c in ds)
            for c in ds:g+=f";[{p}d{c}]asplit=2[{p}m{c}][{p}g{c}]"
            g+=";"+"".join(f"[{p}g{c}]" for c in ds)+(f"amix=inputs={len(ds)}:normalize=0," if len(ds)>1 else "")+f"lowpass=f={DB_CORTE}:poles=2,lowpass=f={DB_CORTE}:poles=2,volume={dk}[{p}gs]"
            g+=f";[{p}L0][{p}gs]amix=inputs=2:normalize=0,alimiter=limit=0.944:attack=10:release=150:level=0:latency=1[{p}eLFE]"
            for c in ds:g+=f";[{p}m{c}][{p}q{c}]amix=inputs=2:normalize=0[{p}e{c}]"
            fin={c:f"[{p}e{c}]" for c in chans}
        g+=";"+"".join(fin[c] for c in chans)+f"join=inputs={len(chans)}:channel_layout={t['lay']}:map="+"|".join(f"{i}.0-{c}" for i,c in enumerate(chans))
        return g+(","+post if post else "")+sal
    def _a_post(self,t):
        """conversion de canales que pide el códec de salida"""
        if t["cod"]=="opus" and t["nch"]>2:return "aformat=channel_layouts="+("7.1" if t["nch"]>=8 else "5.1")
        if t["cod"] in ("ac3","eac3","dts","truehd") and t["nch"]>6:return "aformat=channel_layouts=5.1(side)"
        if t["cod"]=="truehd":return "aresample=48000"
        return None
    AVI_VCOPY=("h264","mpeg4","msmpeg4v2","msmpeg4v3","mjpeg","mpeg2video","mpeg1video","h263")   # lo que se copia tal cual en AVI
    def _cont(self,j,ruta=None):
        c=self.var_cont.get();v=j["v"]["codec"]
        if v in INTRA and c=="mp4":return "mov"   # ProRes y DNxHR no caben en MP4
        if v=="vp9" and c=="mov":return "mp4"     # VP9 no cabe en MOV
        if c=="avi":   # AVI (aparatos antiguos): H.264, o copiar un video H.264 / MPEG-4 / DivX; si no, MKV
            if v=="copy":
                if str((_vstream(self.info.get(ruta or self.actual,{})) or {}).get("codec_name","")) not in self.AVI_VCOPY:return "mkv"
            elif v!="h264":return "mkv"
        if c=="webm":   # WebM (para la web): VP9 o AV1, o copiar un video VP8 / VP9 / AV1; si no, MKV
            if v=="copy":
                if str((_vstream(self.info.get(ruta or self.actual,{})) or {}).get("codec_name","")) not in ("vp8","vp9","av1"):return "mkv"
            elif v not in ("vp9","av1"):return "mkv"
        return c
    @staticmethod
    def _webm_audio_ok(t):
        """WebM: Opus o Vorbis tal cual; lo demas pasa a Opus"""
        if t["cod"]=="copy":return str(t["codec_in"]) in ("opus","vorbis")
        return t["cod"]=="opus"
    @staticmethod
    def _avi_audio_ok(t):
        """AVI: AC3, MP3, DTS (o PCM) tal cual; lo demas pasa a AC3"""
        if t["cod"]=="copy":return str(t["codec_in"]) in ("ac3","mp3","dts","mp2") or str(t["codec_in"]).startswith("pcm")
        return t["cod"] in ("ac3","mp3","dts")
    def _salida(self,ruta,j,probar=False,usados=()):
        """ruta del archivo que se va a crear y avisos"""
        V_=self._vt;av=[];cont=self._cont(j,ruta)
        if cont!=self.var_cont.get():
            av.append({"mov":V_("ProRes y DNxHR no van en MP4: se guarda en MOV.","ProRes and DNxHR do not go in MP4: it is saved as MOV."),
                       "mp4":V_("VP9 no va en MOV: se guarda en MP4.","VP9 does not go in MOV: it is saved as MP4."),
                       "mkv":(V_("AVI solo admite H.264 (o copiar un vídeo H.264, MPEG-4 o DivX): se guarda en MKV.","AVI only takes H.264 (or copying an H.264, MPEG-4 or DivX video): it is saved as MKV.") if self.var_cont.get()=="avi" else
                              V_("WebM solo admite VP9 o AV1 (elígelo en la pestaña Vídeo) o copiar un vídeo VP8, VP9 o AV1: se guarda en MKV.","WebM only takes VP9 or AV1 (choose it in the Video tab) or copying a VP8, VP9 or AV1 video: it is saved as MKV."))}.get(cont,""))
        if cont=="webm":
            im=[s for s in j["s"] if s["incl"] and s["fmt"] in ("hdmv_pgs_subtitle","dvd_subtitle","dvb_subtitle","pgssub")]
            if im:av.append(V_(f"{len(im)} subtítulo(s) de imagen no caben en WebM: se quedan fuera (los de texto van en WebVTT).",f"{len(im)} image subtitle(s) do not fit in WebM: they are left out (text ones go as WebVTT)."))
            na=[a for a in j["a"] if a["incl"] and not self._webm_audio_ok(a)]
            if na:av.append(V_(f"{len(na)} pista(s) de audio pasan a Opus (WebM solo admite Opus y Vorbis).",f"{len(na)} audio track(s) become Opus (WebM only takes Opus and Vorbis)."))
        if cont=="avi":
            if any(s["incl"] for s in j["s"]):av.append(V_("AVI no lleva subtítulos ni capítulos: se quedan fuera.","AVI carries no subtitles or chapters: they are left out."))
            na=[a for a in j["a"] if a["incl"] and not self._avi_audio_ok(a)]
            if na:av.append(V_(f"{len(na)} pista(s) de audio pasan a AC3 (AVI solo admite AC3, MP3 y DTS).",f"{len(na)} audio track(s) become AC3 (AVI only takes AC3, MP3 and DTS)."))
        if self.var_dest_modo.get()!="carpeta" and self._es_disco(ruta):   # (JMG, 16-11) dicho bien claro
            av.append(V_(f"Es un disco o una imagen: se guarda en tu carpeta Vídeos ({self._dir_orig(ruta)}), no «junto al original».",f"It is a disc or an image: it is saved in your Videos folder ({self._dir_orig(ruta)}), not «next to the original»."))
        nu=[t for t in j["a"] if t["incl"] and t.get("nucleo")]   # (JMG, 15-11) el núcleo DTS aparte
        if nu and cont!="mkv":av.append(V_("El núcleo DTS aparte solo va en MKV: se queda fuera.","The separate DTS core only goes in MKV: it is left out."))
        elif any(t.get("delay") or t.get("tramos") or _fps_q(t) for t in nu):av.append(V_("El núcleo DTS no se saca de una pista con delay, tramos o cambio de fps (iría desfasado).","The DTS core is not taken from a track with a delay, parts or a fps change (it would be out of sync)."))
        base=self._base(ruta)   # (JMG, 8-11) de una imagen .iso, su nombre; de un DVD en el lector, su etiqueta
        d=self._dir_orig(ruta) if self.var_dest_modo.get()!="carpeta" or not self.var_dest.get().strip() else self.var_dest.get().strip()
        sal=os.path.join(d,(j.get("nombre") or base+self.var_sufijo.get())+"."+cont)   # (JMG, 8-11) o el nombre puesto a este vídeo
        if os.path.normcase(os.path.abspath(sal))==os.path.normcase(os.path.abspath(ruta)):sal=os.path.join(d,base+"_jmg."+cont)
        if self.var_dup.get()=="rename" and not probar:
            n=1;b0,ext=os.path.splitext(sal)
            while os.path.exists(sal) or os.path.normcase(sal) in usados:sal=f"{b0}_{n}{ext}";n+=1
        if cont in ("mp4","mov"):
            im=[s for s in j["s"] if s["incl"] and s["fmt"] in ("hdmv_pgs_subtitle","dvd_subtitle","dvb_subtitle","pgssub")]
            if im:av.append(V_(f"{len(im)} subtítulo(s) de imagen no caben en {cont.upper()}: se quedan fuera (usa MKV para llevarlos).",f"{len(im)} image subtitle(s) do not fit in {cont.upper()}: they are left out (use MKV to keep them)."))
            if any(a["incl"] and a["cod"]=="copy" and str(a["codec_in"]).startswith("pcm") for a in j["a"]):av.append(V_("El audio PCM pasa a FLAC (no cabe tal cual).","PCM audio becomes FLAC (it does not fit as it is)."))
        return sal,av
    def _portadas_tmp(self,ruta):
        """portadas del original para el MKV: se sacan a la carpeta temporal y se adjuntan (si se copian como pista, salen como video)"""
        out=[]
        for p in _portadas(self.info[ruta]):
            ext="jpg" if "jpeg" in str(p.get("codec_name","")) else "png"
            out.append((p,os.path.join(self._tmp,f"cover_{abs(hash(ruta))}_{p['index']}.{ext}"),ext,"image/jpeg" if ext=="jpg" else "image/png"))
        return out
    def _comando(self,ruta,j,sal,pase=None,log2=None,portadas=True,tramo=None,parte=False,previos=None):
        """comando de FFmpeg de un trabajo (tramo = (ini, fin) en segundos; None = entero; parte = trozo que luego se une:
        sin portada ni adjuntos, que se ponen al unir)"""
        inf=self.info[ruta];vs=_vstream(inf);cont=self._cont(j,ruta)
        ini,fin=tramo if tramo else (0.0,0.0)
        # con el video recomprimido: salto rapido hasta 5 s antes y corte exacto despues (las pistas copiadas empiezan justo ahi);
        # con el video en Passthrough, el corte cae en el fotograma clave (todas las pistas desde el mismo sitio)
        ss0=max(0.0,ini-5.0) if (ini>0 and j["v"]["codec"]!="copy") else ini;ss1=ini-ss0
        seek=["-ss",f"{ss0:.3f}"] if ss0>0 else []
        dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        c=[FFMPEG,"-hide_banner","-nostdin","-y","-v","error","-progress","pipe:1","-nostats"]+dvd+seek+(["-core_only","1"] if self._nucleo_dts(j) else [])+["-i",inf.get("entrada",ruta)]
        ent={None:0};n_in=1;burn=None   # entradas: 0 = el video; luego los archivos de las pistas de audio añadidas, subtitulos externos y portada
        aent={(None,1.0):0};sent={}   # audio: (archivo, velocidad) -> entrada; subtitulos: n.º -> "entrada:pista"
        if pase!=1:
            for t in j["a"]:
                k_=(t["ext"] or None,_fps_f(t))
                if t["incl"] and k_ not in aent:   # con cambio de framerate, la pista se lee desde su segundo (el del video x la velocidad)
                    aent[k_]=n_in;c+=(["-ss",f"{ss0*k_[1]:.3f}"] if ss0>0 else [])+(dvd if not t["ext"] else [])+["-i",t["ext"] or inf.get("entrada",ruta)];n_in+=1
            for q,s in enumerate(j["s"]):
                quema=bool(s.get("burn")) and j["v"]["codec"]!="copy"   # (JMG, 11-11) grabado en la imagen: también en AVI y WebM
                if not s["incl"] or ((cont=="avi" or (cont=="webm" and s["fmt"] in ("hdmv_pgs_subtitle","dvd_subtitle","dvb_subtitle","pgssub"))) and not quema):continue   # AVI no lleva subtitulos; WebM, solo de texto
                sc,so=_s_esc(s)
                if s["ext"] and ss0<=0 and sc==1.0 and not so and not quema:
                    if s["ext"] not in ent:ent[s["ext"]]=n_in;c+=["-i",s["ext"]];n_in+=1
                    sent[q]=f"{ent[s['ext']]}:0"
                elif s["ext"] or sc!=1.0 or so or quema:   # (el grabado, siempre desde un temporal ya en su sitio)
                    # el subtitulo se prepara antes en un archivo aparte, ya en su sitio: velocidad (-itsscale), delay (-itsoffset, que
                    # FFmpeg aplica antes de la escala) y corte con -ss de SALIDA (el -ss de entrada no sirve en los SRT: FFmpeg lo ignora
                    # y luego pone el primero en el 0)
                    tmp=f"{log2 or os.path.join(self._tmp,'vista')}_s{q}.mks"
                    pc=[FFMPEG,"-hide_banner","-nostdin","-y","-v","error"]+(["-itsscale",f"{sc:.10f}"] if sc!=1.0 else [])+(["-itsoffset",f"{so/sc:.4f}"] if so else [])
                    pc+=(dvd if not s["ext"] else [])+["-i",s["ext"] or inf.get("entrada",ruta)]+(["-ss",f"{ss0:.3f}"] if ss0>0 else [])
                    pc+=["-map",f"0:{0 if s['ext'] else s['idx']}","-c:s","copy","-f","matroska",tmp]
                    if previos is not None:previos.append(pc)
                    sent[q]=f"{n_in}:0";c+=["-i",tmp];n_in+=1
                    if quema:burn=(q,tmp,s["fmt"] in ("hdmv_pgs_subtitle","dvd_subtitle","dvb_subtitle","pgssub"))
        pt=j.get("portada")
        cov_in=None
        if pase!=1 and pt and cont in ("mp4","mov") and self.var_adj.get() and os.path.isfile(pt):cov_in=n_in;c+=["-i",pt];n_in+=1
        ins=len(c)   # (JMG, 8-11) aquí se meten los AC3 que hace Aften (las entradas van antes de las opciones de salida)
        if ss1>0:c+=["-ss",f"{ss1:.3f}"]
        if fin>ini:c+=["-t",f"{fin-ini:.3f}"]
        vf=self._vfiltros(ruta,j);vfc=None
        if burn and not burn[2]:   # (JMG, 11-11) de texto (SRT, ASS): se dibuja sobre la imagen final (ya recortada o escalada)
            vf=vf+["subtitles=filename='"+burn[1].replace("\\","/").replace(":","\\:").replace("'","\\'")+"'"]
        if burn and burn[2]:   # de imagen (PGS, DVD): encima del fotograma original y después los ajustes de imagen
            vfc=f"[0:{vs['index']}][{sent[burn[0]]}]overlay=(W-w)/2:(H-h):eof_action=pass"+(","+",".join(vf) if vf else "")+"[vquema]";c+=["-map","[vquema]"]
        else:
            c+=["-map",f"0:{vs['index']}"]
            if vf and j["v"]["codec"]!="copy":c+=["-filter:v:0",",".join(vf)]
        c+=self._venc(ruta,j,pase,log2)
        if cont=="avi" and j["v"]["codec"]=="copy" and str((vs or {}).get("codec_name",""))=="h264":c+=["-bsf:v","h264_mp4toannexb"]   # el H.264 de MKV/MP4 en AVI
        if pase==1:
            nul="NUL" if sys.platform=="win32" else "/dev/null";c+=["-an","-sn","-dn","-map_chapters","-1","-f","null",nul]
            if self._enc(j["v"]) in ("libvpx-vp9","libvvenc"):   # (JMG, 21-11) su 1.ª pasada no escribe nada: FFmpeg no da el tiempo y la barra
                # no se movía. Una salida extra diminuta (1 fotograma por segundo, 16x16, sin codificar, mismo corte) se lo da
                c+=(["-ss",f"{ss1:.3f}"] if ss1>0 else [])+(["-t",f"{fin-ini:.3f}"] if fin>ini else [])+["-map",f"0:{vs['index']}","-vf","fps=1,scale=16:16","-c:v","rawvideo","-an","-sn","-dn","-map_chapters","-1","-f","null",nul]
            return c
        if self.var_adj.get() and cont in ("mp4","mov") and not parte:   # MP4/MOV: la portada va como imagen adjunta (covr)
            if cov_in is not None:c+=["-map",f"{cov_in}:0","-c:v:1","copy","-disposition:v:1","attached_pic"]
            elif pt is None and portadas:
                for k,p in enumerate(_portadas(inf),start=1):c+=["-map",f"0:{p['index']}",f"-c:v:{k}","copy",f"-disposition:v:{k}","attached_pic"]
        fc=[];K=0;prim=[];resto=[]   # como en Jmg AudioProcesador: las procesadas las primeras (la 1.ª por defecto), luego las demas y las originales
        for t in j["a"]:
            if not t["incl"]:continue
            proc=_a_proc(t)   # (JMG, 8-11) procesada = con efectos; otro códec, bitrate, delay, tramos o framerate: se recomprime en su sitio
            cod=t["cod"];src=f"{aent[(t['ext'] or None,_fps_f(t))]}:{t['idx']}"
            if cod=="copy" and cont in ("mp4","mov") and str(t["codec_in"]).startswith("pcm"):cod="flac"
            if cod=="truehd" and cont!="mkv":cod="eac3"
            if cod=="copy" and self._a_recodificar(t):cod=ACOD_DE_ORIGEN.get(t["codec_in"],"eac3")
            if cont=="avi" and not self._avi_audio_ok(dict(t,cod=cod)):cod="ac3"   # AVI: AC3, MP3 o DTS
            if cont=="webm" and not self._webm_audio_ok(dict(t,cod=cod)):cod="opus"   # WebM: Opus
            if proc:
                prim.append(("proc",t,cod,src))
                o_src=aent.get((t["ext"] or None,1.0))
                if cont=="webm" and not self._webm_audio_ok(dict(t,cod="copy")):o_src=None   # la original no cabe en WebM
                if t.get("conservar",True) and o_src is not None and not _fps_q(t):resto.append(("orig",t,None,f"{o_src}:{t['idx']}"))
            else:resto.append(("tal",t,cod,src))
        for n_,(tipo,t,cod,src) in enumerate(prim+resto):
            if tipo=="orig":   # la original, tal cual (o al codec que admite el contenedor)
                oc="copy"
                if cont in ("mp4","mov") and str(t["codec_in"]).startswith("pcm"):oc="flac"
                if cont=="avi" and not self._avi_audio_ok(dict(t,cod="copy")):oc="ac3"
                if cont!="mkv" and t["codec_in"]=="truehd":oc="eac3"
                c+=["-map",src,f"-c:a:{K}",oc]+([f"-b:a:{K}","640k"] if oc in ("eac3","ac3") else [])
                tit=t["tit"];dflt=False
            else:
                af_=self._aften_previo(t,cod,ss0,ss1,ini,fin,dvd,inf,ruta,log2,K,previos)   # (JMG, 8-11) AC3 hecho por Aften antes
                g=self._a_grafo(t,f"[{src}]",f"[ao{K}]",post=self._a_post(dict(t,cod=cod)),off=ss0) if (cod!="copy" and af_ is None) else None
                if af_ is not None:
                    _oa=max(0.0,float(t.get("start") or 0)-_num((vs or {}).get("start_time"))) if (ss0==0 and not t["ext"]) else 0.0   # (JMG, 17-11) el audio que empieza después que el vídeo
                    o_=(["-itsoffset",f"{ss1+_oa:.3f}"] if ss1+_oa>0.0005 else [])+["-i",af_];c[ins:ins]=o_;ins+=len(o_);c+=["-map",f"{n_in}:0"];n_in+=1
                elif g:fc.append(g);c+=["-map",f"[ao{K}]"]
                else:c+=["-map",src]
                if cod=="copy" or af_ is not None:c+=[f"-c:a:{K}","copy"]
                else:
                    c+=[f"-c:a:{K}",{"dts":"dca","opus":"libopus","mp3":"libmp3lame"}.get(cod,cod)]
                    kb=t["kbps"] if (t["kbps"] in AKBPS.get(cod,()) or (cod=="eac3" and _eac3_ok(t["kbps"],t["nch"]))) else (t.get("bits_in",24) if cod in ABITS else _akbps_def(cod,t["nch"]))   # el de su codec
                    if cod=="flac":c+=[f"-sample_fmt:a:{K}","s32" if kb>16 else "s16"]+([f"-bits_per_raw_sample:a:{K}","24"] if kb>16 else [])
                    elif cod=="truehd":c+=[f"-sample_fmt:a:{K}","s32p" if kb>16 else "s16p"]
                    else:c+=[f"-b:a:{K}",f"{kb}k"]
                    if cod=="opus" and t["nch"]>2:c+=[f"-mapping_family:a:{K}","1"]
                    if cod=="mp3" and t["nch"]>2:c+=[f"-ac:a:{K}","2"]   # el MP3 solo es estéreo: el 5.1 se baja a estéreo
                    if cod in OPC:c+=self._opc_a_args(cod,self._opc_norm(cod,(t.get("opc") or {}).get(cod)),f":a:{K}")   # (JMG, 12-11) opciones avanzadas
                tit=(t.get("tit_proc") or "Jmg procesada") if tipo=="proc" else t["tit"]
                dflt=(n_==0) if prim else bool(t["def"])   # con procesadas, la 1.ª va por defecto; si no, la que marque quien codifica
            c+=[f"-metadata:s:a:{K}","language="+(t["lang"] or "und"),f"-metadata:s:a:{K}","title="+tit,f"-disposition:a:{K}","default" if dflt else "0"]
            K+=1
        if cont=="mkv":   # (JMG, 15-11) el núcleo DTS de las pistas DTS-HD marcadas, aparte y sin recomprimir (detrás de las demás)
            for t in j["a"]:
                o_src=aent.get((t["ext"] or None,1.0))
                if t["incl"] and t.get("nucleo") and o_src is not None and not _fps_q(t) and not t.get("delay") and not t.get("tramos"):
                    c+=["-map",f"{o_src}:{t['idx']}",f"-c:a:{K}","copy",f"-bsf:a:{K}","dca_core",f"-metadata:s:a:{K}","language="+(t["lang"] or "und"),
                        f"-metadata:s:a:{K}","title="+((t["tit"]+" · ") if t["tit"] else "")+self._vt("DTS (núcleo)","DTS (core)"),f"-disposition:a:{K}","0"];K+=1
        if fc or vfc:c+=["-filter_complex",";".join(([vfc] if vfc else [])+fc)]
        # (JMG, 10-11) con más entradas que la película (los AC3 de Aften, pistas añadidas...), sus subtítulos se leen de otra
        # apertura del mismo archivo: si no, FFmpeg deja el principio de esas pistas de audio cientos de segundos más adelante en el
        # MKV (por los subtítulos, que van a saltos) y VLC se queda sin audio y corre el vídeo. Medido: 0,3 s y la misma memoria
        sub_in=None
        if n_in>1 and any(s["incl"] and not s["ext"] and q not in sent for q,s in enumerate(j["s"])):
            o_=dvd+seek+["-i",inf.get("entrada",ruta)];c[ins:ins]=o_;ins+=len(o_);sub_in=n_in;n_in+=1
        S=0
        for q,s in enumerate(j["s"]):
            if not s["incl"] or cont=="avi" or (burn and burn[0]==q):continue   # (el grabado ya va en la imagen)
            imagen=s["fmt"] in ("hdmv_pgs_subtitle","dvd_subtitle","dvb_subtitle","pgssub")
            if cont!="mkv" and imagen:continue
            c+=["-map",sent.get(q) or f"{sub_in if sub_in is not None else 0}:{s['idx']}",f"-c:s:{S}",{"mkv":"copy","webm":"webvtt"}.get(cont,"mov_text")]
            d="+".join(x for x,on in (("default",s["def"]),("forced",s["forz"])) if on) or "0"
            c+=[f"-metadata:s:s:{S}","language="+(s["lang"] or "und"),f"-metadata:s:s:{S}","title="+s["tit"],f"-disposition:s:{S}",d]
            S+=1
        c+=["-map_chapters","0" if (self.var_caps.get() and not tramo and cont!="avi") else "-1","-map_metadata","0" if self.var_meta.get() else "-1"]
        if cont=="mkv" and self.var_adj.get() and not parte:
            c+=["-map","0:t?","-c:t","copy"]
            na=sum(1 for s in inf.get("streams",[]) if s.get("codec_type")=="attachment")
            if pt:
                if os.path.isfile(pt):
                    e_=os.path.splitext(pt)[1].lower().lstrip(".").replace("jpeg","jpg")
                    c+=["-attach",pt,f"-metadata:s:t:{na}","mimetype="+("image/png" if e_=="png" else "image/jpeg"),f"-metadata:s:t:{na}",f"filename=cover.{e_}"]
            elif pt is None and portadas:
                for k,(p,f,ext,mime) in enumerate(self._portadas_tmp(ruta)):
                    c+=["-attach",f,f"-metadata:s:t:{na+k}","mimetype="+mime,f"-metadata:s:t:{na+k}",f"filename=cover{'' if k==0 else k+1}.{ext}"]
        if cont in ("mp4","mov"):c+=["-movflags","+faststart"]
        return c+["-strict","-2","-max_muxing_queue_size","4096",sal]
    def _ver_cmd(self):
        j=self._job()
        if not j:return
        sal,_=self._salida(self.actual,j);self.nb.select(self._tab_log_w)
        for w in self._pasos(self.actual,j,sal,"pase",0)["pasos"]:
            x=w[0];self._log("\n"+(subprocess.list2cmdline(x["ff"])+" | "+subprocess.list2cmdline(x["af"]) if isinstance(x,dict) else subprocess.list2cmdline(x)))
    def _pasos(self,ruta,j,sal,lgn,i,portadas=True):
        """lo que hay que lanzar para un trabajo: [(comando, segundos)] y, si hay varios tramos, como se unen al final"""
        n=self._pasadas(j);lg=os.path.join(self._tmp,lgn);cont=self._cont(j,ruta)
        tr=self._tramos_job(j,ruta);out={"pasos":[],"concat":None}
        if len(tr)<=1:
            t0=tr[0] if tr else None;d=(t0[1]-t0[0]) if t0 else self._dur_trabajo(j,ruta)
            for p in ((1,2) if n==2 else (None,)):
                pv=[];c_=self._comando(ruta,j,sal,p,lg,portadas,t0,previos=pv);out["pasos"]+=[(x,d if isinstance(x,dict) else 1.0) for x in pv]+[(c_,d)]
            return out
        partes=[]
        for k,(a,b) in enumerate(tr):
            pf=os.path.join(self._tmp,f"parte{i}_{k}.{cont}");partes.append(pf)
            for p in ((1,2) if n==2 else (None,)):
                pv=[];c_=self._comando(ruta,j,pf,p,lg+f"_{k}",portadas,(a,b),parte=True,previos=pv);out["pasos"]+=[(x,(b-a) if isinstance(x,dict) else 1.0) for x in pv]+[(c_,b-a)]
        lista=os.path.join(self._tmp,f"partes{i}.txt");inf=self.info[ruta]
        fin=[FFMPEG,"-hide_banner","-nostdin","-y","-v","error","-progress","pipe:1","-nostats","-f","concat","-safe","0","-i",lista]
        mp=["-map","0","-c","copy","-map_chapters","-1"];pt=j.get("portada")
        if self.var_adj.get():   # portada y adjuntos (fuentes de los ASS) al unir: del original o la imagen elegida
            if cont=="mkv":
                if not inf.get("dvd"):fin+=["-i",inf.get("entrada",ruta)];mp+=["-map","1:t?"]
                na=0 if inf.get("dvd") else sum(1 for s in inf.get("streams",[]) if s.get("codec_type")=="attachment")
                if pt and os.path.isfile(pt):
                    e_=os.path.splitext(pt)[1].lower().lstrip(".").replace("jpeg","jpg")
                    mp+=["-attach",pt,f"-metadata:s:t:{na}","mimetype="+("image/png" if e_=="png" else "image/jpeg"),f"-metadata:s:t:{na}",f"filename=cover.{e_}"]
                elif pt is None and portadas:
                    for q,(p_,f_,ext_,mime) in enumerate(self._portadas_tmp(ruta)):
                        mp+=["-attach",f_,f"-metadata:s:t:{na+q}","mimetype="+mime,f"-metadata:s:t:{na+q}",f"filename=cover{'' if q==0 else q+1}.{ext_}"]
            elif cont in ("mp4","mov"):
                if pt and os.path.isfile(pt):fin+=["-i",pt];mp+=["-map","1:0","-c:v:1","copy","-disposition:v:1","attached_pic"]
                elif pt is None and portadas and _portadas(inf) and not inf.get("dvd"):
                    fin+=["-i",inf.get("entrada",ruta)];mp+=["-map",f"1:{_portadas(inf)[0]['index']}","-c:v:1","copy","-disposition:v:1","attached_pic"]
        fin+=mp
        if cont in ("mp4","mov"):fin+=["-movflags","+faststart"]
        out["concat"]={"lista":lista,"partes":partes,"durs":[b-a for a,b in tr],"cmd":fin+["-strict","-2",sal],"dur":sum(b-a for a,b in tr)}
        return out

    # ---------- procesar ----------
    def _conf(self):
        self._guardar_trabajo()
        cola=[f for f in self.files if f in self.jobs]
        if not cola:self._toast(T("info_tit"),self._vt("Agrega al menos un vídeo (selecciónalo y pulsa «Agregar»).","Add at least one video (select it and press «Add to queue»)."),seg=4);return
        mn,det=self._resumen(cola)
        if not self._confirm(self._vt("Confirmar procesado","Confirm processing"),mn,det):return
        if self.var_dup.get()=="sobre":
            ex=[self._salida(f,self.jobs[f])[0] for f in cola if os.path.exists(self._salida(f,self.jobs[f])[0])]
            if ex and not self._confirm(self._vt("Archivos existentes","Existing files"),self._vt("Se van a sobrescribir:\n","These will be overwritten:\n")+"\n".join(os.path.basename(x) for x in ex[:8])):return
        self._oir_parar()
        self.procesando=True;self._cancelar.clear()
        self.btn_c.state(["!disabled"]);self._refrescar_estado();self._estado_general()
        self._bp_poner(True)   # (JMG, 14-11) codificando: solo las pestañas y «Cancelar»
        # todo se prepara aqui, en el hilo de la ventana: el hilo de trabajo no lee nada de la pantalla
        plan=[];usados=set()
        for i,ruta in enumerate(cola):
            j=self.jobs[ruta];sal,av=self._salida(ruta,j,usados=usados);usados.add(os.path.normcase(sal))
            w=self._pasos(ruta,j,sal,f"pase{i}",i)
            w.update({"ruta":ruta,"fps":_fps(_vstream(self.info[ruta]) or {}),"trozo":bool(self._tramos_job(j,ruta)),"sal":sal,"av":av,"nom":self._nombre(ruta),"sin_portada":self._pasos(ruta,j,sal,f"pase{i}",i,portadas=False),
                      "pre":[[FFMPEG,"-hide_banner","-v","error","-y","-i",self.info[ruta].get("entrada",ruta),"-map",f"0:{p['index']}","-c","copy",f]
                             for p,f,_,_ in (self._portadas_tmp(ruta) if self._cont(j,ruta)=="mkv" and self.var_adj.get() and j.get("portada") is None else [])]})
            plan.append(w)
        self.prog.configure(value=0)
        threading.Thread(target=self._lote,args=(plan,),daemon=True).start()
    def _cancel(self):
        if getattr(self,"_pausa_on",False):self._pausa_poner(False)   # (JMG, 13-11) en pausa: primero sigue (y así nada se queda parado)
        self._cancelar.set()
        p=self._proc
        if p and p.poll() is None:
            try:p.kill()
            except Exception:pass
        self._st(self._vt("Cancelando...","Cancelling..."))
    def _peso_paso(self,cmd,d):
        """(JMG, 13-11) lo que cuesta cada paso, para que la barra vaya al ritmo real: codificar el vídeo pesa su duración; la primera de
        dos pasadas, menos; el audio (Aften) y copiar sin recomprimir (o unir tramos), casi nada"""
        if isinstance(cmd,dict):return 0.05*d
        try:
            c=[str(x) for x in cmd]
            cv=[c[i+1] for i in range(len(c)-1) if c[i] in ("-c:v","-vcodec","-c:v:0")]
            if not cv or all(x=="copy" for x in cv):return 0.08*d
            if "-pass" in c and c[c.index("-pass")+1]=="1":return 0.45*d
        except Exception:pass
        return 1.0*d
    def _ejecutar(self,cmd,dur,base,peso,txt,fps=0.0):
        """lanza FFmpeg y va moviendo la barra; devuelve (ok, ultimas lineas de error). (JMG, 23-11) Con fps (el del vídeo), la barra va por
        los fotogramas ya escritos: el out_time de FFmpeg es el de la pista que más avanza (una pista hecha con Aften se lee enseguida y
        VVC va despacio: la barra se quedaba en el 31 % y el «quedan» no se movía)"""
        self._ls("$ "+subprocess.list2cmdline(cmd))
        err=[]
        try:self._proc=p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="ignore",creationflags=CNW)
        except Exception as e:return False,[str(e)]
        def lee_err():
            for l in p.stderr:
                l=l.rstrip()
                if l and not l.startswith("Svt[info]"):err.append(l);del err[:-40]
        th=threading.Thread(target=lee_err,daemon=True);th.start()
        t0=time.time();hay_t=False;nfr=0;frm=0.0
        for l in p.stdout:
            if l.startswith("progress=end"):   # (23-11) acabado: su parte entera (fotogramas / fps no llega justo a la duración)
                self._set_prog(base+peso);continue
            if l.startswith("frame="):   # (JMG, 23-11) fotogramas de vídeo escritos (llega antes que el out_time)
                try:nfr=int(l.split("=")[1])
                except ValueError:pass
                continue
            if l.startswith("progress=") and not hay_t:   # (JMG, 21-11) mientras FFmpeg no da el tiempo, al menos el paso y lo que lleva
                el=time.time()-t0-self._pausa_desde(t0)
                self._st(f"{txt} · {base:.0f} % · "+self._vt(f"lleva {_hms(el).split('.')[0]}",f"{_hms(el).split('.')[0]} elapsed"))
            if l.startswith("out_time_us=") or l.startswith("out_time_ms="):
                try:s=int(l.split("=")[1])/1e6
                except ValueError:continue
                if fps>0 and nfr>0:s=min(s,nfr/fps)   # (JMG, 23-11) lo que va de vídeo, no lo que va de la pista más adelantada
                hay_t=True
                fr=max(frm,max(0.0,min(1.0,s/dur)) if dur>0 else 0.0);frm=fr   # (23-11) dentro del paso, nunca hacia atrás
                self._set_prog(base+peso*fr)
                el=time.time()-t0-self._pausa_desde(t0);rest=el*(1-fr)/fr if fr>0.02 else 0
                self._st(f"{txt} · {base+peso*fr:.0f} %"+(self._vt(f" · quedan {_hms(rest).split('.')[0]}",f" · {_hms(rest).split('.')[0]} left") if rest else ""))
        p.wait();th.join(timeout=2);self._proc=None
        return p.returncode==0,err
    def _lote(self,plan):
        """hilo de trabajo: solo ejecuta lo que _conf preparo (no lee nada de la ventana)"""
        V_=self._vt;ok=0;mal=0;hechos=[];t0=time.time();N=len(plan);self._lote_lista=[]
        for i,w in enumerate(plan):
            if self._cancelar.is_set():break
            sal=w["sal"]
            for a in w["av"]:self._ls("[!] "+a)
            try:os.makedirs(os.path.dirname(sal),exist_ok=True)
            except OSError:pass
            self._ls(f"\n[{i+1}/{N}] {w['nom']} -> {sal}")
            for pc in w["pre"]:   # portadas a la carpeta temporal; si alguna falla, el video sale sin portada
                try:ok_=rh(pc,timeout=60).returncode==0 and os.path.isfile(pc[-1])
                except Exception:ok_=False
                if not ok_:
                    w["pasos"]=w["sin_portada"]["pasos"];w["concat"]=w["sin_portada"]["concat"]
                    self._ls("[!] "+V_("No se ha podido copiar la portada: sale sin ella.","Could not copy the cover: it is saved without it."));break
            pasos=list(w["pasos"]);cc=w["concat"]
            if cc:pasos.append((cc["cmd"],cc["dur"]))
            pes=[self._peso_paso(c_,d_) for c_,d_ in pasos];tot=sum(pes) or 1.0;hecho=0.0;bien=True   # (JMG, 13-11) cada paso pesa lo que cuesta
            npar=len(cc["partes"]) if cc else 0
            for k,(cmd,d) in enumerate(pasos):
                if cc and k==len(pasos)-1:
                    with open(cc["lista"],"w",encoding="utf-8") as fl:
                        for pf,dt in zip(cc["partes"],cc["durs"]):fl.write("file '"+pf.replace("\\","/").replace("'","'\\''")+f"'\noutpoint {dt:.3f}\n")   # cada trozo acaba en su sitio (los subtitulos no lo alargan)
                    txt=V_(f"Vídeo {i+1}/{N} · uniendo {npar} tramos",f"Video {i+1}/{N} · joining {npar} parts")
                else:
                    txt=V_(f"Vídeo {i+1}/{N}",f"Video {i+1}/{N}")+(V_(f" · paso {k+1}/{len(pasos)}",f" · step {k+1}/{len(pasos)}") if len(pasos)>1 else "")+f" · {w['nom']}"
                r,err=(self._aften_tubo(cmd,d,100.0*hecho/tot,100.0*pes[k]/tot,txt) if isinstance(cmd,dict) else self._ejecutar(cmd,d,100.0*hecho/tot,100.0*pes[k]/tot,txt,fps=w.get("fps",0.0)));hecho+=pes[k]   # (JMG, 13-11) la barra es la de este vídeo: la misma cifra que el texto
                if not r:
                    bien=False
                    if not self._cancelar.is_set():self._ls("[ERROR] "+"\n".join(err[-12:]))
                    break
            for f_ in os.listdir(self._tmp):
                if f_.startswith(f"pase{i}") or f_.startswith(f"parte{i}_") or f_==f"partes{i}.txt":
                    try:os.remove(os.path.join(self._tmp,f_))
                    except OSError:pass
            if bien and os.path.isfile(sal):
                ok+=1;hechos.append(sal);self._ls("[OK] "+sal)
                if w.get("trozo"):self._lote_lista.append(sal)   # (JMG, 8-11) el vídeo troceado entra en la lista
            else:
                mal+=1
                try:
                    if os.path.isfile(sal):os.remove(sal)
                except OSError:pass
        self._ui(self._fin_lote,ok,mal,hechos,time.time()-t0)
    def _fin_lote(self,ok,mal,hechos,seg):
        V_=self._vt;self.procesando=False;self._bp_poner(False);self.btn_c.state(["disabled"]);self._refrescar_estado();self._estado_general()
        canc=self._cancelar.is_set()
        self.prog.configure(value=0 if canc else 100);self.root.after(1500,lambda:self.prog.configure(value=0))
        self.var_progreso.set(V_(f"Terminado: {ok} bien, {mal} con error · {_hms(seg).split('.')[0]}",f"Done: {ok} OK, {mal} failed · {_hms(seg).split('.')[0]}"))
        if canc:self._toast(T("cancelado_tit"),V_("Proceso cancelado. Los archivos a medias se han borrado.","Process cancelled. Unfinished files have been deleted."),seg=5);return
        self._toast(T("info_tit") if not mal else T("warn_tit"),V_(f"{ok} vídeo(s) terminados"+(f", {mal} con error (mira Edit/Log)." if mal else "."),f"{ok} video(s) done"+(f", {mal} failed (see Edit/Log)." if mal else ".")),tipo="info" if not mal else "warning",seg=8)
        if getattr(self,"_lote_lista",None):self._addl(list(self._lote_lista))
        if self.var_abrir.get() and hechos and self.var_al_terminar.get()!="apagar":   # (JMG, 8-11) si se va a apagar el PC, no se abre nada
            for d in dict.fromkeys(os.path.dirname(h) for h in hechos):
                try:_abrir_externo(d)
                except Exception:pass
        a=self.var_al_terminar.get()
        if a=="salir":self.root.after(1500,lambda:self._on_close(forzar=True))
        elif a=="apagar":self._apagar()
        elif a=="suspender":self._suspender()   # (JMG, 15-11)
    def _apagar(self):
        V_=self._vt
        try:
            if sys.platform=="win32":rh(["shutdown","/s","/t","60"])
            else:rh(["shutdown","-h","+1"])
        except Exception as e:self._log(f"[!] {e}");return
        top=tk.Toplevel(self.root);top.title(V_("Apagado programado","Shutdown scheduled"));top.configure(bg=CF);top.attributes("-topmost",True)
        ttk.Label(top,text=V_("El PC se apagará en 1 minuto.","The PC will shut down in 1 minute."),font=("",11,"bold")).pack(padx=30,pady=(20,10))
        def no():
            try:rh(["shutdown","/a"] if sys.platform=="win32" else ["shutdown","-c"])
            except Exception:pass
            top.destroy()
        ttk.Button(top,text=V_("Cancelar el apagado","Cancel the shutdown"),command=no).pack(pady=(0,20))

    _SUSP_SEG=60
    def _suspender(self):
        """(JMG, 15-11) «Suspender el PC» al terminar: como el apagado, con 1 minuto para cancelarlo"""
        V_=self._vt
        top=tk.Toplevel(self.root);top.title(V_("Suspensión programada","Sleep scheduled"));top.configure(bg=CF);top.attributes("-topmost",True)
        ttk.Label(top,text=V_("El PC se suspenderá en 1 minuto.","The PC will go to sleep in 1 minute."),font=("",11,"bold")).pack(padx=30,pady=(20,10))
        def ya():
            try:top.destroy()
            except Exception:pass
            try:
                if sys.platform=="win32":
                    import ctypes;ctypes.windll.powrprof.SetSuspendState(False,False,False)
                else:subprocess.Popen(["systemctl","suspend"])
            except Exception as e:self._log(f"[!] {e}")
        aid=self.root.after(int(self._SUSP_SEG*1000),ya);self._susp_id=aid
        def no():
            try:self.root.after_cancel(aid)
            except Exception:pass
            try:top.destroy()
            except Exception:pass
        ttk.Button(top,text=V_("Cancelar la suspensión","Cancel sleep"),command=no).pack(pady=(0,20))
        top.protocol("WM_DELETE_WINDOW",no)
    # ---------- «Auto» ----------
    _AUTO_PROPIAS={"video":("codec","motor","modo","crf","kbps","pasadas2","vel","res","bits","deint"),"gama":("gama","gama_c"),
                   "vol":("fl","fr","fc","lfe","bl","br"),"suav":("suav",),"eq3":("eq_bass","eq_mids","eq_treble"),"db":("db",),"pres":("voz","amb","efc","sub")}
    def _auto(self,ef):
        j=self._job();V_=self._vt
        if not j:self._toast(T("info_tit"),V_("Primero agrega un vídeo.","First add a video."),seg=3);return
        if self._escaneando:return
        if ef=="img":
            if not self._escaneando:self._auto_img()
            return
        if ef=="video":
            v=j["v"];k=(self.actual,"v","video");h=self._auto_hecho.get(k)
            if h and all(v.get(x)==h.get(x) for x in self._AUTO_PROPIAS["video"]):
                v["codec"]="copy";self._auto_hecho.pop(k,None);self._pintar_trabajo()
                self._toast(T("info_tit"),V_("«Auto» otra vez: el vídeo vuelve a Passthrough (sin tocar).","«Auto» again: the video goes back to Passthrough (untouched)."),seg=4);return
            nv,txt=self._auto_video(self.actual)
            for x in ("lut","color","log","crop","crop_on","opc")+VIMG_KEYS:nv[x]=v.get(x,nv.get(x))   # la imagen y el color no son cosa del Auto del codec
            if nv["codec"]=="copy" and (nv.get("crop_on") or any(nv.get(x) for x in VIMG_KEYS)):nv["codec"]="hevc"
            nv["motor_pref"]=j["v"].get("motor_pref");j["v"]=nv;self._pintar_trabajo();self._estado_video()   # (JMG, 16-11) con el motor elegido
            self._auto_hecho[k]={x:j["v"][x] for x in self._AUTO_PROPIAS["video"]}
            self._medir_kbps_pedir(self.actual)   # (JMG, 17-11) el bitrate, según la película
            self._toast("Auto",txt,seg=6);return
        if self._a_i is None:self._toast(T("info_tit"),V_("Este vídeo no tiene pistas de audio.","This video has no audio tracks."),seg=3);return
        t=j["a"][self._a_i];k=(self.actual,t["idx"],ef);h=self._auto_hecho.get(k)
        if h and all(t["ef"].get(x,0)==h.get(x,0) for x in self._AUTO_PROPIAS[ef]):
            for x in self._AUTO_PROPIAS[ef]:t["ef"][x]=0
            self._auto_hecho.pop(k,None);self._a_cargar();self._cambio_a()
            self._toast(T("info_tit"),V_("«Auto» otra vez: se quita lo que puso y vuelve a 0.","«Auto» again: what it set is removed and it goes back to 0."),seg=4);return
        self._escaneando=True
        for b in self._auto_bts.values():b.state(["disabled"])
        self._st(V_("Midiendo la pista...","Measuring the track..."))
        ruta=self.actual
        def hilo():
            try:aj,txt=self._auto_calc(ruta,t,ef)
            except Exception as e:aj,txt=None,str(e)
            self._ui(self._auto_fin,ruta,t,ef,aj,txt)
        threading.Thread(target=hilo,daemon=True).start()
    def _auto_fin(self,ruta,t,ef,aj,txt):
        self._escaneando=False;self._st("")
        for b in self._auto_bts.values():b.state(["!disabled"])
        if aj is None:self._toast(T("warn_tit"),txt,tipo="warning",seg=6);return
        t["ef"].update(aj);self._auto_hecho[(ruta,t["idx"],ef)]={x:t["ef"].get(x,0) for x in self._AUTO_PROPIAS[ef]}
        if ruta==self.actual:self._a_cargar();self._cambio_a()
        self._toast("Auto",txt,seg=7)
    def _muestra(self,ruta,t):
        """muestra de la pista (12 trozos de 10 s repartidos por la pelicula), WAV en la carpeta temporal"""
        k=(t["ext"] or ruta,t["idx"])
        if k in self._muestras and os.path.isfile(self._muestras[k]):return self._muestras[k]
        inf=self._ext_info.get(t["ext"],{}) if t["ext"] else self.info[ruta];d=_dur(inf);ent=t["ext"] or inf.get("entrada",ruta)
        dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        if d>=180:
            N=12;ps=[d*0.05+i*(d*0.9-10)/(N-1) for i in range(N)];c=[FFMPEG,"-hide_banner","-v","error","-y"]
            for p in ps:c+=dvd+["-ss",f"{p:.2f}","-t","10","-i",ent]
            c+=["-filter_complex","".join(f"[{i}:{t['idx']}]" for i in range(N))+f"concat=n={N}:v=0:a=1[o]","-map","[o]"]
        else:c=[FFMPEG,"-hide_banner","-v","error","-y"]+dvd+["-t","120","-i",ent,"-map",f"0:{t['idx']}"]
        out=os.path.join(self._tmp,f"m_{abs(hash(k))}.wav")
        r=rh(c+["-c:a","pcm_f32le",out],timeout=900)
        if r.returncode!=0 or not os.path.isfile(out):raise RuntimeError(self._vt("No se ha podido leer la pista: ","Could not read the track: ")+(r.stderr or "")[-300:])
        self._muestras[k]=out;return out
    def _db_medir(self,ruta,t):
        """(JMG, 8-11) graves de 63 Hz y 1 kHz de FL, FR y el subwoofer, medidos igual que Jmg AudioProcesador: 12 trozos de 20 s
        repartidos por la película y los mismos filtros de octava -> {canal: {63: dB, 1000: dB}}"""
        inf=self._ext_info.get(t["ext"],{}) if t["ext"] else self.info[ruta];d=_dur(inf);ent=t["ext"] or inf.get("entrada",ruta)
        dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        chans=[c for c in ("FL","FR","LFE") if c in (LAYCH.get(t["lay"]) or [])]
        if d<=1 or not chans:return {}
        n=12 if d>=300 else max(1,min(12,int(d//10)));L=min(20.0,d/n)
        pos=[max(0.0,(d-L)*(0.04+0.92*i/(n-1))) if n>1 else 0.0 for i in range(n)]
        c=[FFMPEG,"-hide_banner","-nostats"]
        for p in pos:c+=dvd+["-ss",f"{p:.3f}","-t",f"{L:.3f}","-i",ent]
        g="".join(f"[{i}:{t['idx']}]aresample=48000[s{i}];" for i in range(n))
        g+="".join(f"[s{i}]" for i in range(n))+f"concat=n={n}:v=0:a=1,asplit={len(chans)}"+"".join(f"[c{x}]" for x in chans)
        for x in chans:
            g+=f";[c{x}]pan=mono|c0={x},asplit=2[{x}63][{x}1000]"
            for f in (63,1000):
                lo,hi=f/2**0.5,f*2**0.5
                g+=(f";[{x}{f}]highpass=f={lo:.1f}:p=2,highpass=f={lo:.1f}:p=2,lowpass=f={hi:.1f}:p=2,lowpass=f={hi:.1f}:p=2,"
                    f"astats@{x}_{f}=metadata=0:measure_perchannel=none:measure_overall=RMS_level"+("[o]" if (x,f)==(chans[-1],1000) else ",anullsink"))
        r=rh(c+["-filter_complex",g,"-map","[o]","-f","null","-"],timeout=900)
        res={x:{} for x in chans}
        for l in (r.stderr or "").splitlines():
            m=re.match(r"\[astats@(\w+?)_(\d+) @[^\]]*\] RMS level dB: (-?[\d.]+|-inf)",l)
            if m and m.group(1) in res and m.group(3)!="-inf" and float(m.group(3))>-150:res[m.group(1)][int(m.group(2))]=float(m.group(3))
        return res
    def _medir(self,wav,t,ef):
        """volumen (I) y rango dinamico (LRA) de cada canal, y nivel de las bandas de octava de la voz y de la mezcla"""
        chans=LAYCH.get(t["lay"]) or ["FL","FR"][:t["nch"]]
        res={"I":{},"LRA":{},"b":{}}
        g=f"[0:a]channelsplit=channel_layout={t['lay']}"+"".join(f"[{c}]" for c in chans)+";"
        g+=";".join(f"[{c}]ebur128@{c}=framelog=quiet,anullsink" for c in chans[1:])+(";" if len(chans)>1 else "")+f"[{chans[0]}]ebur128@{chans[0]}=framelog=quiet[o]"
        if not LAYCH.get(t["lay"]):g=f"[0:a]ebur128@FL=framelog=quiet[o]";chans=["FL"]
        r=rh([FFMPEG,"-hide_banner","-nostats","-i",wav,"-filter_complex",g,"-map","[o]","-f","null","-"],timeout=600)
        cur=None
        for l in (r.stderr or "").splitlines():
            m=re.match(r"\[ebur128@(\w+) @",l)
            if m:cur=m.group(1);continue
            m=re.match(r"\s+(I|LRA):\s+(-?[\d.]+)",l)
            if m and cur:res[m.group(1)][cur]=float(m.group(2))
        grupos=[]
        if ef in ("suav","eq3","db"):
            if ef=="suav":src=["FC"] if "FC" in chans else [c for c in chans if c!="LFE"]
            elif ef=="db":src=[c for c in ("FL","FR") if c in chans] or [c for c in chans if c!="LFE"]
            else:src=[c for c in chans if c!="LFE"]
            grupos.append(("b",src))
        if ef=="pres":
            grupos+=[(k_,[c for c in s_ if c in chans]) for k_,s_ in (("b",("FL","FR")),("bc",("FC",)))]
        for clave,src in grupos:
            if not src:continue
            mix="+".join(src) if LAYCH.get(t["lay"]) else "c0"
            fs=(125,500,1000,2000,4000,8000)
            g=f"[0:a]pan=mono|c0={mix},asplit={len(fs)}"+"".join(f"[b{f}]" for f in fs)+";"
            g+=";".join(f"[b{f}]bandpass=f={f}:width_type=o:width=1,astats@b{f}=metadata=0:measure_perchannel=none:measure_overall=RMS_level"+(",anullsink" if i_ else "[o]") for i_,f in enumerate(fs))
            r=rh([FFMPEG,"-hide_banner","-nostats","-i",wav,"-filter_complex",g,"-map","[o]","-f","null","-"],timeout=600)
            res.setdefault(clave,{})
            for l in (r.stderr or "").splitlines():
                m=re.match(r"\[astats@b(\d+) @[^\]]*\] RMS level dB: (-?[\d.]+|-inf)",l)
                if m and m.group(2)!="-inf":res[clave][int(m.group(1))]=float(m.group(2))
        return res
    def _auto_calc(self,ruta,t,ef):
        """lo que pone cada «Auto» de audio (las mismas medidas y objetivos que Jmg AudioProcesador) -> (ajustes, texto)"""
        V_=self._vt;cl=lambda x,a,b:max(a,min(b,x));med=lambda a:sum(a)/len(a)
        if t["nch"]<1:return None,V_("pista sin canales.","track without channels.")
        crudo=self._muestra(ruta,t)
        if ef=="db" and "LFE" not in (LAYCH.get(t["lay"]) or []):return None,V_("esta pista no tiene subwoofer.","this track has no subwoofer.")
        g=self._a_grafo(dict(t,delay=0,tramos=None),"[0:a]","[o]",sin=ef)   # la muestra con los demas efectos de la pista ya puestos (sin la sincronizacion)
        wav=crudo
        if g:
            wav=os.path.join(self._tmp,f"p_{abs(hash((ruta,t['idx'],ef)))}.wav")
            r=rh([FFMPEG,"-hide_banner","-v","error","-y","-i",crudo,"-filter_complex",g,"-map","[o]","-c:a","pcm_f32le",wav],timeout=600)
            if r.returncode!=0:wav=crudo
        m=self._medir(wav,t,ef);I=m["I"];R=m["LRA"];B=m["b"]
        ok=lambda c:I.get(c,-99.0)>-60
        if ef=="gama":
            ft=[R[c] for c in ("FL","FR","BL","BR","SL","SR") if ok(c) and c in R];ce=R.get("FC") if ok("FC") else None
            if not ft and ce is None:return None,V_("la pista está casi en silencio.","the track is almost silent.")
            aj={"gama":0,"gama_c":0};lra=med(ft) if ft else ce
            if lra<15.5:aj["gama"]=-int(cl(round((17.0-lra)/3.0),1,2))
            elif lra>20.0:aj["gama"]=int(cl(round((lra-17.0)/3.0),1,3))
            if ce is not None:
                if ce<8.5:aj["gama_c"]=-1
                elif ce>20.0:aj["gama_c"]=int(cl(round((ce-17.0)/3.0),1,2))
            if not ft:aj["gama"]=0
            aj={k_:2*v_ for k_,v_ in aj.items()}   # (JMG, 9-11) el deslizador va de -10 a +10
            d=lambda x:(V_("gama dinámica ","dynamic range ")+str(-x)) if x<0 else ((V_("compresión ","compression ")+str(x)) if x>0 else V_("apagado","off"))
            txt=V_(f"Rango dinámico: delanteros/traseros {lra:.0f} LU","Dynamic range: fronts/surrounds {0:.0f} LU".format(lra))+(f" · {V_('central','center')} {ce:.0f} LU" if ce is not None else "")
            return aj,txt+"\n"+V_("Delanteros y traseros: ","Fronts and surrounds: ")+d(aj["gama"])+" · "+V_("Central: ","Center: ")+d(aj["gama_c"])
        if ef=="vol":
            if not ok("FC"):return None,V_("esta pista no tiene canal central: no hay con qué equilibrar.","this track has no center channel: nothing to balance against.")
            fc=I["FC"];obj={"FL":-3.0,"FR":-3.0,"BL":-7.0,"BR":-7.0,"SL":-7.0,"SR":-7.0,"LFE":-6.0};aj={}
            for c,o in obj.items():
                if ok(c):
                    lim=3 if c=="LFE" else 6
                    aj[SLIDER_CH[c]]=int(cl(round(o-(I[c]-fc)),-lim,lim))
            aj["fc"]=0
            return aj,V_("Equilibrio de cine (el central no se toca): ","Cinema balance (the center is not touched): ")+" · ".join(f"{k.upper()} {v:+d}" for k,v in aj.items() if k!="fc")
        if ef=="suav":
            a=[B[f] for f in (4000,8000) if f in B];b=[B[f] for f in (500,1000,2000) if f in B]
            if not a or not b:return None,V_("no se ha podido medir el tono.","could not measure the tone.")
            ex=med(a)-med(b)+18.0;n=int(cl(round((ex-2.0)/4.0),0,5))
            return {"suav":n},V_(f"Agudos {ex:+.0f} dB respecto a lo normal · intensidad {n}","Treble {0:+.0f} dB against normal · amount {1}".format(ex,n))
        if ef=="eq3":
            if not all(f in B for f in (125,1000,4000,8000)):return None,V_("no se ha podido medir el tono.","could not measure the tone.")
            dg=cl(0.5*(-2.0-(B[125]-B[1000])),-3.0,3.0)
            da=0.0 if t["ef"].get("suav") else cl(0.5*(-9.0-(med([B[4000],B[8000]])-B[1000])),-2.0,3.0)
            aj={"eq_bass":int(round(dg)),"eq_mids":0,"eq_treble":int(round(da))}
            return aj,V_("graves ","bass ")+f"{aj['eq_bass']:+d} · "+V_("medios ","mids ")+"0 · "+V_("agudos ","treble ")+f"{aj['eq_treble']:+d}"+(V_("\n(con Suavizado no se devuelven los agudos que quita)","\n(with Smoothing the treble it removes is not given back)") if t["ef"].get("suav") else "")
        if ef=="pres":   # las mismas cuentas que el «Auto» de Presencia de Jmg AudioProcesador
            fr=[I[c] for c in ("FL","FR") if ok(c)];tr=[I[c] for c in ("BL","BR","SL","SR") if ok(c)];fc=I["FC"] if ok("FC") else None
            if not fr and fc is None:return None,V_("la pista está casi en silencio.","the track is almost silent.")
            Bc=m.get("bc") or {};aj={}
            band=lambda D,fs:(med([D[f] for f in fs if f in D]) if any(f in D for f in fs) else None)
            if fc is not None and fr:aj["voz"]=_eff_inv(cl(2.0+cl((3.0-(fc-med(fr)))*0.25,-1.5,1.5),0.0,6.0),8,24)
            if fr:aj["amb"]=_eff_inv(cl((med(fr)-med(tr)-4.0)*0.25,-1.0,1.5) if tr else 0.0,7,14)
            a_=band(B,(4000,8000));b_=band(Bc,(4000,8000))
            if fr:aj["efc"]=_eff_inv(cl((-6.0-(a_-b_))*0.2,-1.0,1.5) if (a_ is not None and b_ is not None) else 0.0,7,14)
            if ok("LFE") and fc is not None:aj["sub"]=_eff_inv(cl(-6.0-(I["LFE"]-fc),-6.0,6.0),9,20)
            if not aj:return None,V_("no se aplica a esta pista.","it does not apply to this track.")
            return aj," · ".join(f"{n} {aj[k]:+d}" for k,n in (("voz",V_("Voz","Voice")),("amb",V_("Ambiente","Ambience")),("efc",V_("Efectos","Effects")),("sub","Subwoofer")) if k in aj)
        if ef=="db":   # (JMG, 8-11) el mismo criterio y la misma medida que Jmg AudioProcesador: altavoces flojos de graves o subwoofer flojo
            D=self._db_medir(ruta,t);fr=[D[c] for c in ("FL","FR") if 63 in D.get(c,{}) and 1000 in D.get(c,{})]
            if not fr:return None,V_("no se ha podido medir el tono.","could not measure the tone.")
            n,txt=_db_auto(med([x[63] for x in fr]),med([x[1000] for x in fr]),(D.get("LFE") or {}).get(63),3,V_)
            return {"db":n},(V_("intensidad ","amount ")+f"{n} · {DB_CORTE} Hz · " if n else "")+txt
        return None,"?"

    # ---------- Deshacer / Rehacer (las ultimas 5 acciones) ----------
    _UD_MAX=5
    def _ud_estado(self):
        import copy
        return {"files":list(self.files),"jobs":copy.deepcopy(self.jobs),"actual":self.actual,"sal":self._salida_cfg(),"fin":self.var_al_terminar.get()}
    @staticmethod
    def _ud_firma(e):return json.dumps({k:e[k] for k in ("files","jobs","sal")},sort_keys=True,default=str)
    def _ud_tick(self):
        """cada 300 ms: un cambio que lleva 0,6 s quieto cuenta como una accion (arrastrar un deslizador = una sola)"""
        try:
            if not (self.procesando or self._escaneando or self._cargando):self._ud_reg()
        except Exception as e:self._log(f"[UD] {e}")
        self._ud_botones()
        try:self.root.after(300,self._ud_tick)
        except Exception:pass
    def _ud_reg(self,ya=False):
        self._guardar_trabajo()
        e=self._ud_estado();f=self._ud_firma(e)
        if self._ud_act is None:self._ud_act=(e,f);return
        if f==self._ud_act[1]:self._ud_pend=None;return
        if ya or (self._ud_pend and self._ud_pend[0]==f and time.time()-self._ud_pend[1]>=0.6):
            self._ud_pila.append(self._ud_act);del self._ud_pila[:-self._UD_MAX]
            self._ud_re=[];self._ud_act=(e,f);self._ud_pend=None
        elif not self._ud_pend or self._ud_pend[0]!=f:self._ud_pend=(f,time.time())
    def _ud_botones(self):
        if getattr(self,"_bloq_n",0):return
        try:
            hay=bool(self._ud_pila) or bool(self._ud_pend)
            self.btn_ud.state(["!disabled"] if hay and not self.procesando else ["disabled"])
            self.btn_ur.state(["!disabled"] if self._ud_re and not self.procesando else ["disabled"])
        except Exception:pass
    def _ud_tecla(self,e,sen):
        if getattr(self,"_bp_prev",None) is not None:return "break"   # (JMG, 14-11) codificando
        if isinstance(e.widget,(tk.Entry,ttk.Entry,ttk.Combobox)):return   # en una casilla de texto, Ctrl+Z es de la casilla
        self._ud_mover(sen)
    def _ud_mover(self,sen):
        if self.procesando or self._escaneando:return
        if self._ud_pend:self._ud_reg(ya=True)
        de,a=(self._ud_pila,self._ud_re) if sen<0 else (self._ud_re,self._ud_pila)
        if not de:return
        a.append(self._ud_act);self._ud_act=de.pop();self._ud_poner(self._ud_act[0]);self._ud_botones()
    def _ud_poner(self,e):
        import copy
        self._cargando=True
        try:
            self.files=list(e["files"]);self.jobs=copy.deepcopy(e["jobs"])
            self.actual=e["actual"] if e["actual"] in self.jobs else next((f for f in self.files if f in self.jobs),None)
            s=e["sal"]
            for k,var in (("cont",self.var_cont),("dest_modo",self.var_dest_modo),("dest",self.var_dest),("sufijo",self.var_sufijo),("dup",self.var_dup),("caps",self.var_caps),("meta",self.var_meta),("adj",self.var_adj),("abrir",self.var_abrir)):var.set(s[k])
        finally:self._cargando=False
        falta=[f for f in self.files if f not in self.info]
        self._pintar_lista();self._pintar_trabajo();self._sarch();self._refrescar_estado()
        # al pintarlo, el programa puede completar algun dato (p. ej. el bitrate de una pista): eso no es una accion nueva
        self._guardar_trabajo();e2=self._ud_estado();self._ud_act=(e2,self._ud_firma(e2));self._ud_pend=None
        if falta:
            def hilo():
                for r in falta:self._ui(self._probe_fin,r,self._probe(r))
            threading.Thread(target=hilo,daemon=True).start()

    # ---------- presets, configuración y cierre ----------
    def _gp(self):
        j=self._job()
        if not j:return
        f=filedialog.asksaveasfilename(title=T("guardar_p"),initialdir=os.path.join(_data_dir(),"presets"),defaultextension=".json",filetypes=[("Preset","*.json")])
        if not f:return
        self._guardar_trabajo()
        try:
            os.makedirs(os.path.dirname(f),exist_ok=True)
            with open(f,"w",encoding="utf-8") as fh:json.dump({"jve":1,"v":j["v"],"salida":self._salida_cfg()},fh,indent=2,ensure_ascii=False)
            self._toast(T("info_tit"),self._vt("Preset guardado.","Preset saved."),seg=3)
        except Exception as e:self._toast(T("error_tit"),str(e),tipo="error")
    def _mp(self):
        j=self._job()
        if not j:return
        try:os.makedirs(os.path.join(_data_dir(),"presets"),exist_ok=True)
        except OSError:pass
        f=filedialog.askopenfilename(title=T("cargar_p"),initialdir=os.path.join(_data_dir(),"presets"),filetypes=[("Preset","*.json")])
        if not f:return
        try:
            with open(f,encoding="utf-8") as fh:d=json.load(fh)
            j["v"].update({k:v for k,v in d.get("v",{}).items() if k in j["v"]})
            for k,var in (("cont",self.var_cont),("dest_modo",self.var_dest_modo),("dest",self.var_dest),("sufijo",self.var_sufijo),("dup",self.var_dup),("caps",self.var_caps),("meta",self.var_meta),("adj",self.var_adj),("abrir",self.var_abrir)):
                if k in d.get("salida",{}):var.set(d["salida"][k])
            self._pintar_trabajo()
        except Exception as e:self._toast(T("error_tit"),str(e),tipo="error")
    def _salida_cfg(self):
        return {"cont":self.var_cont.get(),"dest_modo":self.var_dest_modo.get(),"dest":self.var_dest.get(),"sufijo":self.var_sufijo.get(),"dup":self.var_dup.get(),
                "caps":bool(self.var_caps.get()),"meta":bool(self.var_meta.get()),"adj":bool(self.var_adj.get()),"abrir":bool(self.var_abrir.get()),"bandeja":bool(self.var_bandeja.get()),"aften":dict(getattr(self,"_aften",AFTEN_DEF))}
    def _save_cfg(self):
        try:
            d=dict(self._cfg);d.update({"tema":self.var_tema.get(),"idioma":IDIOMA,"salida":self._salida_cfg()})
            try:
                y=int(self.vpan.sash_coord(0)[1])
                if y>=120 and not self._tab_vis():d["panel_alto4"]=y   # en Visualizacion el panel de arriba esta recogido
            except Exception:pass
            d["oir_sal"]=self.var_oir_sal.get()
            with open(os.path.join(_data_dir(),"config.json"),"w",encoding="utf-8") as f:json.dump(d,f,indent=2,ensure_ascii=False)
            self._cfg=d
        except Exception as e:self._log(f"[CFG] {e}")
    def _copiar_log(self):
        try:self.root.clipboard_clear();self.root.clipboard_append(self.txt_log.get("1.0","end-1c"))
        except Exception:pass
    def _on_close(self,forzar=False):
        if self.procesando and not forzar:
            if not self._confirm(self._vt("Proceso en marcha","Process running"),self._vt("Hay un vídeo procesándose.\n\n¿Cancelarlo y salir? El archivo a medias se borrará.","A video is being processed.\n\nCancel it and exit? The unfinished file will be deleted.")):return
            self._cancel()
            self.root.after(1500,lambda:self._on_close(forzar=True));return
        self._oir_parar();self._save_cfg();self._iso_soltar_todo()
        shutil.rmtree(self._tmp,ignore_errors=True)
        try:self.root.destroy()
        except Exception:pass
    # ---------- Visualización / Edición: tramos, fotogramas, imagen y bandas negras ----------
    def _pintar_tramos(self):
        j=self._job();lb=self.lb_tramos
        try:
            st=lb.cget("state");lb.configure(state="normal");lb.delete(0,"end")
            if j:
                for i,(a,b) in enumerate(j["rec"].get("tramos") or [],1):lb.insert("end",f"{i}) {_hms(a)} → {_hms(b)}  ({_hms(b-a).split('.')[0]})")
            lb.configure(state=st)
        except Exception:pass
    def _tramo_add(self):
        j=self._job();V_=self._vt
        if not j:return
        d=_dur(self.info[self.actual]);a=_seg(self.var_ini.get());b=_seg(self.var_fin.get())
        if a is None or b is None:self._toast(T("warn_tit"),V_("No entiendo el tiempo. Escríbelo así: 1:02:03.500","I do not understand the time. Write it like this: 1:02:03.500"),tipo="warning",seg=4);return
        if not b:b=d
        if d:b=min(b,d)
        if b<=a:self._toast(T("warn_tit"),V_("El fin tiene que ir después del inicio.","The end has to come after the start."),tipo="warning",seg=4);return
        j["rec"].setdefault("tramos",[]).append([round(a,3),round(b,3)])
        self._cargando=True
        try:self.var_ini.set("");self.var_fin.set("")
        finally:self._cargando=False
        j["rec"]["ini"]=j["rec"]["fin"]=""
        self._pintar_tramos();self._estado_video();self._refrescar_estado()
    def _tramo_quitar(self):
        j=self._job()
        if not j or not j["rec"].get("tramos"):return
        s=self.lb_tramos.curselection();i=s[0] if s else len(j["rec"]["tramos"])-1
        j["rec"]["tramos"].pop(i);self._pintar_tramos();self._estado_video();self._refrescar_estado()
    def _tramo_ninguno(self):
        j=self._job()
        if not j:return
        j["rec"]["tramos"]=[];self.var_ini.set("");self.var_fin.set("");self._pintar_tramos();self._estado_video();self._refrescar_estado()
    def _tramo_ir(self):
        j=self._job();s=self.lb_tramos.curselection()
        if j and s:self.var_pos.set(j["rec"]["tramos"][s[0]][0]);self._prev_pronto(50)
    def _paso(self,s,seg=False):
        """flechas: un fotograma (o un segundo con Mayusculas) adelante o atras"""
        j=self._job()
        if not j:return
        inf=self.info[self.actual];fps=_fps(_vstream(inf)) or 25.0;d=_dur(inf) or 0.0
        v=self.var_pos.get()+s*(1.0 if seg else 1.0/fps)
        self.var_pos.set(round(max(0.0,min(d,v)),3));self._prev_pronto(250)
    def _prev_pronto(self,ms=300):
        """se pide un fotograma nuevo cuando para el movimiento (deslizador, flechas, ajustes de imagen)"""
        try:
            if not self._tab_vis() or not self._job():return
            if getattr(self,"_prev_id",None):self.root.after_cancel(self._prev_id)
            self._prev_id=self.root.after(ms,self._preview)
        except Exception:pass
    def _prev_tam(self,vs):
        """tamaño de cada fotograma (uno encima del otro), lo mas grande que quepa"""
        try:W=max(320,self.fr_imgs.winfo_width()-6);H=max(240,self.fr_imgs.winfo_height())
        except Exception:W,H=640,600
        try:
            a,b=str(vs.get("sample_aspect_ratio","1:1")).split(":");sar=float(a)/float(b) if float(b) and float(a) else 1.0
        except Exception:sar=1.0
        ar=max(0.5,_num(vs.get("width"),16)*sar/max(1.0,_num(vs.get("height"),9)))
        w=min((W-16)/2.0,(H-26)*ar);h=w/ar   # uno al lado del otro
        return max(160,int(w)//2*2),max(90,int(h)//2*2)
    def _preview(self):
        self._prev_id=None
        j=self._job()
        if not j:return
        self._guardar_trabajo()
        ruta=self.actual;inf=self.info[ruta];vs=_vstream(inf);t=float(self.var_pos.get() or 0)
        ent=inf.get("entrada",ruta);dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        vf=self._vfiltros(ruta,j,vista=True)
        w,h=self._prev_tam(vs)
        fit=f"scale=iw*sar:ih,scale=w={w}:h={h}:force_original_aspect_ratio=decrease"
        self._prev_de=ruta;self._st(self._vt("Sacando el fotograma...","Grabbing the frame..."))
        def hilo():
            out=[]
            for chain in ([fit],vf+[fit]):
                try:
                    r=subprocess.run([FFMPEG,"-hide_banner","-v","error"]+dvd+["-ss",f"{t:.3f}","-i",ent,"-map",f"0:{vs['index']}","-frames:v","1","-vf",",".join(chain),"-f","image2pipe","-c:v","png","-"],capture_output=True,timeout=60,creationflags=CNW)
                    out.append(base64.b64encode(r.stdout).decode("ascii") if r.returncode==0 and r.stdout else None)
                    if r.returncode!=0:self._ls("[VIS] "+(r.stderr or b"").decode("utf-8","ignore")[-300:])
                except Exception as e:out.append(None);self._ls(f"[VIS] {e}")
            self._ui(self._preview_fin,ruta,out)
        threading.Thread(target=hilo,daemon=True).start()
    def _preview_fin(self,ruta,out):
        self._st("")
        if ruta!=self.actual:return
        for i,d in enumerate(out):
            try:
                img=tk.PhotoImage(data=d) if d else None
                setattr(self,"_img%d"%i,img);getattr(self,"lbl_img%d"%i).configure(image=img or "")
            except Exception as e:self._log(f"[VIS] {e}")
    def _pintar_crop(self):
        j=self._job();V_=self._vt
        try:
            if not j:self.lbl_crop.configure(text="");return
            c=j["v"].get("crop","");vs=_vstream(self.info[self.actual]) or {}
            if c=="no":self.lbl_crop.configure(text=V_("No tiene bandas negras.","It has no black bars."));return
            if not c:self.lbl_crop.configure(text=V_("Pulsa «Detectar» para buscarlas.","Press «Detect» to look for them."));return
            w,h,x,y=[int(q) for q in c.split(":")];W=int(_num(vs.get("width")));H=int(_num(vs.get("height")))
            q=[]
            if H-h:q.append(V_(f"{y} px arriba y {H-h-y} abajo",f"{y} px top and {H-h-y} bottom"))
            if W-w:q.append(V_(f"{x} px a la izquierda y {W-w-x} a la derecha",f"{x} px left and {W-w-x} right"))
            self.lbl_crop.configure(text=V_("Bandas negras: ","Black bars: ")+", ".join(q)+f" → {w}x{h}")
        except Exception:pass
    def _crop_detectar(self,ruta=None,callado=False):
        """busca las bandas negras en 8 puntos de la pelicula; se queda con lo que tiene imagen en alguno (las escenas oscuras no recortan de mas)"""
        ruta=ruta or self.actual
        if not ruta or ruta not in self.jobs:return
        inf=self.info[ruta];vs=_vstream(inf) or {};d=_dur(inf) or 60.0;ent=inf.get("entrada",ruta)
        dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        if not callado:self._st(self._vt("Buscando bandas negras...","Looking for black bars..."))
        def hilo():
            cs=[]
            for k in range(8):
                p=d*(0.1+0.8*k/7)
                try:
                    r=rh([FFMPEG,"-hide_banner"]+dvd+["-ss",f"{p:.2f}","-i",ent,"-map",f"0:{vs['index']}","-t","2","-vf","cropdetect=limit=24:round=2:reset=0","-f","null","-"],timeout=60)
                    m=re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)",r.stderr or "")
                    if m:cs.append([int(x) for x in m[-1]])
                except Exception:pass
            self._ui(self._crop_fin,ruta,cs,callado)
        threading.Thread(target=hilo,daemon=True).start()
    def _crop_fin(self,ruta,cs,callado):
        if not callado:self._st("")
        j=self.jobs.get(ruta)
        if not j:return
        vs=_vstream(self.info[ruta]) or {};W=int(_num(vs.get("width")));H=int(_num(vs.get("height")))
        if not cs or not W or not H:
            if not callado:self._toast(T("warn_tit"),self._vt("No se han podido buscar las bandas negras.","Could not look for the black bars."),tipo="warning",seg=4)
            return
        x0=min(c[2] for c in cs);y0=min(c[3] for c in cs);x1=max(c[2]+c[0] for c in cs);y1=max(c[3]+c[1] for c in cs)
        w=(x1-x0)//2*2;h=(y1-y0)//2*2
        hay=(H-h>=8) or (W-w>=8)
        j["v"]["crop"]=f"{w}:{h}:{x0}:{y0}" if hay else "no"
        if hay and j["v"]["codec"]!="copy":j["v"]["crop_on"]=True   # con Passthrough no: habria que recomprimir el video
        if not hay:j["v"]["crop_on"]=False
        if ruta==self.actual:
            self._cargando=True
            try:self.var_crop_on.set(j["v"]["crop_on"])
            finally:self._cargando=False
            self._pintar_crop();self._prev_pronto(100)
    # ---------- escuchar la pista con los ajustes ----------
    def _oir(self,proc,desde=None):
        j=self._job();V_=self._vt
        if not j or self._a_i is None:return
        self._oir_parar()
        t=j["a"][self._a_i];inf=self.info[self.actual]
        src=t["ext"] or inf.get("entrada",self.actual);pos=float(self.var_pos.get() or 0) if desde is None else float(desde)
        g=self._a_grafo(t,f"[0:{t['idx']}]","[o]",off=pos) if proc else None
        arg=(["-filter_complex",g,"-map","[o]"] if g else ["-map",f"0:{t['idx']}"])
        est=self.var_oir_sal.get()=="st"
        if est:arg+=["-ac","2"]
        try:
            ps=pos*(_fps_f(t) if proc else 1.0)   # con cambio de framerate, el segundo del archivo original
            if sys.platform=="win32":self._repro=_ReproMC(src,ps,2 if est else t["nch"],None,arg)
            else:self._repro=_ReproFF(src,ps,t["nch"],estereo=est,arg=arg)
        except Exception as e:self._toast(T("error_tit"),str(e),tipo="error");return
        self._oir_t0=time.time();self._oir_desde=pos;self._oir_proc=proc;self._onda_pausado=False
        self.lbl_oir.configure(text=(V_("Sonando con los ajustes","Playing with the settings") if proc else V_("Sonando el original","Playing the original"))+V_(" desde "," from ")+_hms(pos).split(".")[0])
        self.root.after(200,self._onda_sigue)
        self.root.after(1500,self._oir_vigila)
    def _oir_vigila(self):
        r=getattr(self,"_repro",None)
        if r is None:return
        if getattr(r,"err",None):self.lbl_oir.configure(text="⚠ "+str(r.err)[:120]);self._repro=None;return
        self.root.after(1500,self._oir_vigila)
    def _oir_ajuste(self):
        """(JMG, 16-11) en «Visual / Ondas», al mover Presencia o Gama dinámica lo que suena se para (sonaba con los ajustes de antes)"""
        if getattr(self,"_repro",None) is None:return
        self._oir_parar()
        try:self.lbl_oir.configure(text=self._vt("Parado: has cambiado un ajuste. Pulsa ▶ para oírlo con el cambio.","Stopped: you changed a setting. Press ▶ to hear it with the change."))
        except Exception:pass
    def _oir_parar(self):
        r=getattr(self,"_repro",None);self._repro=None
        if r:
            try:r.stop()
            except Exception:pass
        try:self.lbl_oir.configure(text="")
        except Exception:pass
    # ---------- pistas de audio de otro archivo ----------
    def _a_externa(self):
        j=self._job();V_=self._vt
        if not j:return
        f=filedialog.askopenfilename(title=V_("Pista de audio de otro archivo","Audio track from another file"),filetypes=[(V_("Audio y vídeo","Audio and video"),"*.mka *.ac3 *.eac3 *.dts *.thd *.flac *.wav *.m4a *.aac *.opus *.mp3 "+_EXT_VID),(V_("Todos los archivos","All files"),"*.*")])
        if not f:return
        inf=self._probe(os.path.normpath(f));self._ext_info[os.path.normpath(f)]=inf
        nuevas=[self._pista_a(s,os.path.normpath(f)) for s in inf.get("streams",[]) if s.get("codec_type")=="audio"]
        if not nuevas:self._toast(T("warn_tit"),V_("Ese archivo no tiene pistas de audio.","That file has no audio tracks."),tipo="warning",seg=4);return
        aviso=self._fps_detectar(nuevas,inf)
        j["a"]+=nuevas;self._pintar_a(len(j["a"])-len(nuevas));self._estado_video();self._refrescar_estado()
        if aviso:self._toast("Auto",aviso,seg=9)
    def _a_quitar_ext(self):
        """«Eliminar pista»: la añadida o una del vídeo (no sale en el archivo procesado; el original no se toca)"""
        j=self._job()
        if not j or self._a_i is None:return
        j["a"].pop(self._a_i)
        self._pintar_a(max(0,self._a_i-1));self._estado_video();self._refrescar_estado()
    # ---------- portada ----------
    def _pintar_portada(self):
        j=self._job();V_=self._vt
        try:
            if not j:self.lbl_portada.configure(text="");return
            p=j.get("portada")
            if p is None:
                ps=_portadas(self.info[self.actual])
                txt=(V_("La del vídeo: ","The video's: ")+", ".join(f"{str(x.get('codec_name','')).upper().replace('MJPEG','JPG')} {x.get('width')}x{x.get('height')}" for x in ps)) if ps else V_("El vídeo no tiene portada.","The video has no cover.")
            elif p=="":txt=V_("Sin portada.","No cover.")
            else:txt=V_("Imagen elegida: ","Chosen image: ")+os.path.basename(p)
            self.lbl_portada.configure(text=txt)
        except Exception:pass
    def _portada_buscar(self):
        """(JMG, 16-11) «🔍 Buscar en internet...»: el póster de TMDB de portada y el nombre «Título (Año)»"""
        j=self._job()
        if not j:self._toast(T("info_tit"),self._vt("Primero agrega un vídeo.","First add a video."),seg=3);return
        ruta=self.actual
        def puesto(f,t,y):
            if self.actual!=ruta:return
            self._portada_poner(f)
            n=re.sub(r'[<>:"/\\|?*]',"_",f"{t} ({y})" if y else t).strip().rstrip(".")
            if n:j["nombre"]=n;self._nom_pintar()
            self._refrescar_estado()
            self._toast(T("info_tit"),self._vt(f"Portada y nombre: «{n}».",f"Cover and name: «{n}»."),seg=5)
        self._portada_web(self._base(ruta),puesto)
    def _portada_elegir(self):
        j=self._job()
        if not j:return
        f=filedialog.askopenfilename(title=self._vt("Imagen de portada","Cover image"),filetypes=[(self._vt("Imágenes","Images"),"*.jpg *.jpeg *.png"),(self._vt("Todos los archivos","All files"),"*.*")])
        if f:self._portada_poner(os.path.normpath(f))
    def _portada_poner(self,v):
        j=self._job()
        if not j:return
        j["portada"]=v;self._pintar_portada();self._refrescar_estado()
    # ---------- sincronización (los cálculos de Jmg AudioProcesador: Calcular delay y Corregir por tramos) ----------
    _TRAMO_TOL=4.0   # ms: salto minimo entre escenas
    def _sinc_src(self,t):
        """(archivo, pista, marca de tiempo del archivo que cae en el segundo 0 del video, inicio del archivo, segundos que dura)"""
        if t["ext"]:
            inf=self._ext_info.get(t["ext"]) or {};f0=_num((inf.get("format") or {}).get("start_time"))
            return t["ext"],t["idx"],f0,f0,_dur(inf)
        inf=self.info[self.actual];vs=_vstream(inf) or {};f0=_num((inf.get("format") or {}).get("start_time"))
        return inf.get("entrada",self.actual),t["idx"],_num(vs.get("start_time"),f0),f0,_dur(inf)
    def _sinc_trozo(self,t,a,b,sr=8000,con_fc=False):
        """trozo [a, b] s del video de la pista (sin su delay), mono a 8 kHz y sin el central (los dialogos cambian con el idioma;
        la musica y los efectos no). Lista de muestras"""
        from array import array
        src,idx,base,f0,_=t["_src"];n=max(1,int(t["nch"]))
        chans=LAYCH.get(t["lay"]) or [f"c{i}" for i in range(n)]
        usa=[i for i,c in enumerate(chans) if con_fc or not (n>2 and c=="FC")] or list(range(n))
        pan="mono|c0="+"+".join(f"{1.0/len(usa):.4f}*c{i}" for i in usa)
        fa=_fps_f(t);cv=_fps_cad(t)   # con cambio de framerate: el trozo del original que cae ahi, ya convertido
        st=_num(t.get("start"),base);t0=base+a*fa;t1=base+b*fa;pre=0
        if t0<st:pre=int(round((st-t0)/fa*sr));t0=st      # el trozo empieza antes que la pista: silencio delante
        if t1<=t0:return [0]*int(round((b-a)*sr))
        cmd=[FFMPEG,"-v","error","-copyts","-ss",f"{max(0.0,t0-f0-3):.3f}","-i",src,"-map",f"0:{idx}",
             "-af",f"atrim=start={t0:.4f}:end={t1:.4f},asetpts=PTS-STARTPTS,"+(cv+"," if cv else "")+f"pan={pan},aresample={sr}","-f","s16le","-ac","1","-"]
        r=subprocess.run(cmd,capture_output=True,timeout=300,creationflags=CNW)
        x=array("h");x.frombytes(r.stdout[:len(r.stdout)//2*2])
        return [0]*pre+list(x)
    def _sinc_par(self):
        """(pista de referencia, pista activa) con su origen; avisa si falta algo"""
        j=self._job();V_=self._vt
        if not j or self._a_i is None:return None
        ops=getattr(self,"_aref_ops",[]);i=self.cb_aref.current()
        if not ops or i<0:
            self._toast(T("warn_tit"),V_("Hace falta otra pista con la que comparar (la del idioma original). Si está en otro archivo, añádela con «Añadir pista de otro archivo».","Another track to compare with is needed (the original-language one). If it is in another file, add it with «Add a track from another file»."),tipo="warning",seg=7);return None
        ref=j["a"][ops[i][0]];t=j["a"][self._a_i]
        if self._escaneando or self.procesando:return None
        ref["_src"]=self._sinc_src(ref);t["_src"]=self._sinc_src(t)
        return ref,t
    def _sinc_em(self,on,txt=""):
        self._escaneando=on
        try:
            self.bt_sinc.state(["disabled"] if on else ["!disabled"]);self.bt_tramos.state(["disabled"] if on else ["!disabled"])
            self.btn_c.state(["!disabled"] if on else ["disabled"])
            if on:self._cancelar.clear();self.prog.configure(value=0)
            else:self.prog.configure(value=0)
        except Exception:pass
        self._st(txt)
    def _sinc_fin_prog(self,txt,fr):self._st(txt);self.prog.configure(value=100.0*fr)
    def _sinc_calc(self):
        """«Calcular delay»: un desfase para toda la pelicula, comparando con la pista de referencia"""
        q=self._sinc_par()
        if not q:return
        ref,t=q;V_=self._vt;ruta=self.actual
        self._sinc_em(True,V_("Comparando las pistas...","Comparing the tracks..."))
        def hilo():
            try:
                dr=ref.get("delay",0)/1000.0;do=t.get("delay",0)/1000.0
                dur_r=ref["_src"][4];dur_o=t["_src"][4]
                lo=max(0.0,dr,do);hi=min(dur_r+dr,dur_o+do);T_=hi-lo
                pal=self._sinc_pal(dur_r,dur_o)
                if pal:return self._ui(self._sinc_calc_fin,ruta,t,None,[pal])
                if T_<6:return self._ui(self._sinc_calc_fin,ruta,t,None,[V_("Las pistas coinciden muy poco tiempo (menos de 6 s): pon el delay a mano.","The tracks overlap for too short a time (under 6 s): set the delay by hand.")])
                W=min(40.0,T_*0.4);M=min(10.0,T_*0.2)
                puntos=[lo+T_*fr-W/2 for fr in ((0.2,0.5,0.8) if T_>=180 else (0.5,))]
                puntos=[min(max(a,lo+M),hi-W-M) for a in puntos];med=[]
                for n_,a in enumerate(puntos,1):
                    if self._cancelar.is_set():return self._ui(self._sinc_calc_fin,ruta,t,None,["cancel"])
                    self._ui(self._sinc_fin_prog,V_("Comparando las pistas... ","Comparing the tracks... ")+f"{n_}/{len(puntos)}",(n_-1)/len(puntos))
                    ms,r=self._sinc_medir(ref,t,a,W,M,dr=dr,do=do)
                    self._ls(f"[SINC] #{t['idx']} @ {_hms(a)}: "+(f"{ms:+.1f} ms (r={r:.2f})" if ms is not None else "?"))
                    if ms is not None and r>=0.3:med.append(ms)
                if not med:return self._ui(self._sinc_calc_fin,ruta,t,None,[V_("No se parece lo bastante a la de referencia: pon su delay a mano.","It is not similar enough to the reference: set its delay by hand.")])
                med.sort();inf=[]
                if med[-1]-med[0]>3:
                    inf.append(V_("⚠ El desfase cambia a lo largo de la película (","⚠ The offset changes over the movie (")+" / ".join("%+d"%round(v) for v in med)+" ms)"+V_(": prueba «Corregir por tramos».",": try «Fix by parts»."))
                self._ui(self._sinc_calc_fin,ruta,t,int(round(t.get("delay",0)-med[len(med)//2])),inf)
            except Exception as e:
                self._ls(f"[SINC] [ERR] {e}");self._ui(self._sinc_calc_fin,ruta,t,None,[V_("No se ha podido calcular (mira Edit/Log).","Could not calculate (see Edit/Log).")])
        threading.Thread(target=hilo,daemon=True).start()
    def _sinc_calc_fin(self,ruta,t,d,inf):
        V_=self._vt;self._sinc_em(False)
        if inf==["cancel"]:self._toast(T("cancelado_tit"),V_("Medida cancelada.","Measurement cancelled."),seg=3);return
        if d is None:self._toast(T("warn_tit"),"\n".join(inf),tipo="warning",seg=8);return
        if abs(d)>6000:self._toast(T("warn_tit"),V_(f"Sale un desfase de {d:+d} ms, más del máximo. Comprueba que sean la misma versión de la película.",f"The offset is {d:+d} ms, more than the maximum. Check they are the same version of the movie."),tipo="warning",seg=8);return
        t["delay"]=d;t["tramos"]=None
        if ruta==self.actual:self._a_cargar();self._cambio_a()
        self._toast(T("info_tit"),"\n".join([V_(f"Delay: {d:+d} ms. Queda en el deslizador: puedes retocarlo a mano.",f"Delay: {d:+d} ms. It stays on the slider: you can adjust it by hand.")]+inf),seg=8)
    def _sinc_pal(self,ref,d):
        """aviso si una pista dura un ~4 % menos o mas que la otra: 25 fps (PAL) frente a 23,976 / 24. No se arregla con delays"""
        V_=self._vt
        if ref<60 or d<60:return ""
        q=ref/d
        if 1.025<q<1.065 or 1/1.065<q<1/1.025:
            return V_(f"⚠ Las dos pistas duran distinto ({abs(1-d/ref)*100:.1f} %): parece que una va a 25 fps (PAL) y la otra a 23,976 o 24. Eso no se arregla con un delay: hay que cambiar antes la velocidad.",
                      f"⚠ The two tracks have different lengths ({abs(1-d/ref)*100:.1f} %): one seems to be 25 fps (PAL) and the other 23.976 or 24. A delay cannot fix that: the speed must be changed first.")
        return ""
    def _huella(self,t,con_fc,prog=None):
        """recorre la pista entera: (golpes cada 1 ms, nivel cada 10 ms) como array('f'); indice 0 = primera muestra de la pista.
        None si se cancela. prog(fraccion)"""
        from array import array
        src,idx,base,f0,du=t["_src"];n=max(1,int(t["nch"]))
        chans=LAYCH.get(t["lay"]) or [f"c{i}" for i in range(n)]
        usa=[i for i,c in enumerate(chans) if con_fc or not (n>2 and c=="FC")] or list(range(n))
        pan="mono|c0="+"+".join(f"{1.0/len(usa):.4f}*c{i}" for i in usa)
        du=max(1.0,du)
        cmd=[FFMPEG,"-v","error","-i",src,"-map",f"0:{idx}","-af",f"pan={pan},highpass=f=300,aresample=8000","-f","s16le","-ac","1","-"]
        pr=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,creationflags=CNW)
        e1=array("f");resto=b"";leido=0
        try:
            while True:
                if self._cancelar.is_set():
                    try:pr.kill()
                    except Exception:pass
                    return None
                buf=pr.stdout.read(160000)
                if not buf:break
                buf=resto+buf;cut=len(buf)//16*16;resto=buf[cut:]
                a=array("h");a.frombytes(buf[:cut])
                e1.extend(sum(map(abs,a[i:i+8])) for i in range(0,len(a),8))
                leido+=cut
                if prog:prog(min(1.0,leido/16000.0/du))
        finally:
            try:pr.stdout.close()
            except Exception:pass
            try:pr.wait(timeout=10)
            except Exception:pass
        import math
        lg=array("f",[0.0])*len(e1);s4=0.0
        for i in range(len(e1)):
            s4+=e1[i]
            if i>=4:s4-=e1[i-4]
            lg[i]=math.log10(s4+4.0)
        on=array("f",[0.0])*len(e1)
        for i in range(4,len(e1)):
            d=lg[i]-lg[i-4]
            if d>0:on[i]=d
        nv=array("f",(sum(e1[i:i+10]) for i in range(0,len(e1),10)))
        return on,nv
    def _sinc_tramos(self):
        """«Corregir por tramos»: el desfase cada 5 s, escenas y cortes en el momento mas silencioso (se aplica al procesar)"""
        q=self._sinc_par()
        if not q:return
        ref,t=q;V_=self._vt;ruta=self.actual
        self._sinc_em(True,V_("Midiendo el desfase por toda la película...","Measuring the offset throughout the movie..."))
        def hilo():
            try:self._ui(self._sinc_tramos_fin,ruta,t,*self._sinc_tramos_calc(ref,t))
            except Exception as e:
                self._ls(f"[TRAMOS] [ERR] {e}");self._ui(self._sinc_tramos_fin,ruta,t,None,[V_("No se ha podido calcular (mira Edit/Log).","Could not calculate (see Edit/Log).")])
        threading.Thread(target=hilo,daemon=True).start()
    def _sinc_tramos_calc(self,ref,t):
        """(tramos [(c0, c1, v0, v1)] o None, lineas de aviso). Igual que el «Corregir por tramos» de Jmg AudioProcesador"""
        V=self._vt;tol=self._TRAMO_TOL
        dr=ref.get("delay",0)/1000.0;do=t.get("delay",0)/1000.0
        ini_r=_num(ref.get("start"),ref["_src"][2])-ref["_src"][2];ini_o=_num(t.get("start"),t["_src"][2])-t["_src"][2]
        ext={0:(ini_r+dr,ini_r+dr+ref["_src"][4]),1:(ini_o+do,ini_o+do+t["_src"][4])}
        bases={0:int(round((ini_r+dr)*1000)),1:int(round((ini_o+do)*1000))}
        lo=max(e[0] for e in ext.values());hi=min(e[1] for e in ext.values());T_=hi-lo
        pal=self._sinc_pal(ref["_src"][4],t["_src"][4])
        if pal:return None,[pal]
        if T_<60:return None,[V("Las pistas coinciden muy poco tiempo para partirlas en tramos.","The tracks overlap for too short a time to split them into parts.")]
        def pr_(fr,txt):self._ui(self._sinc_fin_prog,txt,fr)
        V1=V("Leyendo ","Reading ")
        hr=self._huella(ref,False,lambda f:pr_(0.3*f,V1+V("la pista de referencia","the reference track")+f"... {int(f*100)} %"))
        if hr is None:return None,["cancel"]
        ho=self._huella(t,True,lambda f:pr_(0.3+0.3*f,V1+V("esta pista","this track")+f"... {int(f*100)} %"))
        if ho is None:return None,["cancel"]
        HR=(hr[0],bases[0]);HO=(ho[0],bases[1]);W=10.0;R=3.0;paso=5.0
        vals=[];x=lo+R;puntos=[]
        while x<=hi-W-R:puntos.append(x);x+=paso
        for i,x in enumerate(puntos):
            if self._cancelar.is_set():return None,["cancel"]
            if i%20==0:pr_(0.6+0.3*i/len(puntos),V("Midiendo el desfase cada 5 s... ","Measuring the offset every 5 s... ")+_hms(x)[:-4])
            vals.append((x+W/2,self._hu_medir(HR,HO,x,W,R)))
        n0=sum(1 for _,v in vals if v is not None)
        vals=self._tramos_limpiar(vals);esc=self._tramos_escenas(vals,tol)
        self._ls(f"[TRAMOS] {sum(1 for _,v in vals if v is not None)}/{len(vals)} "+V("puntos medidos","points measured")+f" ({n0-sum(1 for _,v in vals if v is not None)} "+V("falsos descartados","false ones discarded")+f"), {len(esc)} "+V("escenas","scenes"))
        if not esc:return None,[V("No se parece lo bastante a la de referencia para medirla.","It is not similar enough to the reference to measure it.")]
        partes=[self._tramos_modelo(q) for q in esc]
        def val(p,x):
            t0,t1,a,b,tm=p;return a+b*(min(max(x,t0),t1)-tm)
        cortes=[]
        for k in range(len(esc)-1):
            if self._cancelar.is_set():return None,["cancel"]
            pA=partes[k][-1];pB=partes[k+1][0];l_=esc[k][-1][0];h_=esc[k+1][0][0]
            while h_-l_>0.3:
                mid=(l_+h_)/2;vA=val(pA,mid);vB=val(pB,mid)
                ms=self._hu_medir(HR,HO,mid-1.5,3.0,max(R,abs(vA)/1000+0.5,abs(vB)/1000+0.5),cand=[vA,vB])
                if ms is None:break
                if abs(ms-vA)<abs(ms-vB):l_=mid
                else:h_=mid
            a_=max(l_-3.0,(l_+h_)/2-90.0);b_=min(h_+3.0,(l_+h_)/2+90.0)
            c_=self._tramos_cambio(HR,HO,a_,b_,val(pA,l_),val(pB,h_))
            cortes.append(self._tramos_silencio(ho[1],bases[1],c_-0.1,c_+0.1) if c_ is not None else self._tramos_silencio(ho[1],bases[1],l_-1.0,h_+1.0))
        tl=[];ini_=0.0
        for k,ps in enumerate(partes):
            fin_=cortes[k] if k<len(cortes) else hi+1.0
            lim=[ini_]
            for p,p2 in zip(ps,ps[1:]):
                u=(p[1]+p2[0])/2;lim.append(min(fin_-0.1,max(lim[-1]+0.5,self._tramos_silencio(ho[1],bases[1],u-3,u+3))))
            lim.append(fin_)
            for i,p in enumerate(ps):
                c0,c1=lim[i],lim[i+1]
                if c1-c0<0.05:continue
                v0,v1=val(p,c0),val(p,c1)
                if abs(v1-v0)<0.5:v0=v1=float(round((v0+v1)/2))
                tl.append((c0,c1,v0,v1))
            ini_=fin_
        self._ls("[TRAMOS] → "+" · ".join(f"{_hms(c0)[:-4]} {v0:+.0f}"+(f"→{v1:+.0f}" if abs(v1-v0)>=0.5 else "") for c0,c1,v0,v1 in tl))
        pr_(1.0,"")
        return tl,[]
    def _sinc_tramos_fin(self,ruta,t,tl,inf):
        V_=self._vt;self._sinc_em(False)
        if inf==["cancel"]:self._toast(T("cancelado_tit"),V_("Medida cancelada.","Measurement cancelled."),seg=3);return
        if not tl:self._toast(T("warn_tit"),"\n".join(inf) or V_("No se ha podido calcular.","Could not calculate."),tipo="warning",seg=8);return
        if len(tl)==1 and abs(tl[0][2]-tl[0][3])<0.5:   # igual en toda la pelicula: basta con un delay
            t["delay"]=int(round(t.get("delay",0)-tl[0][2]));t["tramos"]=None
            msg=V_(f"Va igual en toda la película: basta con un delay de {t['delay']:+d} ms, y ya está puesto.",f"It is the same throughout the movie: a delay of {t['delay']:+d} ms is enough, and it is set.")
        else:
            t["tramos"]={"tl":[list(q) for q in tl],"d":int(t.get("delay",0))}
            msg=V_(f"Corregida por tramos: {len(tl)} tramos, de {min(min(q[2],q[3]) for q in tl):+.0f} a {max(max(q[2],q[3]) for q in tl):+.0f} ms. Se aplica al procesar (mira Edit/Log para ver cada tramo).",
                   f"Fixed by parts: {len(tl)} parts, from {min(min(q[2],q[3]) for q in tl):+.0f} to {max(max(q[2],q[3]) for q in tl):+.0f} ms. It is applied when processing (see Edit/Log for each part).")
        if ruta==self.actual:self._a_cargar();self._cambio_a()
        self._toast(T("info_tit"),msg,seg=9)
    def _sinc_quitar_tramos(self):
        j=self._job()
        if not j or self._a_i is None:return
        j["a"][self._a_i]["tramos"]=None;self._a_cargar();self._cambio_a()
    def _sinc_txt(self,t):
        tr=t.get("tramos");V_=self._vt
        if tr:
            if abs(int(t.get("delay",0))-tr["d"])>0:return V_("⚠ Hay tramos medidos con otro delay: no se aplican. Vuelve a medir o quítalos.","⚠ There are parts measured with another delay: they are not applied. Measure again or remove them.")
            tl=tr["tl"];return V_(f"✂ Corregida por tramos: {len(tl)} tramos ({min(min(q[2],q[3]) for q in tl):+.0f} a {max(max(q[2],q[3]) for q in tl):+.0f} ms).",f"✂ Fixed by parts: {len(tl)} parts ({min(min(q[2],q[3]) for q in tl):+.0f} to {max(max(q[2],q[3]) for q in tl):+.0f} ms).")
        return ""
    def _tramos_grafo(self,t,ent,lbl,off=0.0):
        """el delay y luego los tramos (como al medirlos), a 48 kHz; off = segundo del video donde empieza la salida (recortes)"""
        tr=t.get("tramos")
        d=int(t.get("delay") or 0)
        pre=(f"adelay=delays={d}:all=1," if d>0 else (f"atrim=start={-d/1000.0:.3f},asetpts=PTS-STARTPTS," if d<0 else ""))
        if not tr or abs(d-tr["d"])>0:return f"{ent}{pre}anull[{lbl}]" if pre else None
        tot=_dur(self.info.get(self.actual,{})) or tr["tl"][-1][1]
        tl=[(c0-off,c1-off,v0,v1) for c0,c1,v0,v1 in tr["tl"] if c1-off>0]
        if not tl:return f"{ent}{pre}anull[{lbl}]" if pre else None
        tl[0]=(max(0.0,tl[0][0]),)+tuple(tl[0][1:])
        P,sal=self._tramos_cad(lbl,f"{ent}{pre}aresample=48000",[q for q in tl if q[0]<tot-off],tot-off)
        return ";".join(P)+";"+sal+f"[{lbl}]"
    @staticmethod
    def _sinc_corr(x,y,l0,l1,signo=False,todos=False):
        """correlacion normalizada de x con y desplazada (y[l:l+len(x)]) para l en [l0, l1] -> (mejor l, r)
        (todos=True: tambien {l: r} de todos los desplazamientos)"""
        import math,operator
        n=len(x);sx=math.sqrt(sum(map(operator.mul,x,x))) or 1.0
        cy=[0.0]
        for v in y:cy.append(cy[-1]+v*v)
        mejor=(None,0.0);rs={}
        for l in range(max(0,l0),min(l1,len(y)-n)+1):
            r=sum(map(operator.mul,x,y[l:l+n]))/(sx*(math.sqrt(max(cy[l+n]-cy[l],1e-9))))
            rs[l]=r
            if (abs(r) if signo else r)>(abs(mejor[1]) if signo else mejor[1]):mejor=(l,r)
        return mejor+(rs,) if todos else mejor
    @staticmethod
    def _sinc_env(x,blq=80,sr=8000,fc=300.0):
        """golpes de sonido cada 10 ms (subidas de la envolvente en dB, sin graves: los dialogos fuertes no tapan los golpes flojos), sin la media"""
        import math
        k=math.exp(-2*math.pi*fc/sr);h=[];yp=0.0;xp=0
        for v in x:
            yp=k*(yp+v-xp);xp=v;h.append(abs(yp))
        env=[math.log10(sum(h[i:i+blq])+blq) for i in range(0,len(h)-blq+1,blq)]
        on=[0.0]+[max(0.0,env[i]-env[i-1]) for i in range(1,len(env))]
        m=sum(on)/max(1,len(on));return [v-m for v in on]
    @staticmethod
    def _sinc_env_fino(x,sr=8000,fc=300.0):
        """golpes cada 1 ms: sin graves (sus ciclos enganan al afinar), envolvente de 4 ms y su subida en 4 ms, sin la media"""
        import math,itertools
        k=math.exp(-2*math.pi*fc/sr);h=[];yp=0.0;xp=0
        for v in x:
            yp=k*(yp+v-xp);xp=v;h.append(abs(yp))
        c=[0.0];c.extend(itertools.accumulate(h))
        hop=sr//1000;win=4*hop
        e=[c[i+win]-c[i] for i in range(0,len(h)-win+1,hop)]
        on=[0.0]*4+[max(0.0,e[i]-e[i-4]) for i in range(4,len(e))]
        m=sum(on)/max(1,len(on));return [v-m for v in on]
    @staticmethod
    def _hu_corr(x,y,l0,l1):
        """r de x (media 0) con y[l:l+len(x)] para l en [l0, l1] -> {l: r}"""
        import math,operator
        n=len(x);sx=math.sqrt(sum(map(operator.mul,x,x))) or 1.0
        out={}
        for l in range(max(0,l0),min(l1,len(y)-n)+1):
            yy=y[l:l+n];sy=sum(yy);q=sum(map(operator.mul,yy,yy))-sy*sy/n
            out[l]=sum(map(operator.mul,x,yy))/(sx*math.sqrt(q)) if q>1e-12 else 0.0
        return out
    def _hu_medir(self,hr,ho,t,W,R,cand=None):
        """ms que «otra» llega tarde en la ventana [t, t+W] s de la salida (hr/ho = (golpes, desplazamiento en ms de su indice 0)),
        buscando en +-R s; cand: solo alrededor de esos valores. (ms o None)"""
        xr,br=hr;yo,bo=ho
        i0=int(round(t*1000))-br;w=int(W*1000);Rm=int(R*1000)
        j0=int(round(t*1000))-bo-Rm
        if i0<0 or i0+w>len(xr) or j0<0 or j0+w+2*Rm>len(yo):return None
        x=xr[i0:i0+w];y=yo[j0:j0+w+2*Rm]
        if cand is None:
            # grueso cada 10 ms en +-R: los 3 mejores picos (separados mas de 100 ms), que se afinan al ms
            x10=[sum(x[i:i+10]) for i in range(0,w,10)];m=sum(x10)/len(x10);x10=[v-m for v in x10]
            y10=[sum(y[i:i+10]) for i in range(0,len(y)-9,10)]
            g=self._hu_corr(x10,y10,0,2*Rm//10)
            if not g:return None
            cs=[]
            for l_,v in sorted(g.items(),key=lambda kv:-kv[1]):
                if all(abs(l_-c)>10 for c in cs):cs.append(l_)
                if len(cs)==3:break
            cs=[c*10 for c in cs]
        else:cs=[Rm+int(round(c)) for c in cand]
        m=sum(x)/w;x=[v-m for v in x];fin_=[]
        for c in cs:
            f=self._hu_corr(x,y,c-12,c+12)
            if f:l=max(f,key=f.get);fin_.append((f[l],l,f))
        if not fin_:return None
        fin_.sort(key=lambda q:-q[0])
        # el mejor pico tiene que ser claro: 1,6 veces el siguiente (musica con ritmo, dialogos...)
        if cand is None and (fin_[0][0]<=0 or (len(fin_)>1 and fin_[0][0]<1.6*max(fin_[1][0],0.0))):return None
        rf,l,f=fin_[0];d=0.0
        if l-1 in f and l+1 in f:
            den=f[l-1]-2*rf+f[l+1]
            if den<0:d=max(-0.5,min(0.5,0.5*(f[l-1]-f[l+1])/den))
        if cand is not None and rf<0.08:return None
        return l+d-Rm
    @staticmethod
    def _tramos_cambio(hr,ho,a,b,vA,vB):
        """instante (s) en que la pista pasa del desfase vA al vB, entre a y b: en cada golpe de la referencia se mira cual de los dos
        encaja; la suma acumulada de esa diferencia llega a su maximo justo en el cambio. None si no hay golpes que lo digan"""
        xr,br=hr;yo,bo=ho;va=int(round(vA));vb=int(round(vB));s=0.0;mx=0.0;tm=None;tot=0.0
        for t in range(int(a*1000),int(b*1000)):
            i=t-br;ja=t-bo+va;jb=t-bo+vb
            if i<0 or i>=len(xr) or min(ja,jb)<2 or max(ja,jb)+3>=len(yo):continue
            x=xr[i]
            if x<=0:continue
            ga=sum(yo[ja-2:ja+3]);gb=sum(yo[jb-2:jb+3])
            s+=x*(ga-gb);tot+=x*abs(ga-gb)
            if s>mx:mx=s;tm=t
        return tm/1000.0 if (tm is not None and tot>0 and mx>=0.05*tot) else None
    @staticmethod
    def _tramos_recta(pts):
        """recta por mínimos cuadrados v = a + b·(t - tm) (b en ms/s) -> (a, b, tm, error max)"""
        n=len(pts);tm=sum(t for t,v in pts)/n;vm=sum(v for t,v in pts)/n
        sxx=sum((t-tm)**2 for t,v in pts)
        b=sum((t-tm)*(v-vm) for t,v in pts)/sxx if sxx>1e-9 else 0.0
        return vm,b,tm,max(abs(v-(vm+b*(t-tm))) for t,v in pts)
    @staticmethod
    def _tramos_limpiar(vals,lim=400.0,rad=120.0):
        """quita las medidas falsas: [(t, ms o None)] -> igual, con None en las que se alejan mas de lim ms de la mediana de los
        +-rad s de alrededor. Las ventanas se solapan, asi que un pico falso sale en dos puntos seguidos y parece una escena;
        un desfase de verdad (aunque sea de segundos) dura lo bastante para mover esa mediana"""
        v=[(t,ms) for t,ms in vals if ms is not None];out=[];q=0
        if not v:return list(vals)
        tod=sorted(ms for t,ms in v);glob_=tod[len(tod)//2]
        i0=i1=0
        for t,ms in vals:
            if ms is None:out.append((t,None));continue
            while i0<len(v) and v[i0][0]<t-rad:i0+=1
            while i1<len(v) and v[i1][0]<=t+rad:i1+=1
            veci=sorted(x for _,x in v[i0:i1])
            med=veci[len(veci)//2] if len(veci)>=5 else glob_
            out.append((t,ms if abs(ms-med)<=lim else None))
        return out
    def _tramos_escenas(self,vals,tol=4.0):
        """[(t, ms o None)] cada 5 s -> escenas [[(t, ms)...]]: el desfase va seguido (puede resbalar despacio) y cambia de golpe
        entre escenas; un punto suelto distinto no abre escena"""
        v=[(t,ms) for t,ms in vals if ms is not None];esc=[];cur=[]
        for i,(t,ms) in enumerate(v):
            if cur:
                hueco=t-cur[-1][0];tl=tol+0.25*max(0.0,hueco-5.0)   # cuanto mas hueco, mas puede haber resbalado
                if abs(ms-cur[-1][1])<=tl:cur.append((t,ms));continue
                # cambio de escena si lo confirma el siguiente punto; si no, punto suelto
                if not (i+1<len(v) and abs(v[i+1][1]-ms)<=tol+0.25*max(0.0,v[i+1][0]-t-5.0)):continue
                if len(cur)>=2:esc.append(cur)
            cur=[(t,ms)]
        if len(cur)>=2:esc.append(cur)
        # una escena muy distinta de las de su lado tiene que durar (al menos 4 puntos): si no, no se le hace caso
        esc=[q for j,q in enumerate(esc) if len(q)>=4 or not ((j>0 and abs(q[0][1]-esc[j-1][-1][1])>300) or (j+1<len(esc) and abs(q[-1][1]-esc[j+1][0][1])>300))]
        # escenas seguidas con el mismo desfase (un hueco de dialogos en medio): una sola
        out=[]
        for q in esc:
            if out and abs(out[-1][-1][1]-q[0][1])<=tol:out[-1]=out[-1]+q
            else:out.append(q)
        return out
    def _tramos_modelo(self,pts,prof=0):
        """partes rectas de una escena: [(t_ini, t_fin, a, b, tm)]; si no cabe en una recta (+-3 ms), se parte donde mejor queda"""
        a,b,tm,err=self._tramos_recta(pts)
        if abs(b)<0.02:   # menos de 20 ppm: sin resbalon
            vs=sorted(v for t,v in pts);a=vs[len(vs)//2];b=0.0;err=max(abs(v-a) for t,v in pts)
        if err<=3.0 or len(pts)<8 or prof>=4:return [(pts[0][0],pts[-1][0],a,b,tm)]
        mejor=None
        for i in range(4,len(pts)-3):
            e=max(self._tramos_recta(pts[:i])[3],self._tramos_recta(pts[i:])[3])
            if mejor is None or e<mejor[0]:mejor=(e,i)
        i=mejor[1]
        return self._tramos_modelo(pts[:i],prof+1)+self._tramos_modelo(pts[i:],prof+1)
    @staticmethod
    def _tramos_silencio(nv,bo,a,b):
        """instante (s, salida) con menos nivel (100 ms) de la pista entre a y b; nv = nivel cada 10 ms, bo = desplazamiento en ms"""
        i0=max(0,int((a*1000-bo)/10));i1=min(len(nv)-10,int((b*1000-bo)/10))
        if i1<=i0:return (a+b)/2
        s=sum(nv[i0:i0+10]);mejor=(s,i0)
        for i in range(i0+1,i1):
            s+=nv[i+9]-nv[i-1]
            if s<mejor[0]:mejor=(s,i)
        return (mejor[1]*10+50+bo)/1000.0
    @staticmethod
    def _tramos_cad(n,cad,tl,tot):
        """filtros que corrigen por tramos la señal de cad (a 48 kHz, de uno o varios canales) -> (lineas de filtro, cadena de salida).
        tl=[(c0, c1, v0, v1)]: el trozo [c0, c1] de la salida sale de la señal en [c0 + v0, c1 + v1] (v = ms que llegaba tarde):
        si v0 != v1 va un poco mas rapido o mas lento (asetrate entero + aresample: cambio de tono inapreciable).
        Largo exacto a la muestra, y un fundido de 3 ms en cada corte (van en silencios) para que no haga clic"""
        import math
        # seguidos y sin huecos: cada tramo empieza donde acaba el anterior; uno de menos de 20 ms se lo queda el anterior
        tl2=[]
        for c0,c1,v0,v1 in tl:
            if tl2:c0=tl2[-1][1]
            if tl2 and c1-c0<0.02:
                a_,b_,w0,w1=tl2[-1];tl2[-1]=(a_,c1,w0,w1);continue
            tl2.append((c0,c1,v0,v1))
        tl=tl2;P=[]
        pre=max(1,math.ceil(-min(min(c0+v0/1000.0,c1+v1/1000.0) for c0,c1,v0,v1 in tl)+0.1))   # silencio delante (s)
        P.append(cad+f",adelay=delays={pre*48000}S:all=1,asplit={len(tl)}"+"".join(f"[t{n}_{i}]" for i in range(len(tl))))
        for i,(c0,c1,v0,v1) in enumerate(tl):
            ult=i==len(tl)-1
            if ult:c1=max(c0+1.0,tot)
            o0=int(round(c0*48000));o1=int(round(c1*48000));N=o1-o0
            S0=int(round((c0+v0/1000.0+pre)*48000));S1=int(round((c1+v1/1000.0+pre)*48000))
            if N<=0 or abs((S1-S0)-N)>0.01*N:S1=S0+max(N,1)   # resbalon imposible (>1 %): el tramo va a delay fijo
            q=f"[t{n}_{i}]atrim=start_sample={S0}:end_sample={S1},asetpts=PTS-STARTPTS"
            R=int(round(48000.0*(S1-S0)/N)) if N>0 else 48000
            if R!=48000:q+=f",asetrate={R},aresample=48000"
            q+=f",apad=whole_len={max(N,1)},atrim=end_sample={max(N,1)}"
            if N>=960:   # fundidos de 3 ms solo si el tramo dura algo (20 ms o mas)
                if i>0:q+=",afade=t=in:d=0.003"
                if not ult:q+=f",afade=t=out:st={N/48000.0-0.003:.6f}:d=0.003"
            P.append(q+f"[u{n}_{i}]")
        return P,"".join(f"[u{n}_{i}]" for i in range(len(tl)))+f"concat=n={len(tl)}:v=0:a=1"
    def _sinc_medir(self,ref,otra,a,W,M,sr=8000,dr=0.0,do=0.0):
        """cuanto va «otra» por detras de «ref» (ms, + = mas tarde) en el trozo que empieza en a, y fiabilidad (0-1).
        dr / do: delay (s) ya puesto a cada pista (el trozo de la salida en a es el de la pista en a - delay)"""
        x=self._sinc_trozo(ref,a-dr,a+W-dr,sr);y=self._sinc_trozo(otra,a-M-do,a+W+M-do,sr)
        ex=self._sinc_env(x);ey=self._sinc_env(y);m=int(round(M*100))
        lc,rc,todos=self._sinc_corr(ex,ey,0,2*m,todos=True)
        if lc is None or rc<=0:return None,0.0
        # el pico tiene que destacar: el mejor de los demas (a mas de 100 ms) no puede acercarse (musica con ritmo, dialogos...)
        otro=max([v for l_,v in todos.items() if abs(l_-lc)>10] or [0.0])
        claro=rc>=0.12 and rc>=1.6*max(otro,0.0)
        # afinado al milisegundo con los golpes (no con la forma de onda: entre mezclas distintas se engancha a un ciclo vecino, +-5 ms),
        # +-15 ms alrededor de lo encontrado, y por debajo del ms con una parabola
        import math,operator
        fx=self._sinc_env_fino(x,sr);fy=self._sinc_env_fino(y,sr);M0=int(round(M*1000));c0=M0+(lc-m)*10
        n=len(fx);sx=math.sqrt(sum(map(operator.mul,fx,fx))) or 1.0;rs={}
        for l in range(max(0,c0-15),min(c0+15,len(fy)-n)+1):
            yy=fy[l:l+n];rs[l]=sum(map(operator.mul,fx,yy))/(sx*(math.sqrt(sum(map(operator.mul,yy,yy))) or 1.0))
        if not rs:return None,0.0
        l=max(rs,key=rs.get);rf=rs[l];d=0.0
        if l-1 in rs and l+1 in rs:
            den=rs[l-1]-2*rf+rs[l+1]
            if den<0:d=max(-0.5,min(0.5,0.5*(rs[l-1]-rs[l+1])/den))
        ms=l+d-M0
        # fiabilidad: la mejor de las dos envolventes, o la forma de onda si en ese punto tambien coincide
        # (en trozos de 4 s: basta con que en uno coincida, aunque en el resto tape el dialogo)
        p=int(round((ms/1000.0+M)*sr));rw=0.0
        for q in range(0,max(1,len(x)-4*sr+1),4*sr):
            xa=x[q:q+4*sr];xa=xa[:max(0,min(len(xa),len(y)-p-q))];ya=y[p+q:p+q+len(xa)]
            try:rw=max(rw,abs(sum(map(operator.mul,xa,ya)))/(math.sqrt(sum(map(operator.mul,xa,xa))*sum(map(operator.mul,ya,ya))) or 1.0))
            except Exception:pass
        # sin un pico grueso claro solo se fia si la forma de onda coincide de verdad (la misma mezcla)
        return ms,(max(0.3,rc,rf,rw) if claro or rw>=0.5 else min(rc,0.29))
    # ---------- Combinar vídeos: trozos de varios vídeos en uno solo ----------
    def _combinar(self):
        V_=self._vt
        if getattr(self,"_cb_top",None) is not None:
            try:self._cb_top.deiconify();self._cb_top.lift();return
            except Exception:self._cb_top=None
        if not hasattr(self,"_clips"):self._clips=[]
        top=tk.Toplevel(self.root);self._cb_top=top;top.title(V_("Combinar vídeos","Combine videos"));top.configure(bg=CF);top.transient(self.root)
        top.protocol("WM_DELETE_WINDOW",self._cb_cerrar)
        f=ttk.Frame(top);f.pack(fill="both",expand=True,padx=14,pady=10)
        ttk.Label(f,text="🎬 "+V_("Combinar vídeos","Combine videos"),font=("",11,"bold")).pack(anchor="w")
        ttk.Label(f,text=V_("Une trozos de varios vídeos (o del mismo) en uno solo, en este orden, con el tamaño y los fotogramas por segundo del primero. Lleva las pistas de audio marcadas de cada vídeo (o la que elijas para cada trozo) y sus subtítulos de texto marcados. El resultado entra en la lista de vídeos.",
                            "Joins parts of several videos (or of the same one) into a single one, in this order, with the size and frame rate of the first one. It carries the marked audio tracks of each video (or the one you choose for each part) and its marked text subtitles. The result goes into the video list."),
                  foreground=CA,font=("",8,"italic"),wraplength=760,justify="left").pack(anchor="w",pady=(2,8))
        tw=ttk.Frame(f);tw.pack(fill="x")
        cols=("n","vid","ini","fin","dur","aud")
        self.tv_cb=ttk.Treeview(tw,columns=cols,show="headings",height=6,selectmode="browse")
        for c,t,w in zip(cols,("#",V_("Vídeo","Video"),V_("Inicio","Start"),V_("Fin","End"),V_("Duración","Length"),"Audio"),(30,330,100,100,90,170)):
            self.tv_cb.heading(c,text=t);self.tv_cb.column(c,width=w,anchor="w" if c=="vid" else "center",stretch=c=="vid")
        self.tv_cb.pack(side="left",fill="x",expand=True);self.tv_cb.bind("<<TreeviewSelect>>",lambda e:self._cb_sel())
        bb=ttk.Frame(tw);bb.pack(side="left",padx=6,anchor="n")
        ttk.Button(bb,text="⬆",width=3,command=lambda:self._cb_mover(-1)).pack(pady=1)
        ttk.Button(bb,text="⬇",width=3,command=lambda:self._cb_mover(1)).pack(pady=1)
        fb=ttk.Frame(f);fb.pack(fill="x",pady=(6,0))
        fa0=ttk.Frame(f);fa0.pack(fill="x",pady=(6,0),before=fb)   # (JMG, 8-11) el vídeo se elige aquí (la ventana principal queda bloqueada)
        ttk.Label(fa0,text=V_("Vídeo:","Video:")).pack(side="left")
        self.cb_cb_vid=ttk.Combobox(fa0,width=46,state="readonly",postcommand=self._cb_vids);self.cb_cb_vid.pack(side="left",padx=6)
        ttk.Button(fa0,text="➕ "+V_("Añadir","Add"),command=self._cb_add).pack(side="left")
        ttk.Button(fa0,text="➖ "+V_("Quitar","Remove"),command=self._cb_quitar).pack(side="left",padx=6)
        ttk.Button(fa0,text="↺ "+V_("Resetear","Reset"),command=self._cb_reset).pack(side="left")
        self.btn_cb_ud=ttk.Button(fa0,text="↶",width=3,command=lambda:self._cb_ud_mover(-1));self.btn_cb_ud.pack(side="left",padx=(12,2))
        self.btn_cb_ur=ttk.Button(fa0,text="↷",width=3,command=lambda:self._cb_ud_mover(1));self.btn_cb_ur.pack(side="left")
        self._ayuda_flotante(self.btn_cb_ud,V_("Deshacer (Ctrl+Z)","Undo (Ctrl+Z)"));self._ayuda_flotante(self.btn_cb_ur,V_("Rehacer (Ctrl+Y)","Redo (Ctrl+Y)"))
        self._cb_vids()
        self.var_cb_ini=tk.StringVar();self.var_cb_fin=tk.StringVar()
        ttk.Label(fb,text=V_("Inicio:","Start:")).pack(side="left",padx=(16,2))
        self._entry(fb,self.var_cb_ini,12).pack(side="left",ipady=2)
        ttk.Label(fb,text=V_("Fin:","End:")).pack(side="left",padx=(8,2))
        self._entry(fb,self.var_cb_fin,12).pack(side="left",ipady=2)
        ttk.Button(fb,text="✔ "+V_("Poner","Set"),command=self._cb_poner).pack(side="left",padx=6)
        self._cb_vista(f)   # (JMG, 8-11) la imagen para elegir inicio y fin, y la pista de audio del trozo
        ttk.Label(f,text=V_("Al añadir un vídeo agregado que tiene tramos (Visualización / Edición), entra cada tramo. Inicio y fin vacíos = el vídeo entero.","When you add an added video that has parts (Visualization / Editing), each part goes in. Empty start and end = the whole video."),
                  foreground=CA,font=("",8,"italic"),wraplength=760,justify="left").pack(anchor="w",pady=(4,6))
        self.var_cb_color=tk.BooleanVar(value=True)
        ttk.Checkbutton(f,text="🎨 "+V_("Igualar color y brillo con el primero (mide cada trozo y lo ajusta)","Match color and brightness to the first one (measures each part and adjusts it)"),variable=self.var_cb_color,style="G.TCheckbutton").pack(anchor="w")
        self.lbl_cb=ttk.Label(f,text="",foreground=CID,wraplength=760,justify="left");self.lbl_cb.pack(anchor="w",pady=(4,0))
        bf=ttk.Frame(f);bf.pack(fill="x",pady=(10,0))
        self.btn_cb=ttk.Button(bf,text="🎬 "+V_("Combinar","Combine"),command=self._cb_empezar);self.btn_cb.pack(side="left")
        self.btn_cb_canc=ttk.Button(bf,text=T("cancelar"),command=self._cancel,state="disabled");self.btn_cb_canc.pack(side="left",padx=6)
        ttk.Button(bf,text=T("cerrar"),command=self._cb_cerrar).pack(side="right")
        self._cb_pintar()
        try:top.update_idletasks();top.geometry(f"+{self.root.winfo_rootx()+60}+{self.root.winfo_rooty()+60}")
        except Exception:pass
        # (JMG, 8-11) ventana modal: la principal no responde mientras está abierta; flechas, Ctrl+Z / Ctrl+Y
        self._cb_ud=[];self._cb_ur=[];self._cb_teclas(top);self._bloquear_principal(True)
        try:top.grab_set()
        except Exception:pass
    def _cb_cerrar(self):
        try:self._cb_top.grab_release();self._cb_top.destroy()
        except Exception:pass
        if self._cb_top is not None:self._cb_top=None;self._bloquear_principal(False)
    def _cb_pintar(self,sel=None):
        tv=self.tv_cb;tv.delete(*tv.get_children())
        for k,c in enumerate(self._clips):
            d=(c["fin"] or _dur(self.info.get(c["ruta"],{})))-c["ini"]
            tv.insert("","end",iid=str(k),values=(k+1,self._nombre(c["ruta"]),_hms(c["ini"]).split(".")[0],_hms(c["fin"]).split(".")[0] if c["fin"] else self._vt("final","end"),_hms(d).split(".")[0],self._cb_aud_txt(c)))
        if sel is not None and self._clips:tv.selection_set(str(max(0,min(sel,len(self._clips)-1))))
        if self._clips:
            vs=_vstream(self.info.get(self._clips[0]["ruta"],{})) or {}
            tot=sum((c["fin"] or _dur(self.info.get(c["ruta"],{})))-c["ini"] for c in self._clips)
            self.lbl_cb.configure(text=self._vt(f"{len(self._clips)} trozos · {_hms(tot).split('.')[0]} · salida {vs.get('width')}x{vs.get('height')} a {_fps(vs):.3f} fps",f"{len(self._clips)} parts · {_hms(tot).split('.')[0]} · output {vs.get('width')}x{vs.get('height')} at {_fps(vs):.3f} fps"))
        else:self.lbl_cb.configure(text=self._vt("Selecciona vídeos en la lista de la ventana principal y pulsa «Añadir».","Select videos in the main window list and press «Add»."))
    def _cb_vids(self):
        """los vídeos de la lista, para elegirlos en Combinar (por defecto, el seleccionado en la ventana principal)"""
        self._cb_vid_l=[f for f in self.files if f in self.info]
        try:
            prev=self.cb_cb_vid.current()
            self.cb_cb_vid.configure(values=[self._nombre(f) for f in self._cb_vid_l])
            if self._cb_vid_l and (prev<0 or prev>=len(self._cb_vid_l)):
                s=[self.files[i] for i in self.la.curselection() if i<len(self.files)]
                self.cb_cb_vid.current(self._cb_vid_l.index(s[0]) if s and s[0] in self._cb_vid_l else 0)
        except Exception:pass
    def _cb_add(self):
        k=self.cb_cb_vid.current() if getattr(self,"cb_cb_vid",None) else -1
        sel=[self._cb_vid_l[k]] if 0<=k<len(getattr(self,"_cb_vid_l",[])) else [self.files[i] for i in self.la.curselection() if i<len(self.files) and self.files[i] in self.info]
        if not sel:return
        self._cb_ud_antes()
        for f in sel:
            j=self.jobs.get(f);tr=self._tramos_job(j,f) if j else []
            for a,b in (tr or [(0.0,0.0)]):self._clips.append({"ruta":f,"ini":a,"fin":b,"a":None})
        self._cb_pintar(len(self._clips)-1)
    def _cb_quitar(self):
        s=self.tv_cb.selection()
        if s:self._cb_ud_antes();self._clips.pop(int(s[0]));self._cb_vis_i=None;self._cb_pintar(int(s[0])-1)
    def _cb_reset(self):
        """(JMG, 8-11) vacía la lista de trozos (↶ la recupera)"""
        if not self._clips:return
        self._cb_ud_antes();self._clips=[];self._cb_vis_i=None;self._cb_pintar()
        try:self.lbl_cb_img.configure(image="",text=self._vt("Elige un trozo de la lista","Choose a part from the list"));self.var_cb_ini.set("");self.var_cb_fin.set("")
        except Exception:pass
    def _cb_mover(self,d):
        s=self.tv_cb.selection()
        if not s:return
        i=int(s[0])
        if 0<=i+d<len(self._clips):self._cb_ud_antes();self._clips[i],self._clips[i+d]=self._clips[i+d],self._clips[i];self._cb_vis_i=None;self._cb_pintar(i+d)
    def _cb_sel(self):
        s=self.tv_cb.selection()
        if s:
            c=self._clips[int(s[0])];self.var_cb_ini.set(_hms(c["ini"]) if c["ini"] else "");self.var_cb_fin.set(_hms(c["fin"]) if c["fin"] else "")
            if getattr(self,"_cb_vis_i",None)!=(int(s[0]),c["ruta"]):self._cb_vista_ir(int(s[0]))
    def _cb_poner(self):
        V_=self._vt;s=self.tv_cb.selection()
        if not s and len(self._clips)==1:s=("0",)
        if not s:self._toast(T("info_tit"),V_("Elige primero un trozo de la lista.","First choose a part from the list."),seg=4);return
        i=int(s[0]);c=self._clips[i];a=_seg(self.var_cb_ini.get());b=_seg(self.var_cb_fin.get())
        if a is None or b is None or (b and b<=a):self._toast(T("warn_tit"),V_("Revisa el inicio y el fin.","Check the start and the end."),tipo="warning",seg=4);return
        self._cb_ud_antes();c["ini"]=a;c["fin"]=b;self._cb_pintar(i)
        self.var_cb_pos.set(a);self.lbl_cb_t.configure(text=_hms(a));self._cb_foto()   # (JMG, 8-11) se ve dónde empieza
        self._toast(T("info_tit"),V_(f"Trozo {i+1}: de {_hms(a).split('.')[0]} a {_hms(b).split('.')[0] if b else 'el final'}",f"Part {i+1}: from {_hms(a).split('.')[0]} to {_hms(b).split('.')[0] if b else 'the end'}"),seg=3)
    def _cb_medir(self,c):
        """brillo medio, contraste (de lo oscuro a lo claro) y saturacion de un trozo"""
        inf=self.info[c["ruta"]];vs=_vstream(inf);d=(c["fin"] or _dur(inf))-c["ini"]
        dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        r=rh([FFMPEG,"-hide_banner","-v","error"]+dvd+["-ss",f"{c['ini']+d*0.1:.2f}","-t",f"{max(2.0,min(30.0,d*0.8)):.2f}","-i",inf.get("entrada",c["ruta"]),"-map",f"0:{vs['index']}",
                "-vf","fps=2,scale=320:-2,signalstats,metadata=print:file=-","-f","null","-"],timeout=300)
        v={}
        for k in ("YAVG","YLOW","YHIGH","SATAVG"):
            xs=[float(x) for x in re.findall(r"lavfi\.signalstats\."+k+r"=([\d.]+)",r.stdout or "")]
            if xs:v[k]=sum(xs)/len(xs)
        return v if len(v)==4 else None
    def _cb_empezar(self):
        V_=self._vt
        if len(self._clips)<2:self._toast(T("info_tit"),V_("Añade al menos dos trozos.","Add at least two parts."),seg=4);return
        if self.procesando:return
        c0=self._clips[0];inf0=self.info[c0["ruta"]];vs0=_vstream(inf0) or {}
        W=int(_num(vs0.get("width"),1920))//2*2;H=int(_num(vs0.get("height"),1080))//2*2;F=_fps(vs0) or 25.0
        j0=self._cb_job(c0["ruta"])
        jv={"v":dict(j0["v"])}
        if jv["v"]["codec"]=="copy":jv["v"]["codec"]="hevc"
        if self.var_cont.get()=="avi":jv["v"]["codec"]="h264"   # AVI: H.264 y audio AC3
        if self.var_cont.get()=="webm" and jv["v"]["codec"] not in ("vp9","av1"):jv["v"]["codec"]="vp9"   # WebM: VP9 y Opus
        cont=self.var_cont.get();cont="mov" if (jv["v"]["codec"] in INTRA and cont=="mp4") else ("mp4" if (jv["v"]["codec"]=="vp9" and cont=="mov") else cont)
        base=self._base(c0["ruta"])
        d=self._dir_orig(c0["ruta"]) if self.var_dest_modo.get()!="carpeta" or not self.var_dest.get().strip() else self.var_dest.get().strip()
        sal=os.path.join(d,base+V_(" (combinado).",' (combined).')+cont);n=1;b0,e0=os.path.splitext(sal)
        while os.path.exists(sal):sal=f"{b0}_{n}{e0}";n+=1
        venc=self._venc(c0["ruta"],jv)
        clips=[dict(c) for c in self._clips];color=bool(self.var_cb_color.get())
        # (JMG, 8-11) pistas: las de audio marcadas de cada vídeo (o la elegida para el trozo) y sus subtítulos de texto marcados;
        # la pista k de la salida sale de la k-ésima de cada trozo (si un trozo no la tiene: silencio / sin subtítulo)
        datos=[]
        for c in clips:
            inf=self.info[c["ruta"]];vs=_vstream(inf);jc=self._cb_job(c["ruta"])
            if c.get("a") is not None:la=[c["a"]]
            else:la=[t["idx"] for t in jc["a"] if t["incl"] and not t["ext"]] or [s["index"] for s in inf.get("streams",[]) if s.get("codec_type")=="audio"][:1]
            ls=[s for s in jc["s"] if s["incl"] and not s["ext"]] if cont!="avi" else []
            datos.append({"c":c,"ent":inf.get("entrada",c["ruta"]),"dvd":bool(inf.get("dvd")),"v":vs["index"],"a":la,"s":ls,"inf":inf,"dur":(c["fin"] or _dur(inf))-c["ini"],"deint":_entrelazado(vs)})
        def st_de(inf,idx):return next((s for s in inf.get("streams",[]) if s.get("index")==idx),{})
        pa=[]   # pistas de audio de la salida: (disposición, layout, canales, idioma, título)
        for k,idx in enumerate(datos[0]["a"] or [None]):
            s=st_de(inf0,idx) if idx is not None else {};nch=int(_num(s.get("channels"),2)) or 2;lay=str(s.get("channel_layout") or "")
            if nch>6 or lay in ("","unknown") or "(" in lay and lay not in ("5.1(side)","7.1(wide)"):lay={1:"mono",2:"stereo",6:"5.1(side)"}.get(min(nch,6),"stereo")
            if nch>6:lay="5.1(side)";nch=6
            t0=next((t for t in j0["a"] if t["idx"]==idx and not t["ext"]),None)
            pa.append({"lay":lay,"nch":nch,"lang":(t0 or {}).get("lang") or (s.get("tags") or {}).get("language","und"),"tit":(t0 or {}).get("tit") or (s.get("tags") or {}).get("title","")})
        ps=[s for s in datos[0]["s"] if s["fmt"] not in IMG_SUB and not (cont=="webm" and s["fmt"] in IMG_SUB)]
        sin_img=sum(1 for dd in datos for s in dd["s"] if s["fmt"] in IMG_SUB)
        self.procesando=True;self._cancelar.clear();self.btn_c.state(["!disabled"]);self._refrescar_estado()
        try:self.btn_cb.state(["disabled"]);self.btn_cb_canc.state(["!disabled"])
        except Exception:pass
        self._bp_poner(True)   # (JMG, 14-11)
        def acod_de(nch):
            if cont=="avi":return "ac3",640 if nch>2 else 224
            if cont=="webm":return "libopus",384 if nch>2 else 160
            return ("eac3",640) if nch>2 else ("aac",224)
        def hilo():
            ok=False;err=[]
            try:
                eqs=[None]*len(datos)
                if color:
                    med=[]
                    for i,dd in enumerate(datos):
                        if self._cancelar.is_set():break
                        self._st(V_(f"Midiendo el color del trozo {i+1}/{len(datos)}...",f"Measuring the color of part {i+1}/{len(datos)}..."))
                        med.append(self._cb_medir(dd["c"]))
                    r0=med[0] if med else None
                    for i,m in enumerate(med):
                        if i==0 or not r0 or not m:continue
                        br=max(-0.15,min(0.15,(r0["YAVG"]-m["YAVG"])/255.0))
                        ct=max(0.7,min(1.4,(r0["YHIGH"]-r0["YLOW"])/max(1.0,m["YHIGH"]-m["YLOW"])))
                        sa=max(0.6,min(1.6,r0["SATAVG"]/max(1.0,m["SATAVG"])))
                        eqs[i]=f"eq=brightness={br:.3f}:contrast={ct:.3f}:saturation={sa:.3f}"
                        self._ls(f"[COMBINAR] {i+1}: {eqs[i]}")
                # subtitulos de texto: cada trozo a SRT y se unen, cada uno en su sitio
                subs=[]
                if sin_img:self._ls("[COMBINAR] "+V_(f"{sin_img} subtítulo(s) de imagen (PGS / DVD) no se pueden unir: se quedan fuera.",f"{sin_img} image subtitle(s) (PGS / DVD) cannot be joined: they are left out."))
                for k,s0 in enumerate(ps):
                    if self._cancelar.is_set():break
                    self._st(V_(f"Preparando los subtítulos {k+1}/{len(ps)}...",f"Preparing subtitles {k+1}/{len(ps)}..."))
                    cues=[];off=0.0
                    for i,dd in enumerate(datos):
                        tx=[s for s in dd["s"] if s["fmt"] not in IMG_SUB]
                        if k<len(tx):
                            for a,b,t in self._cb_srt(dd,tx[k]["idx"],os.path.join(self._tmp,f"cb_s{k}_{i}.srt")):
                                if a<dd["dur"]:cues.append((a+off,min(b,dd["dur"])+off,t))
                        off+=dd["dur"]
                    if cues:
                        ruta_s=os.path.join(self._tmp,f"cb_s{k}.srt");_srt_escribir(cues,ruta_s);subs.append((ruta_s,s0))
                cmd=[FFMPEG,"-hide_banner","-nostdin","-y","-v","error","-progress","pipe:1","-nostats"]
                fc=[];K=len(pa)
                for i,dd in enumerate(datos):
                    c=dd["c"];cmd+=(["-analyzeduration","100M","-probesize","100M"] if dd["dvd"] else [])+(["-ss",f"{c['ini']:.3f}"] if c["ini"] else [])+["-t",f"{dd['dur']:.3f}","-i",dd["ent"]]
                    vf=(["bwdif=mode=send_frame:parity=auto:deint=all"] if dd["deint"] else [])+[f"scale={W}:{H}:force_original_aspect_ratio=decrease",f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2","setsar=1",f"fps={F:.6f}"]+([eqs[i]] if eqs[i] else [])+["format=yuv420p"]
                    fc.append(f"[{i}:{dd['v']}]"+",".join(vf)+f"[v{i}]")
                    for k,p_ in enumerate(pa):
                        src=dd["a"][k] if k<len(dd["a"]) else None
                        if src is not None:fc.append(f"[{i}:{src}]aformat=sample_rates=48000:channel_layouts={p_['lay']},aresample=async=1,apad,atrim=end={dd['dur']:.3f}[a{i}_{k}]")
                        else:fc.append(f"anullsrc=r=48000:cl={p_['lay']},atrim=end={dd['dur']:.3f}[a{i}_{k}]")
                fc.append("".join(f"[v{i}]"+"".join(f"[a{i}_{k}]" for k in range(K)) for i in range(len(datos)))+f"concat=n={len(datos)}:v=1:a={K}[v]"+"".join(f"[a{k}]" for k in range(K)))
                ve=list(venc)
                if "-pix_fmt" in ve:   # el formato de imagen ya lo pone el filtro (8 bits)
                    q=ve.index("-pix_fmt");del ve[q:q+2]
                n_in=len(datos)
                for ruta_s,_ in subs:cmd+=["-i",ruta_s]
                cmd+=["-filter_complex",";".join(fc),"-map","[v]"]+sum((["-map",f"[a{k}]"] for k in range(K)),[])
                for q,_ in enumerate(subs):cmd+=["-map",f"{n_in+q}:0"]
                cmd+=ve
                for k,p_ in enumerate(pa):
                    ac,kb=acod_de(p_["nch"])
                    cmd+=[f"-c:a:{k}",ac,f"-b:a:{k}",f"{kb}k",f"-metadata:s:a:{k}","language="+(p_["lang"] or "und"),f"-metadata:s:a:{k}","title="+(p_["tit"] or ""),f"-disposition:a:{k}","default" if k==0 else "0"]
                    if ac=="libopus" and p_["nch"]>2:cmd+=[f"-mapping_family:a:{k}","1"]
                for q,(_,s0) in enumerate(subs):
                    dsp="+".join(x for x,on in (("default",s0.get("def")),("forced",s0.get("forz"))) if on) or "0"
                    cmd+=[f"-c:s:{q}",{"mkv":"srt","webm":"webvtt"}.get(cont,"mov_text"),f"-metadata:s:s:{q}","language="+(s0.get("lang") or "und"),f"-metadata:s:s:{q}","title="+(s0.get("tit") or ""),f"-disposition:s:{q}",dsp]
                cmd+=(["-movflags","+faststart"] if cont in ("mp4","mov") else [])+["-strict","-2",sal]
                if not self._cancelar.is_set():
                    ok,err=self._ejecutar(cmd,sum(dd["dur"] for dd in datos),0.0,100.0,V_("Combinando","Combining"),fps=F)
            except Exception as e:err=[str(e)]
            self._ui(self._cb_fin,ok,err,sal)
        threading.Thread(target=hilo,daemon=True).start()
    def _cb_fin(self,ok,err,sal):
        V_=self._vt;self.procesando=False;self._bp_poner(False);self.btn_c.state(["disabled"]);self._refrescar_estado();self._st("");self.prog.configure(value=0)
        try:self.btn_cb.state(["!disabled"]);self.btn_cb_canc.state(["disabled"])
        except Exception:pass
        if ok and os.path.isfile(sal):
            self._log("[OK] "+sal);self._toast(T("info_tit"),V_("Vídeo combinado:\n","Combined video:\n")+sal,seg=8)
            self._addl([sal])   # (JMG, 8-11) el combinado entra en la lista de vídeos
            if self.var_abrir.get() and self.var_al_terminar.get()!="apagar":
                try:_abrir_externo(os.path.dirname(sal))
                except Exception:pass
        else:
            try:
                if os.path.isfile(sal):os.remove(sal)
            except OSError:pass
            if self._cancelar.is_set():self._toast(T("cancelado_tit"),V_("Cancelado.","Cancelled."),seg=4)
            else:self._log("[ERROR] "+"\n".join(err[-12:]));self._toast(T("warn_tit"),V_("No se ha podido combinar (mira Edit/Log).","Could not combine (see Edit/Log)."),tipo="warning",seg=6)
    # ---------- «Opciones avanzadas»: Visualización dentro de la ventana (vídeo y audio), con «Volver» ----------
    def _av_cab(self,p,titulo):
        cab=ttk.Frame(p);cab.pack(fill="x",padx=10,pady=(8,4))
        ttk.Button(cab,text="⬅ "+self._vt("Volver","Back"),command=self._avz_volver).pack(side="left")
        bu=ttk.Button(cab,text="↶",width=3,command=lambda:self._avz_ud(-1));bu.pack(side="left",padx=(10,2))   # (JMG, 8-11) aquí la principal no responde
        br=ttk.Button(cab,text="↷",width=3,command=lambda:self._avz_ud(1));br.pack(side="left")
        self._ayuda_flotante(bu,self._vt("Deshacer (Ctrl+Z)","Undo (Ctrl+Z)"));self._ayuda_flotante(br,self._vt("Rehacer (Ctrl+Y)","Redo (Ctrl+Y)"))
        l=ttk.Label(cab,text=titulo,font=("",11,"bold"));l.pack(side="left",padx=12)
        return l
    def _av_video(self):
        """vista avanzada de video: arriba el antes y el despues; abajo el recorte por tramos, la imagen, las bandas negras y la reproduccion"""
        V_=self._vt
        f=ttk.Frame(self.root);self._avv=f
        self.lbl_avv=self._av_cab(f,V_("Vídeo · más opciones","Video · more options"))
        self.fr_imgs=ttk.Frame(f);self.fr_imgs.pack(fill="both",expand=True,padx=10)
        self.fr_imgs.columnconfigure(0,weight=1);self.fr_imgs.columnconfigure(1,weight=1)
        for i,t in enumerate((V_("Antes (original)","Before (original)"),V_("Después (con los ajustes de imagen)","After (with the picture settings)"))):
            c=ttk.Frame(self.fr_imgs);c.grid(row=0,column=i,sticky="n",padx=4)
            ttk.Label(c,text=t,font=("",9,"bold")).pack(anchor="w")
            im=tk.Label(c,bg="#000000");im.pack()
            setattr(self,"lbl_img%d"%i,im)
        self.fr_imgs.bind("<Configure>",lambda e:self._prev_pronto(500),add="+")
        bar=ttk.Frame(f);bar.pack(fill="x",padx=10,pady=(4,0))
        self.var_pos=tk.DoubleVar(value=0.0)
        ttk.Button(bar,text="◀",width=3,command=lambda:self._paso(-1)).pack(side="left")
        self.sc_pos=ttk.Scale(bar,from_=0,to=100,variable=self.var_pos,orient="horizontal");self.sc_pos.pack(side="left",fill="x",expand=True,padx=4)
        ttk.Button(bar,text="▶",width=3,command=lambda:self._paso(1)).pack(side="left")
        self.lbl_pos=ttk.Label(bar,text="0:00:00.000",font=("Consolas",10));self.lbl_pos.pack(side="left",padx=(8,12))
        ttk.Label(bar,text="🎬 "+V_("Reproducir:","Play:"),font=("",9,"bold")).pack(side="left")
        ttk.Button(bar,text="▶ "+V_("Original","Original"),command=lambda:self._vplay(False)).pack(side="left",padx=(4,2))
        ttk.Button(bar,text="▶ "+V_("Con los ajustes","With the settings"),command=lambda:self._vplay(True)).pack(side="left",padx=2)
        ttk.Button(bar,text="⏹",width=3,command=self._vplay_parar).pack(side="left",padx=(2,6))
        self._combo(bar,[("mc",V_("Multicanal","Multichannel")),("st",V_("Estéreo","Stereo"))],self.var_oir_sal,12).pack(side="left")
        self.sc_pos.bind("<ButtonRelease-1>",lambda e:self._prev_pronto(50),add="+")
        self.sc_pos.configure(takefocus=1);self.sc_pos.bind("<Button-1>",lambda e:self.sc_pos.focus_set(),add="+")
        for k,s in (("<Left>",-1),("<Right>",1),("<Down>",-1),("<Up>",1)):self.sc_pos.bind(k,lambda e,s=s:(self._paso(s),"break")[1])
        for k,s in (("<Shift-Left>",-1),("<Shift-Right>",1)):self.sc_pos.bind(k,lambda e,s=s:(self._paso(s,seg=True),"break")[1])
        self._tra(self.var_pos,lambda *a:self.lbl_pos.configure(text=_hms(self.var_pos.get())),self.sc_pos)
        ttk.Label(f,text=V_("Clic en la barra: las flechas ← → la mueven fotograma a fotograma (con Mayúsculas, de segundo en segundo). «Reproducir» abre una ventana de vídeo con sonido desde ese punto (con la primera pista de audio incluida); se cierra con ⏹ o con su X.",
                            "Click the bar: the ← → arrows move it frame by frame (with Shift, second by second). «Play» opens a video window with sound from that point (with the first included audio track); close it with ⏹ or its X."),
                  foreground=CA,font=("",8,"italic"),wraplength=1200,justify="left").pack(anchor="w",padx=10)
        ttk.Separator(f,orient="horizontal").pack(fill="x",padx=10,pady=4)
        ops=ttk.Frame(f);ops.pack(fill="x",padx=10,pady=(0,6))
        for i in range(3):ops.columnconfigure(i,weight=1,uniform="op")
        A=ttk.Frame(ops);A.grid(row=0,column=0,sticky="nw",padx=(0,10))
        B=ttk.Frame(ops);B.grid(row=0,column=1,sticky="nw",padx=10)
        C=ttk.Frame(ops);C.grid(row=0,column=2,sticky="nw",padx=(10,0))
        self._sec(A,0,V_("Recorte por tramos","Trimming by parts"))
        for r,(t,var) in enumerate(((V_("Inicio:","Start:"),self.var_ini),(V_("Fin:","End:"),self.var_fin)),start=1):
            fr=self._fila(A,r,t,lw=7)
            self._entry(fr,var,13).pack(side="left",ipady=2)
            ttk.Button(fr,text="⏱ "+V_("Aquí","Here"),command=lambda v=var:v.set(_hms(self.var_pos.get()))).pack(side="left",padx=6)
        fb=ttk.Frame(A);fb.grid(row=3,column=0,columnspan=3,sticky="w",padx=5,pady=2)
        ttk.Button(fb,text="➕ "+V_("Añadir tramo","Add part"),command=self._tramo_add).pack(side="left")
        ttk.Button(fb,text="➖ "+V_("Quitar","Remove"),command=self._tramo_quitar).pack(side="left",padx=4)
        ttk.Button(fb,text=V_("Sin recorte","No trim"),command=self._tramo_ninguno).pack(side="left")
        self.lb_tramos=tk.Listbox(A,height=4,width=42,bg=CDN,fg=CT,relief="flat",highlightthickness=1,highlightbackground=CSB,font=("Consolas",9),activestyle="none",exportselection=False)
        self.lb_tramos.grid(row=4,column=0,columnspan=3,sticky="w",padx=6,pady=2)
        self.lb_tramos.bind("<Double-Button-1>",lambda e:self._tramo_ir())
        self._nota(A,5,V_("Varios tramos se unen, en orden, en un solo vídeo (doble clic = ir a él). Con Passthrough los cortes caen en el fotograma clave más cercano.","Several parts are joined, in order, into one video (double-click = go to it). With Passthrough the cuts land on the nearest keyframe."),wrap=360)
        self._sec(B,0,V_("Imagen","Picture"),"img")
        for i,(k,t,a,b) in enumerate((("brillo",V_("Brillo","Brightness"),-10,10),("contraste",V_("Contraste","Contrast"),-10,10),("satur",V_("Saturación","Saturation"),-10,10),("tono",V_("Tono","Hue"),-10,10),("nitidez",V_("Nitidez","Sharpness"),0,10),("ruido",V_("Quitar ruido","Denoise"),0,10)),start=1):
            self._sl(B,t,getattr(self,"var_"+k),a,b,i,sl=150)
        self._sec(C,0,V_("Bandas negras","Black bars"))
        fc=ttk.Frame(C);fc.grid(row=1,column=0,columnspan=3,sticky="w",padx=2)
        ttk.Checkbutton(fc,text=V_("Quitarlas","Remove them"),variable=self.var_crop_on,style="G.TCheckbutton").pack(side="left")
        ttk.Button(fc,text="🔍 "+V_("Detectar","Detect"),command=self._crop_detectar).pack(side="left",padx=6)
        self.lbl_crop=ttk.Label(C,text="",foreground=CID,wraplength=330,justify="left");self.lbl_crop.grid(row=2,column=0,columnspan=3,sticky="w",padx=6)
        self._nota(C,3,V_("Las bandas se buscan solas al agregar el vídeo. Retocar la imagen o quitar las bandas obliga a recomprimir el vídeo.","The bars are looked for by themselves when the video is added. Touching up the picture or removing the bars requires re-encoding the video."),wrap=330)
        for v in (self.var_ini,self.var_fin):self._tra(v,lambda *a:self._cambio(),f)
        for k in ("brillo","contraste","satur","tono","nitidez","ruido","crop_on"):
            self._tra(getattr(self,"var_"+k),lambda *a:(self._cambio(),self._prev_pronto(400)),f)
    def _av_audio(self):
        """vista avanzada de audio: las ondas de cada canal antes y despues (todos los efectos se suman), escucha, tramo y Presencia"""
        V_=self._vt
        f=ttk.Frame(self.root);self._ava=f
        self.lbl_ava=self._av_cab(f,V_("Audio · Visual / Ondas","Audio · Visual / Waves"))
        self.cv_onda=tk.Canvas(f,bg="#1e1e1e",highlightthickness=1,highlightbackground=CSB,cursor="hand2")
        self.cv_onda.pack(fill="both",expand=True,padx=10)
        self.sb_onda=ttk.Scrollbar(f,orient="horizontal",command=self._onda_scroll);self.sb_onda.pack(fill="x",padx=10)
        self.cv_onda.bind("<Configure>",lambda e:self._onda_pintar(),add="+")
        self.cv_onda.bind("<Button-1>",self._onda_clic)
        self.cv_onda.bind("<MouseWheel>",lambda e:self._onda_scroll("scroll",-1 if e.delta>0 else 1,"units"))
        bar=ttk.Frame(f);bar.pack(fill="x",padx=10,pady=(4,2))
        ttk.Label(bar,text=V_("Tramo:","Segment:")).pack(side="left")
        self.var_onda_tr=tk.StringVar(value="300")
        self._combo(bar,[("300",V_("Primeros 5 min","First 5 min")),("600",V_("Primeros 10 min","First 10 min")),("1800",V_("Primeros 30 min","First 30 min")),("0",V_("Todo el archivo","The whole file"))],self.var_onda_tr,16).pack(side="left",padx=(2,6))
        ttk.Button(bar,text="🔄 "+V_("Generar visualización","Generate visualization"),command=self._onda_generar).pack(side="left",padx=(0,8))
        ttk.Label(bar,text="Zoom:").pack(side="left")
        self.var_onda_zoom=tk.StringVar(value="2")
        self._combo(bar,[("1","x1"),("2","x2"),("4","x4"),("8","x8"),("16","x16")],self.var_onda_zoom,5).pack(side="left",padx=(2,8))
        self._tra(self.var_onda_zoom,lambda *a:self._onda_pintar(),bar)
        ttk.Label(bar,text=V_("Detalle:","Detail:")).pack(side="left")
        self.var_onda_det=tk.StringVar(value="1")
        self._combo(bar,[("1","x1"),("2","x2"),("4","x4"),("8","x8")],self.var_onda_det,5).pack(side="left",padx=(2,12))
        self._tra(self.var_onda_det,lambda *a:self._onda_detalle(),bar)
        self._tra(self.var_onda_tr,lambda *a:self._onda_pronto(300),bar)
        ttk.Label(bar,text="🔊",font=("",10)).pack(side="left")
        ttk.Button(bar,text="▶ "+V_("Antes","Before"),command=lambda:self._oir(False,desde=self._onda_pos)).pack(side="left",padx=(4,2))
        ttk.Button(bar,text="▶ "+V_("Después","After"),command=lambda:self._oir(True,desde=self._onda_pos)).pack(side="left",padx=2)
        ttk.Button(bar,text="⏸",width=3,command=self._onda_pausa).pack(side="left",padx=(2,2))
        ttk.Button(bar,text="⏹",width=3,command=self._onda_parar).pack(side="left",padx=(2,6))
        self._combo(bar,[("mc",V_("Multicanal (5.1 / 7.1)","Multichannel (5.1 / 7.1)")),("st",V_("Estéreo","Stereo"))],self.var_oir_sal,20).pack(side="left")
        self.lbl_onda=ttk.Label(bar,text="",foreground=CID,font=("",9,"italic"));self.lbl_onda.pack(side="left",padx=10)
        self.lbl_oir=ttk.Label(bar,text="",foreground=CID,font=("",8,"italic"));self.lbl_oir.pack(side="left",padx=4)
        ttk.Label(f,text=V_("Clic en las ondas = escuchar desde ahí · ⏸ = pausa (otra vez, sigue) · ⏹ = parar y volver al principio · «Detalle» = más resolución (la rueda o la barra para moverse). Los efectos se suman: el «Después» lleva todos los de la pista.",
                            "Click on the waves = listen from there · ⏸ = pause (again, it goes on) · ⏹ = stop and go back to the start · «Detail» = more resolution (wheel or bar to move). The effects add up: «After» carries all those of the track."),
                  foreground=CA,font=("",8,"italic"),wraplength=1200,justify="left").pack(anchor="w",padx=10)
        ttk.Separator(f,orient="horizontal").pack(fill="x",padx=10,pady=4)
        ops=ttk.Frame(f);ops.pack(fill="x",padx=10,pady=(0,6))
        P_=ttk.Frame(ops);P_.pack(side="left",anchor="n")
        self._sec(P_,0,V_("Presencia","Presence"),"pres")
        for i,(k,t) in enumerate((("voz",V_("Voz (solo central)","Voice (center only)")),("amb",V_("Música / ambiente (no central)","Music / ambience (not center)")),("efc",V_("Efectos (no central)","Effects (not center)")),("sub","Subwoofer")),start=1):
            self._sl(P_,t,getattr(self,"var_"+k),-10,10,i)
        self._nota(P_,5,V_("Realza o baja las voces, el ambiente, los efectos y el subwoofer (la Presencia de Jmg AudioProcesador). «Auto» la coloca según la película; pulsado otra vez sin tocar nada, vuelve a 0.",
                           "Raises or lowers the voices, the ambience, the effects and the subwoofer (the Presence of Jmg AudioProcesador). «Auto» sets it for the movie; pressed again without touching anything, it goes back to 0."),wrap=560)
        for k in ("voz","amb","efc","sub"):self._tra(getattr(self,"var_"+k),lambda *a:(self._cambio_a(),self._onda_pronto(1200),self._oir_ajuste()),f)
        # Gama dinamica / Compresion, a la derecha de Presencia (las mismas de la pestaña Audio: se mueven en los dos sitios)
        ttk.Separator(ops,orient="vertical").pack(side="left",fill="y",padx=18)
        G_=ttk.Frame(ops);G_.pack(side="left",anchor="n")
        self._sec(G_,0,V_("Gama dinámica / Compresión","Dynamic range / Compression"))
        fg_,bg_=self._caja_auto(G_,lambda:self._auto("gama"));fg_.grid(row=0,column=2,padx=(1,5),pady=(10,2));self._auto_bts["gama"]=bg_
        self._sl(G_,V_("Delanteros y traseros","Fronts and surrounds"),self.var_gama,-10,10,1)
        self._sl(G_,V_("Central","Center"),self.var_gama_c,-10,10,2)
        self._nota(G_,3,V_("En el centro, apagado. A la izquierda, gama dinámica: más contraste. A la derecha, compresión: suben los sonidos flojos (de noche). Con ella no hace falta subir tanto la Presencia.",
                           "In the middle, off. To the left, dynamic range: more contrast. To the right, compression: quiet sounds go up (at night). With it there is no need to raise Presence so much."),wrap=440)
        for k in ("gama","gama_c"):self._tra(getattr(self,"var_"+k),lambda *a:(self._onda_pronto(1200),self._oir_ajuste()),f)
        self._onda=None;self._onda_pos=0.0;self._onda_x0=0.0
    def _avz_mostrar(self,tipo):
        """abre la vista avanzada («v» video, «a» audio) en lugar de la lista y las pestañas"""
        j=self._job()
        if not j:return
        if tipo=="a" and getattr(self,"_a_i",None) is None:
            self._toast(T("info_tit"),self._vt("Este vídeo no tiene pistas de audio.","This video has no audio tracks."),seg=3);return
        self._guardar_trabajo();self._avz_volver(pintar=False)
        self.vpan.pack_forget();self._avz=tipo
        (self._avv if tipo=="v" else self._ava).pack(side="top",fill="both",expand=True)
        if not getattr(self,"_avz_bloq",False):self._avz_bloq=True;self._bloquear_principal(True)
        if tipo=="v":
            self.lbl_avv.configure(text=self._vt("Vídeo · más opciones · ","Video · more options · ")+self._nombre(self.actual))
            self._pintar_tramos();self._pintar_crop();self._prev_pronto(150)
        else:
            t=j["a"][self._a_i]
            self.lbl_ava.configure(text=self._vt("Audio · Visual / Ondas · pista ","Audio · Visual / Waves · track ")+f"#{t['idx'] if not t['ext'] else 'ext.'} [{t['lang']}] {t['tit']}")
            if getattr(self,"_onda_de",None)!=(self.actual,self._a_i):self._onda=None;self._onda_pintar()
            self.root.after(200,self._onda_generar)   # siempre al entrar: el «Después» lleva los efectos de ahora
    def _avz_volver(self,pintar=True):
        if not getattr(self,"_avz",None):return
        self._vplay_parar();self._oir_parar()
        for w in (self._avv,self._ava):w.pack_forget()
        self._avz=None
        if getattr(self,"_avz_bloq",False):self._avz_bloq=False;self._bloquear_principal(False)
        self.vpan.pack(side="top",fill="both",expand=True)
        if pintar:self._pintar_trabajo()
    # ---------- reproducir el vídeo (ventana de ffplay) ----------
    def _vplay(self,proc):
        """FFmpeg prepara la imagen (con o sin los ajustes) y la primera pista de audio incluida, y ffplay lo enseña en su ventana"""
        j=self._job();V_=self._vt
        if not j:return
        self._vplay_parar();self._oir_parar();self._guardar_trabajo()
        ruta=self.actual;inf=self.info[ruta];vs=_vstream(inf);pos=float(self.var_pos.get() or 0)
        dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        c=[FFMPEG,"-hide_banner","-v","error"]+dvd+["-ss",f"{pos:.3f}","-i",inf.get("entrada",ruta)]
        t=next((x for x in j["a"] if x["incl"]),None);fa=_fps_f(t) if (t and proc) else 1.0
        if t and (t["ext"] or fa!=1.0):c+=["-ss",f"{pos*fa:.3f}"]+(dvd if not t["ext"] else [])+["-i",t["ext"] or inf.get("entrada",ruta)]
        vf=self._vfiltros(ruta,j) if proc else []
        c+=["-map",f"0:{vs['index']}"]+(["-vf",",".join(vf+["format=yuv420p"])] if vf else ["-vf","format=yuv420p"])
        if t:
            src=f"{1 if (t['ext'] or fa!=1.0) else 0}:{t['idx']}"
            g=self._a_grafo(t,f"[{src}]","[ao]",off=pos) if proc else None
            c+=(["-filter_complex",g,"-map","[ao]"] if g else ["-map",src])+(["-ac","2"] if self.var_oir_sal.get()=="st" else [])+["-c:a","pcm_s16le"]
        c+=["-c:v","libx264","-preset","ultrafast","-tune","zerolatency","-crf","18","-f","matroska","-"]
        tit=("Jmg VideoEncoder · "+(V_("con los ajustes","with the settings") if proc else V_("original","original"))+" · "+self._nombre(ruta))
        ff=[FFPLAY,"-hide_banner","-loglevel","error","-autoexit","-window_title",tit,"-x","1280","-y","720","-i","-"]
        try:
            p1=subprocess.Popen(c,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,creationflags=CNW)
            p2=subprocess.Popen(ff,stdin=p1.stdout,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=CNW)
            p1.stdout.close();self._vproc=(p1,p2)
            self._log("[VER] "+subprocess.list2cmdline(c))
        except FileNotFoundError:
            self._toast(T("warn_tit"),V_("No se encuentra ffplay (tiene que estar en la carpeta «bin», junto a ffmpeg).","ffplay not found (it must be in the «bin» folder, next to ffmpeg)."),tipo="warning",seg=6)
        except Exception as e:self._toast(T("error_tit"),str(e),tipo="error")
    def _vplay_parar(self):
        for p in getattr(self,"_vproc",()) or ():
            try:
                if p.poll() is None:p.kill()
            except Exception:pass
        self._vproc=()
    # ---------- ondas de cada canal (antes y después) ----------
    def _onda_generar(self):
        j=self._job()
        if not j or self._a_i is None:return
        t=j["a"][self._a_i];ruta=self.actual;V_=self._vt
        if t["ext"]:inf=self._ext_info.get(t["ext"],{});src=t["ext"]
        else:inf=self.info[ruta];src=inf.get("entrada",ruta)
        d=_dur(inf) or 0.0;tr=float(self.var_onda_tr.get() or 0);T_=min(d,tr) if tr>0 and d else (d or tr or 300.0)
        g=self._a_grafo(t,f"[0:{t['idx']}]","[o]")
        dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        try:W=max(400,self.cv_onda.winfo_width()-112)
        except Exception:W=1100
        K=max(1,int(round(48000.0*T_/(W*8))))   # 8 columnas por pixel: el «Detalle» x8 sigue siendo de la señal entera
        env=(f"aresample=48000,aformat=sample_fmts=fltp,asetnsamples=n={K}:p=0,astats=metadata=1:reset=1:measure_perchannel=Min_level+Max_level:"
             "measure_overall=none,ametadata=mode=print:file=-")
        self.lbl_onda.configure(text=V_("Calculando las ondas...","Computing the waves..."));self._onda_n=getattr(self,"_onda_n",0)+1;n=self._onda_n
        def hilo():
            res=[]
            for proc in (False,True):
                if proc and g:i_=g.rfind("[o]");arg=["-filter_complex",g[:i_]+"[o0];[o0]"+env+g[i_:],"-map","[o]"]
                else:arg=["-map",f"0:{t['idx']}","-af",env]
                c=[FFMPEG,"-hide_banner","-nostats","-v","error"]+dvd+["-t",f"{T_*(_fps_f(t) if proc else 1.0):.3f}","-i",src]+arg+["-f","null","-"]
                try:res.append(self._onda_env(self._onda_ff(c,T_*(_fps_f(t) if proc else 1.0),0.5 if proc else 0.0,n),t["nch"]))
                except Exception as e:self._ls(f"[ONDAS] {e}");res.append(None)
            self._ui(self._onda_fin,n,(self.actual,self._a_i),t,T_,res)
        threading.Thread(target=hilo,daemon=True).start()
    @staticmethod
    def _onda_env(txt,nch):
        """lo que escribe astats por bloques -> por canal (minimos, maximos, pico), de -1 a 1: la señal entera, sin reducir"""
        mn=[[] for _ in range(nch)];mx=[[] for _ in range(nch)]
        for m_ in re.finditer(r"lavfi\.astats\.(\d+)\.(Min|Max)_level=(\S+)",txt):
            c=int(m_.group(1))-1
            if 0<=c<nch:
                try:v=max(-1.0,min(1.0,float(m_.group(3))))
                except ValueError:v=0.0
                (mn if m_.group(2)=="Min" else mx)[c].append(v)
        out=[]
        for a,b in zip(mn,mx):
            n=min(len(a),len(b))
            if n<2:return None
            a=a[:n];b=b[:n];out.append((a,b,max(max(b),-min(a))))
        return out
    def _onda_pronto(self,ms=800):
        """se rehacen las ondas cuando paran los cambios (Presencia, tramo)"""
        try:
            if getattr(self,"_avz",None)!="a":return
            if getattr(self,"_onda_id",None):self.root.after_cancel(self._onda_id)
            self._onda_id=self.root.after(ms,self._onda_generar)
        except Exception:pass
    def _onda_ff(self,c,tot,base,n):
        """(JMG, 10-11) el FFmpeg de las ondas con su avance en la barra de abajo (antes 0-50 %, después 50-100 %): así se ve que trabaja"""
        c=c[:-3]+["-progress","pipe:2"]+c[-3:]
        p=subprocess.Popen(c,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CNW)
        out=[];th=threading.Thread(target=lambda:out.append(p.stdout.read()),daemon=True);th.start()
        V_=self._vt
        for l in p.stderr:
            l=l.decode("utf-8","ignore").strip()
            if not (l.startswith("out_time_us=") or l.startswith("out_time_ms=")):continue
            try:s=int(l.split("=")[1])/1e6
            except ValueError:continue
            if n!=getattr(self,"_onda_n",0) or getattr(self,"procesando",False):continue
            fr=base+0.5*max(0.0,min(1.0,s/tot)) if tot>0 else base
            self._set_prog(100.0*fr);self._st(V_(f"Calculando las ondas · {100*fr:.0f} %",f"Computing the waves · {100*fr:.0f} %"))
        p.wait();th.join(timeout=10)
        return (out[0] if out else b"").decode("utf-8","ignore")
    def _onda_fin(self,n,de,t,T_,res):
        if n!=getattr(self,"_onda_n",0):return
        if not getattr(self,"procesando",False):self.prog.configure(value=0);self._st("")
        if getattr(self,"_onda_de",None)!=de:self._onda_x0=0.0
        self._onda=(t,T_,res);self._onda_de=de;self._onda_pos=min(self._onda_pos,T_)
        self.lbl_onda.configure(text=self._vt(f"Tramo de {_hms(T_).split('.')[0]}",f"Segment of {_hms(T_).split('.')[0]}"));self._onda_pintar()
    _ONDA_COL={"FL":"#5c7cfa","FR":"#5c7cfa","FC":"#e64980","LFE":"#e64980","BL":"#d4a017","BR":"#d4a017","SL":"#d4a017","SR":"#d4a017","BC":"#d4a017"}
    _ONDA_OSC={"#5c7cfa":"#3b5bdb","#e64980":"#c2255c","#d4a017":"#b07d00"}
    def _onda_pintar(self):
        """como la Visualizacion de Jmg AudioProcesador: cada canal relleno (arriba y abajo), ANTES en claro y DESPUES en oscuro"""
        import math
        cv=self.cv_onda;cv.delete("all")
        W=cv.winfo_width();H=cv.winfo_height()
        if W<50 or H<50:return
        if not self._onda:
            cv.create_text(W//2,H//2,text=self._vt("Calculando las ondas de cada canal, antes y después de los efectos...","Computing the waves of each channel, before and after the effects..."),fill="#c0c0c0",font=("",10));return
        t,T_,res=self._onda;chans=LAYCH.get(t["lay"]) or [f"c{i}" for i in range(t["nch"])]
        try:zoom=float(self.var_onda_zoom.get() or 1)
        except Exception:zoom=1.0
        izq=110;n=len(chans);fila=(H-44)/(2*max(1,n));ancho=W-izq-2
        det=self._onda_det();x0=self._onda_x0;tot=ancho*det;p0=int(x0*tot)
        try:self.sb_onda.set(x0,min(1.0,x0+1.0/det))
        except Exception:pass
        for b_,(tit,datos) in enumerate(((self._vt("ANTES · original","BEFORE · original"),res[0]),(self._vt("DESPUÉS · con todos los efectos","AFTER · with all the effects"),res[1]))):
            despues=b_==1;y0=22+b_*(n*fila+22)
            bg="#0b0b0b" if despues else "#f5f5f5";lin="#3b82f6" if despues else "#9a9a9a";guia="#2e2e2e" if despues else "#d0d0d0"
            cv.create_rectangle(0,y0-20,W,y0,fill="#3a3a3a" if despues else "#5a5a5a",outline="");cv.create_text(8,y0-10,text=tit,anchor="w",fill="#ffffff",font=("",9,"bold"))
            for k,c in enumerate(chans):
                y=y0+k*fila;yc=y+fila/2.0;mitad=fila/2.0-3
                col=self._ONDA_COL.get(c,"#22b8cf")
                if not despues:col=self._ONDA_OSC.get(col,col)
                cv.create_rectangle(izq,y,izq+ancho,y+fila,fill=bg,outline="")
                g=0.5*mitad*zoom
                if g<mitad:
                    for s in (-1,1):cv.create_line(izq,yc+s*g,izq+ancho,yc+s*g,fill=guia)
                cv.create_rectangle(2,y+4,5,y+fila-4,fill=col,outline="")
                cv.create_text(10,yc-7,text=c,anchor="w",fill="#e0e0e0",font=("",9,"bold"))
                if datos and k<len(datos) and datos[k]:
                    mins,maxs,pk=datos[k];m=len(maxs);paso=m/float(tot)
                    sup=[];inf_=[]
                    for i in range(int(ancho)):
                        a_=int((p0+i)*paso);b_=max(a_+1,int((p0+i+1)*paso))
                        if a_>=m:break
                        x=izq+i;hi=max(maxs[a_:b_]);lo=min(mins[a_:b_])
                        y1=yc-max(-1.0,min(1.0,hi*zoom))*mitad;y2=yc-max(-1.0,min(1.0,lo*zoom))*mitad
                        if y2-y1<1.0:y2=y1+1.0
                        sup.append((x,y1));inf_.append((x,y2))
                    pts=[]
                    for q in sup+inf_[::-1]:pts.extend(q)
                    cv.create_line(izq,yc,izq+ancho,yc,fill=lin)
                    if len(pts)>=6:cv.create_polygon(pts,fill=col,outline=col)
                    cv.create_text(10,yc+8,anchor="w",text=(self._vt("pico ","peak ")+"%.1f dBFS"%(20*math.log10(pk))) if pk>1e-6 else self._vt("silencio","silence"),fill="#a0a0a0",font=("",8))
                cv.create_line(0,y+fila,W,y+fila,fill="#404040")
        self._onda_geo=(izq,ancho,n,fila,T_)
        self._onda_cursor()
    def _onda_det(self):
        try:return max(1,int(self.var_onda_det.get() or 1))
        except Exception:return 1
    def _onda_cursor(self,p=None):
        """la raya roja: donde se escucha (p) o donde esta el cursor; si se sale de lo que se ve mientras suena, la vista la sigue"""
        cv=self.cv_onda;cv.delete("cur")
        g=getattr(self,"_onda_geo",None)
        if not g or not self._onda:return
        izq,ancho,n,fila,T_=g;det=self._onda_det();tot=ancho*det
        q=self._onda_pos if p is None else p
        xv=q/max(1.0,T_)*tot-self._onda_x0*tot
        if p is not None and det>1 and not (0<=xv<ancho):   # sonando: pasa a la pagina siguiente
            self._onda_x0=max(0.0,min(1.0-1.0/det,q/max(1.0,T_)-0.05/det));self._onda_pintar();return
        if 0<=xv<=ancho:
            for b_ in (0,1):
                y0=22+b_*(n*fila+22);cv.create_line(izq+xv,y0,izq+xv,y0+n*fila,fill="#ff4040",width=2,tags="cur")
    def _onda_scroll(self,*a):
        det=self._onda_det();x0=self._onda_x0
        if a and a[0]=="moveto":x0=float(a[1])
        elif a and a[0]=="scroll":x0+=int(a[1])*(0.1 if a[2]=="units" else 0.9)/det
        self._onda_x0=max(0.0,min(1.0-1.0/det,x0));self._onda_pintar()
    def _onda_detalle(self):
        """al cambiar el «Detalle», la vista se queda alrededor del cursor"""
        det=self._onda_det();T_=self._onda[1] if self._onda else 1.0
        self._onda_x0=max(0.0,min(1.0-1.0/det,self._onda_pos/max(1.0,T_)-0.5/det));self._onda_pintar()
    def _onda_clic(self,e):
        if not self._onda or not getattr(self,"_onda_geo",None):return
        izq,ancho,n,fila,T_=self._onda_geo;tot=ancho*self._onda_det()
        if e.x<izq:return
        self._onda_pos=round(max(0.0,min(T_,(e.x-izq+self._onda_x0*tot)/tot*T_)),3);self._onda_cursor()
        self._oir(True,desde=self._onda_pos)
    def _oir_pos(self):
        """segundo que esta sonando (desde donde empezo + lo que lleva) o None si no suena"""
        if getattr(self,"_repro",None) is None:return None
        return getattr(self,"_oir_desde",0.0)+max(0.0,time.time()-getattr(self,"_oir_t0",time.time())-0.25)   # 0,25 s en arrancar
    def _onda_sigue(self):
        """mientras suena, la raya roja va con el sonido"""
        if getattr(self,"_avz",None)!="a":return
        p=self._oir_pos()
        if p is None:return
        if self._onda and p>=self._onda[1]:p=self._onda[1]
        self._onda_cursor(p);self.root.after(150,self._onda_sigue)
    def _onda_pausa(self):
        """⏸: se para donde va (y la raya se queda ahí); otra vez: sigue desde ahí, igual que sonaba"""
        p=self._oir_pos()
        if p is not None:
            self._oir_parar();self._onda_pos=round(min(p,self._onda[1]) if self._onda else p,3);self._onda_pausado=True;self._onda_cursor()
        elif getattr(self,"_onda_pausado",False):self._oir(getattr(self,"_oir_proc",True),desde=self._onda_pos)
    def _onda_parar(self):
        """⏹: se para y vuelve al principio"""
        self._oir_parar();self._onda_pos=0.0;self._onda_pausado=False;self._onda_x0=0.0;self._onda_pintar()
    # ---------- «Auto» de la imagen (brillo, contraste, saturación, nitidez y ruido) ----------
    def _img_medir(self,ruta,j):
        """mide 8 puntos de la pelicula (sin las bandas negras): brillo medio, contraste, saturacion, ruido (PSNR frente a quitarle
        el ruido) y nitidez (PSNR frente a desenfocarla) -> (ajustes, texto). Prudente: el cine es oscuro y poco saturado a proposito"""
        V_=self._vt;inf=self.info[ruta];vs=_vstream(inf) or {}
        if _hdr_tipo(vs)!="SDR":return None,V_("Película HDR: su imagen no se mide con las reglas de SDR; retócala a mano si hace falta.","HDR movie: its picture is not measured with SDR rules; adjust it by hand if needed.")
        d=_dur(inf) or 60.0;ent=inf.get("entrada",ruta);dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        c=j["v"].get("crop","");pre=(f"crop={c}," if c not in ("","no",None) else "")+("bwdif," if _entrelazado(vs) else "")+"fps=4,scale=480:-2,format=yuv420p"
        Y=[];R=[];S=[];pn=[];ps=[]
        for k in range(8):
            p=d*(0.1+0.8*k/7)
            g=(f"[0:{vs['index']}]{pre},split=5[a][b][c][d][e];[a]signalstats,metadata=print:file=-[s];[b]hqdn3d=4:3:6:4.5[bn];[c][bn]psnr@n,nullsink;"
               f"[d]gblur=sigma=1.2[bs];[e][bs]psnr@s,nullsink")
            try:r=rh([FFMPEG,"-hide_banner"]+dvd+["-ss",f"{p:.2f}","-t","1","-i",ent,"-filter_complex",g,"-map","[s]","-f","null","-"],timeout=120)
            except Exception:continue
            Y+=[float(x) for x in re.findall(r"signalstats\.YAVG=([\d.]+)",r.stdout or "")]
            S+=[float(x) for x in re.findall(r"signalstats\.SATAVG=([\d.]+)",r.stdout or "")]
            lo=[float(x) for x in re.findall(r"signalstats\.YLOW=([\d.]+)",r.stdout or "")];hi=[float(x) for x in re.findall(r"signalstats\.YHIGH=([\d.]+)",r.stdout or "")]
            R+=[h-l for h,l in zip(hi,lo)]
            for nm,L in (("n",pn),("s",ps)):
                m=re.search(r"\[psnr@"+nm+r" @[^\]]*\] PSNR .*?average:([\d.]+|inf)",r.stderr or "")
                if m and m.group(1)!="inf":L.append(float(m.group(1)))
        if not Y or not R:return None,V_("No se ha podido medir la imagen.","Could not measure the picture.")
        av=lambda L:sum(L)/len(L);cl=lambda x,a,b:max(a,min(b,x))
        y=av(Y);rg=av(R);sa=av(S) if S else 10.0;n_=av(pn) if pn else 50.0;s_=av(ps) if ps else 40.0
        aj={k:0 for k in VIMG_KEYS if k!="tono"}   # (JMG, 20-11) el tono no se mide: el Auto no lo toca
        if y<45:aj["brillo"]=int(cl(round((55-y)/6),1,3))
        elif y>120:aj["brillo"]=-int(cl(round((y-110)/6),1,3))
        if rg<65:aj["contraste"]=int(cl(round((75.0/max(1.0,rg)-1)/0.05),1,3))
        if sa<7:aj["satur"]=int(cl(round((8.5/max(0.5,sa)-1)/0.08),1,3))
        aj["ruido"]=3 if n_<43 else (2 if n_<45.5 else (1 if n_<46.5 else 0))   # peliculas limpias: 47-49
        aj["nitidez"]=2 if s_>44 else (1 if s_>42.5 else 0)
        if aj["ruido"]>=2:aj["nitidez"]=max(0,aj["nitidez"]-1)   # no se afila el ruido
        self._ls(f"[IMAGEN] Y {y:.0f} · rango {rg:.0f} · saturación {sa:.1f} · PSNR ruido {n_:.1f} · PSNR desenfoque {s_:.1f} -> {aj}")
        if not any(aj.values()):return aj,V_("La imagen ya está bien: no hace falta tocarla (todo a 0).","The picture is already fine: no need to touch it (all at 0).")
        nom={"brillo":V_("brillo","brightness"),"contraste":V_("contraste","contrast"),"satur":V_("saturación","saturation"),"tono":V_("tono","hue"),"nitidez":V_("nitidez","sharpness"),"ruido":V_("quitar ruido","denoise")}
        return aj," · ".join(f"{nom[k]} {v:+d}" if k in ("brillo","contraste","satur") else f"{nom[k]} {v}" for k,v in aj.items() if v)+V_("\nEs un punto de partida: retócalo a mano si quieres.","\nIt is a starting point: adjust it by hand if you like.")
    def _auto_img(self):
        j=self._job();V_=self._vt;ruta=self.actual;k=(ruta,"v","img");h=self._auto_hecho.get(k)
        if h and all(j["v"].get(x,0)==h.get(x,0) for x in h):
            for x in h:getattr(self,"var_"+x).set(0)
            self._auto_hecho.pop(k,None)
            self._toast(T("info_tit"),V_("«Auto» otra vez: la imagen vuelve a 0.","«Auto» again: the picture goes back to 0."),seg=4);return
        self._escaneando=True
        for b in self._auto_bts.values():b.state(["disabled"])
        self._st(V_("Midiendo la imagen...","Measuring the picture..."))
        def hilo():
            try:aj,txt=self._img_medir(ruta,j)
            except Exception as e:aj,txt=None,str(e)
            self._ui(self._auto_img_fin,ruta,aj,txt)
        threading.Thread(target=hilo,daemon=True).start()
    def _auto_img_fin(self,ruta,aj,txt):
        self._escaneando=False;self._st("")
        for b in self._auto_bts.values():b.state(["!disabled"])
        if aj is None:self._toast(T("warn_tit"),txt,tipo="warning",seg=6);return
        j=self.jobs.get(ruta)
        if not j:return
        if ruta==self.actual:
            for x in aj:getattr(self,"var_"+x).set(aj[x])   # las trazas guardan, pasan de Passthrough a recomprimir y refrescan la vista
        else:j["v"].update(aj)
        self._auto_hecho[(ruta,"v","img")]=dict(aj)
        self._toast("Auto",txt,seg=7)
    # ---------- «▶ Revisar sincronización»: la película con la pista, en una ventana de vídeo con sonido (ffplay) ----------
    def _rev_ventana(self,nombre,dur,tl,dl,ref_txt,jugar,parar,sal0="mc"):
        """ventana comun (igual en Jmg AudioProcesador y Jmg VideoEncoder): desde donde, que se oye y por donde.
        jugar(pos, modo, sal) con modo corr / sin / ref y sal mc / st; parar() corta la reproduccion"""
        V=self._vt;hm=lambda s:"%d:%02d:%02d"%(int(s)//3600,int(s)%3600//60,int(s)%60)
        try:
            w0=getattr(self,"_rev_top",None)
            if w0 is not None and w0.winfo_exists():w0.destroy()
        except Exception:pass
        parar()
        w=tk.Toplevel(self.root);w.title(V("Revisar sincronización","Check synchronization"));w.configure(bg=CF);w.transient(self.root);self._rev_top=w
        self._bloquear_principal(True);w.bind("<Destroy>",lambda e:self._bloquear_principal(False) if e.widget is w else None,add="+")   # (JMG, 8-11) modal
        w.after(200,lambda:(w.winfo_exists() and w.grab_set()))
        f=ttk.Frame(w);f.pack(fill="both",expand=True,padx=14,pady=12)
        ttk.Label(f,text="▶ "+V("Revisar sincronización","Check synchronization")+" · "+nombre,font=("",10,"bold")).grid(row=0,column=0,columnspan=4,sticky="w")
        ttk.Label(f,text=V("La película se ve en su propia ventana, con la pista tal como saldrá. Mira los labios y los golpes: si se oyen a la vez que se ven, está bien. "
                           "Si dudas, escucha también la de referencia en el mismo momento.",
                           "The movie plays in its own window, with the track as it will come out. Watch the lips and the hits: if they are heard when they are seen, it is fine. "
                           "If in doubt, also listen to the reference one at the same moment."),
                  foreground=CA,font=("",8,"italic"),wraplength=540,justify="left").grid(row=1,column=0,columnspan=4,sticky="w",pady=(2,8))
        D=max(1,int(dur or 0))
        pos=tk.IntVar(value=max(0,min(D-1,int(getattr(self,"_rev_pos",0) or min(600,D//3)))))
        self._sl(f,V("Desde (s):","From (s):"),pos,0,D,2,sl=380)
        lh=ttk.Label(f,text=hm(pos.get()),font=("",10,"bold"));lh.grid(row=2,column=3,sticky="w",padx=(4,0))
        def _pos_cambio(*a):
            try:lh.configure(text=hm(pos.get()));self._rev_pos=pos.get()
            except Exception:pass
        pos.trace_add("write",_pos_cambio)
        fi=ttk.Frame(f);fi.grid(row=3,column=0,columnspan=4,sticky="w",pady=(2,4))
        for s_ in (-60,-10,10,60):
            ttk.Button(fi,text=("%+d s"%s_) if abs(s_)<60 else ("%+d min"%(s_//60)),width=7,command=lambda s_=s_:pos.set(max(0,min(D,pos.get()+s_)))).pack(side="left",padx=(0,4))
        if tl:
            ttk.Label(fi,text="   "+V("Ir al tramo:","Go to part:")).pack(side="left",padx=(4,4))
            ops=[f"{i+1} · {hm(c0)} · {dl-v0:+.0f} ms" for i,(c0,c1,v0,v1) in enumerate(tl)]
            cb=ttk.Combobox(fi,values=ops,state="readonly",width=26);cb.pack(side="left")
            cb.bind("<<ComboboxSelected>>",lambda e:pos.set(max(0,int(tl[cb.current()][0])-3)))   # 3 s antes del corte: se ve el cambio
        modo=tk.StringVar(value="corr")
        ttk.Label(f,text=V("Se oye:","You hear:"),font=("",9,"bold")).grid(row=4,column=0,columnspan=4,sticky="w",pady=(8,2))
        for i,(v_,t_) in enumerate((("corr",V("La pista corregida (como saldrá)","The corrected track (as it will come out)")),
                                    ("sin",V("La pista sin corregir","The track without correction")),
                                    ("ref",V("La de referencia: ","The reference one: ")+(ref_txt or V("(ninguna)","(none)"))))):
            rb=ttk.Radiobutton(f,text=t_,variable=modo,value=v_);rb.grid(row=5+i,column=0,columnspan=4,sticky="w",padx=8)
            if v_=="ref" and not ref_txt:rb.state(["disabled"])
        sal=tk.StringVar(value=sal0 if sal0 in ("mc","st") else "mc")
        fs=ttk.Frame(f);fs.grid(row=8,column=0,columnspan=4,sticky="w",pady=(8,2))
        ttk.Label(fs,text=V("Salida:","Output:"),font=("",9,"bold")).pack(side="left",padx=(0,6))
        ttk.Radiobutton(fs,text=V("Multicanal (5.1 / 7.1)","Multichannel (5.1 / 7.1)"),variable=sal,value="mc").pack(side="left",padx=(0,8))
        ttk.Radiobutton(fs,text=V("Estéreo","Stereo"),variable=sal,value="st").pack(side="left")
        fb=ttk.Frame(f);fb.grid(row=9,column=0,columnspan=4,sticky="ew",pady=(12,0))
        ttk.Button(fb,text="▶ "+V("Reproducir","Play"),command=lambda:jugar(float(pos.get()),modo.get(),sal.get())).pack(side="left")
        ttk.Button(fb,text="⏹ "+V("Parar","Stop"),command=parar).pack(side="left",padx=6)
        ttk.Button(fb,text=V("Cerrar","Close"),command=w.destroy).pack(side="right")
        ttk.Label(f,text=V("Cada vez que pulsas «Reproducir» empieza desde el punto elegido. Puedes cambiar el delay en la ventana principal y volver a reproducir.",
                           "Each time you press «Play» it starts from the chosen point. You can change the delay in the main window and play again."),
                  foreground=CA,font=("",8,"italic"),wraplength=540,justify="left").grid(row=10,column=0,columnspan=4,sticky="w",pady=(8,0))
        w.bind("<Destroy>",lambda e:parar() if e.widget is w else None,add="+")   # (JMG, 11-11) add="+": sin él se perdía el desbloqueo de la ventana principal
        try:
            w.update_idletasks();w.geometry(f"+{self.root.winfo_rootx()+60}+{self.root.winfo_rooty()+60}")
        except Exception:pass
        return w
    def _rev_lanzar(self,c,tit):
        """FFmpeg prepara la imagen y el sonido -> ffplay los enseña en su ventana"""
        V=self._vt;self._rev_parar()
        ff=[FFPLAY,"-hide_banner","-loglevel","error","-autoexit","-window_title",tit,"-x","1280","-y","720","-i","-"]
        try:
            p1=subprocess.Popen(c,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,creationflags=CNW)
            p2=subprocess.Popen(ff,stdin=p1.stdout,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=CNW)
            p1.stdout.close();self._rev_proc=(p1,p2)
            self._log("[REVISAR] "+subprocess.list2cmdline(c))
        except FileNotFoundError:
            self._toast(T("warn_tit"),V("No se encuentra ffplay (tiene que estar en la carpeta «bin», junto a ffmpeg).","ffplay not found (it must be in the «bin» folder, next to ffmpeg)."),tipo="warning",seg=6)
        except Exception as e:self._toast(T("error_tit"),str(e),tipo="error")
    def _rev_parar(self):
        for p in getattr(self,"_rev_proc",()) or ():
            try:
                if p.poll() is None:p.kill()
            except Exception:pass
        self._rev_proc=()
    _REV_VID=["-vf","scale=w=min(1280\\,iw):h=-2,format=yuv420p","-sn","-dn","-c:v","libx264","-preset","ultrafast","-tune","zerolatency","-crf","20","-c:a","pcm_s16le","-f","matroska","-"]
    def _sinc_revisar(self):
        """«▶ Revisar sincronización»: el vídeo con la pista activa como saldrá (delay, tramos y efectos), la sin corregir o la de referencia"""
        j=self._job();V_=self._vt
        if not j or self._a_i is None:
            self._toast(T("warn_tit"),V_("Elige primero una pista de audio.","Choose an audio track first."),tipo="warning",seg=4);return
        self._guardar_trabajo()
        ruta=self.actual;inf=self.info[ruta];ai=self._a_i
        ops=getattr(self,"_aref_ops",[]);i=self.cb_aref.current()
        ref_i=ops[i][0] if ops and i>=0 else None;ref_txt=self.cb_aref.get() if ref_i is not None else ""
        t=j["a"][ai];tr=t.get("tramos");d=int(t.get("delay") or 0)
        tl=tr["tl"] if tr and abs(d-tr["d"])==0 else []
        def jugar(pos,modo,sal):
            jj=self.jobs.get(ruta)
            if not jj:return
            self._rev_sal=sal;self._vplay_parar();self._oir_parar()
            tt=jj["a"][ref_i if modo=="ref" and ref_i is not None else ai];fa=_fps_f(tt) if modo=="corr" else 1.0
            vs=_vstream(inf) or {};dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
            c=[FFMPEG,"-hide_banner","-v","error"]+dvd+["-ss",f"{pos:.3f}","-i",inf.get("entrada",ruta)]
            if tt["ext"] or fa!=1.0:c+=["-ss",f"{pos*fa:.3f}"]+(dvd if not tt["ext"] else [])+["-i",tt["ext"] or inf.get("entrada",ruta)]
            src=f"{1 if (tt['ext'] or fa!=1.0) else 0}:{tt['idx']}"
            g=self._a_grafo(tt,f"[{src}]","[ao]",off=pos) if modo=="corr" else None
            c+=["-map",f"0:{vs.get('index',0)}"]+(["-filter_complex",g,"-map","[ao]"] if g else ["-map",src])+(["-ac","2"] if sal=="st" else [])
            vid=list(self._REV_VID)
            if _entrelazado(vs):vid[1]="bwdif,"+vid[1]
            tit=("Jmg VideoEncoder · "+{"corr":V_("corregida","corrected"),"sin":V_("sin corregir","uncorrected"),"ref":V_("referencia","reference")}[modo]+
                 f" · #{tt['idx'] if not tt['ext'] else 'ext.'} [{tt['lang']}] · "+self._nombre(ruta))
            self._rev_lanzar(c+vid,tit)
        nom=f"#{t['idx'] if not t['ext'] else 'ext.'} [{t['lang']}] {t['tit']}".strip()
        self._rev_ventana(nom,_dur(inf),tl,d,ref_txt,jugar,self._rev_parar,getattr(self,"_rev_sal",None) or self.var_oir_sal.get())
    # ---------- framerate de las pistas y los subtítulos (25 fps de una edición PAL en una película de 23,976) ----------
    def _fps_video(self):
        """framerate del video activo, como codigo de FPS_OPS"""
        try:return _fps_cerca(_fps(_vstream(self.info[self.actual])))
        except Exception:return "23.976"
    def _fps_fila(self,p,row,v_de,v_a,v_met):
        """fila «Framerate: De [..] a [..] fps» (y el método, en el audio) en la fila row de p (grid)"""
        V_=self._vt;fr=ttk.Frame(p);fr.grid(row=row,column=0,columnspan=3,sticky="w",padx=5,pady=(2,4))
        ttk.Label(fr,text=V_("Framerate: de","Framerate: from")).pack(side="left")
        self._combo(fr,FPS_OPS,v_de,7).pack(side="left",padx=(4,4))
        ttk.Label(fr,text=V_("a","to")).pack(side="left")
        self._combo(fr,FPS_OPS,v_a,7).pack(side="left",padx=(4,4))
        ttk.Label(fr,text="fps").pack(side="left",padx=(0,10))
        if v_met is not None:
            self._combo(fr,[("tono",V_("Con cambio de tono (el más limpio)","With pitch change (the cleanest)")),("atempo",V_("Sin cambio de tono","Without pitch change"))],v_met,28).pack(side="left")
        return fr
    def _fps_detectar(self,nuevas,inf):
        """pista de otro archivo: si dura un 4 % menos (o más) que el video, viene de una edición de 25 fps (o al revés):
        se le pone el cambio de framerate y se avisa. Devuelve el aviso o "" """
        try:
            dv=_dur(self.info[self.actual]);da=_dur(inf);vf=self._fps_video()
            if dv<20 or da<20:return ""   # en clips muy cortos no se puede saber
            r=da/dv;fv=float(_fps_fr(vf))
            if abs(r-1.0)<0.006:return ""   # dura lo mismo que el video: va a su misma velocidad (23,976 y 24 solo se llevan un 0,1 %)
            err,c=min((abs(r-fv/float(_fps_fr(c_))),c_) for c_,_ in FPS_OPS if c_!=vf)   # el framerate que mejor encaja
            for c in ([c] if err<0.0035 else []):   # misma pelicula a otra velocidad (25 y 23,976 se llevan un 4 %)
                    for t in nuevas:
                        t["fps_de"],t["fps_a"],t["fps_met"]=c,vf,"tono"
                        if t["cod"]=="copy":t["cod"]=ACOD_DE_ORIGEN.get(t["codec_in"],"eac3");t["kbps"]=0
                    V_=self._vt;a_=c.replace(".",",");b_=vf.replace(".",",")
                    self._log(f"[FPS] {os.path.basename(str(inf.get('format',{}).get('filename','')))}: {da:.1f} s / {dv:.1f} s -> {a_} -> {b_} fps")
                    return V_(f"La pista dura un {abs(1-r)*100:.1f} % ".replace(".",",")+f"{'menos' if r<1 else 'más'} que el vídeo: viene de una edición de {a_} fps. "
                              f"Le he puesto el cambio de framerate de {a_} a {b_} (Audio → Sincronización). Después calcula el delay.",
                              f"The track is {abs(1-r)*100:.1f} % {'shorter' if r<1 else 'longer'} than the video: it comes from a {a_} fps edition. "
                              f"I have set the framerate change from {a_} to {b_} (Audio → Synchronization). Then calculate the delay.")
        except Exception as e:self._log(f"[FPS] {e}")
        return ""
    def _s_fmt_txt(self,s):
        """columna Formato de la lista de subtitulos, con su framerate y delay si los tiene"""
        x=str(s["fmt"]).upper()
        if _fps_q(s):x+=f" · {s['fps_de'].replace('.',',')}→{s['fps_a'].replace('.',',')}"
        if s.get("delay"):x+=f" · {int(s['delay']):+d} ms"
        return x
    # ---------- ventana de información antes de procesar (como la de Jmg AudioProcesador) ----------
    def _resumen(self,cola):
        V_=self._vt;lin=[];usados=set();mini=[]
        nom={"brillo":V_("brillo","brightness"),"contraste":V_("contraste","contrast"),"satur":V_("saturación","saturation"),"tono":V_("tono","hue"),"nitidez":V_("nitidez","sharpness"),"ruido":V_("quitar ruido","denoise")}
        for ruta in cola:
            j=self.jobs[ruta];v=j["v"]
            try:sal,av=self._salida(ruta,j,probar=True,usados=usados);usados.add(os.path.normcase(sal))
            except Exception:sal,av="?",[]
            mini.append(f"• {self._nombre(ruta)}  →  {os.path.basename(sal)}")
            lin.append(f"\n  >> {self._nombre(ruta)}");lin.append("     → "+sal)
            if v["codec"]=="copy":vt=V_("Vídeo: Passthrough (no se recomprime)","Video: Passthrough (not re-encoded)")
            else:
                vt=V_("Vídeo: ","Video: ")+dict(VCODECS).get(v["codec"],v["codec"])+" · "+("CPU" if v.get("motor","cpu")=="cpu" else str(v.get("motor")).upper())
                if v["codec"] not in INTRA:
                    vt+=(V_(f" · calidad {v.get('crf')}",f" · quality {v.get('crf')}") if v.get("modo")=="q" else f" · {v.get('kbps')} kbps"+(V_(" · 2 pasadas"," · 2 passes") if v.get("pasadas2") else ""))
            e_=self._enc(v)
            if e_ in OPC and self._opc_cambiadas(e_,(v.get("opc") or {}).get(e_)):vt+=" · ⚙ "+self._opc_resumen(e_,(v.get("opc") or {}).get(e_))   # (JMG, 12-11)
            lin.append("     "+vt)
            im=[f"{nom[k]} {int(v.get(k) or 0):+d}" for k in VIMG_KEYS if v.get(k)]
            if im:lin.append("     "+V_("Imagen: ","Picture: ")+", ".join(im))
            tr=(j.get("rec") or {}).get("tramos") or []
            if tr:lin.append("     "+V_(f"Recorte: {len(tr)} tramo(s), {_hms(sum(b-a for a,b in tr)).split('.')[0]}",f"Trim: {len(tr)} part(s), {_hms(sum(b-a for a,b in tr)).split('.')[0]}"))
            for t in j["a"]:
                if t["incl"]:lin.append(f"     ♪ #{t['idx'] if not t['ext'] else 'ext.'} [{t['lang']}] {t['tit'][:28]} → "+self._a_texto(t))
            ns=sum(1 for s in j["s"] if s["incl"])
            if ns:lin.append("     "+V_(f"Subtítulos: {ns}",f"Subtitles: {ns}"))
            for s_ in j["s"]:
                if s_.get("burn"):lin.append("     "+V_("Subtítulo grabado en la imagen: ","Subtitle burned in: ")+f"[{s_['lang']}] {s_['tit'] or (os.path.basename(s_['ext']) if s_['ext'] else '')}")
            for a_ in av:lin.append("     ⚠ "+a_);mini.append("   ⚠ "+a_)
            try:
                w_=self._pasos(ruta,j,sal,"pase",0)
                lin.append("     "+V_("Órdenes de FFmpeg:","FFmpeg commands:"))
                for c_,_ in w_["pasos"]+([(w_["concat"]["cmd"],0)] if w_["concat"] else []):lin.append("       "+subprocess.list2cmdline(c_))
            except Exception as e:lin.append(f"     ({e})")
        cab=V_(f"Vídeos: {len(cola)}    Contenedor: {self._cont(self.jobs[cola[0]],cola[0]).upper()}",f"Videos: {len(cola)}    Container: {self._cont(self.jobs[cola[0]],cola[0]).upper()}")
        mn=cab+"\n\n"+"\n".join(mini)+V_("\n\n«🔍 Ver todo»: vídeo, imagen, recorte, cada pista, subtítulos y las órdenes de FFmpeg (se puede copiar).\n\n¿Empezar?",
                                         "\n\n«🔍 See everything»: video, picture, trimming, each track, subtitles and the FFmpeg commands (it can be copied).\n\nStart?")
        return mn,cab+"\n"+"\n".join(lin)
    def _cfg_x(self,k,v=None):
        """ajuste suelto de config.json (carpeta de FFmpeg, donde esta el otro programa); v=None = leer"""
        if v is None:return self._cfg.get(k,"")
        self._cfg[k]=v;self._save_cfg()
    # ---------- Salida -> FFmpeg: usar el de otra carpeta ----------
    def _ff_ui(self,P,row):
        V=self._vt
        ttk.Separator(P,orient="horizontal").grid(row=row,column=0,columnspan=3,sticky="ew",pady=(12,6))
        ttk.Label(P,text="FFmpeg",font=("",10,"bold")).grid(row=row+1,column=0,columnspan=3,sticky="w",pady=(4,2))
        fr=ttk.Frame(P);fr.grid(row=row+2,column=0,columnspan=3,sticky="w")
        self.lbl_ff=ttk.Label(fr,text="",foreground=CID,wraplength=420,justify="left");self.lbl_ff.pack(anchor="w")
        fb=ttk.Frame(fr);fb.pack(anchor="w",pady=(4,0))
        ttk.Button(fb,text="📁 "+V("Elegir carpeta...","Choose folder..."),command=self._ff_elegir).pack(side="left")
        ttk.Button(fb,text=V("Usar el del programa","Use the program's own"),command=lambda:self._ff_poner("")).pack(side="left",padx=6)
        ttk.Label(P,text=V("Si tienes Jmg AudioProcesador y Jmg VideoEncoder, los dos pueden usar el mismo FFmpeg: elige la carpeta «bin» del otro "
                           "(con ffmpeg, ffprobe y ffplay) y podrás borrar esos tres de la carpeta «bin» de este (unos 500 MB).",
                           "If you have Jmg AudioProcesador and Jmg VideoEncoder, both can use the same FFmpeg: choose the other one's «bin» folder "
                           "(with ffmpeg, ffprobe and ffplay) and you can delete those three from this one's «bin» folder (about 500 MB)."),
                  foreground=CA,font=("",8,"italic"),wraplength=420,justify="left").grid(row=row+3,column=0,columnspan=3,sticky="w",pady=(4,0))
        self._ff_txt()
    def _ff_txt(self):
        d=self._cfg_x("ffmpeg_dir")
        try:self.lbl_ff.configure(text=(self._vt("Usa el de: ","Uses the one in: ")+d) if d else self._vt("Usa el del programa (su carpeta «bin»).","Uses the program's own (its «bin» folder)."))
        except Exception:pass
    def _ff_elegir(self):
        d=filedialog.askdirectory(title=self._vt("Carpeta con ffmpeg y ffprobe","Folder with ffmpeg and ffprobe"))
        if d:self._ff_poner(os.path.normpath(d))
    def _ff_poner(self,d):
        V=self._vt
        if self.procesando:
            self._toast(T("warn_tit"),V("Espera a que termine el proceso en marcha.","Wait until the running process finishes."),tipo="warning",seg=4);return
        if d:
            r=_ff_carpeta_ok(d)
            if not r:
                self._toast(T("warn_tit"),V("En esa carpeta no están ffmpeg y ffprobe.","ffmpeg and ffprobe are not in that folder."),tipo="warning",seg=5);return
            try:ok=rh([r[0],"-version"],timeout=20).returncode==0
            except Exception:ok=False
            if not ok:
                self._toast(T("warn_tit"),V("Ese FFmpeg no funciona en este PC.","That FFmpeg does not work on this PC."),tipo="warning",seg=5);return
        _ff_aplicar(d);self._cfg_x("ffmpeg_dir",d);self._ff_txt();self._log("[FFMPEG] "+FFMPEG)
        falta=d and not _ff_carpeta_ok(d)[2]
        self._toast(T("info_tit"),(V("Hecho: desde ahora se usa ese FFmpeg.","Done: that FFmpeg is used from now on.") if d else V("Hecho: se usa el FFmpeg del programa.","Done: the program's own FFmpeg is used."))+
                    (V("\nFalta ffplay en esa carpeta: no se podrá reproducir.","\nffplay is missing in that folder: playback will not work.") if falta else ""),seg=6)
    # ---------- pasar los archivos al otro programa de Jmg Software ----------
    def _pasar_otro(self):
        """los archivos seleccionados (o todos) a Jmg AudioProcesador: si está abierto, a su lista; si no, se abre con ellos"""
        V=self._vt
        sel=[self.files[i] for i in self.la.curselection() if i<len(self.files)] or list(self.files)
        if not sel:
            self._toast(T("warn_tit"),V("Añade antes algún archivo a la lista.","Add some file to the list first."),tipo="warning",seg=4);return
        if _otro_enviar(sel):
            self._log(f"[->] {OTRO_NOMBRE}: "+", ".join(os.path.basename(x) for x in sel))
            self._toast(T("info_tit"),V(f"Pasados a {OTRO_NOMBRE}: {len(sel)} archivo(s).",f"Sent to {OTRO_NOMBRE}: {len(sel)} file(s)."),seg=4)
            self.root.after(700,self._on_close);return   # (JMG, 16-11) los dos no se quedan abiertos a la vez
        exe=_otro_buscar(self._cfg_x("otro_exe"))
        if not exe:
            if not self._confirm(OTRO_NOMBRE,V(f"No encuentro {OTRO_NOMBRE} en este PC.\n¿Lo buscas tú? (se recuerda para la próxima vez)",
                                               f"I cannot find {OTRO_NOMBRE} on this PC.\nWill you look for it? (it is remembered for next time)")):return
            f=filedialog.askopenfilename(title=OTRO_NOMBRE,filetypes=[(OTRO_NOMBRE,"*.exe *.pyw" if sys.platform=="win32" else "*"),(V("Todos los archivos","All files"),"*.*")])
            if not f:return
            exe=os.path.normpath(f);self._cfg_x("otro_exe",exe)
        try:
            cmd=[exe]+sel
            if exe.lower().endswith((".pyw",".py")):
                import shutil
                py=shutil.which("pythonw") or shutil.which("python") or shutil.which("python3")
                if not py:raise RuntimeError(V("no se encuentra Python para abrir ","Python not found to open ")+os.path.basename(exe))
                cmd=[py]+cmd
            subprocess.Popen(cmd,cwd=os.path.dirname(exe) or None)
            self._log(f"[->] {OTRO_NOMBRE} ({exe}): "+", ".join(os.path.basename(x) for x in sel))
            self._toast(T("info_tit"),V(f"Abriendo {OTRO_NOMBRE} con {len(sel)} archivo(s)...",f"Opening {OTRO_NOMBRE} with {len(sel)} file(s)..."),seg=5)
            self.root.after(700,self._on_close)   # (JMG, 16-11) los dos no se quedan abiertos a la vez
        except Exception as e:self._toast(T("error_tit"),str(e),tipo="error")
    def _alto_inicio(self,n=0):
        """(JMG, 8-11) al abrir: la pestaña Vídeo se ve entera y la lista y la Información se quedan con el resto (mínimo 230 px).
        Si se arrastra la raya, esa altura se recuerda (panel_alto4) y se usa la próxima vez"""
        try:
            y_=getattr(self,"_sash_rest",None)
            if y_:   # (JMG, 10-11) después de cambiar de idioma: la raya donde estaba (el inglés es más largo y la subía)
                self.root.update_idletasks()
                if self.vpan.winfo_height()<450:
                    if n<20:self.root.after(250,lambda:self._alto_inicio(n+1))
                    return
                self._sash_rest=None;self.vpan.sash_place(0,0,y_);return
            if getattr(self,"_avz",None):return   # (JMG, 9-11) siempre como sale por defecto, no la raya de la última vez
            self.root.update_idletasks();tot=self.vpan.winfo_height()
            if tot<450:   # la ventana aun no tiene su tamaño
                if n<20:self.root.after(250,lambda:self._alto_inicio(n+1))
                return
            tab=self.nb.tabs()[0];f=self._tab_in.get(tab)
            if f is None:return
            need=f.winfo_reqheight()+self.nb.winfo_height()-self.nb.nametowidget(tab).winfo_height()+16
            self.vpan.sash_place(0,0,max(230,min(tot-need,int(tot*0.6))))
        except Exception:pass
    # ---------- listas de pistas: columnas fijas que se ajustan solas a lo que llevan (JMG, 8-11) ----------
    def _tv_caber(self,tv,flex=()):
        """las columnas no se arrastran (se movían raro): cada una toma el ancho de lo que lleva y las de texto largo (flex)
        se reparten el sitio que sobra, o ceden si no cabe todo"""
        import tkinter.font as tkf
        tag=f"fija{id(tv)}"
        def sep(e):
            try:
                if tv.identify_region(e.x,e.y)=="separator":return "break"
            except Exception:pass
        for ev in ("<Button-1>","<B1-Motion>","<ButtonRelease-1>","<Double-Button-1>"):tv.bind_class(tag,ev,sep)
        tv.bindtags((tag,)+tuple(tv.bindtags()))
        firma=[None]
        def fuente(n,por):
            try:
                f_=ttk.Style().lookup("Treeview" if n=="f" else "Treeview.Heading","font")
                return tkf.nametofont(f_) if f_ in tkf.names() else (tkf.Font(font=f_) if f_ else tkf.nametofont(por))
            except Exception:return tkf.nametofont(por)
        def aj(forzar=False):
            try:
                cs=list(tv["columns"]);W=tv.winfo_width()-4
                filas=[tuple(tv.item(i,"values")) for i in tv.get_children()]
                fi=(W,tuple(tv.heading(c,"text") for c in cs),tuple(filas),tuple(int(tv.column(c,"width")) for c in cs))
                if W<100 or (fi==firma[0] and not forzar):return
                f=fuente("f","TkDefaultFont");fh=fuente("h","TkHeadingFont")
                nat={}
                for k,c in enumerate(cs):
                    w=fh.measure(str(tv.heading(c,"text")))+20
                    for v in filas:
                        if k<len(v):w=max(w,f.measure(str(v[k]))+18)
                    nat[c]=w
                fx=[c for c in cs if c not in flex];fl=[c for c in cs if c in flex]
                resto=W-sum(nat[c] for c in fx);hace=sum(nat[c] for c in fl) or 1
                for c in fx:tv.column(c,width=nat[c],minwidth=20,stretch=False)
                for c in fl:
                    w=nat[c]+(resto-hace)*nat[c]/hace if resto>=hace else max(70,resto*nat[c]/hace)
                    tv.column(c,width=int(w),minwidth=20,stretch=False)
                firma[0]=fi[:3]+(tuple(int(tv.column(c,"width")) for c in cs),)   # si algo cambia un ancho, se vuelve a poner
            except Exception:pass
        def bucle():
            try:
                if tv.winfo_exists():aj();tv.after(500,bucle)
            except Exception:pass
        tv.after(300,bucle)
        return aj
    # ---------- ventanas emergentes: la principal queda bloqueada (JMG, 8-11) ----------
    def _opc_v_enc(self):
        """el codificador de vídeo que sale con lo elegido ahora en la pestaña Vídeo"""
        try:return self._enc({"codec":self.var_vcodec.get(),"motor":self.var_vmotor.get()})
        except Exception:return None
    def _opc_v_estado(self):
        try:
            e=self._opc_v_enc();self.btn_vopc.state(["!disabled"] if (e in OPC and self._job()) else ["disabled"])
        except Exception:pass
    def _opc_video(self):
        """(JMG, 12-11) opciones avanzadas del códec de vídeo de este vídeo"""
        j=self._job();e=self._opc_v_enc()
        if not j or e not in OPC:return
        self._guardar_trabajo();v=j["v"]
        def guardar(x):
            v.setdefault("opc",{})[e]=x;self._refrescar_estado()
        self._opc_ventana(e,(v.get("opc") or {}).get(e)," · "+self._nombre(self.actual),guardar)
    def _opc_audio(self):
        """(JMG, 12-11) «⚙» de la pista: con Aften, su ventana; con otro códec, sus opciones avanzadas"""
        c=self.var_a_cod.get()
        if c=="aften":return self._aften_ventana()
        t=self._af_pista()
        if t is None or c not in OPC:return
        def guardar(x):
            t.setdefault("opc",{})[c]=x
            try:self.tv_a.item(str(self._a_i),values=self._a_fila(self._a_i,t),tags=self._a_tags(t))
            except Exception:pass
        self._opc_ventana(c,(t.get("opc") or {}).get(c),self._af_titulo(),guardar)
    # ---------- (JMG, 14-11) mientras codifica: no funciona nada de la ventana principal menos cambiar de pestaña (y «Cancelar») ----------
    _BP_TAG="JmgBloqueoProc"
    _BP_ESTADO=("TButton","TCheckbutton","TRadiobutton","TCombobox","TEntry","TSpinbox","TScale","TMenubutton",
                "Button","Checkbutton","Radiobutton","Entry","Spinbox","Scale","Menubutton")
    _BP_RUEDA=("TCombobox","TSpinbox","TScale","Scale","Spinbox")   # la rueda cambiaría su valor (en las listas solo desplaza)
    _BP_LIBRES=("TNotebook","TScrollbar","Scrollbar")
    _BP_REFRESCAR=("_refrescar_estado","_estado_video","_opc_v_estado","_ex_suav_eq","_lay_estado","_ud_botones","_aften_estado")   # los que haya en cada programa
    # ---------- (JMG, 13-11) «⏸ Pausa»: para el procesado y lo sigue donde estaba ----------
    def _pausa_raices(self):
        """los procesos del procesado en marcha (los que «Cancelar» pararía)"""
        p=getattr(self,"_proc",None)
        return [p.pid] if p is not None and p.poll() is None else []
    def _pausa_pulsar(self):
        if getattr(self,"_pausa_on",False):self._pausa_poner(False)
        elif getattr(self,"procesando",False) and not self._cancelar.is_set():self._pausa_poner(True)
    def _pausa_poner(self,on):
        V=self._vt
        if on:
            if getattr(self,"_pausa_on",False):return
            self._pausa_on=True;self._pausa_pids=set();self._pausas=getattr(self,"_pausas",[])+[[time.time(),None]]
            self._pausa_suspender()
            m=V("⏸ En pausa: «▶ Continuar» lo sigue donde estaba.","⏸ Paused: «▶ Resume» carries on where it was.")
        else:
            if not getattr(self,"_pausa_on",False):return
            self._pausa_on=False
            for pid in list(getattr(self,"_pausa_pids",())):_pausar_pid(pid,False)
            self._pausa_pids=set()
            for x in getattr(self,"_pausas",[]):
                if x[1] is None:x[1]=time.time()
            m=V("▶ Sigue el procesado.","▶ Processing goes on.")
        try:
            self._log("[PAUSA] "+m);self._st(m)
        except Exception:pass
        self._pausa_boton()
    def _pausa_suspender(self):
        for pid in _arbol_pids(self._pausa_raices()):
            if pid not in self._pausa_pids and _pausar_pid(pid,True):self._pausa_pids.add(pid)
    def _pausa_desde(self,t0):
        """segundos en pausa desde t0 (lo que queda no los cuenta)"""
        a=time.time();return sum(max(0.0,(f or a)-max(i,t0)) for i,f in list(getattr(self,"_pausas",[])))
    def _pausa_boton(self):
        b=getattr(self,"btn_pausa",None)
        if b is None:return
        try:
            on=getattr(self,"_pausa_on",False)
            t=("▶ "+self._vt("Continuar","Resume")) if on else ("⏸ "+self._vt("Pausa","Pause"))
            if str(b.cget("text"))!=t:b.configure(text=t)
            q=bool(getattr(self,"procesando",False)) and not self._cancelar.is_set()
            if q==b.instate(["disabled"]):b.state(["!disabled"] if q else ["disabled"])
        except Exception:pass
    def _trabajando(self):
        """(JMG, 13-11) hay algo largo en marcha (procesar, combinar, extraer, copiar un disco a ISO, ripear): el PC no debe suspenderse"""
        return bool(getattr(self,"procesando",False) or getattr(self,"_combinando",False) or (getattr(self,"_ext_corre",None) or {}).get("on")
                    or getattr(self,"_isoc_proc",None) is not None or getattr(self,"_ripeando",False))
    def _pausa_tick(self):
        """cada medio segundo: el botón al día; en pausa, también los procesos que empiecen después; al acabar, fuera la pausa"""
        try:
            if getattr(self,"_pausa_on",False):
                if not getattr(self,"procesando",False) or self._cancelar.is_set():self._pausa_poner(False)
                else:self._pausa_suspender()
            self._pausa_boton()
        except Exception:pass
        try:_no_dormir(self._trabajando())   # (JMG, 13-11) que el PC no se suspenda mientras trabaja
        except Exception:pass
        try:self.root.after(500,self._pausa_tick)
        except Exception:pass
    def _bp_libres(self):
        """lo que sigue funcionando mientras codifica (además de las pestañas y las barras de desplazamiento)"""
        return [w for w in (getattr(self,"btn_c",None),getattr(self,"btn_pausa",None),getattr(self,"cmb_fin",None)) if w is not None]   # (JMG, 13-11) y «Pausa» y «Al terminar»
    def _bp_aplicar(self):
        """recorre la ventana principal: desactiva lo que esté activo y pone el freno de clics, teclas y rueda donde no esté
        (también lo que el programa haya vuelto a activar o haya creado después de empezar)"""
        r=self.root;libres={str(w) for w in self._bp_libres()};prev=self._bp_prev;tags=self._bp_tags;pila=[r]
        while pila:
            w=pila.pop()
            try:pila+=[h for h in w.winfo_children() if not isinstance(h,tk.Toplevel)]
            except Exception:pass
            if str(w) in libres:continue
            try:cl=w.winfo_class()
            except Exception:continue
            if cl in self._BP_LIBRES:continue
            try:
                bt=tuple(w.bindtags())
                if self._BP_TAG not in bt:w.bindtags((self._BP_TAG,)+bt);tags.append(w)
            except Exception:pass
            if cl in self._BP_ESTADO:
                try:
                    if cl.startswith("T"):
                        if not w.instate(["disabled"]):
                            w.state(["disabled"])
                            if str(w) not in prev:prev[str(w)]=(w,None)
                    else:
                        s=str(w.cget("state"))
                        if s!="disabled":
                            w.configure(state="disabled")
                            if str(w) not in prev:prev[str(w)]=(w,s)
                except Exception:pass
    def _bp_poner(self,on):
        """(JMG, 14-11) codificando, la ventana principal no hace nada salvo cambiar de pestaña y «Cancelar»: sus controles se
        desactivan (y al terminar vuelven como estaban, y cada programa recalcula los que dependen de algo) y los clics, teclas y la
        rueda de lo demás (listas, gráficos, enlaces, atajos) no llegan. Las ventanas aparte (Combinar...) siguen con lo suyo.
        Una vigilancia lo mantiene mientras dura y lo quita sola al acabar."""
        r=self.root
        if on:
            if getattr(self,"_bp_prev",None) is not None:return
            if not getattr(self,"_bp_tag_hecho",False):
                for ev in ("<ButtonPress>","<ButtonRelease>","<Double-ButtonPress>","<Triple-ButtonPress>","<B1-Motion>","<B2-Motion>","<B3-Motion>","<KeyPress>","<KeyRelease>"):
                    r.bind_class(self._BP_TAG,ev,lambda e:"break")
                def rueda(e):
                    try:return "break" if e.widget.winfo_class() in self._BP_RUEDA else None
                    except Exception:return None
                r.bind_class(self._BP_TAG,"<MouseWheel>",rueda)
                self._bp_tag_hecho=True
            self._bp_prev={};self._bp_tags=[]
            self._bp_aplicar()
            r.after(700,self._bp_vigilar)
        else:
            prev=getattr(self,"_bp_prev",None)
            if prev is None:return
            self._bp_prev=None
            for w,s in prev.values():
                try:
                    if s is None:
                        if w.instate(["disabled"]):w.state(["!disabled"])
                    elif str(w.cget("state"))=="disabled":w.configure(state=s)
                except Exception:pass
            for w in getattr(self,"_bp_tags",[]):
                try:w.bindtags(tuple(t for t in w.bindtags() if t!=self._BP_TAG))
                except Exception:pass
            self._bp_tags=[]
            for f in self._BP_REFRESCAR:
                try:getattr(self,f)()
                except Exception:pass
    def _bp_vigilar(self):
        """mientras dura el bloqueo: lo mantiene (lo que se haya vuelto a activar o sea nuevo) y, si ya no se está codificando
        (por donde sea que haya terminado), lo quita"""
        if getattr(self,"_bp_prev",None) is None:return
        if not (getattr(self,"procesando",False) or getattr(self,"_combinando",False)):self._bp_poner(False);return
        try:self._bp_aplicar()
        except Exception:pass
        self.root.after(700,self._bp_vigilar)
    # ---------- (JMG, 15-11) «📤 Extracción»: saca todo lo que lleva el vídeo, cada cosa en su formato original (sin recomprimir) ----------
    _EXT_AUD={"ac3":("ac3","ac3"),"eac3":("eac3","eac3"),"dts":("dts","dts"),"truehd":("thd","truehd"),"aac":("m4a","ipod"),"alac":("m4a","ipod"),
              "flac":("flac","flac"),"mp3":("mp3","mp3"),"mp2":("mp2","mp2"),"opus":("opus","opus"),"vorbis":("ogg","ogg")}
    _EXT_SUB={"subrip":("srt","srt"),"ass":("ass","ass"),"ssa":("ass","ass"),"webvtt":("vtt","webvtt"),"hdmv_pgs_subtitle":("sup","sup"),"mov_text":("srt","srt")}
    _EXT_IMG={"mjpeg":"jpg","png":"png","bmp":"bmp","gif":"gif","webp":"webp"}
    @staticmethod
    def _ext_limpio(t,largo=80):
        """un trozo de nombre de archivo válido en Windows"""
        t=re.sub(r'[\\/:*?"<>|\r\n\t]+',"_",str(t or "")).strip(" .")
        return t[:largo].rstrip(" .")
    def _ext_carpeta(self,ruta,crear=False):
        """la carpeta de la extracción: «<vídeo> (extracción)», donde diga la Salida (junto al original o la carpeta elegida);
        si ya existe y tiene algo y «Si el archivo ya existe» es Renombrar, «(extracción 2)», «(extracción 3)»..."""
        V_=self._vt;base=self._ext_limpio(self._base(ruta),120) or "video";pal=V_("extracción","extraction")
        d=self._dir_orig(ruta) if self.var_dest_modo.get()!="carpeta" or not self.var_dest.get().strip() else self.var_dest.get().strip()
        p=os.path.join(d,f"{base} ({pal})")
        if crear and self.var_dup.get()=="rename":
            n=2
            while os.path.isdir(p) and os.listdir(p):p=os.path.join(d,f"{base} ({pal} {n})");n+=1
        return p
    def _ext_elementos(self,ruta):
        """lo que lleva el archivo: [{tipo v/a/s/img/t/c, idx, txt (columnas de la lista), nombre, ext, fmt...}], duración"""
        p=subprocess.run([FFPROBE,"-v","error","-show_streams","-show_chapters","-show_format","-of","json",ruta],capture_output=True,text=True,
                         encoding="utf-8",errors="replace",creationflags=CNW)
        d=json.loads(p.stdout or "{}");V_=self._vt;el=[];n={"v":0,"a":0,"s":0,"img":0,"t":0}
        for s in d.get("streams",[]):
            ct=s.get("codec_type");cn=str(s.get("codec_name") or "?");tg=s.get("tags") or {};idx=s.get("index")
            lang=str(tg.get("language") or "");lang="" if lang in ("und","") else lang;tit=str(tg.get("title") or "")
            nfr=str(s.get("nb_frames") or tg.get("NUMBER_OF_FRAMES") or "")
            img=(s.get("disposition") or {}).get("attached_pic")==1 or cn in ("png","bmp","gif","webp") or (cn=="mjpeg" and (nfr=="1" or bool(tg.get("filename"))))
            if ct=="video" and img:   # una portada (o una imagen que va como pista de vídeo de un fotograma, como al copiar un MKV con portada)
                n["img"]+=1;ext=self._EXT_IMG.get(cn,"jpg");fn=str(tg.get("filename") or "")
                el.append({"tipo":"img","idx":idx,"txt":(V_("Portada","Cover"),"",fn or tit,cn),"et":f"{V_('portada','cover')} {n['img']}"+(f" - {os.path.splitext(fn)[0]}" if fn else ""),"ext":ext,"fmt":"image2"})
            elif ct=="video":
                n["v"]+=1;el.append({"tipo":"v","idx":idx,"txt":(V_("Vídeo","Video"),lang,tit,cn),"et":f"{V_('vídeo','video')} {n['v']}","lang":lang,"tit":tit,"cod":cn,"ext":"mkv","fmt":"matroska"})
            elif ct=="audio":
                n["a"]+=1;ext,fm=self._EXT_AUD.get(cn,("wav","wav") if cn.startswith("pcm_") else ("mka","matroska"))
                el.append({"tipo":"a","idx":idx,"txt":("Audio",lang,tit,f"{cn} · {s.get('channels','?')} can."),"et":f"audio {n['a']}","lang":lang,"tit":tit,"cod":cn,"ext":ext,"fmt":fm})
            elif ct=="subtitle":
                n["s"]+=1;ext,fm=self._EXT_SUB.get(cn,("mks","matroska"))
                el.append({"tipo":"s","idx":idx,"txt":(V_("Subtítulos","Subtitles"),lang,tit,cn),"et":f"{V_('subtítulos','subtitles')} {n['s']}","lang":lang,"tit":tit,"cod":cn,"ext":ext,"fmt":fm,
                           "conv":"srt" if cn=="mov_text" else None})
            elif ct=="attachment":
                n["t"]+=1;fn=os.path.basename(str(tg.get("filename") or "").replace("\\","/")) or f"{V_('adjunto','attachment')} {n['t']}"
                el.append({"tipo":"t","idx":idx,"txt":(V_("Adjunto","Attachment"),"",fn,str(tg.get("mimetype") or "")),"fn":fn})
        caps=d.get("chapters") or []
        if caps:el.append({"tipo":"c","txt":(V_("Capítulos","Chapters"),"",V_(f"{len(caps)} capítulos",f"{len(caps)} chapters"),V_("texto OGM","OGM text")),"caps":caps})
        try:dur=float((d.get("format") or {}).get("duration") or 0)
        except (TypeError,ValueError):dur=0.0
        return el,dur
    def _ext_nombre(self,e,k):
        """nombre del archivo de cada cosa: «02 - audio 1 [spa] - Castellano (eac3).eac3»"""
        if e["tipo"]=="t":return self._ext_limpio(f"{k:02d} - "+self._vt("adjunto","attachment")+" - "+e["fn"],150)
        if e["tipo"]=="c":return f"{k:02d} - "+self._vt("capítulos","chapters")+".txt"
        if e["tipo"]=="img":return self._ext_limpio(f"{k:02d} - {e['et']}")+"."+e["ext"]
        t=f"{k:02d} - {e['et']}"+(f" [{e['lang']}]" if e.get("lang") else "")+(f" - {e['tit']}" if e.get("tit") else "")+f" ({e['cod']})"
        return self._ext_limpio(t,120)+"."+e["ext"]
    @staticmethod
    def _ext_capitulos(caps):
        """los capítulos en texto OGM (CHAPTER01=00:00:00.000 / CHAPTER01NAME=...), el que leen MKVToolNix y casi todos"""
        lin=[]
        for i,c in enumerate(caps,1):
            try:t=max(0.0,float(c.get("start_time") or 0))
            except (TypeError,ValueError):t=0.0
            h=int(t//3600);m_=int(t%3600//60);s_=t-h*3600-m_*60
            lin+=[f"CHAPTER{i:02d}={h:02d}:{m_:02d}:{s_:06.3f}",f"CHAPTER{i:02d}NAME="+str((c.get("tags") or {}).get("title") or f"Chapter {i:02d}")]
        return "\n".join(lin)+"\n"
    def _ext_orden(self,ruta,sel,d):
        """la orden de FFmpeg (una sola lectura del archivo para todo) y los archivos que va a crear [(elemento, ruta)]"""
        cmd=[FFMPEG,"-hide_banner","-nostdin","-y","-v","error"];sal=[];hay=False
        for k,e in enumerate(sel,1):
            if e["tipo"]=="t":
                o=os.path.join(d,self._ext_nombre(e,k));cmd+=[f"-dump_attachment:{e['idx']}",o];sal.append((e,o))
        cmd+=["-i",ruta]
        for k,e in enumerate(sel,1):
            if e["tipo"] not in ("v","a","s","img"):continue
            o=os.path.join(d,self._ext_nombre(e,k));hay=True;sal.append((e,o))
            cmd+=["-map",f"0:{e['idx']}"]+(["-c:s",e["conv"]] if e.get("conv") else ["-c","copy"])
            if e["tipo"]=="img":cmd+=["-frames:v","1","-update","1"]
            cmd+=["-f",e["fmt"],o]
        if not hay:cmd+=["-map","0:0?","-t","0","-f","null","-"]   # solo adjuntos: hace falta una salida (se descarta)
        cmd+=["-progress","pipe:1","-nostats"]
        for k,e in enumerate(sel,1):
            if e["tipo"]=="c":sal.append((e,os.path.join(d,self._ext_nombre(e,k))))
        return cmd,sal
    def _ext_ventana(self,ruta=None):
        """«📤 Extracción...» (pestaña Salida, a la derecha del nombre): la lista de lo que lleva el vídeo, cada cosa con su casilla
        (todo marcado). «Extraer» lo saca a la carpeta «(extracción)», con su barra; «Cancelar» lo para y borra lo que estaba a medias."""
        V_=self._vt;ruta=ruta or self.actual
        if self.procesando:
            self._toast(T("warn_tit"),V_("Espera a que termine el proceso (o cancélalo).","Wait until processing finishes (or cancel it)."),tipo="warning",seg=4);return
        if not ruta or not os.path.isfile(ruta):
            self._toast(T("info_tit"),V_("La extracción es de un archivo de vídeo: elígelo antes en la lista.","Extraction works on a video file: choose it in the list first."),seg=4);return
        if getattr(self,"_ext_top",None) is not None:
            try:
                self._ext_top.lift()
                if ruta!=getattr(self,"_ext_ruta",None):   # (JMG, 15-11) otro vídeo (botón derecho con varios a la vez): en cola
                    self._ext_cola=list(getattr(self,"_ext_cola",[]))+[ruta]
                    self._toast(V_("Extracción","Extraction"),V_("En cola: ","Queued: ")+os.path.basename(ruta),seg=3)
                return
            except Exception:self._ext_top=None
        try:el,dur=self._ext_elementos(ruta)
        except Exception as ex:
            self._toast(T("warn_tit"),V_("No se ha podido leer el archivo: ","Could not read the file: ")+str(ex),tipo="warning",seg=5);return
        if not el:
            self._toast(T("info_tit"),V_("El archivo no lleva nada que sacar.","The file carries nothing to take out."),seg=4);return
        top=tk.Toplevel(self.root);self._ext_top=top;self._ext_ruta=ruta;top.title("📤 "+V_("Extracción","Extraction")+" · "+os.path.basename(ruta));top.configure(bg=CF)
        visible=bool(self.root.winfo_viewable())
        if visible:top.transient(self.root)   # (con la principal escondida —bandeja o botón derecho— va sola, con su botón en la barra de tareas)
        f=ttk.Frame(top);f.pack(fill="both",expand=True,padx=16,pady=12)
        ttk.Label(f,text="📤 "+V_("Extracción","Extraction")+" · "+os.path.basename(ruta),font=("",11,"bold")).grid(row=0,column=0,columnspan=2,sticky="w")
        lbl_d=ttk.Label(f,text="",foreground=CA,font=("",8,"italic"),wraplength=700,justify="left");lbl_d.grid(row=1,column=0,columnspan=2,sticky="w",pady=(2,8))
        def pintar_dest():lbl_d.configure(text=V_("Cada cosa sale en su formato original, sin recomprimir nada. Marca lo que quieras sacar. Se guarda en:\n",
                                                 "Each item comes out in its original format, nothing re-encoded. Tick what you want to take out. Saved in:\n")+self._ext_carpeta(ruta,crear=True))
        pintar_dest()
        # (JMG, 15-11) casillas para marcar, como en el resto del programa (en una lista que se desplaza si hay muchas cosas)
        alto=min(420,44+31*len(el))
        caja=ttk.Frame(f,width=760,height=alto);caja.grid(row=2,column=0,columnspan=2,sticky="nsew");caja.pack_propagate(False)
        lst=self._scroll(caja)
        for c,(t,w) in enumerate(((V_("Qué","What"),16),(V_("Idioma","Language"),9),(V_("Título / nombre","Title / name"),44),(V_("Formato","Format"),20))):
            ttk.Label(lst,text=t,font=("",9,"bold"),width=w).grid(row=0,column=c,sticky="w",padx=(4 if c==0 else 8,0),pady=(0,4))
        marca={};chk={}
        corre={"p":None,"sal":[],"on":False}
        for i,e in enumerate(el):
            marca[i]=tk.BooleanVar(value=True)
            chk[i]=ttk.Checkbutton(lst,text=e["txt"][0],variable=marca[i],style="G.TCheckbutton");chk[i].grid(row=i+1,column=0,sticky="w",padx=(4,0),pady=1)
            for c,t in enumerate(e["txt"][1:],1):
                ttk.Label(lst,text=str(t)[:60],foreground=CT if c!=3 else CA).grid(row=i+1,column=c,sticky="w",padx=(8,0),pady=1)
        def poner(i,v):marca[i].set(bool(v))
        fb=ttk.Frame(f);fb.grid(row=3,column=0,columnspan=2,sticky="ew",pady=(8,0))
        b_todo=ttk.Button(fb,text="☑ "+V_("Todo","All"),command=lambda:[poner(i,True) for i in marca]);b_todo.pack(side="left")
        b_nada=ttk.Button(fb,text="☐ "+V_("Nada","None"),command=lambda:[poner(i,False) for i in marca]);b_nada.pack(side="left",padx=6)
        pb=ttk.Progressbar(f,mode="determinate",maximum=100,style="V.Horizontal.TProgressbar");pb.grid(row=4,column=0,columnspan=2,sticky="ew",pady=(10,2))
        est=tk.StringVar(value=V_(f"{len(el)} elementos, todos marcados.",f"{len(el)} items, all ticked."))
        def contar(*_):   # (JMG, 15-11) cuántos hay marcados, al momento
            if corre["on"]:return
            n_=sum(1 for v in marca.values() if v.get())
            est.set(V_(f"{len(el)} elementos, todos marcados.",f"{len(el)} items, all ticked.") if n_==len(el) else V_(f"{n_} de {len(el)} marcados.",f"{n_} of {len(el)} ticked."))
        for v in marca.values():v.trace_add("write",contar)
        ttk.Label(f,textvariable=est,foreground=CID,wraplength=700,justify="left").grid(row=5,column=0,columnspan=2,sticky="w")
        fz=ttk.Frame(f);fz.grid(row=6,column=0,columnspan=2,sticky="ew",pady=(12,0))
        b_cer=ttk.Button(fz,text=V_("Cerrar","Close"));b_cer.pack(side="right")
        b_ext=ttk.Button(fz,text="📤 "+V_("Extraer","Extract"));b_ext.pack(side="right",padx=6)
        def botones(libre):
            for b_ in (b_ext,b_todo,b_nada)+tuple(chk.values()):b_.state(["!disabled"] if libre else ["disabled"])
            b_cer.configure(text=V_("Cerrar","Close") if libre else V_("Cancelar","Cancel"))
        def cerrar():
            if corre["on"]:   # Cancelar: para FFmpeg (el nuestro) y lo de a medias se borra al acabar el hilo
                corre["canc"]=True
                try:corre["p"].terminate()
                except Exception:pass
                return
            try:top.grab_release();top.destroy()
            except Exception:pass
            if self._ext_top is not None:self._ext_top=None;self._ext_ruta=None;self._af_modal(False);self._ext_siguiente()
        b_cer.configure(command=cerrar);top.protocol("WM_DELETE_WINDOW",cerrar)
        def fin(ok,d,hechos,err,canc):
            corre["on"]=False;botones(True)
            if canc:
                pb.configure(value=0);est.set(V_("Cancelado: lo que estaba a medias se ha borrado.","Cancelled: unfinished files have been deleted."));pintar_dest();return
            pb.configure(value=100 if ok else 0)
            if ok:
                est.set(V_(f"Hecho: {hechos} archivos en «{os.path.basename(d)}».",f"Done: {hechos} files in «{os.path.basename(d)}»."))
                self._log(f"[📤] {hechos} → {d}")
                self._toast(V_("Extracción","Extraction"),V_(f"{hechos} archivos sacados a:\n",f"{hechos} files taken out to:\n")+d,seg=5)
                if self.var_abrir.get():
                    try:_abrir_externo(d)
                    except Exception:pass
            else:
                est.set(V_("Error al extraer: ","Error while extracting: ")+(err or "?")[-300:]);self._log("[📤] [ERR] "+(err or "?")[-600:])
            pintar_dest()
        def extraer():
            sel=[el[i] for i in sorted(marca) if marca[i].get()]
            if not sel:est.set(V_("No hay nada marcado.","Nothing is ticked."));return
            d=self._ext_carpeta(ruta,crear=True)
            try:os.makedirs(d,exist_ok=True)
            except OSError as ex:est.set(V_("No se puede crear la carpeta: ","Cannot create the folder: ")+str(ex));return
            cmd,sal=self._ext_orden(ruta,sel,d);corre.update(on=True,canc=False,sal=sal);botones(False);pb.configure(value=0)
            est.set(V_("Extrayendo...","Extracting..."));self._ls("$ "+subprocess.list2cmdline(cmd))
            antes={os.path.normcase(x) for x in os.listdir(d)}
            def hilo():
                err=[];ok=False
                try:
                    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace",creationflags=CNW);corre["p"]=p
                    threading.Thread(target=lambda:err.extend(p.stderr.read().splitlines()),daemon=True).start()
                    for lin in p.stdout:
                        if lin.startswith("out_time_us=") and dur>0:
                            try:self._ui(pb.configure,{"value":min(99.0,int(lin.split("=")[1])/1e4/dur)})
                            except Exception:pass
                    p.wait();hay=[o for e,o in sal if e["tipo"]!="c"]
                    ok=(p.returncode==0 or (not any(e["tipo"] in ("v","a","s","img") for e,o in sal) and all(os.path.isfile(o) for o in hay)))
                    if ok and not corre.get("canc"):
                        for e,o in sal:
                            if e["tipo"]=="c":open(o,"w",encoding="utf-8").write(self._ext_capitulos(e["caps"]))
                except Exception as ex:err.append(str(ex))
                canc=bool(corre.get("canc"))
                if canc or not ok:   # lo de a medias, fuera (solo lo que ha creado esta extracción)
                    for e,o in sal:
                        try:
                            if os.path.normcase(os.path.basename(o)) not in antes and os.path.isfile(o):os.remove(o)
                        except OSError:pass
                    try:
                        if not os.listdir(d):os.rmdir(d)
                    except OSError:pass
                hechos=sum(1 for e,o in sal if os.path.isfile(o))
                self._ui(fin,ok and not canc,d,hechos,"\n".join(err[-6:]),canc)
            threading.Thread(target=hilo,daemon=True).start()
        b_ext.configure(command=extraer)
        self._af_modal(True)
        try:
            top.update_idletasks()
            if visible:top.geometry(f"+{self.root.winfo_rootx()+100}+{self.root.winfo_rooty()+70}")
            else:top.geometry(f"+{max(0,(top.winfo_screenwidth()-top.winfo_reqwidth())//2)}+{max(0,(top.winfo_screenheight()-top.winfo_reqheight())//3)}")
            top.grab_set()
        except Exception:pass
        self._ext_marca=marca;self._ext_chk=chk;self._ext_extraer=extraer;self._ext_cerrar=cerrar;self._ext_corre=corre;self._ext_el=el;self._ext_btn=(b_ext,b_cer)   # (para las pruebas)
    def _ext_siguiente(self):
        """al cerrar la ventana de Extracción: el siguiente vídeo de la cola; si no queda nada y el programa se abrió solo para
        extraer (botón derecho), se cierra"""
        cola=list(getattr(self,"_ext_cola",[]))
        if cola:
            r_=cola.pop(0);self._ext_cola=cola;self.root.after(150,lambda:self._ext_recibir(r_));return
        if getattr(self,"_ext_solo",False):
            try:self.root.after(150,self.root.destroy)
            except Exception:pass
    def _ext_elegir(self):
        """(JMG, 15-11) «📤 Extracción...» del menú del icono de la bandeja: vuelve la ventana y pide el vídeo"""
        V_=self._vt
        if self.procesando:
            self._toast(T("warn_tit"),V_("Espera a que termine el proceso (o cancélalo).","Wait until processing finishes (or cancel it)."),tipo="warning",seg=4);return
        self._bandeja_volver()
        def pedir():
            f=filedialog.askopenfilename(parent=self.root,title=V_("Extracción: elige el vídeo","Extraction: choose the video"),
                                         filetypes=[(V_("Vídeos","Videos"),_EXT_VID),(V_("Todos los archivos","All files"),"*.*")])
            if f:self._ext_ventana(os.path.normpath(f))
        self.root.after(250,pedir)
    def _ext_recibir(self,ruta):
        """(JMG, 15-11) «Extraer con Jmg VideoEncoder» (botón derecho en el Explorador): su ventana de Extracción, delante de todo"""
        if not ruta or not os.path.isfile(ruta):return
        self._ext_ventana(ruta)
        try:
            t=self._ext_top
            if t is not None:t.deiconify();t.lift();t.attributes("-topmost",True);t.after(500,lambda:t.attributes("-topmost",False));t.focus_force()
        except Exception:pass
    # ---------- (JMG, 16-11) discos: «Ripear» y «Crear imagen ISO» desde el menú de la bandeja y el botón derecho del lector ----------
    @staticmethod
    def _disco_info(r_):
        """(etiqueta, de vídeo —DVD o Blu-ray—, con datos —se puede copiar a ISO—) del disco de un lector; None si no tiene disco"""
        try:
            import ctypes
            k=ctypes.windll.kernel32;viejo=k.SetErrorMode(0x8001)   # sin el aviso de Windows «no hay disco en la unidad»
            try:
                nom=ctypes.create_unicode_buffer(261);fs=ctypes.create_unicode_buffer(261)
                if not k.GetVolumeInformationW(ctypes.c_wchar_p(r_),nom,261,None,None,None,fs,261):return None
                try:ls=os.listdir(r_)
                except OSError:ls=[]
            finally:k.SetErrorMode(viejo)
            up={x.upper() for x in ls}
            musica=bool(ls) and all(x.lower().endswith(".cda") for x in ls)   # un CD de música: ni se ripea aquí ni sale en ISO
            return (nom.value.strip(),("VIDEO_TS" in up or "BDMV" in up),not musica)
        except Exception:return None
    def _discos(self):
        """[(raíz, etiqueta, de vídeo, con datos)] de los lectores de DVD / Blu-ray / CD que tienen un disco (y las imágenes montadas)"""
        l=[]
        if sys.platform!="win32":return l
        import ctypes,string
        for c in string.ascii_uppercase:
            r_=c+":\\"
            try:
                if ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(r_))!=5:continue
            except Exception:continue
            i=self._disco_info(r_)
            if i:l.append((r_,)+i)
        return l
    def _disco_ripear(self,r_):
        """(JMG, 16-11) «Ripear»: la película principal del DVD o Blu-ray entra en la lista en Passthrough («Solo la película»):
        se eligen idiomas y subtítulos y sale un MKV sin perder calidad (si está protegido, se avisa y no entra)"""
        V_=self._vt
        if self.procesando:
            self._toast(T("warn_tit"),V_("Espera a que termine el proceso (o cancélalo).","Wait until processing finishes (or cancel it)."),tipo="warning",seg=4);return
        self._ext_solo=False;self._isoc_solo=False
        self._bandeja_volver()
        r_=os.path.normpath(r_)
        if not os.path.isdir(r_) or not self._vobs(r_):
            self._toast(T("warn_tit"),V_("En ese disco no hay un DVD (VIDEO_TS) ni un Blu-ray (BDMV) de vídeo.","That disc has no video DVD (VIDEO_TS) or Blu-ray (BDMV)."),tipo="warning",seg=5);return
        self._pel_pend=r_;self._addl([r_]);self.root.after(300,self._isoc_pel_espera)
    def _disco_imagen(self,r_):
        """(JMG, 16-11) «Crear imagen ISO» de ese disco: la ventana de Crear ISO con él ya elegido"""
        V_=self._vt
        if self.procesando:
            self._toast(T("warn_tit"),V_("Espera a que termine el proceso (o cancélalo).","Wait until processing finishes (or cancel it)."),tipo="warning",seg=4);return
        if not getattr(self,"_isoc_solo",False):self._bandeja_volver()
        self._isoc_ventana()
        try:
            l=getattr(self,"_isoc_un_l",[]) or []
            k=next((i for i,(x,_) in enumerate(l) if os.path.normcase(x)==os.path.normcase(os.path.normpath(r_))),None)
            if k is not None:self.cb_isoc_un.current(k);self.var_isoc_modo.set("disco");self._isoc_proponer(True)
            t=self._isoc_top;t.deiconify();t.lift();t.attributes("-topmost",True);t.after(500,lambda:t.attributes("-topmost",False));t.focus_force()
        except Exception:pass
    def _bloq_vigilar(self):
        """(JMG, 11-11) red de seguridad: si la ventana principal se ha quedado bloqueada sin ninguna ventana emergente abierta
        (Revisar sincronización, Combinar, Crear ISO, Aften o Más opciones / Visual), se desbloquea sola"""
        if not getattr(self,"_bloq_n",0):return
        if getattr(self,"_avz",None):return
        for k in ("_rev_top","_cb_top","_isoc_top","_af_top","_opc_top","_ext_top"):
            w=getattr(self,k,None)
            try:
                if w is not None and w.winfo_exists():return
            except Exception:pass
        self._bloq_n=1;self._bloquear_principal(False)
        self._log("[!] "+self._vt("La ventana principal se había quedado bloqueada sin ninguna ventana abierta: desbloqueada.","The main window was left blocked with no window open: unblocked."))
    def _bloquear_principal(self,on):
        """con una ventana emergente (Combinar, Revisar sincronización) o las opciones avanzadas abiertas, los botones de la
        ventana principal no funcionan; al cerrarla vuelven como estaban"""
        n=getattr(self,"_bloq_n",0)
        if on:
            n+=1
            if n==1:
                self._bloq_prev=[]
                for fr in (getattr(self,"_fr_sup",None),getattr(self,"_fr_inf",None),getattr(self,"_fr_fila",None)):
                    pila=[fr] if fr is not None else []
                    while pila:
                        w=pila.pop()
                        try:pila+=w.winfo_children()
                        except Exception:continue
                        if w.winfo_class() in ("TButton","TCheckbutton","TCombobox","TRadiobutton"):
                            try:self._bloq_prev.append((w,w.instate(["disabled"])));w.state(["disabled"])
                            except Exception:pass
        else:
            n=max(0,n-1)
            if n==0:
                for w,d in getattr(self,"_bloq_prev",[]):
                    try:w.state(["disabled"] if d else ["!disabled"])
                    except Exception:pass
                self._bloq_prev=[]
        self._bloq_n=n
        if n==0:
            try:self._refrescar_estado();self._ud_botones()
            except Exception:pass
    def _avz_ud(self,s):
        self._ud_mover(s)
        if getattr(self,"_avz",None)=="v":
            try:self._prev_pronto(150)
            except Exception:pass
    # ---------- Combinar: deshacer / rehacer y teclado (JMG, 8-11) ----------
    def _cb_ud_antes(self):
        import copy
        if not hasattr(self,"_cb_ud"):self._cb_ud=[];self._cb_ur=[]
        self._cb_ud.append(copy.deepcopy(self._clips));del self._cb_ud[:-30];self._cb_ur=[];self._cb_ud_botones()
    def _cb_ud_mover(self,s):
        import copy
        de,a=(self._cb_ud,self._cb_ur) if s<0 else (self._cb_ur,self._cb_ud)
        if not de:return
        a.append(copy.deepcopy(self._clips));self._clips=de.pop();self._cb_vis_i=None
        sel=self._cb_actual();self._cb_pintar(min(sel or 0,len(self._clips)-1) if self._clips else None);self._cb_ud_botones()
        if self._clips and self._cb_actual() is not None:self._cb_vista_ir(self._cb_actual())
    def _cb_ud_botones(self):
        try:
            self.btn_cb_ud.state(["!disabled"] if self._cb_ud else ["disabled"]);self.btn_cb_ur.state(["!disabled"] if self._cb_ur else ["disabled"])
        except Exception:pass
    def _cb_teclas(self,top):
        """flechas: una pulsación = un fotograma; mantenida = cada vez más rápido. Ctrl+Z / Ctrl+Y: deshacer / rehacer los trozos"""
        for w in (top,self.sc_cb):
            w.bind("<Left>",lambda e:self._cb_tecla(e,-1));w.bind("<Right>",lambda e:self._cb_tecla(e,1))
        for t_,s_ in (("<Control-z>",-1),("<Control-Z>",-1),("<Control-y>",1),("<Control-Y>",1)):
            top.bind(t_,lambda e,s=s_:None if isinstance(e.widget,(tk.Entry,ttk.Entry)) else self._cb_ud_mover(s))
        self._cb_ud_botones()
    def _cb_tecla(self,e,d):
        if isinstance(e.widget,(tk.Entry,ttk.Entry,ttk.Combobox)):return None   # en una casilla, las flechas son de la casilla
        i=self._cb_actual()
        if i is None:return "break"
        inf=self.info.get(self._clips[i]["ruta"],{});fps=_fps(_vstream(inf) or {}) or 25.0;D=_dur(inf) or 0.0
        ahora=time.time();t0,n=getattr(self,"_cb_k",(0.0,0));n=n+1 if ahora-t0<0.2 else 0;self._cb_k=(ahora,n)
        paso=1.0/fps if n==0 else (2.0/fps if n<6 else (0.5 if n<20 else (2.0 if n<50 else 10.0)))   # mantenida: avance rápido
        v=max(0.0,min(D,float(self.var_cb_pos.get())+d*paso));self.var_cb_pos.set(v);self.lbl_cb_t.configure(text=_hms(v))
        if getattr(self,"_cb_k_id",None):
            try:self.root.after_cancel(self._cb_k_id)
            except Exception:pass
        self._cb_k_id=self.root.after(120 if n==0 else 300,self._cb_foto)
        return "break"
    # ---------- imágenes de disco .iso y nombres de los discos (JMG, 8-11) ----------
    def _dvd_menu(self,btn):
        V_=self._vt;m=tk.Menu(self.root,tearoff=0)
        m.add_command(label=V_("Carpeta (VIDEO_TS o BDMV)...","Folder (VIDEO_TS or BDMV)..."),command=self._add_dvd)
        m.add_command(label=V_("Imagen de disco (.iso)...","Disc image (.iso)..."),command=self._add_iso)
        try:m.tk_popup(btn.winfo_rootx(),btn.winfo_rooty()+btn.winfo_height())
        finally:m.grab_release()
    def _add_iso(self):
        f=filedialog.askopenfilename(title=self._vt("Imagen de disco de un DVD o un Blu-ray","Disc image of a DVD or a Blu-ray"),filetypes=[(self._vt("Imagen de disco","Disc image"),"*.iso"),(self._vt("Todos","All"),"*.*")])
        if f:self._iso_abrir(os.path.normpath(f))
    def _iso_abrir(self,iso):
        V_=self._vt
        if sys.platform!="win32":
            self._toast(T("info_tit"),V_("En Linux, monta la imagen (doble clic en ella) y elige su carpeta con «Carpeta (VIDEO_TS o BDMV)».","On Linux, mount the image (double-click it) and choose its folder with «Folder (VIDEO_TS or BDMV)»."),seg=8);return
        if any(v[0]==iso for v in getattr(self,"_isos",{}).values()):return
        self._st(V_("Montando la imagen de disco...","Mounting the disc image..."))
        def hilo():self._ui(self._iso_fin,iso,self._iso_montar(iso))
        threading.Thread(target=hilo,daemon=True).start()
    def _iso_montar(self,iso):
        """Windows monta la imagen (como el doble clic) -> (raíz, ya estaba montada) o None"""
        ps="$p=$env:JMG_ISO;$d=Get-DiskImage -ImagePath $p;$y=$d.Attached;if(-not $y){$d=Mount-DiskImage -ImagePath $p -PassThru};$l=($d|Get-Volume).DriveLetter;Write-Output ('{0}|{1}' -f $y,$l)"
        try:r=rh(["powershell","-NoProfile","-NonInteractive","-Command",ps],env=dict(os.environ,JMG_ISO=iso),timeout=90)
        except Exception as e:self._ls(f"[ISO] {e}");return None
        ls=[l.strip() for l in (r.stdout or "").splitlines() if "|" in l]
        if not ls:self._ls("[ISO] "+(r.stderr or "")[-300:]);return None
        ya,l=ls[-1].split("|",1)
        if not l.strip():return None
        for _i in range(4):   # (JMG, 14-11) AnyDVD / Windows analizan la imagen recién montada (con un disco nuevo, más rato): que se lea bien
            if not _esperar_lectura(l.strip()+":\\"):break   # y que ya se vea la película; si no, otra espera (sin DVD ni Blu-ray: no se espera más)
            try:
                if self._vobs(l.strip()+":\\"):break
            except Exception:pass
            time.sleep(3)
        return (l.strip()+":\\",ya.strip().lower()=="true")
    def _iso_fin(self,iso,u):
        V_=self._vt;self._st("")
        if not u:self._toast(T("error_tit"),V_("No se ha podido montar la imagen de disco (mira Edit/Log).","Could not mount the disc image (see Edit/Log)."),tipo="error",seg=6);return
        raiz,ya=u
        if not hasattr(self,"_isos"):self._isos={}
        self._isos[raiz]=(iso,ya)
        if not self._vobs(raiz):
            self._toast(T("warn_tit"),V_("La imagen no tiene un DVD (VIDEO_TS) ni un Blu-ray (BDMV).\n\nSi un programa como AnyDVD te pregunta algo sobre el disco (por ejemplo, su región), contéstale y vuelve a abrir la imagen.","The image has no DVD (VIDEO_TS) or Blu-ray (BDMV).\n\nIf a program such as AnyDVD asks you something about the disc (for example, its region), answer it and open the image again."),tipo="warning",seg=12)   # (JMG, 14-11) AnyDVD y su pregunta de la región
            self._iso_soltar(raiz);return
        self._addl([raiz])
    def _iso_soltar(self,raiz):
        """desmonta la imagen (solo si la montó el programa)"""
        iso,ya=getattr(self,"_isos",{}).pop(raiz,(None,True))
        if iso and not ya and sys.platform=="win32":
            try:rh(["powershell","-NoProfile","-NonInteractive","-Command","Dismount-DiskImage -ImagePath $env:JMG_ISO | Out-Null"],env=dict(os.environ,JMG_ISO=iso),timeout=60)
            except Exception:pass
    def _iso_soltar_todo(self):
        for r_ in list(getattr(self,"_isos",{})):self._iso_soltar(r_)
    def _base(self,ruta):
        """nombre del vídeo sin extensión: de una imagen .iso, el de la imagen; de un DVD en el lector, su etiqueta"""
        iso=(getattr(self,"_isos",{}).get(ruta) or (None,))[0]
        if iso:return os.path.splitext(os.path.basename(iso))[0]
        b=os.path.basename(str(ruta).rstrip("\\/"))
        if not b:
            try:
                import ctypes;buf=ctypes.create_unicode_buffer(261)
                if ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(str(ruta)),buf,261,None,None,None,None,0) and buf.value:return buf.value
            except Exception:pass
            return "DVD"
        return b if os.path.isdir(str(ruta)) else os.path.splitext(b)[0]
    def _dir_orig(self,ruta):
        """carpeta «junto al original»; de un disco en el lector o de una imagen .iso, Vídeos (JMG, 14-11)"""
        iso=(getattr(self,"_isos",{}).get(ruta) or (None,))[0]
        if iso or not os.path.basename(str(ruta).rstrip("\\/")):return _carpeta_usuario("videos")
        return os.path.dirname(str(ruta).rstrip("\\/"))
    # ---------- «💿 Crear ISO» (JMG, 8-11) ----------
    _ISO_PS=r"""$ErrorActionPreference='Stop'
$fs=New-Object -ComObject IMAPI2FS.MsftFileSystemImage
$fs.FileSystemsToCreate=[int]$env:JMG_FS
try{$fs.UDFRevision=[int]$env:JMG_UDF}catch{}
try{$fs.FreeMediaBlocks=0}catch{}
$fs.VolumeName=$env:JMG_VOL
$fs.Root.AddTree($env:JMG_SRC,$false)
$r=$fs.CreateResultImage()
Add-Type -TypeDefinition @'
using System; using System.IO; using System.Runtime.InteropServices; using System.Runtime.InteropServices.ComTypes;
public class JmgIso { public static void W(string p, object o, int bs, long n) {
  IStream s = o as IStream; using (FileStream f = new FileStream(p, FileMode.Create, FileAccess.Write)) {
  byte[] b = new byte[bs * 512]; IntPtr r = Marshal.AllocHGlobal(4); long hecho = 0; int ult = -1;
  while (hecho < n) { int q = (int)Math.Min(512, n - hecho); s.Read(b, bs * q, r); int l = Marshal.ReadInt32(r); if (l <= 0) break;
    f.Write(b, 0, l); hecho += q; int pc = (int)(hecho * 100 / n); if (pc != ult) { ult = pc; Console.WriteLine("P " + pc); } }
  Marshal.FreeHGlobal(r); } } }
'@
[JmgIso]::W($env:JMG_OUT,$r.ImageStream,$r.BlockSize,[long]$r.TotalBlocks)
Write-Output "OK"
"""
    def _isoc_ventana(self):
        V_=self._vt
        if getattr(self,"_isoc_top",None) is not None:
            try:self._isoc_top.deiconify();self._isoc_top.lift();return
            except Exception:self._isoc_top=None
        top=tk.Toplevel(self.root);self._isoc_top=top;top.title(V_("Crear imagen ISO","Create ISO image"));top.configure(bg=CF)
        visible=bool(self.root.winfo_viewable())
        if visible:top.transient(self.root)   # (JMG, 16-11) con la principal escondida (botón derecho) va sola, con su botón en la barra de tareas
        top.protocol("WM_DELETE_WINDOW",self._isoc_cerrar)
        f=ttk.Frame(top);f.pack(fill="both",expand=True,padx=14,pady=10)
        ttk.Label(f,text="💿 "+V_("Crear una imagen ISO de un DVD o un Blu-ray","Create an ISO image of a DVD or a Blu-ray"),font=("",11,"bold")).grid(row=0,column=0,columnspan=3,sticky="w")
        ttk.Label(f,text=V_("Desde una carpeta (la de un DVD o Blu-ray tiene VIDEO_TS o BDMV) o copiando tal cual el disco del lector. De un disco protegido sale una copia exacta, igual de protegida. Para quedarte solo con la película y los idiomas que quieras, «🎬 Solo la película».",
                            "From a folder (a DVD or Blu-ray one has VIDEO_TS or BDMV) or copying the disc in the drive as it is. A protected disc gives an exact copy, just as protected. To keep only the movie and the languages you want, «🎬 Only the movie»."),
                  foreground=CA,font=("",8,"italic"),wraplength=640,justify="left").grid(row=1,column=0,columnspan=3,sticky="w",pady=(2,10))
        self.var_isoc_modo=tk.StringVar(value="carpeta");self.var_isoc_src=tk.StringVar();self.var_isoc_sal=tk.StringVar();self.var_isoc_vol=tk.StringVar()
        ttk.Radiobutton(f,text=V_("Carpeta:","Folder:"),variable=self.var_isoc_modo,value="carpeta",style="G.TRadiobutton").grid(row=2,column=0,sticky="w")
        self._entry(f,self.var_isoc_src,54).grid(row=2,column=1,sticky="w",padx=6,ipady=2)
        ttk.Button(f,text="📁 "+V_("Elegir...","Choose..."),command=self._isoc_elegir_src).grid(row=2,column=2,sticky="w")
        ttk.Radiobutton(f,text=V_("Disco del lector:","Disc in the drive:"),variable=self.var_isoc_modo,value="disco",style="G.TRadiobutton").grid(row=3,column=0,sticky="w",pady=(6,0))
        self.cb_isoc_un=ttk.Combobox(f,width=52,state="readonly",postcommand=self._isoc_unidades);self.cb_isoc_un.grid(row=3,column=1,sticky="w",padx=6,pady=(6,0))
        self.cb_isoc_un.bind("<<ComboboxSelected>>",lambda e:(self.var_isoc_modo.set("disco"),self._isoc_proponer(True)))
        ttk.Label(f,text=V_("Imagen ISO:","ISO image:")).grid(row=4,column=0,sticky="w",pady=(12,0))
        self._entry(f,self.var_isoc_sal,54).grid(row=4,column=1,sticky="w",padx=6,pady=(12,0),ipady=2)
        ttk.Button(f,text="💾 "+V_("Guardar como...","Save as..."),command=self._isoc_elegir_sal).grid(row=4,column=2,sticky="w",pady=(12,0))
        ttk.Label(f,text=V_("Nombre del disco:","Disc name:")).grid(row=5,column=0,sticky="w",pady=(6,0))
        self._entry(f,self.var_isoc_vol,32).grid(row=5,column=1,sticky="w",padx=6,pady=(6,0),ipady=2)
        self.pb_isoc=ttk.Progressbar(f,mode="determinate",maximum=100,style="V.Horizontal.TProgressbar");self.pb_isoc.grid(row=6,column=0,columnspan=3,sticky="ew",pady=(14,2))
        self.lbl_isoc=ttk.Label(f,text="",foreground=CID,wraplength=640,justify="left");self.lbl_isoc.grid(row=7,column=0,columnspan=3,sticky="w")
        self.var_isoc_apagar=tk.BooleanVar(value=False)   # (JMG, 8-11) copiar un Blu-ray tarda: se puede dejar y que apague
        ttk.Checkbutton(f,text=V_("Apagar el PC al terminar","Shut down the PC when done"),variable=self.var_isoc_apagar,style="G.TCheckbutton").grid(row=9,column=0,columnspan=3,sticky="w",pady=(8,0))
        bf=ttk.Frame(f);bf.grid(row=8,column=0,columnspan=3,sticky="ew",pady=(12,0))
        self.btn_isoc=ttk.Button(bf,text="💿 "+V_("Crear ISO","Create ISO"),command=self._isoc_crear);self.btn_isoc.pack(side="left")
        self.btn_isoc_c=ttk.Button(bf,text=T("cancelar"),command=self._isoc_cancelar,state="disabled");self.btn_isoc_c.pack(side="left",padx=6)
        self.btn_isoc_ab=ttk.Button(bf,text="📀 "+V_("Abrir en la lista","Open in the list"),command=self._isoc_abrir_lista,state="disabled");self.btn_isoc_ab.pack(side="left",padx=(12,0))
        b_pel=ttk.Button(bf,text="🎬 "+V_("Solo la película...","Only the movie..."),command=self._isoc_pelicula);b_pel.pack(side="left",padx=(12,0))
        self._ayuda_flotante(b_pel,V_("La película principal del DVD o Blu-ray (sin extras ni menús) se abre aquí en Passthrough:\nmarcas los idiomas y subtítulos que quieras y sale un MKV solo con eso, sin perder calidad.",
                                      "The main movie of the DVD or Blu-ray (no extras or menus) opens here in Passthrough:\nyou mark the languages and subtitles you want and you get an MKV with only that, without losing quality."))
        ttk.Button(bf,text=T("cerrar"),command=self._isoc_cerrar).pack(side="right")
        self._isoc_auto=True;self._isoc_proc=None;self._isoc_hecha=None;self._isoc_unidades()
        # (JMG, 8-11) por defecto, el disco del lector (los que tienen disco; antes los que no son imágenes abiertas aquí)
        con=[i for i,(r_,_) in enumerate(getattr(self,"_isoc_un_l",[])) if os.path.isdir(r_)]
        con.sort(key=lambda i:self._isoc_un_l[i][0] in getattr(self,"_isos",{}))
        if con:
            try:self.cb_isoc_un.current(con[0]);self.var_isoc_modo.set("disco");self._isoc_proponer(True)
            except Exception:pass
        try:
            top.update_idletasks()
            if visible:top.geometry(f"+{self.root.winfo_rootx()+80}+{self.root.winfo_rooty()+80}")
            else:top.geometry(f"+{max(0,(top.winfo_screenwidth()-top.winfo_reqwidth())//2)}+{max(0,(top.winfo_screenheight()-top.winfo_reqheight())//3)}")
        except Exception:pass
        self._bloquear_principal(True)
        try:top.grab_set()
        except Exception:pass
    def _isoc_cerrar(self):
        corriendo=False
        try:corriendo=bool(self.btn_isoc.instate(["disabled"]))
        except Exception:pass
        solo=getattr(self,"_isoc_solo",False)
        if getattr(self,"_isoc_proc",None) is not None or (corriendo and solo):self._isoc_cancelar()
        try:self._isoc_top.grab_release();self._isoc_top.destroy()
        except Exception:pass
        if getattr(self,"_isoc_top",None) is not None:self._isoc_top=None;self._bloquear_principal(False)
        if solo:   # (JMG, 16-11) abierto solo para la imagen (botón derecho): al cerrar la ventana, el programa se cierra
            if corriendo:self._isoc_salir=True   # cuando se haya borrado la imagen a medias (_isoc_fin)
            else:self.root.after(150,self.root.destroy)
    def _isoc_unidades(self):
        """lectores de DVD / Blu-ray (y las imágenes montadas, que Windows ve igual)"""
        l=[]
        if sys.platform=="win32":
            import ctypes,string
            for c in string.ascii_uppercase:
                r_=c+":\\"
                try:
                    if ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(r_))==5:l.append((r_,self._base(r_) if os.path.isdir(r_) else self._vt("(sin disco)","(no disc)")))
                except Exception:pass
        self._isoc_un_l=l
        try:
            self.cb_isoc_un.configure(values=[f"{r_}  {t}" for r_,t in l] or [self._vt("No hay ningún lector de DVD / Blu-ray","There is no DVD / Blu-ray drive")])
            if l and self.cb_isoc_un.current()<0:self.cb_isoc_un.current(0)
        except Exception:pass
    def _isoc_raiz(self):
        """(raíz del DVD/BD, es disco) de lo elegido"""
        if self.var_isoc_modo.get()=="disco":
            k=self.cb_isoc_un.current();l=getattr(self,"_isoc_un_l",[])
            return (l[k][0],True) if 0<=k<len(l) else (None,True)
        s=self.var_isoc_src.get().strip().rstrip("\\/")
        if s and os.path.basename(s).upper() in ("VIDEO_TS","BDMV"):s=os.path.dirname(s)
        return (s or None,False)
    def _isoc_proponer(self,forzar=False):
        r_,disco=self._isoc_raiz()
        if not r_:return
        nom=re.sub(r'[<>:"/\\|?*]',"_",self._disco_titulo(r_,disco)).strip().rstrip(".") or "DISCO"   # (JMG, 8-11) el nombre del disco
        vol=(self._etiqueta(r_) if disco else "") or re.sub(r"[^A-Za-z0-9_]","_",nom.upper())[:32].strip("_") or "DVD"
        if forzar or self._isoc_auto or not self.var_isoc_sal.get().strip():
            d=self._dir_orig(r_) if disco else os.path.dirname(r_)
            self.var_isoc_sal.set(os.path.join(d,nom+".iso"));self._isoc_auto=True
        self.var_isoc_vol.set(vol)
    def _isoc_elegir_src(self):
        d=filedialog.askdirectory(title=self._vt("Carpeta del DVD o del Blu-ray (la que tiene VIDEO_TS o BDMV)","DVD or Blu-ray folder (the one with VIDEO_TS or BDMV)"),parent=self._isoc_top)
        if d:self.var_isoc_src.set(os.path.normpath(d));self.var_isoc_modo.set("carpeta");self._isoc_proponer(True)
    def _isoc_elegir_sal(self):
        r_,_=self._isoc_raiz();ini=self.var_isoc_sal.get().strip()
        f=filedialog.asksaveasfilename(title=self._vt("Guardar la imagen ISO","Save the ISO image"),parent=self._isoc_top,defaultextension=".iso",filetypes=[(self._vt("Imagen de disco","Disc image"),"*.iso")],
                                       initialdir=os.path.dirname(ini) if ini else None,initialfile=os.path.basename(ini) if ini else None)
        if f:self.var_isoc_sal.set(os.path.normpath(f));self._isoc_auto=False
    def _isoc_tam(self,r_,disco):
        try:
            if disco and sys.platform=="win32":
                import ctypes;t=ctypes.c_ulonglong(0);ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(r_),None,ctypes.byref(t),None);return t.value
            return sum(os.path.getsize(os.path.join(a,f)) for a,_,fs in os.walk(r_) for f in fs)
        except Exception:return 0
    def _isoc_crear(self):
        V_=self._vt;r_,disco=self._isoc_raiz();sal=self.var_isoc_sal.get().strip()
        if not r_ or not os.path.isdir(r_):self._toast(T("warn_tit"),V_("Elige la carpeta del DVD o del Blu-ray, o un disco.","Choose the DVD or Blu-ray folder, or a disc."),tipo="warning",seg=5);return
        if disco and sys.platform!="win32":self._toast(T("info_tit"),V_("En Linux, monta el disco y elige su carpeta.","On Linux, mount the disc and choose its folder."),seg=6);return
        vs=self._vobs(r_);q=_disco_protegido(vs) if vs else None
        if q:   # (JMG, 8-11) se puede hacer igual: una copia exacta, con su protección (el programa no la quita)
            si=self._confirm(V_("Disco protegido","Protected disc"),V_(f"Este disco está protegido contra copia ({q}).\n\nLa imagen será una copia exacta, igual de protegida: no se podrá abrir en este programa, solo en un reproductor que admita discos protegidos. El programa no quita la protección.\n\n¿Crearla de todos modos?",
                                                                      f"This disc is copy-protected ({q}).\n\nThe image will be an exact copy, just as protected: it cannot be opened in this program, only in a player that supports protected discs. The program does not remove the protection.\n\nCreate it anyway?"))
            try:self._isoc_top.grab_set()
            except Exception:pass
            if not si:return
        if not sal.lower().endswith(".iso"):sal+=".iso"
        sal=os.path.normpath(sal);self.var_isoc_sal.set(sal)
        if os.path.normcase(os.path.abspath(sal)).startswith(os.path.normcase(os.path.abspath(r_))+os.sep):
            self._toast(T("warn_tit"),V_("La imagen no puede ir dentro de la carpeta que se copia.","The image cannot go inside the folder being copied."),tipo="warning",seg=5);return
        tam=self._isoc_tam(r_,disco)
        try:libre=shutil.disk_usage(os.path.dirname(sal) or ".").free
        except OSError:libre=0
        if tam and libre and libre<tam*1.02+50e6:self._toast(T("warn_tit"),V_(f"No hay sitio: hacen falta {tam/1e9:.1f} GB y quedan {libre/1e9:.1f} GB.",f"Not enough space: {tam/1e9:.1f} GB needed and {libre/1e9:.1f} GB free."),tipo="warning",seg=6);return
        if os.path.exists(sal):
            si=self._confirm(V_("Ya existe","It already exists"),V_("Ya hay una imagen con ese nombre. ¿Sustituirla?","There is already an image with that name. Replace it?"))
            try:self._isoc_top.grab_set()
            except Exception:pass
            if not si:return
        bd=os.path.isdir(os.path.join(r_,"BDMV")) or os.path.basename(r_).upper()=="BDMV"
        vol=re.sub(r"[^A-Za-z0-9_]","_",self.var_isoc_vol.get().strip().upper())[:32] or "DVD"
        self._isoc_cancel=False;self._isoc_hecha=None;self.pb_isoc.configure(value=0)
        for b_,s_ in ((self.btn_isoc,"disabled"),(self.btn_isoc_c,"!disabled"),(self.btn_isoc_ab,"disabled")):b_.state([s_])
        self.lbl_isoc.configure(text=V_("Preparando...","Preparing..."))
        def prog(x,txt=""):self._ui(self._isoc_prog,x,txt)
        def hilo():
            t0=time.time()
            try:ok,msg=(self._isoc_disco(r_,sal,prog,tam) if disco else self._isoc_carpeta(r_,sal,vol,bd,prog))
            except Exception as e:ok,msg=False,str(e)
            self._ui(self._isoc_fin,ok,msg,sal,time.time()-t0)
        threading.Thread(target=hilo,daemon=True).start()
    def _isoc_prog(self,x,txt=""):
        try:self.pb_isoc.configure(value=max(0.0,min(100.0,x*100)));self.lbl_isoc.configure(text=txt or f"{x*100:.0f} %")
        except Exception:pass
    def _isoc_carpeta(self,r_,sal,vol,bd,prog):
        """carpeta -> ISO: DVD con ISO 9660 + Joliet + UDF 1.02 (lo que leen los reproductores); Blu-ray solo con UDF 2.50"""
        V_=self._vt
        if sys.platform!="win32":
            x=shutil.which("xorriso")
            if not x:return False,V_("Hace falta «xorriso» (sudo apt install xorriso).","«xorriso» is needed (sudo apt install xorriso).")
            r=rh([x,"-as","mkisofs","-iso-level","3","-udf","-J","-R","-V",vol,"-o",sal,r_],timeout=None)
            return r.returncode==0,(r.stderr or "")[-300:]
        ps=os.path.join(self._tmp,"crear_iso.ps1")
        with open(ps,"w",encoding="utf-8-sig") as fh:fh.write(self._ISO_PS)
        env=dict(os.environ,JMG_SRC=r_,JMG_OUT=sal,JMG_VOL=vol,JMG_FS="4" if bd else "7",JMG_UDF=str(0x250 if bd else 0x102))
        prog(0.0,V_("Leyendo la carpeta...","Reading the folder..."))
        p=subprocess.Popen(["powershell","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-File",ps],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="ignore",env=env,creationflags=CNW)
        self._isoc_proc=p;fin=False
        for l in p.stdout:
            l=l.strip()
            if l.startswith("P "):
                try:x=int(l[2:])/100.0;prog(x,V_(f"Creando la imagen · {x*100:.0f} %",f"Creating the image · {x*100:.0f} %"))
                except ValueError:pass
            elif l=="OK":fin=True
        p.wait();err=p.stderr.read();self._isoc_proc=None
        if self._isoc_cancel:return False,"cancel"
        return (fin and p.returncode==0 and os.path.isfile(sal)),err[-400:]
    def _isoc_disco(self,r_,sal,prog,tam):
        """disco -> ISO: copia exacta, sector a sector (la unidad entera). (JMG, 8-11: «va muy lento») un hilo lee del lector
        bloques de 4 MB mientras este escribe el anterior: el lector no espera al disco duro. El final, de 2 KB en 2 KB"""
        import queue
        V_=self._vt;cola=queue.Queue(maxsize=16);t0=time.time()
        def lee():
            BS=4<<20;n=0
            try:
                with open("\\\\.\\"+r_[:2],"rb",buffering=0) as fi:
                    while not self._isoc_cancel:
                        try:d=fi.read(BS)
                        except OSError as e:
                            if BS>2048:BS=2048;continue   # el final del disco no llena un bloque grande: se termina sector a sector
                            if tam and n>=tam*0.98:break   # algunos lectores fallan en los últimos sectores, fuera de los datos
                            cola.put(("error",n,e));return
                        if not d:
                            if BS>2048:BS=2048;continue
                            break
                        cola.put(("datos",d));n+=len(d)
            except OSError as e:cola.put(("error",n,e));return
            cola.put(("fin",))
        threading.Thread(target=lee,daemon=True).start()
        n=0;ult=0.0
        with open(sal,"wb") as fo:
            while True:
                try:q=cola.get(timeout=0.5)
                except Exception:
                    if self._isoc_cancel:return False,"cancel"
                    continue
                if q[0]=="fin":break
                if q[0]=="error":
                    return False,V_(f"No se puede leer el disco en el {q[1]/1e9:.2f} GB (¿rayado?): {q[2]}",f"The disc cannot be read at {q[1]/1e9:.2f} GB (scratched?): {q[2]}")
                fo.write(q[1]);n+=len(q[1])
                if self._isoc_cancel:return False,"cancel"
                ahora=time.time()
                if tam and ahora-ult>0.25:
                    ult=ahora;v=n/max(1e-6,ahora-t0);x=min(1.0,n/tam);rest=(tam-n)/v if v>0 else 0
                    prog(x,V_(f"Copiando el disco · {x*100:.0f} % · {n/1e9:.2f} de {tam/1e9:.2f} GB · {v/1e6:.1f} MB/s · quedan {_hms(rest).split('.')[0]}",
                              f"Copying the disc · {x*100:.0f} % · {n/1e9:.2f} of {tam/1e9:.2f} GB · {v/1e6:.1f} MB/s · {_hms(rest).split('.')[0]} left"))
        if self._isoc_cancel:return False,"cancel"   # el hilo que lee para al cancelar: no es un final bueno
        return n>0,""
    def _isoc_cancelar(self):
        self._isoc_cancel=True
        p=getattr(self,"_isoc_proc",None)
        if p is not None:
            try:p.kill()
            except Exception:pass
    def _isoc_fin(self,ok,msg,sal,seg):
        V_=self._vt
        try:
            for b_,s_ in ((self.btn_isoc,"!disabled"),(self.btn_isoc_c,"disabled")):b_.state([s_])
        except Exception:pass
        if ok:
            self._isoc_hecha=sal;self._log("[ISO] "+sal)
            try:self.pb_isoc.configure(value=100);self.lbl_isoc.configure(text=V_(f"Imagen creada en {_hms(seg).split('.')[0]}: ",f"Image created in {_hms(seg).split('.')[0]}: ")+sal);self.btn_isoc_ab.state(["!disabled"])
            except Exception:pass
            self._toast(T("info_tit"),V_("Imagen ISO creada:\n","ISO image created:\n")+sal,seg=6)
            if self.var_isoc_apagar.get():self._apagar()   # (JMG, 8-11)
        else:
            try:
                if os.path.isfile(sal):os.remove(sal)
            except OSError:pass
            txt=V_("Cancelado: la imagen a medias se ha borrado.","Cancelled: the unfinished image has been deleted.") if msg=="cancel" else V_("No se ha podido crear la imagen: ","Could not create the image: ")+str(msg).strip()[-300:]
            if msg!="cancel":
                self._log("[ISO] "+txt)
                if self.var_isoc_apagar.get():self._apagar()   # con error también (nadie mira); cancelado, no
            try:self.pb_isoc.configure(value=0);self.lbl_isoc.configure(text=txt)
            except Exception:pass
        if getattr(self,"_isoc_salir",False):   # (JMG, 16-11) se cerró copiando, con el programa abierto solo para la imagen
            self._isoc_salir=False
            if getattr(self,"_isoc_solo",False):self.root.after(300,self.root.destroy)
    def _etiqueta(self,raiz):
        """etiqueta del disco (la de verdad, también de una imagen montada)"""
        try:
            import ctypes;buf=ctypes.create_unicode_buffer(261)
            if ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(str(raiz)),buf,261,None,None,None,None,0):return buf.value.strip()
        except Exception:pass
        return ""
    def _disco_titulo(self,r_,disco):
        """(JMG, 8-11) nombre de la imagen: el título que lleva el Blu-ray (BDMV/META, en español o inglés si los hay);
        si no, la etiqueta del disco (DVD, BD o CD) y, de una carpeta, su nombre"""
        import html
        b=os.path.dirname(r_.rstrip("\\/")) if os.path.basename(r_.rstrip("\\/")).upper()=="BDMV" else r_
        try:
            meta=os.path.join(b,"BDMV","META","DL")
            for n in sorted(os.listdir(meta),key=lambda n:(0 if "spa" in n.lower() else 1 if "eng" in n.lower() else 2,n)):
                if n.lower().startswith("bdmt_") and n.lower().endswith(".xml"):
                    with open(os.path.join(meta,n),encoding="utf-8",errors="ignore") as fh:t=fh.read()
                    m=re.search(r"<di:name>\s*(.*?)\s*</di:name>",t,re.S)
                    if m and m.group(1).strip():return html.unescape(m.group(1).strip())
        except OSError:pass
        if disco:
            et=self._etiqueta(r_)
            if et:return et
        return os.path.basename(b.rstrip("\\/")) or self._base(r_)
    def _isoc_pelicula(self):
        """(JMG, 8-11) «Solo la película»: la película principal se abre en el VideoEncoder en Passthrough para elegir idiomas y
        subtítulos y sacar un MKV solo con eso (una ISO con pistas elegidas obligaría a rehacer los menús del disco)"""
        V_=self._vt;r_,disco=self._isoc_raiz()
        if not r_ or not os.path.isdir(r_):self._toast(T("warn_tit"),V_("Elige la carpeta del DVD o del Blu-ray, o un disco.","Choose the DVD or Blu-ray folder, or a disc."),tipo="warning",seg=5);return
        if not self._vobs(r_):self._toast(T("warn_tit"),V_("Ahí no hay un DVD (VIDEO_TS) ni un Blu-ray (BDMV).","There is no DVD (VIDEO_TS) or Blu-ray (BDMV) there."),tipo="warning",seg=5);return
        self._isoc_solo=False;self._ext_solo=False;self._bandeja_volver()   # (JMG, 16-11) la película va a la lista: el programa entero
        self._isoc_cerrar();r_=os.path.normpath(r_);self._pel_pend=r_
        self._addl([r_]);self.root.after(300,self._isoc_pel_espera)   # si está protegido, _probe_fin avisa y no entra
    def _isoc_pel_espera(self,n=0):
        V_=self._vt;r_=getattr(self,"_pel_pend",None)
        if not r_ or r_ not in self.files:self._pel_pend=None;return
        if r_ not in self.info:
            if n<600:self.root.after(300,lambda:self._isoc_pel_espera(n+1))
            return
        self._pel_pend=None
        try:
            i=self.files.index(r_);self.la.selection_clear(0,"end");self.la.selection_set(i);self.la.see(i);self._sarch();self._agregar()
            j=self.jobs.get(r_)
            if j:j["v"]["codec"]="copy";self._pintar_trabajo()
            w_=self.nb.nametowidget(self.nb.tabs()[0]);self.nb.select(w_)   # (JMG, 14-11) a la pestaña Vídeo (antes Audio), arriba del todo
            self.root.update_idletasks();self._tab_in[str(w_)].master.yview_moveto(0)
        except Exception as e:self._log(f"[ISO] {e}")
        lento=""   # (JMG, 13-11) leída directamente del lector (no de una carpeta ni de una imagen montada): el consejo de la imagen ISO
        if _lector_fisico(r_) and not any(str(k)[:2].upper()==r_[:2].upper() for k in getattr(self,"_isos",{})):   # (JMG, 13-11) un lector de verdad
            lento=V_("\n\n⚠ Ripear directamente del disco es lento e inestable: se aconseja hacer antes una imagen ISO («💿 Crear ISO...») y abrirla con «📀 DVD/BD».",
                     "\n\n⚠ Ripping straight from the disc is slow and unstable: it is better to make an ISO image first («💿 Create ISO...») and open it with «📀 DVD/BD».")
        self._toast(T("info_tit"),V_("La película principal está en la lista, en Passthrough (sin perder calidad).\nMarca en Audio y Subtítulos los idiomas que quieras y pulsa PROCESAR: sale un vídeo solo con eso (mejor en MKV).",
                                    "The main movie is in the list, in Passthrough (no quality loss).\nMark the languages you want in Audio and Subtitles and press PROCESS: you get a video with only that (best as MKV).")+lento,seg=18 if lento else 12)
    def _isoc_abrir_lista(self):
        if self._isoc_hecha and os.path.isfile(self._isoc_hecha):self._isoc_solo=False;self._bandeja_volver();self._iso_abrir(self._isoc_hecha)   # (JMG, 16-11) a la lista: el programa entero
    # ---------- Aften Dolby Digital en el códec de la pista (JMG, 9-11) ----------
    def _aften_estado(self):
        try:
            on=self.var_a_cod.get()=="aften" and AFTEN
            self.btn_af.state(["!disabled"] if (on or self.var_a_cod.get() in OPC) else ["disabled"])   # (JMG, 12-11) y las opciones de los demás
            a=self._af_actual();vbr=on and a.get("modo")=="vbr"   # (JMG, 10-11) con VBR manda la calidad de Aften, no los kbps
            self.lbl_afvbr.configure(text=f"VBR {int(a.get('q',240))}" if vbr else "")
            if vbr:self.cb_akbps.configure(state="disabled")
            elif self.cb_akbps.cget("values"):self.cb_akbps.configure(state="normal" if self.var_a_cod.get()=="eac3" else "readonly")   # (revisión, 17-11) también al salir de Aften en VBR
        except Exception:pass
    def _af_de(self,t=None):
        """(JMG, 10-11) los ajustes de Aften de una pista: cada pista los suyos (si no tiene, los de fábrica)"""
        a=dict(AFTEN_DEF)
        if t is not None and isinstance(t.get("af"),dict):a.update({k:v for k,v in _af_migrar(t["af"]).items() if k in AFTEN_DEF})
        return a
    def _af_pista(self):
        j=self._job();i=getattr(self,"_a_i",None)
        if j and i is not None and 0<=i<len(j["a"]):return j["a"][i]
        return None
    def _af_actual(self):return self._af_de(self._af_pista())
    def _af_titulo(self):
        t=self._af_pista()
        return (self._vt(" · pista "," · track ")+f"#{t['idx'] if not t['ext'] else 'ext.'} [{t['lang']}]") if t else ""
    def _af_guardar(self,x):
        """«Aceptar» en la ventana de Aften: solo para la pista seleccionada"""
        t=self._af_pista()
        if t is not None:
            t["af"]=dict(x)
            try:self.tv_a.item(str(self._a_i),values=self._a_fila(self._a_i,t),tags=self._a_tags(t))
            except Exception:pass
        self._aften_estado()
    def _aften_pintar(self):self._aften_estado()
    def _af_modal(self,on):self._bloquear_principal(on)
    def _ex_suav_eq(self):
        """(JMG, 9-11) el Suavizado digital y el ecualizador de 3 bandas no van juntos (como en Jmg AudioProcesador): mientras uno
        tiene algo puesto, el otro queda desactivado"""
        if getattr(self,"_bp_prev",None) is not None:return   # (JMG, 14-11) codificando: todo quieto (lo llama el bucle de los Auto)
        try:
            nz=lambda *vs:any(abs(float(self._raw(v)))>1e-6 for v in vs)
            e3=nz(self.var_eq_bass,self.var_eq_mids,self.var_eq_treble);su=nz(self.var_suav)
            for ws,on in ((getattr(self,"_w_eq3",[]),e3 or not su),(getattr(self,"_w_suav",[]),su or not e3)):
                for w in ws:
                    if isinstance(w,tk.Entry) and not isinstance(w,ttk.Combobox):   # (JMG, 13-11) un desplegable no se vuelve escribible
                        if str(w.cget("state"))!=("normal" if on else "disabled"):w.configure(state="normal" if on else "disabled")
                    elif w.instate(["disabled"])==on:w.state(["!disabled"] if on else ["disabled"])
        except Exception:pass
    # ---------- Aften Dolby Digital (JMG, 9-11): la misma ventana en Jmg AudioProcesador y Jmg VideoEncoder ----------
    _AF_W=[(-2,"Adaptable variable","Variable adaptive"),(-1,"Adaptable fijo","Fixed adaptive"),(60,"Fijo, completo (sin recortar agudos)","Fixed, full (no treble cut)")]
    _AF_DRC=[(5,"Ninguna (toda la gama dinámica)","None (full dynamic range)"),(0,"Film Light","Film Light"),(1,"Film Standard","Film Standard"),(2,"Music Light","Music Light"),(3,"Music Standard","Music Standard"),(4,"Speech","Speech")]
    _AF_IND=[(0,"No indicado","Not indicated"),(1,"No","No"),(2,"Sí","Yes")]
    _AF_NIV=[(0,"+3,0 dB","+3.0 dB"),(1,"+1,5 dB","+1.5 dB"),(2,"0 dB","0 dB"),(3,"-1,5 dB","-1.5 dB"),(4,"-3,0 dB (normal)","-3.0 dB (normal)"),(5,"-4,5 dB","-4.5 dB"),(6,"-6,0 dB","-6.0 dB"),(7,"-∞ (fuera)","-inf (off)")]
    def _aften_resumen(self,a=None):
        V=self._vt;a=a or self._aften
        w=next((V(x,y) for v,x,y in self._AF_W if v==a["w"]),str(a["w"])).split(" (")[0].lower()
        if a["modo"]=="vbr" and a["w"]==-2:w=V("adaptable fijo (con VBR, Aften no admite el variable)","fixed adaptive (with VBR, Aften does not take the variable one)")
        drc=next((V(x,y) for v,x,y in self._AF_DRC if v==a["drc"]),"").split(" (")[0]
        r=("CBR" if a["modo"]=="cbr" else f"VBR {a['q']}")+f" · {w} · exps {a['exps']} · DRC {drc} · dialnorm -{a['dnorm']} dB"
        if a["bs"]:r+=V(" · conmutación de bloques"," · block switching")
        if a.get("dsurex")==2:r+=" · Dolby Surround EX"
        if a.get("dhead")==2:r+=" · Dolby Headphone"
        if a.get("adconv")==1:r+=" · HDCD"
        return r
    @staticmethod
    def _aften_opciones(a):
        """las opciones de Aften (sin el bitrate ni la calidad VBR) de unos ajustes"""
        g=lambda k:str(int(a.get(k,AFTEN_DEF[k])))
        o=["-w",("-1" if (a.get("modo")=="vbr" and int(a.get("w",-2))==-2) else g("w")),"-exps",g("exps"),"-dynrng",g("drc"),"-dnorm",g("dnorm"),"-s",g("bs"),
           "-bwfilter",g("bwf"),"-dcfilter",g("dcf"),"-lfefilter",g("lfef"),"-dsur",g("dsur"),"-cmix",g("cmix"),"-smix",g("smix")]
        if any(a.get(k,AFTEN_DEF[k])!=AFTEN_DEF[k] for k in ("dmix","ltrtc","ltrts","loroc","loros")):
            o+=["-xbsi1","1","-dmixmod",g("dmix"),"-ltrtcmix",g("ltrtc"),"-ltrtsmix",g("ltrts"),"-lorocmix",g("loroc"),"-lorosmix",g("loros")]
        if any(a.get(k,AFTEN_DEF[k])!=AFTEN_DEF[k] for k in ("dsurex","dhead","adconv")):
            o+=["-xbsi2","1","-dsurexmod",g("dsurex"),"-dheadphon",g("dhead"),"-adconvtyp",g("adconv")]
        try:
            import shlex;o+=shlex.split(str(a.get("extra","") or ""),posix=False)
        except ValueError:pass
        return o
    def _aften_ventana(self):
        """ventana con los ajustes de Aften (modal); «Aceptar» los guarda"""
        V=self._vt
        if not AFTEN:
            self._toast(T("warn_tit"),V("No se encuentra aften.exe (va en la carpeta bin): se usa el AC3 de FFmpeg.","aften.exe not found (it goes in the bin folder): FFmpeg's AC3 is used."),tipo="warning",seg=6);return
        if getattr(self,"_af_top",None) is not None:
            try:self._af_top.lift();return
            except Exception:self._af_top=None
        a=self._af_actual()
        top=tk.Toplevel(self.root);self._af_top=top;top.title("Aften · Dolby Digital (AC3)"+self._af_titulo());top.configure(bg=CF);top.transient(self.root)
        f=ttk.Frame(top);f.pack(fill="both",expand=True,padx=16,pady=12)
        cab=ttk.Frame(f);cab.grid(row=0,column=0,columnspan=4,sticky="w",pady=(0,8))
        try:
            self._af_logo=tk.PhotoImage(data=AFTEN_LOGO);tk.Label(cab,image=self._af_logo,bd=0,bg=CF).pack(side="left")
        except Exception:pass
        ci=ttk.Frame(cab);ci.pack(side="left",padx=12)
        ttk.Label(ci,text=V("Codificador Dolby Digital (AC3)","Dolby Digital (AC3) encoder"),font=("",11,"bold")).pack(anchor="w")
        ttk.Label(ci,text=V("Mejor gama dinámica en las películas que tienen mucha.\nFFmpeg le pasa el audio ya procesado, sin pérdida, y Aften hace el AC3.",
                            "Better dynamic range in movies that have a lot.\nFFmpeg passes it the processed audio, losslessly, and Aften makes the AC3."),foreground=CA,font=("",8,"italic"),justify="left").pack(anchor="w",pady=(2,2))
        ln=ttk.Label(ci,text="aften.sourceforge.net",foreground=CID,cursor="hand2",font=("",9,"underline"));ln.pack(anchor="w")
        def web(e=None):
            try:import webbrowser;webbrowser.open("https://aften.sourceforge.net")
            except Exception:pass
        ln.bind("<Button-1>",web)
        vm=tk.StringVar(value=a["modo"]);vq=tk.StringVar(value=str(a["q"]));vex=tk.StringVar(value=a.get("extra",""))
        chk={k:tk.BooleanVar(value=bool(a[k])) for k in ("bs","bwf","dcf","lfef")}
        cbs={}
        def sec(r,txt):ttk.Label(f,text=txt,font=("",10,"bold")).grid(row=r,column=0,columnspan=4,sticky="w",pady=(10,2))
        def combo(r,c,txt,ops,clave,w=26):
            ttk.Label(f,text=txt).grid(row=r,column=c,sticky="w",pady=(3,0),padx=(0 if c==0 else 14,0))
            w=max(w,max(len(V(x,y)) for _,x,y in ops)+1)   # que se lea entera la opción más larga
            cb=ttk.Combobox(f,values=[V(x,y) for _,x,y in ops],width=w,state="readonly");cb.grid(row=r,column=c+1,sticky="w",padx=6,pady=(3,0))
            cbs[clave]=(cb,ops)
        sec(1,V("Codificación","Encoding"))
        ttk.Label(f,text=V("Modo:","Mode:")).grid(row=2,column=0,sticky="w")
        fm=ttk.Frame(f);fm.grid(row=2,column=1,columnspan=3,sticky="w",padx=6)
        ttk.Radiobutton(fm,text=V("CBR (el bitrate elegido)","CBR (the chosen bitrate)"),variable=vm,value="cbr",style="G.TRadiobutton").pack(side="left",padx=(0,8))
        ttk.Radiobutton(fm,text=V("VBR, calidad:","VBR, quality:"),variable=vm,value="vbr",style="G.TRadiobutton").pack(side="left",padx=(0,4))
        cq=ttk.Combobox(fm,textvariable=vq,values=[str(x) for x in (100,160,240,320,400,512,640,768,896,1023)],width=6);cq.pack(side="left")
        lv=ttk.Label(f,text="",foreground=CA,font=("",8,"italic"));lv.grid(row=3,column=1,columnspan=3,sticky="w",padx=6)
        combo(4,0,V("Ancho de banda:","Bandwidth:"),self._AF_W,"w")
        combo(4,2,V("Precisión (exps):","Accuracy (exps):"),[(n,f"{n}"+(" (la máxima)" if n==32 else " (la de Aften)" if n==8 else ""),f"{n}"+(" (maximum)" if n==32 else " (Aften's)" if n==8 else "")) for n in range(32,0,-1)],"exps",16)
        fk=ttk.Frame(f);fk.grid(row=5,column=0,columnspan=4,sticky="w",pady=(6,0))
        for k,t1,t2 in (("bs","Conmutación de bloques (golpes más nítidos)","Block switching (sharper hits)"),("bwf","Filtro del ancho de banda","Bandwidth low-pass filter"),
                        ("dcf","Filtro de continua (DC)","DC high-pass filter"),("lfef","Filtro del subwoofer (120 Hz)","LFE low-pass filter (120 Hz)")):
            ttk.Checkbutton(fk,text=V(t1,t2),variable=chk[k],style="G.TCheckbutton").pack(side="left",padx=(0,12))
        sec(6,V("Gama dinámica","Dynamic range"))
        combo(7,0,V("Compresión (DRC):","Compression (DRC):"),self._AF_DRC,"drc")
        combo(7,2,V("Nivel de diálogo:","Dialogue level:"),[(n,f"-{n} dB"+(" (sin bajar nada)" if n==31 else ""),f"-{n} dB"+(" (no lowering)" if n==31 else "")) for n in range(31,0,-1)],"dnorm",18)
        sec(8,V("Información del flujo (para el amplificador)","Bitstream information (for the amplifier)"))
        combo(9,0,"Dolby Surround EX:",self._AF_IND,"dsurex",14)
        combo(9,2,V("Dolby Headphone (auriculares):","Dolby Headphone:"),self._AF_IND,"dhead",14)
        combo(10,0,V("Dolby Surround (estéreo):","Dolby Surround (stereo):"),self._AF_IND,"dsur",14)
        combo(10,2,V("Conversor A/D:","A/D converter:"),[(0,"Estándar","Standard"),(1,"HDCD","HDCD")],"adconv",14)
        combo(11,0,V("Central en el downmix:","Center in the downmix:"),[(0,"-3,0 dB","-3.0 dB"),(1,"-4,5 dB","-4.5 dB"),(2,"-6,0 dB","-6.0 dB")],"cmix",14)
        combo(11,2,V("Surround en el downmix:","Surround in the downmix:"),[(0,"-3 dB","-3 dB"),(1,"-6 dB","-6 dB"),(2,V("fuera","off"),"off")],"smix",14)
        combo(12,0,V("Downmix preferido:","Preferred downmix:"),[(0,"No indicado","Not indicated"),(1,"Lt/Rt (Pro Logic)","Lt/Rt (Pro Logic)"),(2,"Lo/Ro (estéreo)","Lo/Ro (stereo)")],"dmix",14)
        combo(13,0,"Lt/Rt: "+V("central","center"),self._AF_NIV,"ltrtc",14);combo(13,2,"Lt/Rt: surround",self._AF_NIV,"ltrts",14)
        combo(14,0,"Lo/Ro: "+V("central","center"),self._AF_NIV,"loroc",14);combo(14,2,"Lo/Ro: surround",self._AF_NIV,"loros",14)
        ttk.Label(f,text=V("Argumentos propios:","Own arguments:")).grid(row=15,column=0,sticky="w",pady=(10,0))
        tk.Entry(f,textvariable=vex,width=58,bg=CDN,fg=CT,insertbackground=CT,relief="flat",highlightthickness=1,highlightbackground=CSB,highlightcolor=CID).grid(row=15,column=1,columnspan=3,sticky="w",padx=6,pady=(10,0),ipady=2)
        def ver(*_):
            cq.state(["!disabled"] if vm.get()=="vbr" else ["disabled"])
            lv.configure(text=V("Un AC3 VBR no lo leen todos los reproductores y amplificadores; CBR va en todos.","Not every player or amplifier reads a VBR AC3; CBR works everywhere.") if vm.get()=="vbr" else "")
        vm.trace_add("write",ver)
        def poner(x):
            vm.set(x["modo"]);vq.set(str(x["q"]));vex.set(x.get("extra",""))
            for k,v in chk.items():v.set(bool(x.get(k,0)))
            for k,(cb,ops) in cbs.items():cb.current(next((i for i,o in enumerate(ops) if o[0]==x.get(k,AFTEN_DEF[k])),0))
            ver()
        def leer():
            x=dict(a);x["modo"]=vm.get();x["extra"]=vex.get().strip()
            for k,v in chk.items():x[k]=1 if v.get() else 0
            try:x["q"]=max(0,min(1023,int(float(vq.get()))))
            except ValueError:pass
            for k,(cb,ops) in cbs.items():
                i=cb.current()
                if 0<=i<len(ops):x[k]=ops[i][0]
            return x
        def cerrar():
            try:top.grab_release();top.destroy()
            except Exception:pass
            if self._af_top is not None:self._af_top=None;self._af_modal(False)
        def aceptar():self._af_guardar(leer());cerrar()
        bf=ttk.Frame(f);bf.grid(row=16,column=0,columnspan=4,sticky="ew",pady=(14,0))
        ttk.Button(bf,text="↺ "+V("Por defecto","Default"),command=lambda:poner(dict(AFTEN_DEF))).pack(side="left")
        ttk.Button(bf,text=V("Cancelar","Cancel"),command=cerrar).pack(side="right")
        ttk.Button(bf,text=V("Aceptar","OK"),command=aceptar).pack(side="right",padx=6)
        top.protocol("WM_DELETE_WINDOW",cerrar);poner(a);self._af_modal(True)
        try:top.update_idletasks();top.geometry(f"+{self.root.winfo_rootx()+100}+{self.root.winfo_rooty()+60}");top.grab_set()
        except Exception:pass
        self._af_leer=leer;self._af_aceptar=aceptar;self._af_poner=poner;self._af_cerrar=cerrar   # (para las pruebas)
    def _aften_cmd(self,kb,t=None):
        a=self._af_de(t)   # (JMG, 10-11) los de la pista
        # -pad 0: sin las 256 muestras de relleno del principio (el AC3 de FFmpeg en el MKV las marca y no se oyen; el de Aften no)
        c=[AFTEN,"-v","0","-readtoeof","1","-pad","0"]+(["-q",str(int(a["q"]))] if a["modo"]=="vbr" else ["-b",str(int(kb))])
        return c+self._aften_opciones(a)+["-","-"]
    def _aften_previo(self,t,cod,ss0,ss1,ini,fin,dvd,inf,ruta,log2,K,previos):
        """si esta pista sale en AC3 y lo hace Aften: el paso previo (FFmpeg -> Aften -> temporal .ac3) y la ruta del temporal; si no, None"""
        if previos is None or cod!="ac3" or not t.get("aften",True) or not AFTEN:return None   # (9-11) «Aften Dolby Digital» de esta pista
        if not t["ext"] and "|" in str(inf.get("entrada","")):   # (JMG, 17-11) varios trozos (su tiempo da saltos): Aften no puede seguirlos
            self._ls(self._vt(f"[AFTEN] Pista #{t['idx']}: la película viene en varios trozos y su tiempo da saltos: este AC3 lo hace FFmpeg (Aften lo desincronizaría).",
                              f"[AFTEN] Track #{t['idx']}: the movie comes in several pieces and its time jumps: this AC3 is made by FFmpeg (Aften would put it out of sync)."))
            return None
        k_=_fps_f(t);ent=t["ext"] or inf.get("entrada",ruta)
        pre=[FFMPEG,"-hide_banner","-nostdin","-y","-v","error"]+(["-ss",f"{ss0*k_:.3f}"] if ss0>0 else [])+(dvd if not t["ext"] else [])+(["-core_only","1"] if (str(t.get("codec_in"))=="dts" and "DTS-HD" in str(t.get("perfil",""))) else [])+["-i",ent]
        _as="aresample=async=1:min_hard_comp=0.05"   # (JMG, 17-11) los pequeños huecos de las marcas de tiempo, con silencio
        g=self._a_grafo(t,"[as0]","[x]",post=self._a_post(dict(t,cod=cod)),off=ss0)
        if g:pre+=["-filter_complex",f"[0:{t['idx']}]{_as}[as0];"+g,"-map","[x]"]
        else:   # sin efectos (solo cambia el códec): la pista tal cual, con la conversión de canales que pida el AC3
            po=self._a_post(dict(t,cod=cod));pre+=["-map",f"0:{t['idx']}","-af",_as+(","+po if po else "")]
        pre+=(["-ss",f"{ss1:.3f}"] if ss1>0 else [])+(["-t",f"{fin-ini:.3f}"] if fin>ini else [])
        pre+=["-c:a","pcm_f32le","-progress","pipe:2","-nostats","-f","wav","-"]
        kb=t["kbps"] if t["kbps"] in AKBPS.get(cod,()) else _akbps_def(cod,t["nch"])
        out=f"{log2 or os.path.join(self._tmp,'vista')}_aften{K}.ac3"
        previos.append({"aften":True,"ff":pre,"af":self._aften_cmd(kb,t),"out":out})
        return out
    def _aften_tubo(self,x,dur,base,peso,txt):
        """FFmpeg (WAV en coma flotante por su salida) -> Aften -> el .ac3 temporal, que escribe Python; devuelve (ok, errores)"""
        self._ls("$ "+subprocess.list2cmdline(x["ff"])+" | "+subprocess.list2cmdline(x["af"]))
        err=[];escrito=[0];fallo=[None];t0=time.time()
        try:
            pf=subprocess.Popen(x["ff"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CNW)
            pa=subprocess.Popen(x["af"],stdin=pf.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CNW)
        except Exception as e:return False,[str(e)]
        try:pf.stdout.close()
        except Exception:pass
        self._proc=pf
        def lee_ff():
            try:
                for l in pf.stderr:
                    l=l.decode("utf-8","ignore").strip()
                    if l.startswith("out_time_us=") or l.startswith("out_time_ms="):
                        try:s=int(l.split("=")[1])/1e6
                        except ValueError:continue
                        fr=max(0.0,min(1.0,s/dur)) if dur>0 else 0.0;self._set_prog(base+peso*fr)
                        el=time.time()-t0-self._pausa_desde(t0);rest=el*(1-fr)/fr if fr>0.02 else 0
                        self._st(f"{txt} · Aften · {base+peso*fr:.0f} %"+(self._vt(f" · quedan {_hms(rest).split('.')[0]}",f" · {_hms(rest).split('.')[0]} left") if rest else ""))
                    elif l and "=" not in l:err.append(l);del err[:-40]
            except Exception:pass
        def lee_af():
            try:
                with open(x["out"],"wb") as fo:
                    while True:
                        b_=pa.stdout.read(1<<16)
                        if not b_:break
                        fo.write(b_);escrito[0]+=len(b_)
            except Exception as e:fallo[0]=e
        def err_af():
            try:
                for l in pa.stderr:
                    l=l.decode("utf-8","ignore").strip()
                    if l and "SIMD" not in l and not l.startswith("Threads"):err.append("aften: "+l)
            except Exception:pass
        hs=[threading.Thread(target=f_,daemon=True) for f_ in (lee_ff,lee_af,err_af)]
        for h in hs:h.start()
        while pa.poll() is None:
            if self._cancelar.is_set() or pf.poll() not in (None,0):break   # FFmpeg ha fallado: Aften se quedaría esperando
            time.sleep(0.15)
        for p_ in (pf,pa):
            if p_.poll() is None and (self._cancelar.is_set() or pf.poll() not in (None,0)):
                try:p_.kill()
                except Exception:pass
        for p_ in (pf,pa):
            try:p_.wait(timeout=10)
            except Exception:pass
        for h in hs:h.join(timeout=5)
        self._proc=None
        ok=pf.returncode==0 and pa.returncode==0 and escrito[0]>0 and fallo[0] is None and not self._cancelar.is_set()
        if not ok:
            try:os.remove(x["out"])
            except OSError:pass
            if fallo[0]:err.append(str(fallo[0]))
        return ok,err
    # ---------- nombre del archivo de cada vídeo (JMG, 8-11) ----------
    def _nom_base(self,ruta):
        return self._base(ruta)
    def _nom_pintar(self):
        j=self._job();prev=self._cargando;self._cargando=True
        try:self.var_nom.set((j.get("nombre") or self._nom_base(self.actual)+self.var_sufijo.get()) if j else "")
        except Exception:pass
        finally:self._cargando=prev
    def _nom_cambio(self):
        if self._cargando:return
        j=self._job()
        if not j:return
        v=re.sub(r'[<>:"/\\|?*]',"_",self.var_nom.get()).strip().rstrip(".")
        j["nombre"]=v if (v and v!=self._nom_base(self.actual)+self.var_sufijo.get()) else None
        try:self._refrescar_estado()
        except Exception:pass
    def _nom_def(self):
        j=self._job()
        if j:j["nombre"]=None
        self._nom_pintar()
    # ---------- Combinar: la imagen para elegir inicio y fin, y la pista de audio de cada trozo (JMG, 8-11) ----------
    def _cb_job(self,ruta):
        """el trabajo del vídeo (el agregado o uno nuevo, para saber qué pistas van marcadas por defecto)"""
        if ruta in self.jobs:return self.jobs[ruta]
        if not hasattr(self,"_cb_jobs"):self._cb_jobs={}
        if ruta not in self._cb_jobs:self._cb_jobs[ruta]=self._nuevo_trabajo(ruta)
        return self._cb_jobs[ruta]
    def _cb_aud_txt(self,c):
        try:
            inf=self.info.get(c["ruta"],{})
            if c.get("a") is not None:
                s=next((s for s in inf.get("streams",[]) if s.get("index")==c["a"]),{})
                return f"#{c['a']} {(s.get('tags') or {}).get('language','und')}"
            ls=[t["lang"] or "und" for t in self._cb_job(c["ruta"])["a"] if t["incl"] and not t["ext"]]
            return ", ".join(ls) or "—"
        except Exception:return ""
    def _cb_vista(self,f):
        V_=self._vt
        fv=ttk.Frame(f);fv.pack(fill="x",pady=(8,0))
        caja=tk.Frame(fv,bg="#000000",width=384,height=216);caja.pack(side="left");caja.pack_propagate(False)
        self.lbl_cb_img=tk.Label(caja,bg="#000000",fg=CA,text=V_("Elige un trozo de la lista","Choose a part from the list"));self.lbl_cb_img.pack(expand=True,fill="both")
        dr=ttk.Frame(fv);dr.pack(side="left",fill="x",expand=True,padx=(12,0),anchor="n")
        self.var_cb_pos=tk.DoubleVar(value=0.0)
        self.lbl_cb_t=ttk.Label(dr,text="0:00:00",font=("",10,"bold"))
        self.sc_cb=ttk.Scale(dr,from_=0,to=1,variable=self.var_cb_pos,orient="horizontal",length=380,command=lambda v:self.lbl_cb_t.configure(text=_hms(float(v)).split(".")[0]))
        self.sc_cb.pack(anchor="w");self.sc_cb.bind("<ButtonRelease-1>",lambda e:self._cb_foto())
        self.lbl_cb_t.pack(anchor="w",pady=(2,4))
        fbt=ttk.Frame(dr);fbt.pack(anchor="w")
        for t_,d_ in (("◀◀ 10 s",-10),("◀ 1 s",-1),("1 s ▶",1),("10 s ▶▶",10)):ttk.Button(fbt,text=t_,command=lambda d_=d_:self._cb_paso(d_)).pack(side="left",padx=(0,4))
        fbi=ttk.Frame(dr);fbi.pack(anchor="w",pady=(6,0))
        ttk.Button(fbi,text="⏮ "+V_("Inicio aquí","Start here"),command=lambda:self._cb_marcar("ini")).pack(side="left")
        ttk.Button(fbi,text=V_("Fin aquí","End here")+" ⏭",command=lambda:self._cb_marcar("fin")).pack(side="left",padx=6)
        fa=ttk.Frame(dr);fa.pack(anchor="w",pady=(10,0))
        ttk.Label(fa,text=V_("Audio de este trozo:","Audio of this part:")).pack(side="left")
        self.cb_cb_aud=ttk.Combobox(fa,width=42,state="readonly");self.cb_cb_aud.pack(side="left",padx=6)
        self.cb_cb_aud.bind("<<ComboboxSelected>>",lambda e:self._cb_aud_elegir())
        ttk.Label(dr,text=V_("Los subtítulos de texto marcados de cada vídeo (pestaña Subtítulos) también van.","The marked text subtitles of each video (Subtitles tab) go too."),
                  foreground=CA,font=("",8,"italic")).pack(anchor="w",pady=(6,0))
        self._cb_aud_ops=[];self._cb_vis_i=None
    def _cb_actual(self):
        try:s=self.tv_cb.selection()
        except Exception:return None
        return int(s[0]) if s and int(s[0])<len(self._clips) else None
    def _cb_vista_ir(self,i):
        try:
            c=self._clips[i];inf=self.info.get(c["ruta"],{});self._cb_vis_i=(i,c["ruta"])
            self.sc_cb.configure(to=max(1.0,_dur(inf)));self.var_cb_pos.set(c["ini"]);self.lbl_cb_t.configure(text=_hms(c["ini"]).split(".")[0])
            self._cb_aud_ops=[(None,self._vt("Las marcadas en la pestaña Audio","The ones marked in the Audio tab"))]+[
                (s["index"],f"#{s['index']} [{(s.get('tags') or {}).get('language','und')}] {str(s.get('codec_name','')).upper()} {s.get('channel_layout') or str(s.get('channels',''))+' ch'}"
                 +(f" · {(s.get('tags') or {}).get('title')}" if (s.get('tags') or {}).get('title') else "")) for s in inf.get("streams",[]) if s.get("codec_type")=="audio"]
            self.cb_cb_aud.configure(values=[t for _,t in self._cb_aud_ops])
            self.cb_cb_aud.current(next((k for k,(x,_) in enumerate(self._cb_aud_ops) if x==c.get("a")),0))
            self._cb_foto()
        except Exception as e:self._log(f"[COMBINAR] {e}")
    def _cb_aud_elegir(self):
        i=self._cb_actual();k=self.cb_cb_aud.current()
        if i is None or not 0<=k<len(self._cb_aud_ops):return
        self._clips[i]["a"]=self._cb_aud_ops[k][0];self._cb_pintar(i)
    def _cb_paso(self,d):
        i=self._cb_actual()
        if i is None:return
        D=_dur(self.info.get(self._clips[i]["ruta"],{})) or 0.0
        self.var_cb_pos.set(max(0.0,min(D,float(self.var_cb_pos.get())+d)));self.lbl_cb_t.configure(text=_hms(float(self.var_cb_pos.get())).split(".")[0]);self._cb_foto()
    def _cb_marcar(self,cual):
        i=self._cb_actual()
        if i is None:return
        c=self._clips[i];t=round(float(self.var_cb_pos.get()),3)
        if cual=="ini":
            c["ini"]=t
            if c["fin"] and c["fin"]<=t:c["fin"]=0.0
        else:
            if t<=c["ini"]:self._toast(T("warn_tit"),self._vt("El fin tiene que ir después del inicio.","The end must come after the start."),tipo="warning",seg=4);return
            c["fin"]=t
        self._cb_pintar(i);self.var_cb_ini.set(_hms(c["ini"]) if c["ini"] else "");self.var_cb_fin.set(_hms(c["fin"]) if c["fin"] else "")
    def _cb_foto(self):
        i=self._cb_actual()
        if i is None:return
        c=self._clips[i];inf=self.info.get(c["ruta"],{});vs=_vstream(inf)
        if not vs:return
        t=float(self.var_cb_pos.get());ent=inf.get("entrada",c["ruta"]);dvd=["-analyzeduration","100M","-probesize","100M"] if inf.get("dvd") else []
        self._cb_foto_n=getattr(self,"_cb_foto_n",0)+1;n=self._cb_foto_n
        def hilo():
            d=None
            try:
                k={"creationflags":CNW} if sys.platform=="win32" else {}
                r=subprocess.run([FFMPEG,"-hide_banner","-v","error"]+dvd+["-ss",f"{t:.3f}","-i",ent,"-map",f"0:{vs['index']}","-frames:v","1",
                                  "-vf","scale=iw*sar:ih,scale=w=384:h=216:force_original_aspect_ratio=decrease","-f","image2pipe","-c:v","png","-"],capture_output=True,timeout=60,**k)
                if r.returncode==0 and r.stdout:d=base64.b64encode(r.stdout).decode("ascii")
            except Exception as e:self._ls(f"[COMBINAR] {e}")
            self._ui(self._cb_foto_fin,n,d)
        threading.Thread(target=hilo,daemon=True).start()
    def _cb_foto_fin(self,n,d):
        if n!=getattr(self,"_cb_foto_n",0) or not d:return
        try:self._cb_img=tk.PhotoImage(data=d);self.lbl_cb_img.configure(image=self._cb_img,text="")
        except Exception as e:self._log(f"[COMBINAR] {e}")
    def _cb_srt(self,dd,idx,out):
        """los subtítulos (de texto) de un trozo en SRT, empezando en 0"""
        c=dd["c"];pre=max(0.0,c["ini"]-30.0)
        r=rh([FFMPEG,"-hide_banner","-v","error","-y"]+(["-analyzeduration","100M","-probesize","100M"] if dd["dvd"] else [])+(["-ss",f"{pre:.3f}"] if pre>0 else [])
             +["-i",dd["ent"],"-ss",f"{c['ini']-pre:.3f}","-t",f"{dd['dur']:.3f}","-map",f"0:{idx}","-c:s","srt","-f","srt",out],timeout=900)
        return _srt_leer(out) if r.returncode==0 and os.path.isfile(out) else []
    # ---------- pistas de audio como en Jmg AudioProcesador ----------
    @staticmethod
    def _a_tags(t):
        """fila en rojo suave: la pista no sale, o es procesada y se ha eliminado su original"""
        return ("elim",) if (not t["incl"] or (_a_proc(t) and not t.get("conservar",True))) else ()
    def _a_nucleo(self):
        """(JMG, 15-11) «➕ Núcleo DTS»: el DTS normal que lleva dentro una pista DTS-HD, también como pista aparte (sin recomprimir). Otra vez: se quita"""
        j=self._job();V_=self._vt
        if not j or self._a_i is None:return
        t=j["a"][self._a_i]
        if not (t.get("codec_in")=="dts" and "DTS-HD" in str(t.get("perfil",""))):
            self._toast(T("info_tit"),V_("Solo en las pistas DTS-HD (Master Audio o High Resolution): llevan dentro un DTS normal que se puede sacar aparte.",
                                         "Only on DTS-HD tracks (Master Audio or High Resolution): they carry a regular DTS inside that can be taken out separately."),seg=6);return
        t["nucleo"]=not t.get("nucleo",False)
        self._pintar_a(self._a_i);self._refrescar_estado()
    def _a_elim_orig(self):
        """«🚫 Eliminar original»: en una pista procesada quita la original (la procesada sí sale); en una sin procesar, la quita del vídeo.
        Otra vez: vuelve"""
        j=self._job()
        if not j or self._a_i is None:return
        t=j["a"][self._a_i]
        if _a_proc(t):t["conservar"]=not t.get("conservar",True)
        else:t["incl"]=not t["incl"]
        self._pintar_a(self._a_i);self._estado_video();self._refrescar_estado()
    # ---------- «Auto» puesto: el rayo y la palabra en verde ----------
    def _auto_pintar(self):
        j=self._job()
        for ef,b in list(getattr(self,"_auto_bts",{}).items()):
            try:
                if ef in ("video","img"):k=(self.actual,"v",ef)
                else:
                    i=getattr(self,"_a_i",None)
                    k=(self.actual,j["a"][i]["idx"],ef) if (j and i is not None and i<len(j["a"])) else None
                h=self._auto_hecho.get(k) if k else None;on=h is not None
                if on:   # (JMG, 8-11) verde solo mientras sigue lo que puso el «Auto» (tocado a mano o reseteado: ya no)
                    src=j["v"] if ef in ("video","img") else j["a"][i]["ef"]
                    on=all(str(src.get(x))==str(v) for x,v in h.items())
                st_="AutoOn.TButton" if on else "Auto.TButton"
                if str(b.cget("style"))!=st_:b.configure(style=st_)
            except Exception:pass
    def _auto_bucle(self):
        try:
            if self.root.winfo_exists():self._auto_pintar();self._ex_suav_eq();self._bloq_vigilar();self.root.after(400,self._auto_bucle)
        except Exception:pass

# ---- Ayuda en 9 idiomas (ventana Ayuda, con selector propio; la interfaz sigue en ES/EN) ----
def _idioma_sistema():
    """(JMG, 13-11) el idioma de Windows (o de Linux), «ru», «hi»...: la ayuda se abre en él si lo tiene"""
    try:
        if sys.platform=="win32":
            import ctypes
            n=ctypes.windll.kernel32.GetUserDefaultUILanguage()&0x3FF
            return {0x0A:"es",0x09:"en",0x0C:"fr",0x07:"de",0x16:"pt",0x19:"ru",0x39:"hi",0x04:"zh",0x11:"ja"}.get(n,"")
        return (os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or "")[:2].lower()
    except Exception:return ""
def _trozos_txt(l,maxb=150):
    """(JMG, 13-11) una línea en trozos de como mucho maxb bytes, cortados en un espacio. Tk (8.6, Windows) dibuja el texto en tramos de
    unos 200 bytes y, si un tramo acaba entre una letra devanagari y su signo vocálico, Windows los pinta por separado (◌ो): en la ayuda
    en hindi cada trozo va con una etiqueta distinta a la del anterior, para que Tk no los junte"""
    out=[];cur=""
    for w in l.split(" "):
        c=(cur+" "+w) if cur else w
        if cur and len(c.encode("utf-8"))>maxb:out.append(cur+" ");cur=w
        else:cur=c
    out.append(cur);return out
AYUDA_IDIOMAS=[("es","Español"),("en","English"),("fr","Français"),("de","Deutsch"),("pt","Português"),("ru","Русский"),("hi","हिन्दी"),("zh","中文 (简体)"),("ja","日本語")]   # (JMG, 13-11) y ruso e hindi
AYUDA={}
AYUDA["es"]="""JMG VIDEOENCODER · AYUDA

CÓMO SE USA
1. Añade vídeos con «Seleccionar», «Añadir» o arrastrándolos a la lista (MKV, MP4, AVI, MOV, M2TS...). Para un DVD o un Blu-ray, «📀 DVD/BD» y eliges la carpeta que tiene VIDEO_TS o BDMV (se coge la película principal). Solo discos sin protección anticopia o ya descifrados: FFmpeg no puede leer los protegidos (CSS en DVD, AACS en Blu-ray) y el programa no quita esa protección; si el disco está protegido, te avisa y no lo añade. Usa una copia sin protección o ya descifrada, si la ley de tu país te lo permite. Ripear directamente del disco es lento e inestable: mejor hacer antes una imagen ISO («💿 Crear ISO...») y abrirla. «📀 DVD/BD» también abre una imagen de disco (.iso): Windows la monta sola y se desmonta al cerrar el programa (en Linux, móntala tú y elige su carpeta). «💿 Crear ISO...» hace una imagen .iso de una carpeta de DVD o Blu-ray (VIDEO_TS o BDMV) o copia tal cual el disco del lector, y luego «📀 Abrir en la lista» la añade. La imagen se llama como el disco (el título del Blu-ray o la etiqueta del DVD, BD o CD). De un disco protegido avisa y, si quieres, hace igualmente una copia exacta, igual de protegida (no se puede abrir aquí). «🎬 Solo la película» abre la película principal en Passthrough para elegir idiomas y subtítulos y sacar un MKV solo con eso, sin perder calidad. Si hay un disco en el lector, la ventana empieza con él; copiarlo lee y escribe a la vez y dice cuánto queda, y «Apagar el PC al terminar» deja hacerlo de noche (algunos lectores van más lentos con discos de películas: lo limita el propio lector).
2. Haz clic en un vídeo: a la derecha sale toda su información. Si seleccionas varios, sale un resumen de cada uno.
3. Pulsa «Agregar» (o doble clic): el vídeo pasa a las pestañas con los ajustes automáticos y queda marcado con ✔. Solo se procesan los agregados.
4. Repasa las pestañas si quieres y pulsa PROCESAR. Tus archivos originales nunca se modifican.

VÍDEO
• Códecs: H.264 (AVC), H.265 (HEVC), H.266 (VVC), AV1, VP9 (para la web) y, para editar, Apple ProRes 422 LT y Avid DNxHR HQ. Passthrough copia el vídeo sin tocarlo. H.266 (VVC) es el que más comprime, pero también el más lento, y solo con el procesador: en «Rápida» tarda unas 2 veces lo que dura el vídeo (una película de hora y media, unas 3 horas en un PC de 16 hilos); en «Media», unas 5 veces, y en «Lenta», unas 20. Son tiempos orientativos: dependen mucho del procesador de cada ordenador. Si tienes prisa, mejor H.265 o AV1.
• Codificar con: procesador o tarjeta gráfica NVIDIA o AMD (el programa comprueba al arrancar cuáles funcionan en tu PC). H.266 y ProRes, solo procesador. En la pestaña, el motor marcado se ve en su color (NVIDIA verde, AMD rojo); un «Auto» puesto se ve con la palabra en verde, y se apaga si cambias a mano lo que puso o le das a «Resetear».
• «Auto» del vídeo mide la película: codifica en segundo plano unos trozos cortos a calidad fija y pone el bitrate que necesita para verse bien (una película tranquila pide menos; una de mucho grano o acción, más). Tarda unos segundos; mientras, pone el de su resolución. Si cambias tú el bitrate, no lo toca.
• Calidad constante (menos = mejor) o Bitrate (tamaño fijo). Con bitrate, «Dos pasadas» reparte mejor los kbps; en las tarjetas gráficas se usa su modo de dos pasadas propio. ProRes no tiene bitrate.
• «Auto» elige el códec, el bitrate y la resolución según el vídeo; si ya está bien comprimido, lo deja en Passthrough. Pulsado otra vez sin tocar nada, vuelve a Passthrough. Es un punto de partida: si no te gusta, retócalo a mano.
• Resolución: igual que el original o más pequeña. Desentrelazar: Auto lo hace solo si el vídeo es entrelazado (DVD, TV).
• Color: las películas HDR (HDR10, HLG) conservan su HDR en 10 bits; «SDR» las convierte para pantallas normales. Para vídeo logarítmico de cámara, elige su LUT (.cube). Dolby Vision: se conserva la capa HDR10.
• Con la tarjeta gráfica, «Dos pasadas» usa su propio sistema: analiza cada fotograma antes de codificarlo. El color solo se activa si hace falta: con HDR, o con vídeo logarítmico (si no lo detecta, marca la casilla).

AUDIO
• Todas las pistas del vídeo: puedes cambiar el orden (⬆ ⬇), el idioma, el título, la pista por defecto y quitar las que no quieras (doble clic).
• Códecs: Passthrough (sin tocar), AC3, E-AC3, DTS, AAC, MP3 (solo estéreo: el 5.1 se baja a estéreo), FLAC y Opus. «Aften Dolby Digital» (por defecto, en el desplegable del códec) hace el AC3 con Aften, que da mejor gama dinámica en las películas que tienen mucha; «AC3 · FFmpeg», con FFmpeg. Sus ajustes, con «⚙ Aften...» como los de los demás formatos (por defecto, conmutación de bloques y ancho de banda fijo completo): CBR o VBR, ancho de banda, precisión, filtros, gama dinámica (DRC y nivel de diálogo) y la información del flujo para el amplificador (Dolby Surround EX, Dolby Headphone, conversor A/D Estándar o HDCD, downmix preferido y sus niveles). Un AC3 VBR no lo leen todos los aparatos.
• Gama dinámica / Compresión: deslizador con el centro apagado. A la izquierda (1-10) gama dinámica: más contraste. A la derecha (1-10) compresión: suben los sonidos flojos (para ver la película de noche). Uno para delanteros y traseros, otro para el central. El subwoofer no se toca. Está en «Visual / Ondas» (pestaña Audio), a la derecha de la Presencia, donde se ve en las ondas.
• Volumen por canal, Suavizado digital (exceso de agudos de las películas de los 80 y 90) y Ecualizador de 3 bandas (delanteros, central y traseros).
• Orden recomendado: primero Presencia y/o Gama dinámica, después los demás efectos y siempre al final el Volumen por canal: así el volumen de cada canal se ajusta sobre el resultado de todo lo demás y se controla mejor y más fino.
• Cada «Auto» mide la pista con los demás efectos ya puestos y coloca sus controles; pulsado otra vez sin tocar nada, vuelve a 0. Los efectos son de la pista seleccionada; con Passthrough la pista pasa a comprimirse con su mismo códec.
• TrueHD y FLAC son sin pérdidas: en vez de kbps eliges 16 o 24 bits.
• Double Bass: copia los graves del subwoofer a los altavoces y los de los altavoces al subwoofer (solo en pistas con subwoofer), con su «Auto». Su «Auto» pone el Double Bass (1-3) si a los altavoces les faltan graves profundos o si el subwoofer va flojo; si están equilibrados, 0. Corte por defecto: 90 Hz.
• Sincronización: Delay de la pista, «Calcular delay» y «Corregir por tramos» comparando con otra pista (normalmente la del idioma original), como en Jmg AudioProcesador. «Añadir pista» suma, por ejemplo, un doblaje que tienes aparte.
• «▶ Revisar sincronización» (en Sincronización): el vídeo en su ventana con la pista tal como saldrá (delay, tramos y efectos), desde el punto que elijas o desde cada tramo, para ver con tus ojos si los labios van con la voz. En el mismo momento también puedes oír la pista sin corregir o la de referencia. Es la misma ventana que en Jmg AudioProcesador.
• Framerate (en Sincronización): para una pista de una edición de 25 fps en una película de 23,976 (o al revés), como en Jmg AudioProcesador: cambia su velocidad exacta, con o sin cambio de tono, antes del delay y los tramos. Al añadir una pista de otro archivo que dura un 4 % menos (o más) que el vídeo, el programa lo detecta y lo pone solo, y avisa. Después calcula el delay.
• Escuchar: en «Visual / Ondas» de Audio, «▶ Antes» o «▶ Después» (o clic en las ondas); ⏸ pausa (pulsado otra vez, sigue) y ⏹ para y vuelve al principio. Por multicanal (para un amplificador AV) o en estéreo.
• Pistas de audio, como en Jmg AudioProcesador: la pista procesada (con efectos; cambiar solo el códec o el bitrate no cuenta) sale la primera y por defecto, con el título «Jmg procesada» (se puede cambiar), y la original se conserva detrás. «🚫 Eliminar original» la quita (la fila se pone en rojo suave; otra vez, vuelve); en una pista sin procesar, la quita del vídeo. «➕ Añadir pista» trae una pista de otro archivo y «➖ Eliminar pista» la quita de la lista (el archivo original no se toca).
• «➕ Núcleo DTS» (pestaña Audio): una pista DTS-HD (Master Audio o High Resolution) lleva dentro un DTS normal para los aparatos que no entienden el HD; esto lo saca también como pista aparte (en MKV), sin recomprimir. Otra vez: se quita.
• En «Información», el botón derecho del ratón: «Copiar» y «Seleccionar todo» (también en el Log). Al abrir el programa, la pestaña Vídeo se ve entera; la raya de en medio se puede arrastrar y se recuerda.
• Al pulsar PROCESAR sale una ventana con lo esencial (cada vídeo y el archivo que va a salir, y los avisos); «🔍 Ver todo» enseña todo (vídeo, imagen, recorte, cada pista, subtítulos y las órdenes de FFmpeg) y se puede copiar con «📋 Copiar todo». «Sí» para empezar.

SUBTÍTULOS
• Todos los del vídeo, con orden, idioma, título, por defecto y forzado. «Añadir subtítulo externo» suma un SRT, ASS, VTT o SUP.
• En MKV van todos. En MP4 y MOV los de texto se convierten y los de imagen (PGS, DVD) se quedan fuera, con aviso.
• Sincronización del subtítulo seleccionado (pestaña Subtítulos): Framerate y Delay, como el audio, para los subtítulos de una edición de 25 fps en una película de 23,976 (o al revés). Se aplican al procesar, también a los de imagen (PGS, DVD) y en el recorte por tramos. Al agregar el vídeo, sale por defecto el subtítulo forzado o, si no hay, el primero de la lista.

OPCIONES AVANZADAS
• Vídeo · «Más opciones» (pestaña Vídeo): se abre dentro de la ventana, con «Volver». Arriba el fotograma antes y después; debajo, la barra (clic y flechas ← → = fotograma a fotograma; con Mayúsculas, de segundo en segundo), el recorte por tramos (varios tramos se unen en un solo vídeo), la imagen (brillo, contraste, saturación, tono, nitidez y quitar ruido) y las bandas negras (se buscan solas al agregar el vídeo). «Auto» de Imagen mide la película y propone los valores (pulsarlo otra vez = todo a 0); si no te gusta cómo queda, retócalo a mano.
• «Reproducir» abre una ventana de vídeo con sonido desde el punto de la barra: el original o con los ajustes, con la primera pista de audio incluida, en multicanal o estéreo.
• Audio · «Visual / Ondas» (pestaña Audio): las ondas de cada canal antes y después del tramo que elijas (primeros 5, 10 o 30 minutos o el archivo entero), como en Jmg AudioProcesador. Clic en las ondas = escuchar desde ahí. Las ondas se generan solas al entrar y se rehacen al cambiar la Presencia o el tramo; cada canal sale relleno, con su pico en dBFS, y «Zoom» agranda las ondas flojas. A la derecha de la Presencia, la Gama dinámica / Compresión: con ella no hace falta subir tanto la Presencia. «Detalle» (x1-x8) enseña las ondas con más resolución; se mueven con la rueda o con la barra de debajo, y mientras suena la vista sigue a la raya roja.
• Los efectos se suman: el «Después» lleva todos los de la pista. Ahí está también la Presencia (voz, ambiente, efectos y subwoofer) con su «Auto». Deshacer y Rehacer siguen abajo.

SALIDA
• MKV (lo admite todo), MP4 (para móviles y teles) o MOV (el de ProRes y DNxHR; VP9 va en MKV o MP4) o AVI (para aparatos antiguos: H.264 con audio AC3, MP3 o DTS, sin subtítulos ni capítulos) o WebM (para la web: VP9 o AV1 con audio Opus y subtítulos de texto en WebVTT). Carpeta junto al original o la que elijas, texto que se añade al nombre y qué hacer si ya existe. La película de un disco o de una imagen ISO va a Vídeos (salvo que elijas otra carpeta).
• También se copian los capítulos, los metadatos y los adjuntos (fuentes de los ASS y portadas).
• La barra de abajo enseña el avance y lo que falta. «Al terminar» puede salir del programa, suspender el PC o apagarlo.
• Portada: la del vídeo, otra imagen (JPG o PNG) o sin portada. El archivo se llama como el vídeo con « (Jmg VideoEncoder)» detrás (el añadido se puede cambiar, y en «Nombre de este vídeo» se le puede poner otro nombre); si ya existe, se le añade _1, _2... Al terminar se abre la carpeta de destino, salvo si se va a apagar el PC. «📤 Extracción...», a la derecha del nombre, saca todo lo que lleva el vídeo a una carpeta «(extracción)», cada cosa en su formato original y sin recomprimir: vídeo, audios, subtítulos, portadas, adjuntos y capítulos (cada cosa con su casilla para marcar). También desde el menú del icono de la bandeja («📤 Extracción...») y, con el programa instalado, con el botón derecho en un archivo de vídeo del Explorador («Extraer con Jmg VideoEncoder»; en Windows 11, dentro de «Mostrar más opciones»): si el programa no está abierto, sale solo la ventana de Extracción y se cierra al terminar. Con un DVD o un Blu-ray de vídeo en el lector, el botón derecho sobre el lector (con el programa instalado) y el menú del icono de la bandeja traen «Ripear» (la película principal entra en la lista en Passthrough para elegir idiomas y subtítulos: sale un MKV sin perder calidad) y «Crear imagen ISO»; en el menú de la bandeja, «Crear imagen ISO» también para los discos de datos.
• «🔍 Buscar en internet...» (Salida → Portada): busca la película en TMDB, enseña sus pósters para elegir uno y lo pone de portada con el nombre «Título (Año)». Si junto al vídeo hay un cover.jpg o folder.jpg (los que dejan muchos programas de ripeo, Kodi o Plex) y el vídeo no trae portada, se usa solo. Necesita tu propia clave de TMDB, gratuita: la primera vez el programa explica cómo conseguirla (cuenta en themoviedb.org → Ajustes → API). Sin conexión, simplemente no busca.

A TENER EN CUENTA
• «↶ Deshacer» y «↷ Rehacer» (abajo; también Ctrl+Z y Ctrl+Y): deshacen y rehacen, una a una, las últimas 5 acciones (ajustes, agregar o quitar vídeos...). «Resetear» vuelve a los ajustes automáticos de la pestaña abierta (Vídeo, Audio, Subtítulos o Salida) del vídeo activo; con «Todo», todo de cero: la lista de vídeos, su información, sus ajustes y la Salida por defecto (↶ lo recupera). Mientras está abierta una ventana como «Combinar vídeos», «Revisar sincronización» o las opciones avanzadas, los botones de la ventana principal no funcionan: esas ventanas llevan sus propios ↶ ↷.
• Al minimizar, el programa queda como un icono junto al reloj (la bandeja del sistema), que dice cómo va el proceso: clic izquierdo = vuelve la ventana; clic derecho = menú (cancelar el proceso, qué hacer al terminar —nada, salir o apagar el PC—, abrir la carpeta al terminar, salir). En Salida se puede quitar, para minimizar a la barra de tareas como siempre. Al dejar el ratón sobre un botón, una casilla o un deslizador sale una descripción, que se va sola a los pocos segundos.
• Opciones avanzadas («⚙» al lado del códec, en Vídeo y en cada pista de Audio): lo más importante de cada códec, para quien lo quiera afinar. Vídeo: ajuste (tune: cine, animación, grano...), perfil y nivel, fotograma clave cada X segundos, fotogramas B y de referencia, cuantización adaptativa, grano de película sintético en AV1, dos pasadas y AQ de NVIDIA, máxima calidad y preanálisis de AMD, perfil de ProRes (Proxy a 4444 XQ) y de DNxHR (LB a 444). Audio: la información del flujo de AC3 y E-AC3 (nivel de diálogo, Dolby Surround EX, auriculares, HDCD, downmix) y el corte de agudos, VBR de MP3 y de Opus, compresión de FLAC. Lo que no se toca queda en automático; cada vídeo y cada pista con lo suyo. En la lista de pistas, «⚙» = con opciones avanzadas. En AC3 y E-AC3 también el tipo de sala (grande o pequeña) con su nivel de mezcla; en DTS, la predicción ADPCM. El DTS de FFmpeg es siempre de bitrate fijo: 768 o 1536 kbps, los estándar (con menos, los reproductores solo dan ruido). AC3 (Aften y FFmpeg): en 5.1, de 224 a 640 kbps; en estéreo, de 96 a 640 (por defecto 192). E-AC3: cualquier bitrate, escrito a mano, desde 192 kbps en 5.1 (en estéreo desde 64; por defecto 192). Dolby TrueHD va detrás de los Dolby.
• Subtítulos · «Grabar en la imagen»: el subtítulo seleccionado queda dibujado en el vídeo; se ve en cualquier aparato, pero ya no se puede quitar. Solo uno, y obliga a recomprimir el vídeo (si estaba en Passthrough, pasa a H.265). Los de texto (SRT, ASS) se dibujan sobre la imagen final; los de imagen (PGS, DVD), sobre la original (con «Bandas negras» → «Quitarlas», lo que esté en las bandas se corta).
• «Edit/Log» guarda todo lo que pasa; «Ver el comando de FFmpeg» enseña el comando exacto del vídeo activo.
• Al arrancar, una vez al día, el programa mira en GitHub si hay una versión nueva y te pregunta si quieres abrir la página de descarga. No descarga ni instala nada solo.
• Cada 45 días, al abrir el programa, sale durante 5 segundos un mensaje que recuerda que se puede contribuir con el proyecto; se cierra solo y, si se pulsa el enlace de contribuir (ahí o en «Acerca de»), no vuelve a salir.
• «⏸ Pausa» (al lado de PROCESAR) para el procesado sin perder nada y «▶ Continuar» lo sigue donde estaba. «Al terminar» se puede cambiar mientras procesa.
• Blu-ray: el idioma de cada pista de audio y de cada subtítulo se lee de la lista de reproducción del disco (los archivos .m2ts no lo traen).
• Mientras trabaja (procesar, combinar, ripear, extraer, crear ISO...), el PC no entra en suspensión; la pantalla sí puede apagarse.
• «➖ Eliminar subtítulo» (pestaña Subtítulos) quita el subtítulo seleccionado, del vídeo o añadido: no sale en el archivo procesado y el original no se toca.
• «Combinar vídeos» (junto a «Agregar») une trozos de varios vídeos en uno solo, con el tamaño del primero; «Igualar color y brillo» mide cada trozo y lo ajusta al primero. Con la imagen y «Inicio aquí» / «Fin aquí» se marca cada trozo sin ir a ciegas. Lleva las pistas de audio marcadas de cada vídeo (o la que elijas en «Audio de este trozo») y sus subtítulos de texto marcados (los de imagen no se pueden unir). El resultado entra en la lista de vídeos, igual que un vídeo con tramos al terminar. El vídeo de cada trozo se elige en la propia ventana («Vídeo:» y «➕ Añadir»). Con las flechas ← → del teclado se avanza un fotograma por pulsación y, manteniéndolas, cada vez más rápido. «Poner» aplica el inicio y el fin escritos al trozo elegido; «↺ Resetear» vacía la lista de trozos; ↶ ↷ (o Ctrl+Z / Ctrl+Y) deshacen y rehacen.
• «🎵 A AudioProcesador» (arriba, detrás de «Crear ISO»): pasa los archivos seleccionados de la lista (o todos) a Jmg AudioProcesador. Si está abierto, van a su lista; si no, se abre con ellos. Si no lo encuentra, te pide que lo busques una vez. Después, este programa se cierra (los dos no se quedan abiertos a la vez).
• Todos los deslizadores se mueven con las flechas del teclado (haz clic antes en el deslizador). Las pestañas toman solas el alto que necesitan.

FFMPEG Y LICENCIA
Usa FFmpeg (ffmpeg.org, compilación de BtbN) con licencia GNU GPL v3.
Jmg VideoEncoder es software libre bajo la licencia GNU GPL v3.
Contacto: jmgsoftwaremultimedia@gmail.com
Apoya el proyecto: https://www.paypal.com/paypalme/JmgSoftware
Realizar Jmg SuiteMultimedia (este programa y Jmg AudioProcesador 5.1) ha costado un trabajo enorme: unos 45 días, con pruebas en películas reales. Desarrollado con la ayuda de Claude, la inteligencia artificial de Anthropic.
"""
AYUDA["en"]="""JMG VIDEOENCODER · HELP

HOW TO USE IT
1. Add videos with «Select», «Add» or by dragging them onto the list (MKV, MP4, AVI, MOV, M2TS...). For a DVD or a Blu-ray, «📀 DVD/BD» and choose the folder that has VIDEO_TS or BDMV (the main movie is taken). Only discs without copy protection or already decrypted: FFmpeg cannot read protected ones (CSS on DVD, AACS on Blu-ray) and the program does not remove that protection; if the disc is protected, it warns you and does not add it. Use an unprotected or already decrypted copy, if the law of your country allows it. Ripping straight from the disc is slow and unstable: better make an ISO image first («💿 Create ISO...») and open it. «📀 DVD/BD» also opens a disc image (.iso): Windows mounts it and it is unmounted when the program closes (on Linux, mount it yourself and choose its folder). «💿 Create ISO...» makes an .iso image of a DVD or Blu-ray folder (VIDEO_TS or BDMV) or copies the disc in the drive as it is, and then «📀 Open in the list» adds it. The image is named like the disc (the Blu-ray title or the DVD, BD or CD label). With a protected disc it warns you and, if you want, still makes an exact copy, just as protected (it cannot be opened here). «🎬 Only the movie» opens the main movie in Passthrough to choose languages and subtitles and get an MKV with only that, without losing quality. If there is a disc in the drive, the window starts with it; copying it reads and writes at the same time and shows the time left, and «Shut down the PC when done» lets it run overnight (some drives are slower with movie discs: the drive itself limits it).
2. Click a video: all its information appears on the right. If you select several, you get a summary of each one.
3. Press «Add to queue» (or double-click): the video goes into the tabs with the automatic settings and is marked with ✔. Only added videos are processed.
4. Check the tabs if you like and press PROCESS. Your original files are never modified.

VIDEO
• Codecs: H.264 (AVC), H.265 (HEVC), H.266 (VVC), AV1, VP9 (for the web) and, for editing, Apple ProRes 422 LT and Avid DNxHR HQ. Passthrough copies the video untouched. H.266 (VVC) compresses the most, but it is also the slowest, and processor only: on «Fast» it takes about 2 times the length of the video (an hour-and-a-half movie, about 3 hours on a 16-thread PC); on «Medium», about 5 times, and on «Slow», about 20. These times are only a guide: they depend a lot on each computer's processor. If you are in a hurry, better H.265 or AV1.
• Encode with: processor or NVIDIA or AMD graphics card (the program checks at startup which ones work on your PC). H.266 and ProRes, processor only. In the tab, the selected engine shows its colour (NVIDIA green, AMD red); an «Auto» that is set shows the word in green, and goes off if you change what it set by hand or press «Reset».
• The video «Auto» measures the movie: it encodes a few short pieces at a fixed quality in the background and sets the bitrate it needs to look good (a calm movie needs less; one with lots of grain or action, more). It takes a few seconds; meanwhile it uses the one for its resolution. If you change the bitrate yourself, it leaves it alone.
• Constant quality (lower = better) or Bitrate (fixed size). With bitrate, «Two passes» spreads the kbps better; graphics cards use their own two-pass mode. ProRes has no bitrate.
• «Auto» picks the codec, bitrate and resolution for the video; if it is already well compressed, it leaves Passthrough. Pressed again without touching anything, it goes back to Passthrough. It is a starting point: if you don't like it, adjust it by hand.
• Resolution: same as the original or smaller. Deinterlace: Auto only does it if the video is interlaced (DVD, TV).
• Color: HDR movies (HDR10, HLG) keep their HDR in 10 bits; «SDR» converts them for normal screens. For camera log video, choose its LUT (.cube). Dolby Vision: the HDR10 layer is kept.
• With the graphics card, «Two passes» uses its own system: it analyzes each frame before encoding it. Color is only enabled when needed: with HDR, or with log video (if it is not detected, tick the box).

AUDIO
• All the video's tracks: you can change the order (⬆ ⬇), the language, the title, the default track and remove the ones you don't want (double-click).
• Codecs: Passthrough (untouched), AC3, E-AC3, DTS, AAC, MP3 (stereo only: 5.1 is downmixed), FLAC and Opus. «Aften Dolby Digital» (default, in the codec list) makes the AC3 with Aften, which gives better dynamic range in movies that have a lot; «AC3 · FFmpeg», with FFmpeg. Its settings, with «⚙ Aften...» like the other formats' ones (by default, block switching and fixed full bandwidth): CBR or VBR, bandwidth, accuracy, filters, dynamic range (DRC and dialogue level) and the bitstream information for the amplifier (Dolby Surround EX, Dolby Headphone, Standard or HDCD A/D converter, preferred downmix and its levels). Not every device reads a VBR AC3.
• Dynamic range / Compression: slider with the middle off. To the left (1-10) dynamic range: more contrast. To the right (1-10) compression: quiet sounds go up (to watch the movie at night). One for fronts and surrounds, another for the center. The subwoofer is not touched. It is in «Visual / Waves» (Audio tab), to the right of Presence, where you see it on the waves.
• Volume per channel, Digital smoothing (excess treble of 80s and 90s movies) and 3-band equalizer (fronts, center and surrounds).
• Recommended order: first Presence and/or Dynamic range, then the other effects, and always last the Volume per channel: that way each channel's volume is set on the result of everything else and is easier to control finely.
• Each «Auto» measures the track with the other effects already applied and sets its controls; pressed again without touching anything, it goes back to 0. The effects belong to the selected track; with Passthrough the track is compressed again with its own codec.
• TrueHD and FLAC are lossless: instead of kbps you choose 16 or 24 bits.
• Double Bass: copies the subwoofer bass to the speakers and the speakers' bass to the subwoofer (only on tracks with a subwoofer), with its «Auto». Its «Auto» sets Double Bass (1-3) if the speakers lack deep bass or the subwoofer is weak; if they are balanced, 0. Default cut: 90 Hz.
• Synchronization: track Delay, «Calculate delay» and «Fix by parts» comparing with another track (normally the original-language one), as in Jmg AudioProcesador. «Add track» adds, for example, a dub you have separately.
• «▶ Check synchronization» (in Synchronization): the video in its window with the track as it will come out (delay, parts and effects), from the point you choose or from each part, so you can see with your own eyes whether the lips match the voice. At the same moment you can also hear the uncorrected track or the reference one. It is the same window as in Jmg AudioProcesador.
• Framerate (in Synchronization): for a track from a 25 fps edition in a 23.976 movie (or the other way round), as in Jmg AudioProcesador: it changes its exact speed, with or without pitch change, before the delay and the parts. When you add a track from another file that is 4 % shorter (or longer) than the video, the program detects it, sets it by itself and tells you. Then calculate the delay.
• Listen: in Audio «Visual / Waves», «▶ Before» or «▶ After» (or click on the waves); ⏸ pause (pressed again, it goes on) and ⏹ stops and goes back to the start. Through multichannel (for an AV receiver) or in stereo.
• Audio tracks, as in Jmg AudioProcesador: the processed track (with effects; changing only the codec or the bitrate does not count) comes first and by default, titled «Jmg procesada» (it can be changed), and the original is kept after it. «🚫 Remove original» removes it (the row turns soft red; again, it comes back); on an unprocessed track, it removes it from the video. «➕ Add track» brings a track from another file and «➖ Delete track» removes it from the list (the original file is not touched).
• «➕ DTS core» (Audio tab): a DTS-HD track (Master Audio or High Resolution) carries a regular DTS inside for devices that do not understand HD; this also takes it out as a separate track (in MKV), not re-encoded. Again: it is removed.
• In «Information», the right mouse button: «Copy» and «Select all» (also in the Log). When the program opens, the Video tab is fully visible; the line in the middle can be dragged and it is remembered.
• When you press PROCESS a window shows the essentials (each video and the file that will come out, and the warnings); «🔍 See everything» shows it all (video, picture, trimming, each track, subtitles and the FFmpeg commands) and it can be copied with «📋 Copy all». «Yes» to start.

SUBTITLES
• All the video's subtitles, with order, language, title, default and forced. «Add external subtitle» adds an SRT, ASS, VTT or SUP.
• In MKV they all go. In MP4 and MOV the text ones are converted and the image ones (PGS, DVD) are left out, with a notice.
• Synchronization of the selected subtitle (Subtitles tab): Framerate and Delay, like the audio, for the subtitles of a 25 fps edition in a 23.976 movie (or the other way round). They are applied when processing, also to the image ones (PGS, DVD) and when trimming by parts. When the video is added, the forced subtitle is the default one or, if there is none, the first in the list.

ADVANCED OPTIONS
• Video · «More options» (Video tab): it opens inside the window, with «Back». At the top the frame before and after; below, the bar (click and ← → arrows = frame by frame; with Shift, second by second), trimming by parts (several parts are joined into one video), the picture (brightness, contrast, saturation, hue, sharpness and denoise) and the black bars (looked for by themselves when the video is added). «Auto» in Picture measures the movie and suggests the values (press it again = all back to 0); if you don't like the result, touch it up by hand.
• «Play» opens a video window with sound from the point of the bar: the original or with the settings, with the first included audio track, in multichannel or stereo.
• Audio · «Visual / Waves» (Audio tab): the waves of each channel before and after, for the segment you choose (first 5, 10 or 30 minutes or the whole file), as in Jmg AudioProcesador. Click on the waves = listen from there. The waves are generated by themselves when you enter and redone when you change Presence or the segment; each channel is drawn filled, with its peak in dBFS, and «Zoom» enlarges quiet waves. To the right of Presence, Dynamic range / Compression: with it there is no need to raise Presence so much. «Detail» (x1-x8) shows the waves with more resolution; move with the wheel or the bar below, and while it plays the view follows the red line.
• The effects add up: «After» carries all those of the track. Presence (voice, ambience, effects and subwoofer) with its «Auto» is there too. Undo and Redo are still at the bottom.

OUTPUT
• MKV (takes everything), MP4 (for phones and TVs) or MOV (the ProRes and DNxHR one; VP9 goes in MKV or MP4) or AVI (for old devices: H.264 with AC3, MP3 or DTS audio, no subtitles or chapters) or WebM (for the web: VP9 or AV1 with Opus audio and text subtitles as WebVTT). Folder next to the original or the one you choose, text added to the name and what to do if it already exists. The movie from a disc or an ISO image goes to Videos (unless you choose another folder).
• Chapters, metadata and attachments (ASS fonts and covers) are also copied.
• The bottom bar shows the progress and the time left. «When done» can exit the program, put the PC to sleep or shut it down.
• Cover: the video's, another image (JPG or PNG) or none. The file is named like the video with « (Jmg VideoEncoder)» added (the addition can be changed, and «Name of this video» gives it another name); if it already exists, _1, _2... is added. When done, the destination folder opens, unless the PC is going to shut down. «📤 Extraction...», right of the name, takes everything the video carries out to an «(extraction)» folder, each in its original format and without re-encoding: video, audio tracks, subtitles, covers, attachments and chapters (each item with its own tick box). Also from the tray icon menu («📤 Extraction...») and, with the program installed, with a right-click on a video file in Explorer («Extract with Jmg VideoEncoder»; on Windows 11, under «Show more options»): if the program is not open, only the Extraction window comes up and it closes when done. With a video DVD or Blu-ray in the drive, the right-click on the drive (with the program installed) and the tray icon menu offer «Rip» (the main movie goes into the list in Passthrough to choose languages and subtitles: you get an MKV without quality loss) and «Create ISO image»; in the tray menu, «Create ISO image» also for data discs.
• «🔍 Search online...» (Output → Cover): looks the movie up on TMDB, shows its posters to choose one and sets it as the cover with the name «Title (Year)». If there is a cover.jpg or folder.jpg next to the video (left by many ripping programs, Kodi or Plex) and the video has no cover, it is used by itself. It needs your own TMDB key, which is free: the first time, the program explains how to get it (account at themoviedb.org → Settings → API). Without a connection, it simply does not search.

KEEP IN MIND
• «↶ Undo» and «↷ Redo» (at the bottom; also Ctrl+Z and Ctrl+Y): undo and redo, one by one, the last 5 actions (settings, adding or removing videos...). «Reset» puts back the automatic settings of the open tab (Video, Audio, Subtitles or Output) of the active video; with «All», everything from scratch: the video list, its information, its settings and the default Output (↶ brings it back). While a window such as «Combine videos», «Check synchronization» or the advanced options is open, the main window buttons do not work: those windows have their own ↶ ↷.
• When minimized, the program stays as an icon next to the clock (the system tray), which shows how the process is going: left click = the window comes back; right click = menu (cancel the process, what to do when done —nothing, exit or shut down the PC—, open the folder when done, exit). In Output it can be turned off, to minimize to the taskbar as usual. Leaving the mouse over a button, box or slider shows a description, which goes away by itself after a few seconds.
• Advanced options («⚙» next to the codec, in Video and on each Audio track): the most important settings of each codec, for whoever wants to fine-tune. Video: tune (film, animation, grain...), profile and level, a keyframe every X seconds, B-frames and reference frames, adaptive quantization, synthetic film grain in AV1, NVIDIA two-pass and AQ, AMD highest quality and pre-analysis, ProRes profile (Proxy to 4444 XQ) and DNxHR profile (LB to 444). Audio: the AC3 and E-AC3 bitstream information (dialogue level, Dolby Surround EX, headphones, HDCD, downmix) and the treble cut-off, MP3 and Opus VBR, FLAC compression. Whatever is not touched stays automatic; each video and each track keeps its own. In the track list, «⚙» = with advanced options. AC3 and E-AC3 also have the room type (large or small) with its mixing level; DTS has ADPCM prediction. FFmpeg's DTS is always constant bitrate: 768 or 1536 kbps, the standard ones (with less, players only give noise). AC3 (Aften and FFmpeg): in 5.1, from 224 to 640 kbps; in stereo, from 96 to 640 (default 192). E-AC3: any bitrate, typed by hand, from 192 kbps in 5.1 (in stereo from 64; default 192). Dolby TrueHD comes after the Dolby ones.
• Subtitles · «Burn into the picture»: the selected subtitle is drawn into the video; it shows on any device, but it can no longer be removed. Only one, and the video must be re-encoded (if it was in Passthrough, it becomes H.265). Text ones (SRT, ASS) are drawn on the final picture; image ones (PGS, DVD), on the original (with «Black bars» → «Remove them», whatever is in the bars is cut).
• «Edit/Log» keeps everything that happens; «Show the FFmpeg command» shows the exact command of the active video.
• On startup, once a day, the program checks GitHub for a new version and asks whether you want to open the download page. It does not download or install anything by itself.
• Every 45 days, when the program opens, a message reminding you that you can support the project is shown for 5 seconds; it closes by itself and, if you click the support link (there or in «About»), it does not come back.
• «⏸ Pause» (next to PROCESS) stops the processing without losing anything and «▶ Resume» carries on where it was. «When done» can be changed while processing.
• Blu-ray: the language of each audio track and subtitle is read from the disc's playlist (the .m2ts files do not carry it).
• While it is working (processing, combining, ripping, extracting, creating an ISO...), the PC does not go to sleep; the screen can still turn off.
• «➖ Delete subtitle» (Subtitles tab) removes the selected subtitle, from the video or added: it is not in the processed file and the original is not touched.
• «Combine videos» (next to «Add to queue») joins parts of several videos into one, with the size of the first one; «Match color and brightness» measures each part and adjusts it to the first one. With the picture and «Start here» / «End here» each part is marked without working blind. It carries the marked audio tracks of each video (or the one chosen in «Audio of this part») and its marked text subtitles (image ones cannot be joined). The result goes into the video list, like a video with parts when it is done. The video of each part is chosen in the window itself («Video:» and «➕ Add»). The ← → arrow keys move one frame per press and, held down, faster and faster. «Set» applies the typed start and end to the chosen part; «↺ Reset» empties the list of parts; ↶ ↷ (or Ctrl+Z / Ctrl+Y) undo and redo.
• «🎵 To AudioProcesador» (at the top, after «Create ISO»): sends the selected files in the list (or all of them) to Jmg AudioProcesador. If it is open, they go to its list; if not, it opens with them. If it is not found, it asks you to look for it once. Then this program closes (both do not stay open at the same time).
• Every slider moves with the keyboard arrows (click the slider first). The tabs take the height they need by themselves.

FFMPEG AND LICENSE
Uses FFmpeg (ffmpeg.org, BtbN build) under the GNU GPL v3 license.
Jmg VideoEncoder is free software under the GNU GPL v3 license.
Contact: jmgsoftwaremultimedia@gmail.com
Support the project: https://www.paypal.com/paypalme/JmgSoftware
Making Jmg SuiteMultimedia (this program and Jmg AudioProcesador 5.1) has taken a huge amount of work: about 45 days, with tests on real movies. Developed with the help of Claude, Anthropic's AI.
"""
AYUDA["fr"]="""JMG VIDEOENCODER · AIDE

UTILISATION
1. Ajoutez des vidéos avec «Select», «Add» ou en les glissant dans la liste (MKV, MP4, AVI, MOV, M2TS...). Pour un DVD ou un Blu-ray, «📀 DVD/BD» et choisissez le dossier qui contient VIDEO_TS ou BDMV (le film principal est pris). Uniquement des disques sans protection anticopie ou déjà déchiffrés : FFmpeg ne peut pas lire les disques protégés (CSS sur DVD, AACS sur Blu-ray) et le programme ne retire pas cette protection ; si le disque est protégé, il vous prévient et ne l'ajoute pas. Utilisez une copie non protégée ou déjà déchiffrée, si la loi de votre pays le permet. Extraire directement depuis le disque est lent et instable : mieux vaut d'abord créer une image ISO («💿 Create ISO...») et l'ouvrir. «📀 DVD/BD» ouvre aussi une image disque (.iso) : Windows la monte et elle est démontée à la fermeture du programme (sous Linux, montez-la vous-même et choisissez son dossier). «💿 Create ISO...» crée une image .iso d'un dossier de DVD ou de Blu-ray (VIDEO_TS ou BDMV) ou copie tel quel le disque du lecteur, puis «📀 Open in the list» l'ajoute. L'image porte le nom du disque (le titre du Blu-ray ou l'étiquette du DVD, BD ou CD). Avec un disque protégé, il prévient et, si vous le voulez, fait quand même une copie exacte, tout aussi protégée (elle ne s'ouvre pas ici). «🎬 Only the movie» ouvre le film principal en Passthrough pour choisir langues et sous-titres et obtenir un MKV avec seulement cela, sans perte de qualité. S'il y a un disque dans le lecteur, la fenêtre commence avec lui ; la copie lit et écrit en même temps et indique le temps restant, et «Shut down the PC when done» permet de la lancer la nuit (certains lecteurs sont plus lents avec les disques de films : c'est le lecteur qui le limite).
2. Cliquez sur une vidéo : toutes ses informations apparaissent à droite. Si vous en sélectionnez plusieurs, vous obtenez un résumé de chacune.
3. Appuyez sur «Add to queue» (ou double-clic) : la vidéo passe dans les onglets avec les réglages automatiques et porte la marque ✔. Seules les vidéos ajoutées sont traitées.
4. Vérifiez les onglets si vous le souhaitez et appuyez sur PROCESS. Vos fichiers d'origine ne sont jamais modifiés.

VIDÉO
• Codecs : H.264 (AVC), H.265 (HEVC), H.266 (VVC), AV1, VP9 (pour le web) et, pour le montage, Apple ProRes 422 LT et Avid DNxHR HQ. Passthrough copie la vidéo sans la toucher. H.266 (VVC) est celui qui compresse le plus, mais aussi le plus lent, et uniquement avec le processeur : en «Fast», il met environ 2 fois la durée de la vidéo (un film d'une heure et demie, environ 3 heures sur un PC à 16 threads) ; en «Medium», environ 5 fois, et en «Slow», environ 20. Ces durées sont indicatives : elles dépendent beaucoup du processeur de chaque ordinateur. Si vous êtes pressé, mieux vaut H.265 ou AV1.
• Encoder avec : le processeur ou une carte graphique NVIDIA ou AMD (le programme vérifie au démarrage celles qui fonctionnent sur votre PC). H.266 et ProRes, processeur uniquement. Dans l'onglet, le moteur coché prend sa couleur (NVIDIA vert, AMD rouge) ; un «Auto» appliqué montre le mot en vert, et s'éteint si vous modifiez à la main ce qu'il a réglé ou appuyez sur «Reset».
• «Auto» de la vidéo mesure le film : il encode en arrière-plan quelques courts extraits à qualité fixe et met le débit nécessaire pour une bonne image (un film calme en demande moins ; un film avec beaucoup de grain ou d'action, plus). Cela prend quelques secondes ; en attendant, il met celui de sa résolution. Si vous changez vous-même le débit, il n'y touche pas.
• Qualité constante (moins = mieux) ou Débit (taille fixe). Avec un débit, «Two passes» répartit mieux les kbps ; les cartes graphiques utilisent leur propre mode en deux passes. ProRes n'a pas de débit.
• «Auto» choisit le codec, le débit et la résolution selon la vidéo ; si elle est déjà bien compressée, il laisse Passthrough. Appuyé de nouveau sans rien toucher, il revient à Passthrough. C'est un point de départ : si le résultat ne vous plaît pas, retouchez-le à la main.
• Résolution : identique à l'original ou plus petite. Désentrelacer : Auto ne le fait que si la vidéo est entrelacée (DVD, TV).
• Couleur : les films HDR (HDR10, HLG) gardent leur HDR en 10 bits ; «SDR» les convertit pour les écrans normaux. Pour une vidéo log de caméra, choisissez son LUT (.cube). Dolby Vision : la couche HDR10 est conservée.
• Avec la carte graphique, «Two passes» utilise son propre système : elle analyse chaque image avant de l'encoder. La couleur ne s'active que si nécessaire : avec le HDR, ou avec une vidéo log (si elle n'est pas détectée, cochez la case).

AUDIO
• Toutes les pistes de la vidéo : vous pouvez changer l'ordre (⬆ ⬇), la langue, le titre, la piste par défaut et retirer celles que vous ne voulez pas (double-clic).
• Codecs : Passthrough (sans toucher), AC3, E-AC3, DTS, AAC, MP3 (stéréo seulement : le 5.1 est réduit en stéréo), FLAC et Opus. «Aften Dolby Digital» (par défaut) fait l'AC3 avec Aften, qui donne une meilleure dynamique dans les films qui en ont beaucoup ; «AC3 · FFmpeg», avec FFmpeg. Ses réglages, avec «⚙ Aften...» comme ceux des autres formats (par défaut, commutation de blocs et bande passante fixe complète) : CBR ou VBR, bande passante, précision, filtres, dynamique (DRC et niveau de dialogue) et les informations du flux pour l'amplificateur (Dolby Surround EX, Dolby Headphone, convertisseur A/D Standard ou HDCD, downmix préféré et ses niveaux). Tous les appareils ne lisent pas un AC3 VBR.
• Plage dynamique / Compression : curseur avec le centre éteint. À gauche (1-10) plage dynamique : plus de contraste. À droite (1-10) compression : les sons faibles montent (pour regarder le film la nuit). Un pour les avant et les arrière, un autre pour le central. Le caisson de basses n'est pas modifié. Elle se trouve dans «Visual / Waves» (onglet Audio), à droite de Presence, où on la voit sur les ondes.
• Volume par canal, Lissage numérique (excès d'aigus des films des années 80 et 90) et Égaliseur 3 bandes (avant, central et arrière).
• Ordre conseillé : d'abord Presence et/ou Dynamic range, puis les autres effets, et toujours en dernier Volume per channel : ainsi le volume de chaque canal se règle sur le résultat de tout le reste, plus finement.
• Chaque «Auto» mesure la piste avec les autres effets déjà appliqués et place ses réglages ; appuyé de nouveau sans rien toucher, il revient à 0. Les effets sont ceux de la piste sélectionnée ; en Passthrough la piste est recompressée avec son propre codec.
• TrueHD et FLAC sont sans perte : au lieu des kbps, vous choisissez 16 ou 24 bits.
• Double Bass : copie les graves du caisson vers les enceintes et ceux des enceintes vers le caisson (seulement sur les pistes avec caisson), avec son «Auto». Son «Auto» règle le Double Bass (1-3) si les enceintes manquent de graves profonds ou si le caisson est faible ; s'ils sont équilibrés, 0. Coupure par défaut : 90 Hz.
• Synchronisation : Delay de la piste, «Calculate delay» et «Fix by parts» en comparant avec une autre piste (normalement celle de la langue d'origine), comme dans Jmg AudioProcesador. «Add track» ajoute, par exemple, un doublage que vous avez à part.
• «▶ Check synchronization» (dans Synchronization) : la vidéo dans sa fenêtre avec la piste telle qu'elle sortira (delay, parties et effets), depuis le point choisi ou depuis chaque partie, pour vérifier de vos propres yeux si les lèvres suivent la voix. Au même moment, vous pouvez aussi écouter la piste non corrigée ou celle de référence. C'est la même fenêtre que dans Jmg AudioProcesador.
• Framerate (dans Synchronization) : pour une piste d'une édition à 25 fps dans un film à 23,976 (ou l'inverse), comme dans Jmg AudioProcesador : change sa vitesse exacte, avec ou sans changement de tonalité, avant le delay et les parties. Quand vous ajoutez une piste d'un autre fichier qui dure 4 % de moins (ou de plus) que la vidéo, le programme le détecte, le règle tout seul et vous prévient. Calculez ensuite le delay.
• Écouter : dans «Visual / Waves» de Audio, «▶ Before» ou «▶ After» (ou clic sur les ondes) ; ⏸ pause (pressé à nouveau, ça continue) et ⏹ arrête et revient au début. En multicanal (pour un amplificateur AV) ou en stéréo.
• Pistes audio, comme dans Jmg AudioProcesador : la piste traitée (avec des effets ; changer seulement le codec ou le bitrate ne compte pas) sort en premier et par défaut, avec le titre «Jmg procesada» (modifiable), et l'originale est conservée derrière. «🚫 Remove original» la retire (la ligne passe en rouge pâle ; à nouveau, elle revient) ; sur une piste non traitée, elle la retire de la vidéo. «➕ Add track» apporte une piste d'un autre fichier et «➖ Delete track» la retire de la liste (le fichier d'origine n'est pas modifié).
• «➕ DTS core» (onglet Audio) : une piste DTS-HD (Master Audio ou High Resolution) contient un DTS normal pour les appareils qui ne comprennent pas le HD ; ceci le sort aussi comme piste séparée (en MKV), sans réencodage. À nouveau : il est retiré.
• Dans «Information», le bouton droit de la souris : «Copy» et «Select all» (aussi dans le Log). À l'ouverture, l'onglet Video se voit en entier ; la ligne du milieu se déplace et elle est mémorisée.
• En appuyant sur PROCESS, une fenêtre montre l'essentiel (chaque vidéo et le fichier qui sortira, et les avertissements) ; «🔍 See everything» montre tout (vidéo, image, découpe, chaque piste, sous-titres et les commandes FFmpeg) et se copie avec «📋 Copy all». «Oui» pour commencer.

SOUS-TITRES
• Tous ceux de la vidéo, avec ordre, langue, titre, par défaut et forcé. «Add external subtitle» ajoute un SRT, ASS, VTT ou SUP.
• En MKV ils passent tous. En MP4 et MOV ceux en texte sont convertis et ceux en image (PGS, DVD) restent dehors, avec un avertissement.
• Synchronisation du sous-titre sélectionné (onglet Subtitles) : Framerate et Delay, comme l'audio, pour les sous-titres d'une édition à 25 fps dans un film à 23,976 (ou l'inverse). Ils s'appliquent au traitement, aussi à ceux en image (PGS, DVD) et dans la découpe par parties. À l'ajout de la vidéo, le sous-titre forcé est celui par défaut ou, s'il n'y en a pas, le premier de la liste.

OPTIONS AVANCÉES
• Vidéo · «More options» (onglet Video) : s'ouvre dans la fenêtre, avec «Back». En haut l'image avant et après ; en dessous, la barre (clic et flèches ← → = image par image ; avec Maj, seconde par seconde), la découpe par parties (plusieurs parties sont réunies en une seule vidéo), l'image (luminosité, contraste, saturation, teinte, netteté et débruitage) et les bandes noires (recherchées toutes seules à l'ajout de la vidéo). «Auto» dans Picture mesure le film et propose les valeurs (le presser à nouveau = tout à 0) ; si le résultat ne vous plaît pas, retouchez-le à la main.
• «Play» ouvre une fenêtre vidéo avec le son depuis le point de la barre : l'original ou avec les réglages, avec la première piste audio incluse, en multicanal ou en stéréo.
• Audio · «Visual / Waves» (onglet Audio) : les ondes de chaque canal avant et après, pour le segment choisi (5, 10 ou 30 premières minutes ou le fichier entier), comme dans Jmg AudioProcesador. Clic sur les ondes = écouter depuis là. Les ondes se génèrent toutes seules à l'entrée et se refont quand vous changez Presence ou le segment ; chaque canal est rempli, avec son pic en dBFS, et «Zoom» agrandit les ondes faibles. À droite de Presence, Dynamic range / Compression : avec elle, inutile de monter autant Presence. «Detail» (x1-x8) montre les ondes avec plus de résolution ; on se déplace avec la molette ou la barre en dessous, et pendant la lecture la vue suit le trait rouge.
• Les effets s'additionnent : «After» porte tous ceux de la piste. La Présence (voix, ambiance, effets et caisson) avec son «Auto» s'y trouve aussi. Undo et Redo restent en bas.

SORTIE
• MKV (accepte tout), MP4 (pour téléphones et téléviseurs) ou MOV (celui de ProRes et DNxHR ; VP9 va en MKV ou MP4) ou AVI (pour les anciens appareils : H.264 avec audio AC3, MP3 ou DTS, sans sous-titres ni chapitres) ou WebM (pour le web : VP9 ou AV1 avec audio Opus et sous-titres texte en WebVTT). Dossier à côté de l'original ou celui de votre choix, texte ajouté au nom et que faire s'il existe déjà. Le film d'un disque ou d'une image ISO va dans Vidéos (sauf si vous choisissez un autre dossier).
• Les chapitres, les métadonnées et les pièces jointes (polices des ASS et pochettes) sont aussi copiés.
• La barre du bas montre l'avancement et le temps restant. «When done» peut quitter le programme, mettre le PC en veille ou l'éteindre.
• Pochette : celle de la vidéo, une autre image (JPG ou PNG) ou aucune. Le fichier porte le nom de la vidéo suivi de « (Jmg VideoEncoder)» (l'ajout est modifiable, et «Name of this video» permet un autre nom) ; s'il existe déjà, _1, _2... est ajouté. À la fin, le dossier de destination s'ouvre, sauf si le PC va s'éteindre. «📤 Extraction...», à droite du nom, sort tout ce que contient la vidéo dans un dossier «(extraction)», chaque élément dans son format d'origine et sans réencodage : vidéo, pistes audio, sous-titres, pochettes, pièces jointes et chapitres (chaque élément avec sa case à cocher). Aussi depuis le menu de l'icône de la zone de notification («📤 Extraction...») et, avec le programme installé, par un clic droit sur un fichier vidéo dans l'Explorateur («Extract with Jmg VideoEncoder» ; sous Windows 11, dans «Afficher plus d'options») : si le programme n'est pas ouvert, seule la fenêtre d'extraction apparaît et elle se ferme à la fin. Avec un DVD ou un Blu-ray vidéo dans le lecteur, le clic droit sur le lecteur (avec le programme installé) et le menu de l'icône de la zone de notification proposent «Rip» (le film principal entre dans la liste en Passthrough pour choisir les langues et sous-titres : on obtient un MKV sans perte de qualité) et «Create ISO image» ; dans le menu de la zone de notification, «Create ISO image» aussi pour les disques de données.
• «🔍 Search online...» (Output → Cover) : cherche le film sur TMDB, montre ses affiches pour en choisir une et la met en pochette avec le nom «Titre (Année)». S'il y a un cover.jpg ou folder.jpg à côté de la vidéo (laissés par de nombreux programmes de rip, Kodi ou Plex) et que la vidéo n'a pas de pochette, il est utilisé tout seul. Il faut votre propre clé TMDB, gratuite : la première fois, le programme explique comment l'obtenir (compte sur themoviedb.org → Paramètres → API). Sans connexion, la recherche ne se fait simplement pas.

À SAVOIR
• «↶ Undo» et «↷ Redo» (en bas ; aussi Ctrl+Z et Ctrl+Y) : annulent et rétablissent, une par une, les 5 dernières actions (réglages, ajout ou retrait de vidéos...). «Reset» remet les réglages automatiques de l'onglet ouvert (Video, Audio, Subtitles ou Output) de la vidéo active ; avec «All», tout repart de zéro : la liste des vidéos, leurs informations, leurs réglages et la Sortie par défaut (↶ la récupère). Tant qu'une fenêtre comme «Combine videos», «Check synchronization» ou les options avancées est ouverte, les boutons de la fenêtre principale ne fonctionnent pas : ces fenêtres ont leurs propres ↶ ↷.
• Une fois réduit, le programme reste en icône près de l'horloge (zone de notification), qui indique l'avancement : clic gauche = la fenêtre revient ; clic droit = menu (annuler le traitement, que faire à la fin —rien, quitter ou éteindre le PC—, ouvrir le dossier à la fin, quitter). Dans Output on peut le désactiver, pour réduire dans la barre des tâches comme d'habitude. En laissant la souris sur un bouton, une case ou un curseur, une description apparaît et disparaît seule après quelques secondes.
• Options avancées («⚙» à côté du codec, dans Video et sur chaque piste Audio) : l'essentiel de chaque codec, pour qui veut affiner. Vidéo : réglage (tune : film, animation, grain...), profil et niveau, une image clé toutes les X secondes, images B et de référence, quantification adaptative, grain de film synthétique en AV1, deux passes et AQ de NVIDIA, qualité maximale et pré-analyse d'AMD, profil ProRes (Proxy à 4444 XQ) et DNxHR (LB à 444). Audio : les informations du flux AC3 et E-AC3 (niveau de dialogue, Dolby Surround EX, casque, HDCD, downmix) et la coupure des aigus, VBR de MP3 et d'Opus, compression FLAC. Ce qui n'est pas touché reste automatique ; chaque vidéo et chaque piste garde le sien. Dans la liste des pistes, «⚙» = avec options avancées. En AC3 et E-AC3 aussi le type de salle (grande ou petite) avec son niveau de mixage ; en DTS, la prédiction ADPCM. Le DTS de FFmpeg est toujours à débit constant : 768 ou 1536 kbps, les débits standard (en dessous, les lecteurs ne donnent que du bruit). AC3 (Aften et FFmpeg) : en 5.1, de 224 à 640 kbps ; en stéréo, de 96 à 640 (192 par défaut). E-AC3 : n'importe quel débit, saisi à la main, dès 192 kbps en 5.1 (en stéréo dès 64 ; 192 par défaut). Dolby TrueHD vient après les Dolby.
• Sous-titres · «Burn into the picture» : le sous-titre choisi est dessiné dans la vidéo ; il se voit sur n'importe quel appareil, mais ne peut plus être retiré. Un seul, et la vidéo doit être réencodée (si elle était en Passthrough, elle passe en H.265). Ceux de texte (SRT, ASS) sont dessinés sur l'image finale ; ceux d'image (PGS, DVD), sur l'originale (en retirant les bandes noires, ce qui s'y trouve est coupé).
• «Edit/Log» garde tout ce qui se passe ; «Show the FFmpeg command» montre la commande exacte de la vidéo active.
• Au démarrage, une fois par jour, le programme vérifie sur GitHub s'il existe une nouvelle version et vous demande si vous voulez ouvrir la page de téléchargement. Il ne télécharge et n'installe rien de lui-même.
• Tous les 45 jours, à l'ouverture du programme, un message rappelant que l'on peut soutenir le projet s'affiche pendant 5 secondes ; il se ferme tout seul et, si vous cliquez sur le lien de soutien (là ou dans «About»), il ne revient plus.
• «⏸ Pause» (à côté de PROCESS) arrête le traitement sans rien perdre et «▶ Resume» le reprend là où il en était. «When done» peut être modifié pendant le traitement.
• Blu-ray : la langue de chaque piste audio et de chaque sous-titre est lue dans la liste de lecture du disque (les fichiers .m2ts ne la contiennent pas).
• Pendant qu'il travaille (traitement, combinaison, extraction, création d'ISO...), le PC ne se met pas en veille ; l'écran peut tout de même s'éteindre.
• «➖ Delete subtitle» (onglet Subtitles) retire le sous-titre sélectionné, de la vidéo ou ajouté : il n'apparaît pas dans le fichier traité et l'original n'est pas modifié.
• «Combine videos» (à côté de «Add to queue») réunit des parties de plusieurs vidéos en une seule, à la taille de la première ; «Match color and brightness» mesure chaque partie et l'ajuste à la première. Avec l'image et «Start here» / «End here», chaque partie se marque sans travailler à l'aveugle. Elle emporte les pistes audio cochées de chaque vidéo (ou celle choisie dans «Audio of this part») et ses sous-titres texte cochés (ceux en image ne peuvent pas être réunis). Le résultat entre dans la liste des vidéos, comme une vidéo avec des parties une fois terminée. La vidéo de chaque partie se choisit dans la fenêtre même («Video:» et «➕ Add»). Les flèches ← → du clavier avancent d'une image par pression et, maintenues, de plus en plus vite. «Set» applique le début et la fin saisis à la partie choisie ; «↺ Reset» vide la liste des parties ; ↶ ↷ (ou Ctrl+Z / Ctrl+Y) annulent et rétablissent.
• «🎵 To AudioProcesador» (en haut, après «Create ISO») : envoie les fichiers sélectionnés de la liste (ou tous) à Jmg AudioProcesador. S'il est ouvert, ils vont dans sa liste ; sinon, il s'ouvre avec eux. S'il est introuvable, il vous demande de le chercher une fois. Ensuite, ce programme se ferme (les deux ne restent pas ouverts en même temps).
• Tous les curseurs se déplacent avec les flèches du clavier (cliquez d'abord sur le curseur). Les onglets prennent seuls la hauteur nécessaire.

FFMPEG ET LICENCE
Utilise FFmpeg (ffmpeg.org, compilation de BtbN) sous licence GNU GPL v3.
Jmg VideoEncoder est un logiciel libre sous licence GNU GPL v3.
Contact : jmgsoftwaremultimedia@gmail.com
Soutenez le projet : https://www.paypal.com/paypalme/JmgSoftware
Réaliser Jmg SuiteMultimedia (ce programme et Jmg AudioProcesador 5.1) a demandé un travail énorme : environ 45 jours, avec des essais sur de vrais films. Développé avec l'aide de Claude, l'intelligence artificielle d'Anthropic.
"""
AYUDA["de"]="""JMG VIDEOENCODER · HILFE

SO GEHT'S
1. Fügen Sie Videos mit «Select», «Add» oder per Ziehen in die Liste hinzu (MKV, MP4, AVI, MOV, M2TS...). Für eine DVD oder Blu-ray «📀 DVD/BD» und den Ordner mit VIDEO_TS oder BDMV wählen (der Hauptfilm wird genommen). Nur Discs ohne Kopierschutz oder bereits entschlüsselte: FFmpeg kann geschützte nicht lesen (CSS bei DVD, AACS bei Blu-ray), und das Programm entfernt diesen Schutz nicht; ist die Disc geschützt, erscheint ein Hinweis und sie wird nicht hinzugefügt. Verwenden Sie eine ungeschützte oder bereits entschlüsselte Kopie, sofern das Recht Ihres Landes es erlaubt. Direkt von der Disc zu rippen ist langsam und instabil: besser zuerst ein ISO-Image erstellen («💿 Create ISO...») und dieses öffnen. «📀 DVD/BD» öffnet auch ein Disc-Image (.iso): Windows bindet es ein, und beim Schließen des Programms wird es wieder ausgehängt (unter Linux selbst einbinden und den Ordner wählen). «💿 Create ISO...» erstellt ein .iso-Image aus einem DVD- oder Blu-ray-Ordner (VIDEO_TS oder BDMV) oder kopiert die Disc im Laufwerk unverändert, danach fügt «📀 Open in the list» es hinzu. Das Image heißt wie die Disc (der Blu-ray-Titel oder das Label der DVD, BD oder CD). Bei einer geschützten Disc erscheint ein Hinweis, und auf Wunsch entsteht trotzdem eine exakte, ebenso geschützte Kopie (hier nicht zu öffnen). «🎬 Only the movie» öffnet den Hauptfilm in Passthrough, um Sprachen und Untertitel zu wählen und ein MKV nur damit zu erhalten, ohne Qualitätsverlust. Liegt eine Disc im Laufwerk, beginnt das Fenster mit ihr; das Kopieren liest und schreibt gleichzeitig und zeigt die Restzeit, und mit «Shut down the PC when done» kann es über Nacht laufen (manche Laufwerke sind bei Film-Discs langsamer: das begrenzt das Laufwerk selbst).
2. Klicken Sie auf ein Video: rechts erscheinen alle seine Informationen. Bei mehreren ausgewählten erscheint eine Zusammenfassung von jedem.
3. Drücken Sie «Add to queue» (oder Doppelklick): das Video kommt mit den automatischen Einstellungen in die Reiter und wird mit ✔ markiert. Nur hinzugefügte Videos werden verarbeitet.
4. Prüfen Sie die Reiter, wenn Sie möchten, und drücken Sie PROCESS. Ihre Originaldateien werden nie verändert.

VIDEO
• Codecs: H.264 (AVC), H.265 (HEVC), H.266 (VVC), AV1, VP9 (fürs Web) und zum Schneiden Apple ProRes 422 LT und Avid DNxHR HQ. Passthrough kopiert das Video unverändert. H.266 (VVC) komprimiert am stärksten, ist aber auch am langsamsten und nur mit dem Prozessor möglich: bei «Fast» dauert es etwa 2-mal so lange wie das Video (ein Film von anderthalb Stunden etwa 3 Stunden auf einem PC mit 16 Threads); bei «Medium» etwa 5-mal und bei «Slow» etwa 20-mal. Diese Zeiten sind nur Richtwerte: Sie hängen stark vom Prozessor des jeweiligen Computers ab. Wenn es schnell gehen soll, besser H.265 oder AV1.
• Kodieren mit: Prozessor oder NVIDIA- bzw. AMD-Grafikkarte (das Programm prüft beim Start, welche auf Ihrem PC funktionieren). H.266 und ProRes nur mit dem Prozessor. Im Reiter zeigt die gewählte Option ihre Farbe (NVIDIA grün, AMD rot); ein gesetztes «Auto» zeigt das Wort in Grün und erlischt, wenn Sie das Eingestellte von Hand ändern oder «Reset» drücken.
• «Auto» beim Video misst den Film: Es kodiert im Hintergrund einige kurze Stücke mit fester Qualität und setzt die Bitrate, die für ein gutes Bild nötig ist (ein ruhiger Film braucht weniger, einer mit viel Korn oder Action mehr). Das dauert einige Sekunden; bis dahin gilt die für seine Auflösung. Ändern Sie die Bitrate selbst, bleibt sie unangetastet.
• Konstante Qualität (weniger = besser) oder Bitrate (feste Größe). Mit Bitrate verteilt «Two passes» die kbps besser; Grafikkarten nutzen ihren eigenen Zwei-Durchgänge-Modus. ProRes hat keine Bitrate.
• «Auto» wählt Codec, Bitrate und Auflösung passend zum Video; ist es schon gut komprimiert, bleibt Passthrough. Erneut gedrückt, ohne etwas zu ändern, geht es zurück auf Passthrough. Das ist ein Ausgangspunkt: Gefällt es Ihnen nicht, stellen Sie es von Hand nach.
• Auflösung: wie das Original oder kleiner. Deinterlacing: Auto macht es nur bei Zeilensprung-Videos (DVD, TV).
• Farbe: HDR-Filme (HDR10, HLG) behalten ihr HDR in 10 Bit; «SDR» wandelt sie für normale Bildschirme um. Für Log-Video einer Kamera wählen Sie deren LUT (.cube). Dolby Vision: die HDR10-Ebene bleibt erhalten.
• Mit der Grafikkarte nutzt «Two passes» ihr eigenes Verfahren: sie analysiert jedes Bild vor dem Kodieren. Farbe wird nur bei Bedarf aktiviert: bei HDR oder bei Log-Video (wird es nicht erkannt, das Kästchen ankreuzen).

AUDIO
• Alle Spuren des Videos: Sie können Reihenfolge (⬆ ⬇), Sprache, Titel und Standardspur ändern und unerwünschte entfernen (Doppelklick).
• Codecs: Passthrough (unverändert), AC3, E-AC3, DTS, AAC, MP3 (nur Stereo: 5.1 wird heruntergemischt), FLAC und Opus. «Aften Dolby Digital» (Standard) erzeugt das AC3 mit Aften, das bei Filmen mit großer Dynamik die bessere Dynamik liefert; «AC3 · FFmpeg» mit FFmpeg. Seine Einstellungen über «⚙ Aften...» wie bei den anderen Formaten (standardmäßig Blockumschaltung und feste volle Bandbreite): CBR oder VBR, Bandbreite, Genauigkeit, Filter, Dynamik (DRC und Dialogpegel) und die Bitstream-Informationen für den Verstärker (Dolby Surround EX, Dolby Headphone, A/D-Wandler Standard oder HDCD, bevorzugter Downmix und seine Pegel). Nicht jedes Gerät liest ein VBR-AC3.
• Dynamikumfang / Kompression: Regler mit ausgeschalteter Mitte. Links (1-10) Dynamikumfang: mehr Kontrast. Rechts (1-10) Kompression: leise Töne werden lauter (für Filme in der Nacht). Einer für Front und Surround, einer für den Center. Der Subwoofer bleibt unverändert. Er befindet sich in «Visual / Waves» (Reiter Audio), rechts neben Presence, wo man ihn an den Wellen sieht.
• Lautstärke pro Kanal, Digitale Glättung (zu viele Höhen in Filmen der 80er und 90er) und 3-Band-Equalizer (Front, Center und Surround).
• Empfohlene Reihenfolge: zuerst Presence und/oder Dynamic range, dann die übrigen Effekte und immer zuletzt Volume per channel: So wird die Lautstärke jedes Kanals auf das Ergebnis aller anderen Einstellungen abgestimmt, feiner und besser kontrollierbar.
• Jedes «Auto» misst die Spur mit den übrigen Effekten und stellt seine Regler ein; erneut gedrückt, ohne etwas zu ändern, geht es auf 0 zurück. Die Effekte gehören zur ausgewählten Spur; bei Passthrough wird die Spur mit ihrem eigenen Codec neu komprimiert.
• TrueHD und FLAC sind verlustfrei: statt kbps wählen Sie 16 oder 24 Bit.
• Double Bass: kopiert den Bass des Subwoofers zu den Lautsprechern und den der Lautsprecher zum Subwoofer (nur bei Spuren mit Subwoofer), mit seinem «Auto». Sein «Auto» setzt Double Bass (1-3), wenn den Lautsprechern tiefer Bass fehlt oder der Subwoofer schwach ist; sind sie ausgewogen, 0. Standard-Trennfrequenz: 90 Hz.
• Synchronisation: Delay der Spur, «Calculate delay» und «Fix by parts» im Vergleich mit einer anderen Spur (meist der Originalsprache), wie in Jmg AudioProcesador. «Add track» fügt z. B. eine separat vorhandene Synchronfassung hinzu.
• «▶ Check synchronization» (in Synchronization): das Video in seinem Fenster mit der Spur so, wie sie herauskommt (Delay, Teile und Effekte), ab dem gewählten Punkt oder ab jedem Teil, damit Sie mit eigenen Augen sehen, ob die Lippen zur Stimme passen. An derselben Stelle können Sie auch die unkorrigierte Spur oder die Referenzspur hören. Es ist dasselbe Fenster wie in Jmg AudioProcesador.
• Framerate (in Synchronization): für eine Spur aus einer 25-fps-Ausgabe in einem 23,976-Film (oder umgekehrt), wie in Jmg AudioProcesador: ändert ihre genaue Geschwindigkeit, mit oder ohne Tonhöhenänderung, vor Delay und Teilen. Fügen Sie eine Spur aus einer anderen Datei hinzu, die 4 % kürzer (oder länger) als das Video ist, erkennt das Programm dies, stellt es selbst ein und meldet es. Danach den Delay berechnen.
• Anhören: in den «Visual / Waves» von Audio, «▶ Before» oder «▶ After» (oder Klick auf die Wellen); ⏸ Pause (erneut gedrückt, geht es weiter) und ⏹ stoppt und springt an den Anfang. Mehrkanalig (für einen AV-Receiver) oder in Stereo.
• Audiospuren wie in Jmg AudioProcesador: Die bearbeitete Spur (mit Effekten; nur Codec oder Bitrate zu ändern zählt nicht) kommt zuerst und als Standard, mit dem Titel «Jmg procesada» (änderbar), und die Originalspur bleibt dahinter erhalten. «🚫 Remove original» entfernt sie (die Zeile wird hellrot; erneut gedrückt, kommt sie zurück); bei einer unbearbeiteten Spur wird sie aus dem Video entfernt. «➕ Add track» holt eine Spur aus einer anderen Datei, «➖ Delete track» nimmt sie aus der Liste (die Originaldatei bleibt unberührt).
• «➕ DTS core» (Registerkarte Audio): Eine DTS-HD-Spur (Master Audio oder High Resolution) enthält ein normales DTS für Geräte, die kein HD verstehen; damit kommt es zusätzlich als eigene Spur heraus (in MKV), ohne Neukodierung. Erneut gedrückt: wird es entfernt.
• In «Information» die rechte Maustaste: «Copy» und «Select all» (auch im Log). Beim Öffnen ist der Reiter Video ganz sichtbar; die Linie in der Mitte lässt sich ziehen und wird gespeichert.
• Beim Drücken von PROCESS zeigt ein Fenster das Wesentliche (jedes Video, die entstehende Datei und die Hinweise); «🔍 See everything» zeigt alles (Video, Bild, Schnitt, jede Spur, Untertitel und die FFmpeg-Befehle) und lässt sich mit «📋 Copy all» kopieren. «Ja» zum Starten.

UNTERTITEL
• Alle Untertitel des Videos mit Reihenfolge, Sprache, Titel, Standard und erzwungen. «Add external subtitle» fügt eine SRT-, ASS-, VTT- oder SUP-Datei hinzu.
• In MKV gehen alle mit. In MP4 und MOV werden Text-Untertitel umgewandelt, Bild-Untertitel (PGS, DVD) bleiben mit Hinweis draußen.
• Synchronisation des gewählten Untertitels (Reiter Subtitles): Framerate und Delay, wie beim Audio, für Untertitel einer 25-fps-Ausgabe in einem 23,976-Film (oder umgekehrt). Sie werden beim Verarbeiten angewendet, auch bei Bild-Untertiteln (PGS, DVD) und beim Schnitt in Teilen. Beim Hinzufügen des Videos ist der erzwungene Untertitel Standard oder, wenn es keinen gibt, der erste der Liste.

ERWEITERTE OPTIONEN
• Video · «More options» (Reiter Video): öffnet sich im Fenster, mit «Back». Oben das Bild vorher und nachher; darunter der Balken (Klick und Pfeile ← → = Bild für Bild; mit Umschalt Sekunde für Sekunde), der Schnitt in Teilen (mehrere Teile werden zu einem Video verbunden), das Bild (Helligkeit, Kontrast, Sättigung, Farbton, Schärfe und Rauschminderung) und die schwarzen Balken (werden beim Hinzufügen des Videos selbst gesucht). «Auto» bei Picture misst den Film und schlägt die Werte vor (erneut drücken = alles auf 0); gefällt Ihnen das Ergebnis nicht, korrigieren Sie es von Hand.
• «Play» öffnet ein Videofenster mit Ton ab der Stelle des Balkens: das Original oder mit den Einstellungen, mit der ersten eingeschlossenen Audiospur, mehrkanalig oder in Stereo.
• Audio · «Visual / Waves» (Reiter Audio): die Wellen jedes Kanals vorher und nachher für den gewählten Abschnitt (erste 5, 10 oder 30 Minuten oder die ganze Datei), wie in Jmg AudioProcesador. Klick auf die Wellen = ab dort anhören. Die Wellen werden beim Öffnen selbst erzeugt und bei Änderung von Presence oder Abschnitt neu berechnet; jeder Kanal wird gefüllt gezeichnet, mit seinem Spitzenpegel in dBFS, und «Zoom» vergrößert leise Wellen. Rechts neben Presence: Dynamic range / Compression: damit muss Presence nicht so stark angehoben werden. «Detail» (x1-x8) zeigt die Wellen mit mehr Auflösung; mit dem Mausrad oder dem Balken darunter verschieben, und beim Abspielen folgt die Ansicht der roten Linie.
• Die Effekte summieren sich: «After» enthält alle der Spur. Dort ist auch Präsenz (Stimme, Ambiente, Effekte und Subwoofer) mit ihrem «Auto». Undo und Redo bleiben unten.

AUSGABE
• MKV (nimmt alles), MP4 (für Handys und Fernseher) oder MOV (das von ProRes und DNxHR; VP9 kommt in MKV oder MP4) oder AVI (für alte Geräte: H.264 mit AC3-, MP3- oder DTS-Ton, ohne Untertitel und Kapitel) oder WebM (fürs Web: VP9 oder AV1 mit Opus-Ton und Text-Untertiteln als WebVTT). Ordner neben dem Original oder ein gewählter, Text, der dem Namen angehängt wird, und was passiert, wenn die Datei schon existiert. Der Film von einer Disc oder einem ISO-Abbild kommt in «Videos» (außer Sie wählen einen anderen Ordner).
• Kapitel, Metadaten und Anhänge (ASS-Schriften und Cover) werden ebenfalls kopiert.
• Der Balken unten zeigt den Fortschritt und die Restzeit. «When done» kann das Programm beenden, den PC in den Energiesparmodus versetzen oder herunterfahren.
• Cover: das des Videos, ein anderes Bild (JPG oder PNG) oder keines. Die Datei heißt wie das Video mit « (Jmg VideoEncoder)» dahinter (der Zusatz ist änderbar, unter «Name of this video» geht auch ein anderer Name); gibt es sie schon, wird _1, _2... angehängt. Am Ende öffnet sich der Zielordner, außer wenn der PC herunterfährt. «📤 Extraction...» rechts neben dem Namen holt alles, was das Video enthält, in einen Ordner «(extraction)», jedes im Originalformat und ohne Neukodierung: Video, Tonspuren, Untertitel, Cover, Anhänge und Kapitel (jedes mit seinem eigenen Kästchen zum Anhaken). Auch über das Menü des Infobereich-Symbols («📤 Extraction...») und, bei installiertem Programm, per Rechtsklick auf eine Videodatei im Explorer («Extract with Jmg VideoEncoder»; unter Windows 11 in «Weitere Optionen anzeigen»): Ist das Programm nicht geöffnet, erscheint nur das Extraktionsfenster, das sich am Ende schließt. Mit einer Video-DVD oder Blu-ray im Laufwerk bieten der Rechtsklick auf das Laufwerk (bei installiertem Programm) und das Menü des Infobereich-Symbols «Rip» (der Hauptfilm kommt in Passthrough in die Liste, um Sprachen und Untertitel zu wählen: es entsteht eine MKV ohne Qualitätsverlust) und «Create ISO image»; im Infobereich-Menü «Create ISO image» auch für Datendiscs.
• «🔍 Search online...» (Output → Cover): sucht den Film bei TMDB, zeigt seine Poster zur Auswahl und setzt das gewählte als Cover, mit dem Namen «Titel (Jahr)». Liegt neben dem Video eine cover.jpg oder folder.jpg (wie sie viele Ripping-Programme, Kodi oder Plex anlegen) und hat das Video kein Cover, wird sie automatisch verwendet. Dafür brauchen Sie einen eigenen, kostenlosen TMDB-Schlüssel: Beim ersten Mal erklärt das Programm, wie Sie ihn bekommen (Konto auf themoviedb.org → Einstellungen → API). Ohne Verbindung wird einfach nicht gesucht.

GUT ZU WISSEN
• «↶ Undo» und «↷ Redo» (unten; auch Strg+Z und Strg+Y): machen die letzten 5 Aktionen einzeln rückgängig bzw. wieder (Einstellungen, Videos hinzufügen oder entfernen...). «Reset» stellt die automatischen Einstellungen des offenen Reiters (Video, Audio, Subtitles oder Output) des aktiven Videos wieder her; mit «All» alles von vorn: die Videoliste, ihre Informationen, ihre Einstellungen und die Standard-Ausgabe (↶ holt es zurück). Solange ein Fenster wie «Combine videos», «Check synchronization» oder die erweiterten Optionen offen ist, funktionieren die Tasten des Hauptfensters nicht: Diese Fenster haben eigene ↶ ↷.
• Minimiert bleibt das Programm als Symbol neben der Uhr (Infobereich), das den Fortschritt zeigt: Linksklick = das Fenster kommt zurück; Rechtsklick = Menü (Vorgang abbrechen, was am Ende passiert —nichts, beenden oder PC herunterfahren—, Ordner am Ende öffnen, beenden). Unter Output lässt es sich abschalten, um wie gewohnt in die Taskleiste zu minimieren. Bleibt die Maus über einer Schaltfläche, einem Kästchen oder einem Regler, erscheint eine Beschreibung, die nach ein paar Sekunden von selbst verschwindet.
• Erweiterte Optionen («⚙» neben dem Codec, unter Video und bei jeder Audiospur): das Wichtigste jedes Codecs, für alle, die feinjustieren wollen. Video: Tune (Film, Animation, Korn...), Profil und Level, alle X Sekunden ein Schlüsselbild, B- und Referenzbilder, adaptive Quantisierung, synthetisches Filmkorn bei AV1, Zwei-Pass und AQ bei NVIDIA, höchste Qualität und Voranalyse bei AMD, ProRes-Profil (Proxy bis 4444 XQ) und DNxHR-Profil (LB bis 444). Audio: die Bitstream-Informationen von AC3 und E-AC3 (Dialogpegel, Dolby Surround EX, Kopfhörer, HDCD, Downmix) und die Höhengrenze, VBR bei MP3 und Opus, FLAC-Kompression. Was nicht angefasst wird, bleibt automatisch; jedes Video und jede Spur behält das Seine. In der Spurliste bedeutet «⚙»: mit erweiterten Optionen. Bei AC3 und E-AC3 außerdem der Raumtyp (groß oder klein) mit seinem Mischpegel; bei DTS die ADPCM-Prädiktion. Das DTS von FFmpeg hat immer eine feste Bitrate: 768 oder 1536 kbps, die Standardwerte (darunter geben Player nur Rauschen aus). AC3 (Aften und FFmpeg): bei 5.1 von 224 bis 640 kbps; bei Stereo von 96 bis 640 (Standard 192). E-AC3: jede Bitrate, von Hand eingegeben, ab 192 kbps bei 5.1 (bei Stereo ab 64; Standard 192). Dolby TrueHD steht hinter den Dolby-Formaten.
• Untertitel · «Burn into the picture»: der gewählte Untertitel wird ins Video gezeichnet; er ist auf jedem Gerät zu sehen, lässt sich aber nicht mehr entfernen. Nur einer, und das Video muss neu kodiert werden (war es Passthrough, wird es H.265). Text-Untertitel (SRT, ASS) werden auf das fertige Bild gezeichnet, Bild-Untertitel (PGS, DVD) auf das Original (beim Entfernen schwarzer Balken wird abgeschnitten, was darin liegt).
• «Edit/Log» hält alles fest, was passiert; «Show the FFmpeg command» zeigt den genauen Befehl des aktiven Videos.
• Beim Start prüft das Programm einmal am Tag auf GitHub, ob es eine neue Version gibt, und fragt, ob Sie die Download-Seite öffnen möchten. Es lädt und installiert nichts von selbst.
• Alle 45 Tage erscheint beim Öffnen des Programms 5 Sekunden lang ein Hinweis, dass man das Projekt unterstützen kann; er schließt sich von selbst und erscheint nicht mehr, wenn Sie auf den Unterstützen-Link klicken (dort oder unter «About»).
• «⏸ Pause» (neben PROCESS) hält die Verarbeitung an, ohne etwas zu verlieren, und «▶ Resume» setzt sie dort fort, wo sie war. «When done» lässt sich während der Verarbeitung ändern.
• Blu-ray: Die Sprache jeder Audiospur und jedes Untertitels wird aus der Wiedergabeliste der Disc gelesen (die .m2ts-Dateien enthalten sie nicht).
• Während das Programm arbeitet (Verarbeiten, Kombinieren, Rippen, Extrahieren, ISO erstellen...), geht der PC nicht in den Energiesparmodus; der Bildschirm kann sich trotzdem ausschalten.
• «➖ Delete subtitle» (Reiter Subtitles) entfernt den ausgewählten Untertitel, aus dem Video oder hinzugefügt: Er ist nicht in der verarbeiteten Datei, und das Original bleibt unverändert.
• «Combine videos» (neben «Add to queue») verbindet Teile mehrerer Videos zu einem, in der Größe des ersten; «Match color and brightness» misst jeden Teil und passt ihn an den ersten an. Mit dem Bild und «Start here» / «End here» wird jeder Teil markiert, ohne blind zu arbeiten. Es nimmt die markierten Audiospuren jedes Videos (oder die unter «Audio of this part» gewählte) und seine markierten Text-Untertitel mit (Bild-Untertitel lassen sich nicht verbinden). Das Ergebnis kommt in die Videoliste, wie ein Video mit Teilen am Ende. Das Video jedes Teils wird im Fenster selbst gewählt («Video:» und «➕ Add»). Die Pfeiltasten ← → gehen pro Druck ein Bild weiter und, gehalten, immer schneller. «Set» übernimmt den eingegebenen Anfang und das Ende für den gewählten Teil; «↺ Reset» leert die Liste der Teile; ↶ ↷ (oder Strg+Z / Strg+Y) machen rückgängig und wiederholen.
• «🎵 To AudioProcesador» (oben, hinter «Create ISO»): übergibt die gewählten Dateien der Liste (oder alle) an Jmg AudioProcesador. Ist es geöffnet, kommen sie in seine Liste; sonst wird es mit ihnen geöffnet. Wird es nicht gefunden, werden Sie einmal gebeten, es zu suchen. Danach schließt sich dieses Programm (beide bleiben nicht gleichzeitig geöffnet).
• Alle Regler lassen sich mit den Pfeiltasten bewegen (vorher auf den Regler klicken). Die Reiter nehmen selbst die nötige Höhe an.

FFMPEG UND LIZENZ
Verwendet FFmpeg (ffmpeg.org, BtbN-Build) unter der Lizenz GNU GPL v3.
Jmg VideoEncoder ist freie Software unter der Lizenz GNU GPL v3.
Kontakt: jmgsoftwaremultimedia@gmail.com
Unterstützen Sie das Projekt: https://www.paypal.com/paypalme/JmgSoftware
Jmg SuiteMultimedia (dieses Programm und Jmg AudioProcesador 5.1) zu entwickeln war eine riesige Arbeit: etwa 45 Tage, mit Tests an echten Filmen. Entwickelt mit Hilfe von Claude, der KI von Anthropic.
"""
AYUDA["pt"]="""JMG VIDEOENCODER · AJUDA

COMO SE USA
1. Adicione vídeos com «Select», «Add» ou arrastando-os para a lista (MKV, MP4, AVI, MOV, M2TS...). Para um DVD ou um Blu-ray, «📀 DVD/BD» e escolha a pasta que tem VIDEO_TS ou BDMV (fica o filme principal). Só discos sem proteção anticópia ou já desencriptados: o FFmpeg não consegue ler os protegidos (CSS em DVD, AACS em Blu-ray) e o programa não remove essa proteção; se o disco estiver protegido, avisa e não o adiciona. Use uma cópia sem proteção ou já desencriptada, se a lei do seu país o permitir. Ripar diretamente do disco é lento e instável: é melhor criar primeiro uma imagem ISO («💿 Create ISO...») e abri-la. «📀 DVD/BD» também abre uma imagem de disco (.iso): o Windows monta-a e é desmontada ao fechar o programa (em Linux, monte-a e escolha a sua pasta). «💿 Create ISO...» cria uma imagem .iso de uma pasta de DVD ou Blu-ray (VIDEO_TS ou BDMV) ou copia tal como está o disco do leitor, e depois «📀 Open in the list» adiciona-a. A imagem tem o nome do disco (o título do Blu-ray ou a etiqueta do DVD, BD ou CD). Com um disco protegido avisa e, se quiser, faz mesmo assim uma cópia exata, igualmente protegida (não se abre aqui). «🎬 Only the movie» abre o filme principal em Passthrough para escolher idiomas e legendas e obter um MKV só com isso, sem perder qualidade. Se houver um disco no leitor, a janela começa com ele; a cópia lê e escreve ao mesmo tempo e indica o tempo que falta, e «Shut down the PC when done» permite deixá-la à noite (alguns leitores são mais lentos com discos de filmes: é o próprio leitor que limita).
2. Clique num vídeo: à direita aparece toda a sua informação. Se selecionar vários, aparece um resumo de cada um.
3. Prima «Add to queue» (ou duplo clique): o vídeo passa para os separadores com as definições automáticas e fica marcado com ✔. Só se processam os adicionados.
4. Reveja os separadores se quiser e prima PROCESS. Os seus ficheiros originais nunca são modificados.

VÍDEO
• Codecs: H.264 (AVC), H.265 (HEVC), H.266 (VVC), AV1, VP9 (para a web) e, para editar, Apple ProRes 422 LT e Avid DNxHR HQ. Passthrough copia o vídeo sem lhe tocar. O H.266 (VVC) é o que mais comprime, mas também o mais lento, e só com o processador: em «Fast» demora cerca de 2 vezes a duração do vídeo (um filme de hora e meia, cerca de 3 horas num PC de 16 threads); em «Medium», cerca de 5 vezes, e em «Slow», cerca de 20. São tempos orientativos: dependem muito do processador de cada computador. Se tiver pressa, melhor H.265 ou AV1.
• Codificar com: processador ou placa gráfica NVIDIA ou AMD (o programa verifica ao arrancar quais funcionam no seu PC). H.266 e ProRes, só processador. No separador, o motor marcado fica com a sua cor (NVIDIA verde, AMD vermelho); um «Auto» aplicado mostra a palavra a verde, e apaga-se se mudar à mão o que ele pôs ou carregar em «Reset».
• «Auto» do vídeo mede o filme: codifica em segundo plano alguns trechos curtos com qualidade fixa e põe o bitrate de que precisa para se ver bem (um filme calmo pede menos; um com muito grão ou ação, mais). Demora alguns segundos; entretanto, usa o da sua resolução. Se mudar o bitrate, não lhe toca.
• Qualidade constante (menos = melhor) ou Bitrate (tamanho fixo). Com bitrate, «Two passes» reparte melhor os kbps; as placas gráficas usam o seu próprio modo de duas passagens. ProRes não tem bitrate.
• «Auto» escolhe o codec, o bitrate e a resolução de acordo com o vídeo; se já estiver bem comprimido, deixa Passthrough. Premido outra vez sem mexer em nada, volta a Passthrough. É um ponto de partida: se não gostar, retoque à mão.
• Resolução: igual ao original ou mais pequena. Desentrelaçar: Auto só o faz se o vídeo for entrelaçado (DVD, TV).
• Cor: os filmes HDR (HDR10, HLG) mantêm o seu HDR em 10 bits; «SDR» converte-os para ecrãs normais. Para vídeo log de câmara, escolha o seu LUT (.cube). Dolby Vision: mantém-se a camada HDR10.
• Com a placa gráfica, «Two passes» usa o seu próprio sistema: analisa cada imagem antes de a codificar. A cor só se ativa quando é preciso: com HDR, ou com vídeo log (se não for detetado, marque a caixa).

ÁUDIO
• Todas as faixas do vídeo: pode mudar a ordem (⬆ ⬇), o idioma, o título, a faixa predefinida e retirar as que não quer (duplo clique).
• Codecs: Passthrough (sem tocar), AC3, E-AC3, DTS, AAC, MP3 (só estéreo: o 5.1 passa a estéreo), FLAC e Opus. «Aften Dolby Digital» (por defeito) faz o AC3 com o Aften, que dá melhor gama dinâmica nos filmes que têm muita; «AC3 · FFmpeg», com o FFmpeg. Os seus ajustes, com «⚙ Aften...» como os dos outros formatos (por defeito, comutação de blocos e largura de banda fixa completa): CBR ou VBR, largura de banda, precisão, filtros, gama dinâmica (DRC e nível de diálogo) e a informação do fluxo para o amplificador (Dolby Surround EX, Dolby Headphone, conversor A/D Standard ou HDCD, downmix preferido e os seus níveis). Nem todos os aparelhos leem um AC3 VBR.
• Gama dinâmica / Compressão: controlo com o centro desligado. À esquerda (1-10) gama dinâmica: mais contraste. À direita (1-10) compressão: os sons fracos sobem (para ver o filme à noite). Um para frontais e traseiros, outro para o central. O subwoofer não é alterado. Está em «Visual / Waves» (separador Audio), à direita de Presence, onde se vê nas ondas.
• Volume por canal, Suavização digital (excesso de agudos dos filmes dos anos 80 e 90) e Equalizador de 3 bandas (frontais, central e traseiros).
• Ordem recomendada: primeiro Presence e/ou Dynamic range, depois os outros efeitos e sempre por último Volume per channel: assim o volume de cada canal ajusta-se sobre o resultado de tudo o resto, com mais controlo e precisão.
• Cada «Auto» mede a faixa com os outros efeitos já aplicados e coloca os seus controlos; premido outra vez sem mexer em nada, volta a 0. Os efeitos são da faixa selecionada; com Passthrough a faixa volta a ser comprimida com o seu próprio codec.
• TrueHD e FLAC são sem perdas: em vez de kbps escolhe 16 ou 24 bits.
• Double Bass: copia os graves do subwoofer para as colunas e os das colunas para o subwoofer (só em faixas com subwoofer), com o seu «Auto». O seu «Auto» põe o Double Bass (1-3) se faltarem graves profundos às colunas ou se o subwoofer estiver fraco; se estiverem equilibrados, 0. Corte por defeito: 90 Hz.
• Sincronização: Delay da faixa, «Calculate delay» e «Fix by parts» comparando com outra faixa (normalmente a do idioma original), como no Jmg AudioProcesador. «Add track» junta, por exemplo, uma dobragem que tem à parte.
• «▶ Check synchronization» (em Synchronization): o vídeo na sua janela com a faixa tal como vai sair (delay, partes e efeitos), a partir do ponto que escolher ou de cada parte, para ver com os próprios olhos se os lábios acompanham a voz. No mesmo momento também pode ouvir a faixa sem correção ou a de referência. É a mesma janela que no Jmg AudioProcesador.
• Framerate (em Synchronization): para uma faixa de uma edição de 25 fps num filme de 23,976 (ou o contrário), como no Jmg AudioProcesador: muda a sua velocidade exata, com ou sem mudança de tom, antes do delay e das partes. Ao juntar uma faixa de outro ficheiro que dura 4 % menos (ou mais) do que o vídeo, o programa deteta-o, põe-no sozinho e avisa. Depois calcule o delay.
• Ouvir: nas «Visual / Waves» de Audio, «▶ Before» ou «▶ After» (ou clique nas ondas); ⏸ pausa (premido outra vez, continua) e ⏹ para e volta ao início. Em multicanal (para um amplificador AV) ou em estéreo.
• Faixas de áudio, como no Jmg AudioProcesador: a faixa processada (com efeitos; mudar só o codec ou o bitrate não conta) sai primeiro e por defeito, com o título «Jmg procesada» (pode mudar-se), e a original fica atrás. «🚫 Remove original» tira-a (a linha fica vermelho-claro; outra vez, volta); numa faixa sem processar, tira-a do vídeo. «➕ Add track» traz uma faixa de outro ficheiro e «➖ Delete track» tira-a da lista (o ficheiro original não é tocado).
• «➕ DTS core» (separador Audio): uma faixa DTS-HD (Master Audio ou High Resolution) leva dentro um DTS normal para os aparelhos que não entendem o HD; isto tira-o também como faixa à parte (em MKV), sem recomprimir. Outra vez: tira-se.
• Em «Information», o botão direito do rato: «Copy» e «Select all» (também no Log). Ao abrir o programa, o separador Video vê-se inteiro; a linha do meio pode arrastar-se e fica guardada.
• Ao premir PROCESS aparece uma janela com o essencial (cada vídeo, o ficheiro que vai sair e os avisos); «🔍 See everything» mostra tudo (vídeo, imagem, corte, cada faixa, legendas e os comandos do FFmpeg) e copia-se com «📋 Copy all». «Sim» para começar.

LEGENDAS
• Todas as do vídeo, com ordem, idioma, título, predefinida e forçada. «Add external subtitle» junta um SRT, ASS, VTT ou SUP.
• Em MKV vão todas. Em MP4 e MOV as de texto são convertidas e as de imagem (PGS, DVD) ficam de fora, com aviso.
• Sincronização da legenda selecionada (separador Subtitles): Framerate e Delay, como o áudio, para as legendas de uma edição de 25 fps num filme de 23,976 (ou o contrário). Aplicam-se ao processar, também às de imagem (PGS, DVD) e no corte por partes. Ao juntar o vídeo, fica por defeito a legenda forçada ou, se não houver, a primeira da lista.

OPÇÕES AVANÇADAS
• Vídeo · «More options» (separador Video): abre-se dentro da janela, com «Back». Em cima a imagem antes e depois; em baixo, a barra (clique e setas ← → = imagem a imagem; com Shift, de segundo em segundo), o corte por partes (várias partes juntam-se num só vídeo), a imagem (brilho, contraste, saturação, tom, nitidez e remover ruído) e as barras pretas (procuradas sozinhas ao adicionar o vídeo). «Auto» em Picture mede o filme e propõe os valores (premir outra vez = tudo a 0); se não gostar do resultado, retoque-o à mão.
• «Play» abre uma janela de vídeo com som a partir do ponto da barra: o original ou com as definições, com a primeira faixa de áudio incluída, em multicanal ou estéreo.
• Áudio · «Visual / Waves» (separador Audio): as ondas de cada canal antes e depois, do troço que escolher (primeiros 5, 10 ou 30 minutos ou o ficheiro inteiro), como no Jmg AudioProcesador. Clique nas ondas = ouvir a partir daí. As ondas geram-se sozinhas ao entrar e refazem-se ao mudar Presence ou o troço; cada canal aparece preenchido, com o seu pico em dBFS, e «Zoom» amplia as ondas fracas. À direita de Presence, Dynamic range / Compression: com ela não é preciso subir tanto a Presence. «Detail» (x1-x8) mostra as ondas com mais resolução; movem-se com a roda ou com a barra de baixo, e enquanto toca a vista segue a linha vermelha.
• Os efeitos somam-se: o «After» leva todos os da faixa. Aí está também a Presença (voz, ambiente, efeitos e subwoofer) com o seu «Auto». Undo e Redo continuam em baixo.

SAÍDA
• MKV (aceita tudo), MP4 (para telemóveis e televisores) ou MOV (o do ProRes e DNxHR; o VP9 vai em MKV ou MP4) ou AVI (para aparelhos antigos: H.264 com áudio AC3, MP3 ou DTS, sem legendas nem capítulos) ou WebM (para a web: VP9 ou AV1 com áudio Opus e legendas de texto em WebVTT). Pasta junto ao original ou a que escolher, texto acrescentado ao nome e o que fazer se já existir. O filme de um disco ou de uma imagem ISO vai para Vídeos (a menos que escolha outra pasta).
• Também se copiam os capítulos, os metadados e os anexos (tipos de letra dos ASS e capas).
• A barra de baixo mostra o progresso e o tempo que falta. «When done» pode sair do programa, suspender o PC ou desligá-lo.
• Capa: a do vídeo, outra imagem (JPG ou PNG) ou nenhuma. O ficheiro chama-se como o vídeo com « (Jmg VideoEncoder)» no fim (o acrescento pode ser mudado, e em «Name of this video» pode ter outro nome); se já existir, junta-se _1, _2... No fim abre-se a pasta de destino, exceto se o PC for desligar. «📤 Extraction...», à direita do nome, tira tudo o que o vídeo leva para uma pasta «(extraction)», cada coisa no seu formato original e sem recomprimir: vídeo, faixas de áudio, legendas, capas, anexos e capítulos (cada coisa com a sua caixa para marcar). Também a partir do menu do ícone da área de notificação («📤 Extraction...») e, com o programa instalado, com o botão direito num ficheiro de vídeo no Explorador («Extract with Jmg VideoEncoder»; no Windows 11, em «Mostrar mais opções»): se o programa não estiver aberto, aparece só a janela de extração, que se fecha no fim. Com um DVD ou Blu-ray de vídeo no leitor, o botão direito sobre o leitor (com o programa instalado) e o menu do ícone da área de notificação oferecem «Rip» (o filme principal entra na lista em Passthrough para escolher idiomas e legendas: sai um MKV sem perder qualidade) e «Create ISO image»; no menu da área de notificação, «Create ISO image» também para discos de dados.
• «🔍 Search online...» (Output → Cover): procura o filme no TMDB, mostra os seus pósteres para escolher um e põe-no como capa com o nome «Título (Ano)». Se junto ao vídeo houver um cover.jpg ou folder.jpg (deixados por muitos programas de ripagem, Kodi ou Plex) e o vídeo não tiver capa, é usado sozinho. Precisa da sua própria chave do TMDB, gratuita: na primeira vez, o programa explica como obtê-la (conta em themoviedb.org → Definições → API). Sem ligação, simplesmente não procura.

A TER EM CONTA
• «↶ Undo» e «↷ Redo» (em baixo; também Ctrl+Z e Ctrl+Y): anulam e refazem, uma a uma, as últimas 5 ações (definições, adicionar ou retirar vídeos...). «Reset» repõe as definições automáticas do separador aberto (Video, Audio, Subtitles ou Output) do vídeo ativo; com «All», tudo do zero: a lista de vídeos, a sua informação, as suas definições e a Saída predefinida (↶ recupera). Enquanto uma janela como «Combine videos», «Check synchronization» ou as opções avançadas estiver aberta, os botões da janela principal não funcionam: essas janelas têm os seus próprios ↶ ↷.
• Ao minimizar, o programa fica como um ícone junto ao relógio (área de notificação), que mostra como vai o processo: clique esquerdo = a janela volta; clique direito = menu (cancelar o processo, o que fazer no fim —nada, sair ou desligar o PC—, abrir a pasta no fim, sair). Em Output pode desligar-se, para minimizar para a barra de tarefas como sempre. Deixando o rato sobre um botão, caixa ou controlo, aparece uma descrição, que desaparece sozinha após alguns segundos.
• Opções avançadas («⚙» junto ao codec, em Video e em cada faixa de Audio): o mais importante de cada codec, para quem quiser afinar. Vídeo: ajuste (tune: cinema, animação, grão...), perfil e nível, uma imagem-chave a cada X segundos, imagens B e de referência, quantização adaptativa, grão de película sintético em AV1, duas passagens e AQ da NVIDIA, qualidade máxima e pré-análise da AMD, perfil ProRes (Proxy a 4444 XQ) e DNxHR (LB a 444). Áudio: a informação do fluxo AC3 e E-AC3 (nível de diálogo, Dolby Surround EX, auscultadores, HDCD, downmix) e o corte de agudos, VBR de MP3 e de Opus, compressão FLAC. O que não se toca fica automático; cada vídeo e cada faixa com o seu. Na lista de faixas, «⚙» = com opções avançadas. Em AC3 e E-AC3 também o tipo de sala (grande ou pequena) com o seu nível de mistura; em DTS, a predição ADPCM. O DTS do FFmpeg é sempre de bitrate fixo: 768 ou 1536 kbps, os padrão (com menos, os leitores só dão ruído). AC3 (Aften e FFmpeg): em 5.1, de 224 a 640 kbps; em estéreo, de 96 a 640 (por defeito 192). E-AC3: qualquer bitrate, escrito à mão, a partir de 192 kbps em 5.1 (em estéreo a partir de 64; por defeito 192). O Dolby TrueHD vem a seguir aos Dolby.
• Legendas · «Burn into the picture»: a legenda escolhida fica desenhada no vídeo; vê-se em qualquer aparelho, mas já não se pode tirar. Só uma, e obriga a recomprimir o vídeo (se estava em Passthrough, passa a H.265). As de texto (SRT, ASS) desenham-se sobre a imagem final; as de imagem (PGS, DVD), sobre a original (ao tirar as barras pretas, o que estiver nelas é cortado).
• «Edit/Log» guarda tudo o que acontece; «Show the FFmpeg command» mostra o comando exato do vídeo ativo.
• Ao arrancar, uma vez por dia, o programa verifica no GitHub se há uma versão nova e pergunta se quer abrir a página de transferência. Não transfere nem instala nada por si.
• De 45 em 45 dias, ao abrir o programa, aparece durante 5 segundos uma mensagem a lembrar que se pode apoiar o projeto; fecha-se sozinha e, se clicar na ligação de apoio (aí ou em «About»), não volta a aparecer.
• «⏸ Pause» (ao lado de PROCESS) para o processamento sem perder nada e «▶ Resume» continua-o onde estava. «When done» pode ser alterado durante o processamento.
• Blu-ray: o idioma de cada faixa de áudio e de cada legenda é lido da lista de reprodução do disco (os ficheiros .m2ts não o trazem).
• Enquanto trabalha (processar, combinar, ripar, extrair, criar ISO...), o PC não entra em suspensão; o ecrã pode desligar-se na mesma.
• «➖ Delete subtitle» (separador Subtitles) retira a legenda selecionada, do vídeo ou adicionada: não sai no ficheiro processado e o original não é alterado.
• «Combine videos» (ao lado de «Add to queue») junta partes de vários vídeos num só, com o tamanho do primeiro; «Match color and brightness» mede cada parte e ajusta-a ao primeiro. Com a imagem e «Start here» / «End here» marca-se cada parte sem trabalhar às cegas. Leva as faixas de áudio marcadas de cada vídeo (ou a escolhida em «Audio of this part») e as suas legendas de texto marcadas (as de imagem não se podem juntar). O resultado entra na lista de vídeos, tal como um vídeo com partes ao terminar. O vídeo de cada parte escolhe-se na própria janela («Video:» e «➕ Add»). As setas ← → do teclado avançam uma imagem por toque e, mantidas, cada vez mais depressa. «Set» aplica o início e o fim escritos à parte escolhida; «↺ Reset» esvazia a lista de partes; ↶ ↷ (ou Ctrl+Z / Ctrl+Y) desfazem e refazem.
• «🎵 To AudioProcesador» (em cima, depois de «Create ISO»): passa os ficheiros selecionados da lista (ou todos) para o Jmg AudioProcesador. Se estiver aberto, vão para a lista dele; se não, abre-se com eles. Se não o encontrar, pede-lhe que o procure uma vez. Depois, este programa fecha-se (os dois não ficam abertos ao mesmo tempo).
• Todos os controlos deslizantes se movem com as setas do teclado (clique antes no controlo). Os separadores ganham sozinhos a altura que precisam.

FFMPEG E LICENÇA
Usa FFmpeg (ffmpeg.org, compilação de BtbN) com licença GNU GPL v3.
Jmg VideoEncoder é software livre sob a licença GNU GPL v3.
Contacto: jmgsoftwaremultimedia@gmail.com
Apoie o projeto: https://www.paypal.com/paypalme/JmgSoftware
Realizar o Jmg SuiteMultimedia (este programa e o Jmg AudioProcesador 5.1) custou um trabalho enorme: cerca de 45 dias, com testes em filmes reais. Desenvolvido com a ajuda do Claude, a inteligência artificial da Anthropic.
"""
AYUDA["zh"]="""JMG VIDEOENCODER · 帮助

使用方法
1. 用「Select」「Add」或拖放添加视频（MKV、MP4、AVI、MOV、M2TS 等）。DVD 或蓝光请用「📀 DVD/BD」，选择包含 VIDEO_TS 或 BDMV 的文件夹（会选取正片）。仅支持无防拷贝保护或已解密的光盘：FFmpeg 无法读取受保护的光盘（DVD 的 CSS、蓝光的 AACS），本程序也不会去除这种保护；如果光盘受保护，会提示并且不添加。请使用无保护或已解密的副本（前提是你所在国家的法律允许）。直接从光盘抓取又慢又不稳定：建议先制作 ISO 映像（「💿 Create ISO...」）再打开。「📀 DVD/BD」也能打开光盘映像（.iso）：Windows 会自动装载，关闭程序时卸载（Linux 下请自行装载并选择其文件夹）。「💿 Create ISO...」可将 DVD 或蓝光文件夹（VIDEO_TS 或 BDMV）制作成 .iso 映像，或原样复制光驱中的光盘，然后用「📀 Open in the list」加入列表。映像文件名与光盘相同（蓝光的标题或 DVD、BD、CD 的卷标）。遇到受保护的光盘会提示，如有需要仍可制作完全相同的副本，但同样受保护（无法在此打开）。「🎬 Only the movie」会以 Passthrough 打开正片，选择语言和字幕后得到只含这些内容的 MKV，画质无损。光驱中有光盘时，窗口会直接选中它；复制时同时读写并显示剩余时间，勾选「Shut down the PC when done」可以放到夜里进行（有些光驱读取电影光盘时会变慢，这是光驱本身的限制）。
2. 点击一个视频：右侧显示它的全部信息。选择多个时，显示每个视频的摘要。
3. 按「Add to queue」（或双击）：视频以自动设置进入各个选项卡，并标上 ✔。只处理已添加的视频。
4. 如需要可检查各选项卡，然后按 PROCESS。原始文件永远不会被修改。

视频
• 编码：H.264 (AVC)、H.265 (HEVC)、H.266 (VVC)、AV1、VP9（用于网络），以及用于剪辑的 Apple ProRes 422 LT 和 Avid DNxHR HQ。Passthrough 原样复制视频。H.266 (VVC) 压缩率最高，但也最慢，而且只能用处理器：「Fast」约需视频时长的 2 倍（一部一个半小时的电影，在 16 线程的电脑上约 3 小时）；「Medium」约 5 倍，「Slow」约 20 倍。这些时间仅供参考，很大程度上取决于每台电脑的处理器。赶时间的话，最好用 H.265 或 AV1。
• 编码方式：处理器，或 NVIDIA / AMD 显卡（程序启动时会检测您的电脑上哪些可用）。H.266 和 ProRes 只能用处理器。选项卡中，选中的编码方式显示其颜色（NVIDIA 绿色、AMD 红色）；已应用的「Auto」其文字显示为绿色，手动更改它设置的值或按「Reset」后绿色消失。
• 视频的「Auto」会测量影片：在后台以固定质量编码几个短片段，然后设定画面清晰所需的码率（平静的电影需要更少，颗粒多或动作多的需要更多）。需要几秒钟；在此之前使用其分辨率对应的码率。如果你自己改了码率，它不会再动。
• 恒定质量（数值越小越好）或码率（固定大小）。使用码率时，「Two passes」能更好地分配码率；显卡使用自己的两遍模式。ProRes 没有码率设置。
• 「Auto」根据视频选择编码、码率和分辨率；如果视频已经压缩得很好，就保持 Passthrough。不做改动再按一次，会恢复为 Passthrough。这只是一个起点：如果不喜欢，可以手动调整。
• 分辨率：与原始相同或更小。去隔行：Auto 只在视频为隔行扫描时处理（DVD、电视）。
• 颜色：HDR 电影（HDR10、HLG）以 10 位保留 HDR；「SDR」将其转换为普通屏幕使用。相机的 Log 视频请选择对应的 LUT（.cube）。Dolby Vision：保留 HDR10 层。
• 使用显卡时，「Two passes」采用显卡自己的方式：先分析每一帧再编码。颜色设置只在需要时启用：HDR，或 Log 视频（如果没有检测到，请勾选该选项）。

音频
• 视频的所有音轨：可以调整顺序（⬆ ⬇）、语言、标题、默认音轨，并去掉不需要的音轨（双击）。
• 编码：Passthrough（不改动）、AC3、E-AC3、DTS、AAC、MP3（仅立体声：5.1 会缩混为立体声）、FLAC 和 Opus。「Aften Dolby Digital」（默认）用 Aften 编码 AC3，对动态范围大的影片效果更好；「AC3 · FFmpeg」用 FFmpeg。其设置在「⚙ Aften...」中，与其他格式相同（默认启用块切换和固定全带宽）：CBR 或 VBR、带宽、精度、滤波器、动态范围（DRC 和对白电平）以及供功放使用的码流信息（Dolby Surround EX、Dolby Headphone、A/D 转换器 Standard 或 HDCD、首选下混及其电平）。并非所有设备都能读取 VBR 的 AC3。
• 动态范围 / 压缩：滑块中间为关闭。向左（1-10）为动态范围：对比更强。向右（1-10）为压缩：小声的部分变大（适合夜间观看）。一个用于前置和环绕，另一个用于中置。低音炮不变。它位于「Visual / Waves」（Audio 选项卡）中 Presence 的右侧，可以在波形上看到效果。
• 各声道音量、数字平滑（80、90 年代电影高音过多）和三段均衡器（前置、中置和环绕）。
• 建议的顺序：先调 Presence 和/或 Dynamic range，再调其他效果，最后才调 Volume per channel：这样每个声道的音量是在其他所有效果的结果上调整的，控制更精细。
• 每个「Auto」在已应用其他效果的情况下测量音轨并设置控件；不做改动再按一次，会恢复为 0。效果属于所选音轨；如果是 Passthrough，音轨会用原来的编码重新压缩。
• TrueHD 和 FLAC 是无损格式：不是选择码率，而是选择 16 或 24 位。
• Double Bass：把低音炮的低频复制到各扬声器，并把各扬声器的低频复制到低音炮（仅限有低音炮的音轨），带「Auto」。其「Auto」在扬声器缺少深沉低频或低音炮偏弱时设置 Double Bass（1-3）；两者平衡时为 0。默认分频点：90 Hz。
• 同步：音轨的 Delay，以及与另一条音轨（通常是原语言音轨）比较的「Calculate delay」和「Fix by parts」，与 Jmg AudioProcesador 相同。「Add track」可以添加单独存放的配音等。
• 「▶ Check synchronization」（在 Synchronization 中）：在窗口中播放视频，音轨与最终输出一致（延迟、分段和效果），可从所选位置或每个分段开始，亲眼确认口型是否与声音一致。在同一时刻也可以试听未校正的音轨或参考音轨。与 Jmg AudioProcesador 中的窗口相同。
• Framerate（在 Synchronization 中）：用于 23.976 fps 影片中来自 25 fps 版本的音轨（或反过来），与 Jmg AudioProcesador 相同：在延迟和分段之前精确改变其速度，可选是否改变音调。添加来自其他文件、比视频短（或长）4% 的音轨时，程序会自动检测并设置，并给出提示。之后再计算延迟。
• 试听：在 Audio 的「Visual / Waves」中，「▶ Before」或「▶ After」（或点击波形）；⏸ 暂停（再按一次继续），⏹ 停止并回到开头。可通过多声道（连接 AV 功放时）或立体声播放。
• 音轨与 Jmg AudioProcesador 相同：处理过的音轨（应用了效果；仅更改编码或比特率不算）排在最前面并设为默认，标题为「Jmg procesada」（可修改），原始音轨保留在后面。「🚫 Remove original」会移除原始音轨（该行变为浅红色；再按一次恢复）；对未处理的音轨，则将其从视频中移除。「➕ Add track」从其他文件添加音轨，「➖ Delete track」将其从列表中删除（原文件不受影响）。
• 「➕ DTS core」（Audio 选项卡）：DTS-HD 音轨（Master Audio 或 High Resolution）内含一条普通 DTS，供不支持 HD 的设备使用；此按钮会把它也作为单独的音轨输出（MKV），不重新编码。再按一次：取消。
• 在「Information」中点击鼠标右键：「Copy」和「Select all」（日志中也可以）。打开程序时，Video 选项卡会完整显示；中间的分隔线可以拖动，并会被记住。
• 按下 PROCESS 时，会弹出窗口显示要点（每个视频、将生成的文件和提示）；「🔍 See everything」显示全部信息（视频、图像、剪切、每条音轨、字幕和 FFmpeg 命令），可用「📋 Copy all」复制。点「是」开始。

字幕
• 视频的所有字幕，可设置顺序、语言、标题、默认和强制。「Add external subtitle」可添加 SRT、ASS、VTT 或 SUP。
• MKV 中全部保留。MP4 和 MOV 中，文字字幕会被转换，图像字幕（PGS、DVD）不会保留，并会提示。
• 所选字幕的同步（Subtitles 选项卡）：Framerate 和 Delay，与音频相同，用于 23.976 fps 影片中来自 25 fps 版本的字幕（或反过来）。在处理时应用，图像字幕（PGS、DVD）和分段剪切同样适用。添加视频时，默认字幕为强制字幕；如果没有，则为列表中的第一个。

高级选项
• 视频 · 「More options」（Video 选项卡）：在窗口内打开，带「Back」按钮。上方是处理前后的画面；下方是滑块（点击后用 ← → 逐帧移动；按住 Shift 逐秒移动）、分段剪切（多个片段合并成一个视频）、图像（亮度、对比度、饱和度、色调、锐度和降噪）以及黑边（添加视频时自动检测）。图像中的「Auto」会测量影片并给出建议值（再按一次 = 全部归 0）；如果不满意，可以手动微调。
• 「Play」从滑块所在位置打开一个带声音的视频窗口：原始的或应用设置后的，使用第一条包含的音轨，多声道或立体声。
• 音频 · 「Visual / Waves」（Audio 选项卡）：所选片段（前 5、10 或 30 分钟，或整个文件）处理前后每个声道的波形，与 Jmg AudioProcesador 相同。点击波形 = 从该处试听。进入时会自动生成波形，修改 Presence 或片段时会重新生成；每个声道以填充方式显示，并标出 dBFS 峰值，「Zoom」可放大较弱的波形。Presence 右侧是 Dynamic range / Compression：有了它，就不必把 Presence 调得太高。「Detail」（x1-x8）以更高分辨率显示波形；可用滚轮或下方的滚动条移动，播放时视图会跟随红线。
• 效果是叠加的：「After」包含该音轨的所有效果。这里还有 Presence（人声、环境、效果和低音炮）及其「Auto」。Undo 和 Redo 仍在底部。

输出
• MKV（全部支持）、MP4（适合手机和电视）或 MOV（ProRes 和 DNxHR 用；VP9 使用 MKV 或 MP4）或 AVI（用于旧设备：H.264 配 AC3、MP3 或 DTS 音频，不含字幕和章节）或 WebM（用于网络：VP9 或 AV1 配 Opus 音频，文字字幕为 WebVTT）。文件夹可在原文件旁边或自选，可在文件名后添加文字，并设置文件已存在时的处理方式。来自光盘或 ISO 镜像的电影保存到「视频」文件夹（除非你选择了其他文件夹）。
• 同时复制章节、元数据和附件（ASS 字体和封面）。
• 底部进度条显示进度和剩余时间。「When done」可以退出程序、让电脑睡眠或关闭电脑。
• 封面：使用视频自带的、另一张图片（JPG 或 PNG），或不用封面。文件名为视频名加上「 (Jmg VideoEncoder)」（附加部分可以修改，也可以在「Name of this video」中另起名字）；如果已存在，会加上 _1、_2……。完成后会打开目标文件夹，除非要关闭电脑。名称右边的「📤 Extraction...」会把视频里的所有内容取出到「(extraction)」文件夹，每样都保持原始格式、不重新编码：视频、音轨、字幕、封面、附件和章节（每一项都有自己的复选框）。也可以从通知区域图标的菜单（「📤 Extraction...」）使用；安装程序后，还可以在资源管理器中右键单击视频文件（「Extract with Jmg VideoEncoder」；Windows 11 中在「显示更多选项」里）：如果程序没有打开，只会出现提取窗口，完成后自动关闭。光驱中放入视频 DVD 或蓝光时，在光驱上右键（安装程序后）以及通知区域图标的菜单中会出现「Rip」（主电影以直通方式加入列表，可选择语言和字幕：得到无损画质的 MKV）和「Create ISO image」；在通知区域菜单中，数据光盘也可以「Create ISO image」。
• 「🔍 Search online...」（Output → Cover）：在 TMDB 上查找电影，显示其海报供你选择，并将其设为封面，文件名改为「标题 (年份)」。如果视频旁边有 cover.jpg 或 folder.jpg（许多抓取软件以及 Kodi、Plex 会生成）且视频本身没有封面，会自动使用。需要你自己的免费 TMDB 密钥：第一次使用时，程序会说明如何获取（在 themoviedb.org 注册账号 → 设置 → API）。没有网络时只是不进行搜索。

注意事项
• 「↶ Undo」和「↷ Redo」（在底部；也可用 Ctrl+Z 和 Ctrl+Y）：逐一撤销和重做最近 5 个操作（设置、添加或移除视频等）。「Reset」恢复当前视频在已打开选项卡（Video、Audio、Subtitles 或 Output）中的自动设置；勾选「All」时全部从头开始：视频列表、其信息、其设置以及默认输出（↶ 可以恢复）。打开「Combine videos」「Check synchronization」或高级选项等窗口时，主窗口的按钮不可用：这些窗口有自己的 ↶ ↷。
• 最小化后，程序会以图标形式留在时钟旁边（系统托盘），并显示处理进度：左键单击 = 恢复窗口；右键单击 = 菜单（取消处理、完成后的操作——无、退出或关机——、完成后打开文件夹、退出）。可在 Output 中关闭此功能，像平常一样最小化到任务栏。将鼠标停在按钮、复选框或滑块上会显示说明，几秒后自动消失。
• 高级选项（编码器旁的「⚙」，在 Video 和每条 Audio 音轨中）：每种编码器最重要的设置，供想要微调的用户使用。视频：调优（tune：电影、动画、颗粒……）、配置文件和级别、每 X 秒一个关键帧、B 帧和参考帧、自适应量化、AV1 的合成胶片颗粒、NVIDIA 的两遍编码和 AQ、AMD 的最高质量和预分析、ProRes 配置（Proxy 到 4444 XQ）和 DNxHR 配置（LB 到 444）。音频：AC3 和 E-AC3 的码流信息（对白电平、Dolby Surround EX、耳机、HDCD、下混）和高频截止、MP3 和 Opus 的 VBR、FLAC 压缩。未更改的保持自动；每个视频和每条音轨各自保存。音轨列表中的「⚙」表示带有高级选项。AC3 和 E-AC3 还有房间类型（大或小）及其混音电平；DTS 有 ADPCM 预测。FFmpeg 的 DTS 始终为固定比特率：768 或 1536 kbps，即标准比特率（更低时播放器只会输出噪音）。AC3（Aften 和 FFmpeg）：5.1 为 224 至 640 kbps；立体声为 96 至 640（默认 192）。E-AC3：可手动输入任意比特率，5.1 从 192 kbps 起（立体声从 64 起；默认 192）。Dolby TrueHD 排在 Dolby 格式之后。
• 字幕 ·「Burn into the picture」：将所选字幕直接绘制到视频画面中；在任何设备上都能看到，但之后无法去除。只能选一条，且必须重新编码视频（若为 Passthrough，会改为 H.265）。文本字幕（SRT、ASS）绘制在最终画面上；图像字幕（PGS、DVD）绘制在原始画面上（去除黑边时，黑边中的内容会被裁掉）。
• 「Edit/Log」记录发生的一切；「Show the FFmpeg command」显示当前视频的确切命令。
• 程序启动时每天一次在 GitHub 上检查是否有新版本，并询问是否打开下载页面。它不会自行下载或安装任何东西。
• 每 45 天，打开程序时会显示 5 秒钟的提示，提醒您可以支持本项目；它会自动关闭，如果点击了支持链接（在提示中或在「About」中），就不会再出现。
• 「⏸ Pause」（在 PROCESS 旁）暂停处理而不丢失任何内容，「▶ Resume」从中断处继续。处理过程中可以更改「When done」。
• 蓝光：每条音轨和每个字幕的语言从光盘的播放列表中读取（.m2ts 文件本身不带语言信息）。
• 程序工作时（处理、合并、抓取、提取、创建 ISO……），电脑不会进入睡眠；屏幕仍可以关闭。
• 「➖ Delete subtitle」（「Subtitles」选项卡）删除所选字幕（视频自带的或添加的）：处理后的文件中不再包含它，原文件不受影响。
• 「Combine videos」（在「Add to queue」旁边）把多个视频的片段合并成一个，大小与第一个相同；「Match color and brightness」会测量每个片段并按第一个调整。借助画面以及「Start here」/「End here」可以看着标记每个片段。会带上每个视频已勾选的音轨（或在「Audio of this part」中选择的音轨）和已勾选的文字字幕（图像字幕无法合并）。结果会加入视频列表，与处理完的分段视频一样。每个片段的视频在该窗口中选择（「Video:」和「➕ Add」）。键盘方向键 ← → 每按一次前进一帧，按住则越来越快。「Set」把输入的开始和结束应用到所选片段；「↺ Reset」清空片段列表；↶ ↷（或 Ctrl+Z / Ctrl+Y）撤销和重做。
• 「🎵 To AudioProcesador」（顶部「Create ISO」之后）：把列表中选中的文件（或全部）交给 Jmg AudioProcesador。如果它已打开，文件会加入它的列表；否则会用这些文件打开它。如果找不到，会请您手动查找一次。之后本程序会关闭（两个程序不会同时开着）。
• 所有滑块都可以用键盘方向键移动（先点击滑块）。各选项卡会自动获得所需的高度。

FFMPEG 与许可证
使用 FFmpeg（ffmpeg.org，BtbN 版本），许可证为 GNU GPL v3。
Jmg VideoEncoder 是基于 GNU GPL v3 许可证的自由软件。
联系方式：jmgsoftwaremultimedia@gmail.com
支持本项目：https://www.paypal.com/paypalme/JmgSoftware
完成 Jmg SuiteMultimedia（本程序和 Jmg AudioProcesador 5.1）付出了巨大的努力：约 45 天，并用真实的电影进行了测试。在 Anthropic 的人工智能 Claude 的帮助下开发。
"""
AYUDA["ja"]="""JMG VIDEOENCODER · ヘルプ

使い方
1. 「Select」「Add」またはリストへのドラッグで動画を追加します（MKV、MP4、AVI、MOV、M2TS など）。DVD やブルーレイは「📀 DVD/BD」で VIDEO_TS または BDMV のあるフォルダーを選びます（本編を使います）。コピー保護のないディスク、またはすでに復号されたディスクのみ対応します。FFmpeg は保護されたディスク（DVD の CSS、ブルーレイの AACS）を読めず、このプログラムも保護を解除しません。保護されたディスクは警告を出して追加しません。保護のないコピー、またはすでに復号されたコピーを使ってください（お住まいの国の法律で認められている場合）。ディスクから直接リッピングすると遅く不安定です。先に ISO イメージを作って（「💿 Create ISO...」）から開くことをおすすめします。「📀 DVD/BD」はディスクイメージ（.iso）も開けます。Windows が自動でマウントし、プログラムを閉じるとマウント解除します（Linux では自分でマウントしてそのフォルダーを選んでください）。「💿 Create ISO...」は DVD やブルーレイのフォルダー（VIDEO_TS または BDMV）から .iso イメージを作るか、ドライブのディスクをそのままコピーし、「📀 Open in the list」でリストに追加します。イメージ名はディスクと同じです（ブルーレイのタイトル、または DVD・BD・CD のラベル）。保護されたディスクは警告を出し、希望すれば同じく保護されたままの完全なコピーを作ります（ここでは開けません）。「🎬 Only the movie」は本編を Passthrough で開き、言語と字幕を選んで、それだけを含む MKV を画質を落とさずに作ります。ドライブにディスクがあれば、ウィンドウは最初からそれを選びます。コピーは読み込みと書き込みを同時に行い残り時間を表示し、「Shut down the PC when done」で夜間に任せられます（映画ディスクでは遅くなるドライブもあり、ドライブ自体の制限です）。
2. 動画をクリックすると、右側にすべての情報が表示されます。複数選ぶと、それぞれの概要が表示されます。
3. 「Add to queue」（またはダブルクリック）を押すと、動画が自動設定でタブに入り、✔ が付きます。処理されるのは追加した動画だけです。
4. 必要ならタブを確認して PROCESS を押します。元のファイルは変更されません。

動画
• コーデック：H.264 (AVC)、H.265 (HEVC)、H.266 (VVC)、AV1、VP9（Web 用）、編集用の Apple ProRes 422 LT と Avid DNxHR HQ。Passthrough は動画をそのままコピーします。H.266 (VVC) は最も圧縮率が高い反面、最も遅く、プロセッサーのみです。「Fast」では動画の長さの約 2 倍（1 時間半の映画なら、16 スレッドの PC で約 3 時間）、「Medium」では約 5 倍、「Slow」では約 20 倍かかります。これらの時間は目安で、パソコンのプロセッサーによって大きく変わります。急ぐときは H.265 か AV1 がおすすめです。
• エンコード方法：プロセッサー、または NVIDIA / AMD のグラフィックカード（起動時に、この PC で使えるものを調べます）。H.266 と ProRes はプロセッサーのみです。タブでは、選択中のエンジンがその色になります（NVIDIA 緑、AMD 赤）。適用中の「Auto」は文字が緑になり、設定された値を手で変えるか「Reset」を押すと消えます。
• 映像の「Auto」は映画を測定します。バックグラウンドで短い部分をいくつか固定品質でエンコードし、きれいに見えるのに必要なビットレートを設定します（静かな映画は少なく、粒子やアクションの多い映画は多く）。数秒かかり、その間は解像度に応じた値を使います。ビットレートを自分で変えた場合は変更しません。
• 固定品質（小さいほど高画質）またはビットレート（固定サイズ）。ビットレートでは「Two passes」がビットレートをよりよく配分します。グラフィックカードは独自の 2 パスモードを使います。ProRes にはビットレートの設定はありません。
• 「Auto」は動画に合わせてコーデック、ビットレート、解像度を選びます。すでに十分圧縮されていれば Passthrough のままにします。何も変えずにもう一度押すと Passthrough に戻ります。これは出発点です。気に入らなければ手動で調整してください。
• 解像度：元と同じか、より小さく。インターレース解除：Auto はインターレースの動画（DVD、テレビ）のときだけ行います。
• 色：HDR 映画（HDR10、HLG）は 10 ビットで HDR を保ちます。「SDR」は通常の画面用に変換します。カメラの Log 動画にはその LUT（.cube）を選びます。Dolby Vision：HDR10 レイヤーが保たれます。
• グラフィックカードでは「Two passes」は独自の方式を使います：各フレームを分析してからエンコードします。色の設定は必要なときだけ有効になります：HDR、または Log 動画（検出されない場合はチェックを入れてください）。

音声
• 動画のすべてのトラック：順番（⬆ ⬇）、言語、タイトル、既定のトラックを変更でき、不要なものを外せます（ダブルクリック）。
• コーデック：Passthrough（そのまま）、AC3、E-AC3、DTS、AAC、MP3（ステレオのみ：5.1 はステレオにダウンミックス）、FLAC、Opus。「Aften Dolby Digital」（既定）は Aften で AC3 を作り、ダイナミックレンジの大きい映画で優れます。「AC3 · FFmpeg」は FFmpeg です。設定はほかの形式と同じく「⚙ Aften...」から（初期値はブロック切り替えと固定・全帯域）：CBR/VBR、帯域幅、精度、フィルター、ダイナミックレンジ（DRC と台詞レベル）、アンプ向けのビットストリーム情報（Dolby Surround EX、Dolby Headphone、A/D コンバーター Standard または HDCD、推奨ダウンミックスとそのレベル）。VBR の AC3 はすべての機器で再生できるわけではありません。
• ダイナミックレンジ / 圧縮：中央がオフのスライダーです。左（1-10）はダイナミックレンジ：コントラストが強くなります。右（1-10）は圧縮：小さな音が大きくなります（夜に映画を見るとき）。フロントとサラウンド用に 1 つ、センター用に 1 つあります。サブウーファーは変更しません。「Visual / Waves」（Audio タブ）の Presence の右にあり、波形で効果を確認できます。
• チャンネルごとの音量、デジタルスムージング（80〜90 年代の映画の高音過多）、3 バンドイコライザー（フロント、センター、サラウンド）。
• おすすめの順番：まず Presence や Dynamic range、次にその他のエフェクト、最後に必ず Volume per channel。こうすると各チャンネルの音量を他のすべての効果をかけた結果に合わせて、より細かく調整できます。
• 各「Auto」は、ほかの効果を適用した状態でトラックを測定し、コントロールを設定します。何も変えずにもう一度押すと 0 に戻ります。効果は選択したトラックのものです。Passthrough の場合、トラックは元のコーデックで再圧縮されます。
• TrueHD と FLAC はロスレスです：kbps ではなく 16 ビットか 24 ビットを選びます。
• Double Bass：サブウーファーの低音をスピーカーへ、スピーカーの低音をサブウーファーへコピーします（サブウーファーのあるトラックのみ）。「Auto」付きです。「Auto」は、スピーカーに深い低音が足りないかサブウーファーが弱いときに Double Bass（1-3）を設定し、バランスが取れていれば 0 にします。既定のカット：90 Hz。
• 同期：トラックの Delay、ほかのトラック（通常は元の言語のトラック）と比べる「Calculate delay」と「Fix by parts」。Jmg AudioProcesador と同じです。「Add track」で、別に持っている吹き替えなどを追加できます。
• 「▶ Check synchronization」（Synchronization 内）：出力と同じ状態のトラック（ディレイ、区間、エフェクト）と一緒に動画をウィンドウで再生します。選んだ位置または各区間から再生でき、口の動きと声が合っているかを自分の目で確認できます。同じ場面で未補正のトラックや参照トラックも聞けます。Jmg AudioProcesador と同じウィンドウです。
• Framerate（Synchronization 内）：23.976 fps の映画に 25 fps 版のトラックを使うとき（またはその逆）、Jmg AudioProcesador と同じく、ディレイと区間の前に速度を正確に変えます（音程の変化あり／なし）。動画より 4 % 短い（または長い）別ファイルのトラックを追加すると、プログラムが自動で検出して設定し、お知らせします。その後ディレイを計算してください。
• 試聴：Audio の「Visual / Waves」で「▶ Before」または「▶ After」（または波形をクリック）。⏸ で一時停止（もう一度押すと続きから）、⏹ で停止して先頭に戻ります。マルチチャンネル（AV アンプ用）またはステレオで再生できます。
• 音声トラックは Jmg AudioProcesador と同じです。処理したトラック（エフェクトを適用したもの。コーデックやビットレートの変更だけでは該当しません）が先頭でデフォルトになり、タイトルは「Jmg procesada」（変更可）、元のトラックはその後ろに残ります。「🚫 Remove original」で元のトラックを外します（行が薄い赤になり、もう一度押すと戻ります）。未処理のトラックでは動画から外します。「➕ Add track」で別ファイルのトラックを追加し、「➖ Delete track」でリストから外します（元のファイルは変更しません）。
• 「➕ DTS core」（Audio タブ）：DTS-HD トラック（Master Audio または High Resolution）には、HD に対応しない機器のための通常の DTS が入っています。これで、それも別のトラックとして（MKV で）再エンコードせずに出力します。もう一度押すと取り消します。
• 「Information」でマウスの右ボタン：「Copy」と「Select all」（ログでも使えます）。起動時は Video タブ全体が見えます。中央の線はドラッグでき、その位置は記憶されます。
• PROCESS を押すと、要点（各動画と作成されるファイル、注意事項）を示すウィンドウが出ます。「🔍 See everything」ですべて（映像、画像、カット、各トラック、字幕、FFmpeg コマンド）を表示し、「📋 Copy all」でコピーできます。「はい」で開始します。

字幕
• 動画のすべての字幕を、順番、言語、タイトル、既定、強制とともに扱えます。「Add external subtitle」で SRT、ASS、VTT、SUP を追加できます。
• MKV ではすべて入ります。MP4 と MOV ではテキスト字幕は変換され、画像字幕（PGS、DVD）は入らず、お知らせが出ます。
• 選択した字幕の同期（Subtitles タブ）：音声と同じく Framerate と Delay で、23.976 fps の映画に 25 fps 版の字幕を使うとき（またはその逆）に合わせます。処理時に適用され、画像字幕（PGS、DVD）や区間カットにも使えます。動画を追加すると、強制字幕がデフォルトになり、なければリストの最初の字幕になります。

詳細オプション
• 動画 · 「More options」（Video タブ）：ウィンドウ内に開き、「Back」で戻ります。上に処理前と処理後のフレーム、下にバー（クリックして ← → で 1 フレームずつ、Shift で 1 秒ずつ）、区間カット（複数の区間は 1 本の動画につながります）、画像（明るさ、コントラスト、彩度、色相、シャープネス、ノイズ除去）、黒帯（動画を追加したときに自動で探します）があります。画像の「Auto」は映画を測定して値を提案します（もう一度押す = すべて 0 に戻る）。仕上がりが気に入らなければ手で調整してください。
• 「Play」はバーの位置から音声付きの動画ウィンドウを開きます：元のもの、または設定を適用したもの。最初に含まれる音声トラックを使い、マルチチャンネルまたはステレオで再生します。
• 音声 · 「Visual / Waves」（Audio タブ）：選んだ区間（最初の 5・10・30 分、またはファイル全体）の各チャンネルの波形を、処理前と処理後で表示します。Jmg AudioProcesador と同じです。波形をクリック = そこから試聴。波形は開いたときに自動で作成され、Presence や区間を変えると作り直されます。各チャンネルは塗りつぶしで表示され、ピーク (dBFS) も示します。「Zoom」で小さな波形を拡大できます。Presence の右に Dynamic range / Compressionがあります。これを使えば Presence をそれほど上げる必要はありません。「Detail」（x1-x8）で波形をより細かく表示します。ホイールまたは下のバーで移動でき、再生中は表示が赤い線を追います。
• 効果は積み重なります：「After」にはトラックのすべての効果が入ります。ここには Presence（声、環境音、効果音、サブウーファー）とその「Auto」もあります。Undo と Redo は下にあります。

出力
• MKV（すべて対応）、MP4（スマートフォンやテレビ用）、MOV（ProRes と DNxHR 用。VP9 は MKV か MP4）、AVI（古い機器用：H.264 と AC3・MP3・DTS 音声、字幕とチャプターなし）、WebM（Web 用：VP9 か AV1 と Opus 音声、テキスト字幕は WebVTT）。保存先は元のファイルの隣か指定したフォルダー。名前に付ける文字と、同じ名前があるときの動作を選べます。ディスクや ISO イメージの映画は「ビデオ」フォルダーに保存されます（別のフォルダーを選んだ場合を除く）。
• チャプター、メタデータ、添付ファイル（ASS のフォントとカバー）もコピーされます。
• 下のバーに進み具合と残り時間が表示されます。「When done」でプログラムの終了、PC のスリープ、シャットダウンができます。
• カバー：動画のもの、別の画像（JPG または PNG）、またはなし。ファイル名は動画名の後ろに「 (Jmg VideoEncoder)」が付きます（付け足しは変更でき、「Name of this video」で別の名前にもできます）。すでにある場合は _1、_2… が付きます。終了すると保存先フォルダーが開きます（PC をシャットダウンする場合を除く）。名前の右にある「📤 Extraction...」で、動画に入っているものすべてを再エンコードせず元の形式のまま「(extraction)」フォルダーに取り出せます：映像、音声トラック、字幕、カバー、添付ファイル、チャプター（それぞれにチェックボックスがあります）。通知領域アイコンのメニュー（「📤 Extraction...」）からも使えます。プログラムをインストールすると、エクスプローラーで動画ファイルを右クリックしても使えます（「Extract with Jmg VideoEncoder」。Windows 11 では「その他のオプションを表示」の中）。プログラムが開いていなければ抽出ウィンドウだけが表示され、終わると閉じます。ドライブにビデオ DVD やブルーレイを入れると、ドライブの右クリック（プログラムをインストールした場合）と通知領域アイコンのメニューに「Rip」（本編がパススルーでリストに入り、言語と字幕を選べます。画質を落とさずに MKV になります）と「Create ISO image」が出ます。通知領域のメニューでは、データディスクでも「Create ISO image」が使えます。
• 「🔍 Search online...」（Output → Cover）：TMDB で映画を検索し、ポスターを表示して選んだものをカバーにし、名前を「タイトル (年)」にします。動画の横に cover.jpg や folder.jpg（多くのリッピングソフトや Kodi、Plex が作るもの）があり、動画にカバーがない場合は自動で使います。ご自身の無料の TMDB キーが必要です。初回に、プログラムが取得方法を説明します（themoviedb.org でアカウント作成 → 設定 → API）。接続がないときは検索しないだけです。

注意点
• 「↶ Undo」と「↷ Redo」（下部。Ctrl+Z と Ctrl+Y も可）：直近 5 つの操作（設定、動画の追加や削除など）を 1 つずつ元に戻し、やり直します。「Reset」は現在の動画の、開いているタブ（Video、Audio、Subtitles、Output）の設定を自動設定に戻します。「All」にチェックすると、動画リスト、その情報、設定、既定の出力まですべて最初からになります（↶ で元に戻せます）。「Combine videos」「Check synchronization」や詳細オプションなどのウィンドウを開いている間は、メインウィンドウのボタンは使えません。これらのウィンドウには専用の ↶ ↷ があります。
• 最小化すると、プログラムは時計の横（システムトレイ）にアイコンとして残り、処理の進み具合を表示します。左クリック = ウィンドウが戻る、右クリック = メニュー（処理の中止、終了時の動作——なし・終了・PC のシャットダウン——、終了時にフォルダーを開く、終了）。Output でオフにすると、いつもどおりタスクバーに最小化されます。ボタン、チェックボックス、スライダーの上にマウスを置くと説明が表示され、数秒で自動的に消えます。
• 詳細オプション（コーデックの横の「⚙」、Video と各 Audio トラック）：各コーデックの最も重要な設定で、細かく調整したい人向けです。映像：チューン（映画、アニメ、粒状感など）、プロファイルとレベル、X 秒ごとのキーフレーム、B フレームと参照フレーム、適応量子化、AV1 の合成フィルムグレイン、NVIDIA の 2 パスと AQ、AMD の最高品質と事前解析、ProRes プロファイル（Proxy〜4444 XQ）と DNxHR プロファイル（LB〜444）。音声：AC3 と E-AC3 のビットストリーム情報（ダイアログレベル、Dolby Surround EX、ヘッドホン、HDCD、ダウンミックス）と高域カット、MP3 と Opus の VBR、FLAC の圧縮。触らない項目は自動のままで、動画やトラックごとに保存されます。トラック一覧の「⚙」は詳細オプションありを意味します。AC3 と E-AC3 には部屋のタイプ（大・小）とミキシングレベルもあり、DTS には ADPCM 予測があります。FFmpeg の DTS は常に固定ビットレートで、標準の 768 または 1536 kbps です（それより低いとプレーヤーはノイズしか出しません）。AC3（Aften と FFmpeg）：5.1 は 224〜640 kbps、ステレオは 96〜640（初期値 192）。E-AC3：任意のビットレートを手入力でき、5.1 は 192 kbps から（ステレオは 64 から、初期値 192）。Dolby TrueHD は Dolby 形式の後に並びます。
• 字幕 ·「Burn into the picture」：選んだ字幕を映像に焼き込みます。どの機器でも表示されますが、後から消すことはできません。1 つだけで、映像の再エンコードが必要です（Passthrough の場合は H.265 になります）。テキスト字幕（SRT、ASS）は最終的な画面に、画像字幕（PGS、DVD）は元の画面に描画されます（黒帯を除去すると、帯の中の部分は切れます）。
• 「Edit/Log」にはすべての記録が残ります。「Show the FFmpeg command」で、現在の動画の正確なコマンドが見られます。
• 起動時に 1 日 1 回、GitHub で新しいバージョンがあるか確認し、ダウンロードページを開くか尋ねます。自動でダウンロードやインストールはしません。
• 45 日ごとに、プログラムを開くとプロジェクトを支援できることを知らせるメッセージが 5 秒間表示されます。自動で閉じ、支援リンク（そこか「About」内）をクリックすると二度と表示されません。
• 「⏸ Pause」（PROCESS の隣）は何も失わずに処理を一時停止し、「▶ Resume」で中断したところから続けます。「When done」は処理中でも変更できます。
• Blu-ray：各音声トラックと字幕の言語はディスクのプレイリストから読み取ります（.m2ts ファイルには含まれていません）。
• 作業中（処理、結合、リッピング、抽出、ISO 作成など）は PC がスリープしません。画面はオフになることがあります。
• 「➖ Delete subtitle」（「Subtitles」タブ）は選択した字幕（動画内のものでも追加したものでも）を取り除きます。処理後のファイルには含まれず、元のファイルは変更されません。
• 「Combine videos」（「Add to queue」の隣）は複数の動画の区間を 1 本にまとめます。サイズは最初の動画に合わせます。「Match color and brightness」は各区間を測定して最初の区間に合わせます。画像と「Start here」/「End here」で、見ながら各区間を指定できます。各動画のチェックした音声トラック（または「Audio of this part」で選んだもの）とチェックしたテキスト字幕が入ります（画像字幕は結合できません）。結果は、区間指定した動画の処理後と同じく、動画リストに追加されます。各区間の動画はこのウィンドウ内で選びます（「Video:」と「➕ Add」）。キーボードの ← → は 1 回押すごとに 1 フレーム進み、押し続けるとどんどん速くなります。「Set」は入力した開始と終了を選んだ区間に適用し、「↺ Reset」は区間リストを空にし、↶ ↷（または Ctrl+Z / Ctrl+Y）で元に戻す・やり直しができます。
• 「🎵 To AudioProcesador」（上部、「Create ISO」の後ろ）：リストで選んだファイル（またはすべて）を Jmg AudioProcesador に渡します。開いていればそのリストに入り、開いていなければそのファイルで起動します。見つからない場合は一度だけ場所を尋ねます。その後、このプログラムは閉じます（両方が同時に開いたままにはなりません）。
• すべてのスライダーはキーボードの矢印キーで動かせます（先にスライダーをクリック）。各タブは必要な高さに自動で合わせます。

FFMPEG とライセンス
FFmpeg（ffmpeg.org、BtbN ビルド）を GNU GPL v3 ライセンスで使用しています。
Jmg VideoEncoder は GNU GPL v3 ライセンスのフリーソフトウェアです。
連絡先：jmgsoftwaremultimedia@gmail.com
プロジェクトを支援する：https://www.paypal.com/paypalme/JmgSoftware
Jmg SuiteMultimedia（このプログラムと Jmg AudioProcesador 5.1）の制作には膨大な作業が必要でした。約 45 日間、実際の映画でテストを重ねています。Anthropic の AI、Claude の協力で開発されました。
"""
AYUDA["ru"]="""JMG VIDEOENCODER · СПРАВКА

КАК ПОЛЬЗОВАТЬСЯ
1. Добавьте видео кнопками «Select», «Add» или перетащив их в список (MKV, MP4, AVI, MOV, M2TS...). Для DVD или Blu-ray нажмите «📀 DVD/BD» и выберите папку, где есть VIDEO_TS или BDMV (берётся основной фильм). Только диски без защиты от копирования или уже расшифрованные: FFmpeg не может читать защищённые (CSS на DVD, AACS на Blu-ray), а программа эту защиту не снимает; если диск защищён, она предупредит и не добавит его. Используйте копию без защиты или уже расшифрованную, если это разрешает закон вашей страны. Рипать прямо с диска медленно и ненадёжно: лучше сначала сделать образ ISO («💿 Create ISO...») и открыть его. «📀 DVD/BD» открывает и образ диска (.iso): Windows монтирует его, а при закрытии программы он размонтируется (в Linux смонтируйте его сами и выберите его папку). «💿 Create ISO...» делает образ .iso из папки DVD или Blu-ray (VIDEO_TS или BDMV) или копирует диск из привода как есть, а затем «📀 Open in the list» добавляет его. Образ называется как диск (название Blu-ray или метка DVD, BD или CD). С защищённым диском программа предупредит и, если хотите, всё равно сделает точную копию, такую же защищённую (здесь она не откроется). «🎬 Only the movie» открывает основной фильм в Passthrough, чтобы выбрать языки и субтитры и получить MKV только с ними, без потери качества. Если в приводе есть диск, окно открывается с ним; копирование читает и пишет одновременно и показывает оставшееся время, а «Shut down the PC when done» позволяет оставить его на ночь (некоторые приводы медленнее с дисками фильмов: ограничивает сам привод).
2. Щёлкните по видео: справа появится вся информация о нём. Если выбрать несколько, будет сводка по каждому.
3. Нажмите «Add to queue» (или двойной щелчок): видео попадает во вкладки с автоматическими настройками и помечается ✔. Обрабатываются только добавленные видео.
4. При желании проверьте вкладки и нажмите PROCESS. Исходные файлы никогда не изменяются.

VIDEO
• Кодеки: H.264 (AVC), H.265 (HEVC), H.266 (VVC), AV1, VP9 (для интернета) и, для монтажа, Apple ProRes 422 LT и Avid DNxHR HQ. Passthrough копирует видео без изменений. H.266 (VVC) сжимает сильнее всех, но и работает медленнее всех, и только процессором: в «Fast» кодирование занимает примерно вдвое больше длительности видео (фильм на полтора часа — около 3 часов на ПК с 16 потоками); в «Medium» — примерно в 5 раз, в «Slow» — примерно в 20. Это ориентировочное время: оно сильно зависит от процессора компьютера. Если торопитесь, лучше H.265 или AV1.
• Кодировать чем: процессором или видеокартой NVIDIA или AMD (при запуске программа проверяет, какие работают на вашем ПК). H.266 и ProRes — только процессором. Во вкладке выбранный движок показывает свой цвет (NVIDIA зелёный, AMD красный); включённый «Auto» показывает слово зелёным и гаснет, если вручную поменять то, что он поставил, или нажать «Reset».
• «Auto» видео измеряет фильм: в фоне кодирует несколько коротких фрагментов с постоянным качеством и ставит битрейт, нужный для хорошей картинки (спокойному фильму нужно меньше, с сильным зерном или экшеном — больше). Это занимает несколько секунд; до этого используется битрейт для его разрешения. Если вы сами изменили битрейт, он его не трогает.
• Постоянное качество (меньше = лучше) или битрейт (фиксированный размер). С битрейтом «Two passes» лучше распределяет kbps; видеокарты используют свой режим двух проходов. У ProRes нет битрейта.
• «Auto» подбирает кодек, битрейт и разрешение под видео; если оно уже хорошо сжато, оставляет Passthrough. Нажатый ещё раз, ничего не трогая, возвращает Passthrough. Это отправная точка: если не нравится, подправьте вручную.
• Разрешение: как у оригинала или меньше. Деинтерлейсинг: Auto делает его, только если видео чересстрочное (DVD, ТВ).
• Цвет: HDR-фильмы (HDR10, HLG) сохраняют HDR в 10 битах; «SDR» переводит их для обычных экранов. Для видео с камеры в log-профиле выберите его LUT (.cube). Dolby Vision: сохраняется слой HDR10.
• С видеокартой «Two passes» использует её собственную систему: она анализирует каждый кадр перед кодированием. Цвет включается только когда нужно: с HDR или с log-видео (если оно не определилось, поставьте флажок).

AUDIO
• Все дорожки видео: можно менять порядок (⬆ ⬇), язык, название, дорожку по умолчанию и убирать ненужные (двойной щелчок).
• Кодеки: Passthrough (без изменений), AC3, E-AC3, DTS, AAC, MP3 (только стерео: 5.1 сводится), FLAC и Opus. «Aften Dolby Digital» (по умолчанию, в списке кодеков) делает AC3 через Aften, что даёт лучший динамический диапазон в фильмах, где его много; «AC3 · FFmpeg» — через FFmpeg. Его настройки — через «⚙ Aften...», как у других форматов (по умолчанию block switching и фиксированная полная полоса): CBR или VBR, полоса, точность, фильтры, динамический диапазон (DRC и уровень диалогов) и служебная информация для ресивера (Dolby Surround EX, Dolby Headphone, преобразователь Standard или HDCD, предпочитаемый даунмикс и его уровни). Не каждое устройство читает AC3 с VBR.
• Динамический диапазон / компрессия: ползунок, в середине выключен. Влево (1-10) — динамический диапазон: больше контраста. Вправо (1-10) — компрессия: тихие звуки поднимаются (чтобы смотреть фильм ночью). Один для фронтов и тылов, другой для центра. Сабвуфер не трогается. Он в «Visual / Waves» (вкладка Audio), справа от Presence, где его видно на волнах.
• Громкость по каналам, цифровое сглаживание (лишние верха фильмов 80-х и 90-х) и 3-полосный эквалайзер (фронты, центр и тылы).
• Рекомендуемый порядок: сначала Presence и/или Dynamic range, затем остальные эффекты и всегда в конце Volume per channel: так громкость каждого канала настраивается по результату всего остального — точнее и удобнее.
• Каждый «Auto» измеряет дорожку с уже применёнными остальными эффектами и выставляет свои регуляторы; нажатый ещё раз, ничего не трогая, возвращает 0. Эффекты относятся к выбранной дорожке; с Passthrough дорожка снова сжимается своим же кодеком.
• TrueHD и FLAC — без потерь: вместо kbps выбирается 16 или 24 бит.
• Double Bass: копирует бас сабвуфера на колонки и бас колонок на сабвуфер (только на дорожках с сабвуфером), со своим «Auto». Его «Auto» ставит Double Bass (1-3), если колонкам не хватает глубокого баса или сабвуфер слабый; если всё сбалансировано — 0. Частота раздела по умолчанию: 90 Hz.
• Синхронизация: задержка дорожки, «Calculate delay» и «Fix by parts» в сравнении с другой дорожкой (обычно оригинальной), как в Jmg AudioProcesador. «Add track» добавляет, например, дубляж, который у вас есть отдельно.
• «▶ Check synchronization» (в Synchronization): видео в своём окне с дорожкой такой, какой она выйдет (задержка, части и эффекты), с выбранного места или с каждой части, чтобы вы сами видели, совпадают ли губы с голосом. В тот же момент можно послушать и неисправленную дорожку, и опорную. Это то же окно, что в Jmg AudioProcesador.
• Частота кадров (в Synchronization): для дорожки из издания 25 fps в фильме 23,976 (или наоборот), как в Jmg AudioProcesador: меняет её точную скорость, со сменой тона или без, до задержки и частей. Когда вы добавляете дорожку из другого файла, которая на 4 % короче (или длиннее) видео, программа это замечает, выставляет сама и сообщает. Потом рассчитайте задержку.
• Прослушивание: в Audio «Visual / Waves», «▶ Before» или «▶ After» (или щелчок по волнам); ⏸ пауза (ещё нажатие — продолжает) и ⏹ останавливает и возвращает к началу. Через многоканальный выход (для AV-ресивера) или в стерео.
• Звуковые дорожки, как в Jmg AudioProcesador: обработанная дорожка (с эффектами; смена только кодека или битрейта не считается) идёт первой и по умолчанию, с названием «Jmg procesada» (его можно изменить), а оригинал сохраняется после неё. «🚫 Remove original» убирает его (строка становится бледно-красной; ещё раз — возвращается); на необработанной дорожке убирает её из видео. «➕ Add track» берёт дорожку из другого файла, а «➖ Delete track» убирает её из списка (исходный файл не трогается).
• «➕ DTS core» (вкладка Audio): дорожка DTS-HD (Master Audio или High Resolution) содержит обычный DTS для устройств, которые не понимают HD; эта кнопка выводит его и отдельной дорожкой (в MKV), без перекодирования. Ещё раз — убирает.
• В «Information» — правая кнопка мыши: «Copy» и «Select all» (также в журнале). При открытии программы вкладка Video видна полностью; линию посередине можно тянуть, и положение запоминается.
• При нажатии PROCESS окно показывает главное (каждое видео и файл, который получится, и предупреждения); «🔍 See everything» показывает всё (видео, изображение, обрезку, каждую дорожку, субтитры и команды FFmpeg), это можно скопировать кнопкой «📋 Copy all». «Yes» — начать.

SUBTITLES
• Все субтитры видео, с порядком, языком, названием, по умолчанию и forced. «Add external subtitle» добавляет SRT, ASS, VTT или SUP.
• В MKV идут все. В MP4 и MOV текстовые преобразуются, а графические (PGS, DVD) не попадают, с предупреждением.
• Синхронизация выбранных субтитров (вкладка Subtitles): частота кадров и задержка, как у звука, для субтитров издания 25 fps в фильме 23,976 (или наоборот). Применяются при обработке, в том числе к графическим (PGS, DVD) и при обрезке по частям. Когда видео добавляется, субтитры forced становятся субтитрами по умолчанию, а если их нет — первые в списке.

ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ
• Видео · «More options» (вкладка Video): открывается внутри окна, с «Back». Вверху кадр до и после; ниже полоса (щелчок и стрелки ← → = кадр за кадром; с Shift — посекундно), обрезка по частям (несколько частей склеиваются в одно видео), изображение (яркость, контраст, насыщенность, оттенок, резкость и шумоподавление) и чёрные полосы (ищутся сами, когда видео добавляется). «Auto» в Picture измеряет фильм и предлагает значения (ещё нажатие = всё обратно на 0); если результат не нравится, подправьте вручную.
• «Play» открывает окно видео со звуком с места на полосе: оригинал или с настройками, с первой включённой звуковой дорожкой, многоканально или в стерео.
• Звук · «Visual / Waves» (вкладка Audio): волны каждого канала до и после, на выбранном отрезке (первые 5, 10 или 30 минут или весь файл), как в Jmg AudioProcesador. Щелчок по волнам = слушать оттуда. Волны строятся сами при входе и перестраиваются при смене Presence или отрезка; каждый канал рисуется заполненным, с пиком в dBFS, а «Zoom» увеличивает тихие волны. Справа от Presence — динамический диапазон / компрессия: с ними не нужно так сильно поднимать Presence. «Detail» (x1-x8) показывает волны подробнее; двигайтесь колесом или нижней полосой, а при воспроизведении вид следует за красной линией.
• Эффекты складываются: «After» несёт все эффекты дорожки. Presence (голос, атмосфера, эффекты и сабвуфер) со своим «Auto» тоже там. Отмена и повтор по-прежнему внизу.

OUTPUT
• MKV (принимает всё), MP4 (для телефонов и телевизоров), MOV (для ProRes и DNxHR; VP9 идёт в MKV или MP4), AVI (для старых устройств: H.264 со звуком AC3, MP3 или DTS, без субтитров и глав) или WebM (для интернета: VP9 или AV1 со звуком Opus и текстовыми субтитрами в WebVTT). Папка рядом с оригиналом или выбранная вами, текст, добавляемый к имени, и что делать, если файл уже есть. Фильм с диска или из образа ISO сохраняется в папку «Видео» (если не выбрана другая папка).
• Главы, метаданные и вложения (шрифты ASS и обложки) тоже копируются.
• Нижняя полоса показывает ход и оставшееся время. «When done» может закрыть программу, перевести ПК в спящий режим или выключить его.
• Обложка: видео, другое изображение (JPG или PNG) или никакой. Файл называется как видео с добавкой « (Jmg VideoEncoder)» (добавку можно изменить, а «Name of this video» даёт ему другое имя); если такой уже есть, добавляется _1, _2... По окончании открывается папка назначения, если только ПК не будет выключен. «📤 Extraction...», справа от имени, выносит всё, что содержит видео, в папку «(extraction)», каждое в исходном формате и без перекодирования: видео, звуковые дорожки, субтитры, обложки, вложения и главы (у каждого свой флажок). Также из меню значка в трее («📤 Extraction...») и, если программа установлена, правым щелчком по видеофайлу в Проводнике («Extract with Jmg VideoEncoder»; в Windows 11 — в «Show more options»): если программа не открыта, появляется только окно извлечения, и оно закрывается по окончании. С DVD или Blu-ray с видео в приводе правый щелчок по приводу (если программа установлена) и меню значка в трее предлагают «Rip» (основной фильм попадает в список в Passthrough, чтобы выбрать языки и субтитры: получается MKV без потери качества) и «Create ISO image»; в меню трея «Create ISO image» есть и для дисков с данными.
• «🔍 Search online...» (Output → Cover): ищет фильм на TMDB, показывает его постеры, чтобы выбрать один, и ставит его обложкой с именем «Название (Год)». Если рядом с видео есть cover.jpg или folder.jpg (их оставляют многие программы для рипа, Kodi или Plex), а у видео нет обложки, он используется сам. Нужен ваш собственный бесплатный ключ TMDB: в первый раз программа объяснит, как его получить (аккаунт на themoviedb.org → Настройки → API). Без подключения поиск просто не выполняется.

ПОМНИТЕ
• «↶ Undo» и «↷ Redo» (внизу; также Ctrl+Z и Ctrl+Y): отменяют и повторяют по одному последние 5 действий (настройки, добавление или удаление видео...). «Reset» возвращает автоматические настройки открытой вкладки (Video, Audio, Subtitles или Output) активного видео; с «All» — всё с нуля: список видео, их информация, настройки и Output по умолчанию (↶ возвращает обратно). Пока открыто окно вроде «Combine videos», «Check synchronization» или дополнительных настроек, кнопки главного окна не работают: у этих окон свои ↶ ↷.
• В свёрнутом виде программа остаётся значком у часов (в области уведомлений), который показывает ход обработки: левый щелчок = окно возвращается; правый щелчок = меню (отменить обработку, что делать по окончании — ничего, выйти или выключить ПК —, открыть папку по окончании, выход). Во вкладке Output это можно отключить, чтобы сворачивать на панель задач как обычно. Если задержать мышь над кнопкой, полем или ползунком, появляется описание, которое само исчезает через несколько секунд.
• Дополнительные настройки («⚙» рядом с кодеком, в Video и у каждой дорожки Audio): самое важное для каждого кодека, для тех, кто хочет тонкой настройки. Видео: tune (film, animation, grain...), профиль и уровень, ключевой кадр каждые X секунд, B-кадры и опорные кадры, адаптивное квантование, синтетическое зерно плёнки в AV1, два прохода и AQ у NVIDIA, максимальное качество и предварительный анализ у AMD, профиль ProRes (от Proxy до 4444 XQ) и профиль DNxHR (от LB до 444). Звук: служебная информация AC3 и E-AC3 (уровень диалогов, Dolby Surround EX, наушники, HDCD, даунмикс) и срез верхов, VBR у MP3 и Opus, сжатие FLAC. Всё, что не трогали, остаётся автоматическим; у каждого видео и каждой дорожки свои. В списке дорожек «⚙» = с дополнительными настройками. У AC3 и E-AC3 есть также тип помещения (большое или маленькое) с уровнем сведения; у DTS — предсказание ADPCM. DTS от FFmpeg всегда с постоянным битрейтом: 768 или 1536 kbps, стандартные (при меньшем плееры выдают только шум). AC3 (Aften и FFmpeg): в 5.1 от 224 до 640 kbps; в стерео от 96 до 640 (по умолчанию 192). E-AC3: любой битрейт, вводится вручную, от 192 kbps в 5.1 (в стерео от 64; по умолчанию 192). Dolby TrueHD идёт после форматов Dolby.
• Субтитры · «Burn into the picture»: выбранные субтитры впечатываются в видео; они видны на любом устройстве, но убрать их уже нельзя. Только одни, и видео нужно перекодировать (если оно было в Passthrough, станет H.265). Текстовые (SRT, ASS) рисуются на итоговом изображении; графические (PGS, DVD) — на оригинале (с «Black bars» → «Remove them» то, что было на полосах, обрезается).
• «Edit/Log» хранит всё, что происходит; «Show the FFmpeg command» показывает точную команду активного видео.
• При запуске, раз в день, программа проверяет на GitHub, нет ли новой версии, и спрашивает, открыть ли страницу загрузки. Сама она ничего не скачивает и не устанавливает.
• Раз в 45 дней при открытии программы на 5 секунд появляется сообщение о том, что проект можно поддержать; оно закрывается само, а если нажать ссылку поддержки (там или в «About»), больше не появляется.
• «⏸ Pause» (рядом с PROCESS) останавливает обработку, ничего не теряя, а «▶ Resume» продолжает с того же места. «When done» можно менять во время обработки.
• Blu-ray: язык каждой звуковой дорожки и каждых субтитров читается из списка воспроизведения диска (в файлах .m2ts его нет).
• Пока программа работает (обработка, объединение, рип, извлечение, создание ISO...), ПК не уходит в спящий режим; экран при этом может гаснуть.
• «➖ Delete subtitle» (вкладка Subtitles) убирает выбранные субтитры, из видео или добавленные: их не будет в обработанном файле, а оригинал не трогается.
• «Combine videos» (рядом с «Add to queue») склеивает части нескольких видео в одно, с размером первого; «Match color and brightness» измеряет каждую часть и подгоняет её к первой. По изображению и кнопками «Start here» / «End here» каждая часть отмечается не вслепую. Переносит отмеченные звуковые дорожки каждого видео (или выбранную в «Audio of this part») и его отмеченные текстовые субтитры (графические склеить нельзя). Результат попадает в список видео, как видео с частями, когда готов. Видео каждой части выбирается в самом окне («Video:» и «➕ Add»). Стрелки ← → двигают на один кадр за нажатие, а при удержании — всё быстрее. «Set» применяет введённые начало и конец к выбранной части; «↺ Reset» очищает список частей; ↶ ↷ (или Ctrl+Z / Ctrl+Y) отменяют и повторяют.
• «🎵 To AudioProcesador» (вверху, после «Create ISO»): отправляет выбранные в списке файлы (или все) в Jmg AudioProcesador. Если он открыт, они попадают в его список; если нет — он открывается с ними. Если его не найти, программа один раз попросит указать, где он. После этого эта программа закрывается (обе сразу открытыми не остаются).
• Любой ползунок двигается стрелками клавиатуры (сначала щёлкните по ползунку). Вкладки сами принимают нужную высоту.

FFMPEG И ЛИЦЕНЗИЯ
Использует FFmpeg (ffmpeg.org, сборка BtbN) по лицензии GNU GPL v3.
Jmg VideoEncoder — свободная программа под лицензией GNU GPL v3.
Контакт: jmgsoftwaremultimedia@gmail.com
Поддержать проект: https://www.paypal.com/paypalme/JmgSoftware
На создание Jmg SuiteMultimedia (этой программы и Jmg AudioProcesador 5.1) ушла огромная работа: около 45 дней, с проверками на настоящих фильмах. Создано с помощью Claude, искусственного интеллекта компании Anthropic.
"""
AYUDA["hi"]="""JMG VIDEOENCODER · सहायता

इस्तेमाल कैसे करें
1. «Select», «Add» से या सूची पर खींचकर वीडियो जोड़ें (MKV, MP4, AVI, MOV, M2TS...)। DVD या Blu-ray के लिए «📀 DVD/BD» दबाएँ और वह फ़ोल्डर चुनें जिसमें VIDEO_TS या BDMV हो (मुख्य फ़िल्म ली जाती है)। सिर्फ़ बिना कॉपी-सुरक्षा वाली या पहले से डिक्रिप्ट की गई डिस्कें: FFmpeg सुरक्षित डिस्कें नहीं पढ़ सकता (DVD पर CSS, Blu-ray पर AACS) और प्रोग्राम वह सुरक्षा नहीं हटाता; अगर डिस्क सुरक्षित है, तो वह चेतावनी देता है और उसे नहीं जोड़ता। बिना सुरक्षा वाली या पहले से डिक्रिप्ट की गई कॉपी इस्तेमाल करें, अगर आपके देश का कानून इसकी अनुमति देता है। सीधे डिस्क से रिप करना धीमा और अस्थिर है: बेहतर है पहले एक ISO इमेज बनाएँ («💿 Create ISO...») और उसे खोलें। «📀 DVD/BD» डिस्क इमेज (.iso) भी खोलता है: Windows उसे माउंट करता है और प्रोग्राम बंद होने पर अनमाउंट हो जाती है (Linux पर उसे ख़ुद माउंट करें और उसका फ़ोल्डर चुनें)। «💿 Create ISO...» DVD या Blu-ray फ़ोल्डर (VIDEO_TS या BDMV) की .iso इमेज बनाता है या ड्राइव की डिस्क को जैसी है वैसी कॉपी करता है, और फिर «📀 Open in the list» उसे जोड़ता है। इमेज का नाम डिस्क जैसा होता है (Blu-ray का शीर्षक या DVD, BD या CD का लेबल)। सुरक्षित डिस्क के साथ यह चेतावनी देता है और, अगर आप चाहें, फिर भी एक हूबहू कॉपी बनाता है, उतनी ही सुरक्षित (वह यहाँ नहीं खुलती)। «🎬 Only the movie» मुख्य फ़िल्म को Passthrough में खोलता है ताकि आप भाषाएँ और सबटाइटल चुनकर सिर्फ़ उन्हीं वाली MKV पाएँ, बिना गुणवत्ता खोए। अगर ड्राइव में डिस्क है, तो विंडो उसी से शुरू होती है; कॉपी करना एक साथ पढ़ता और लिखता है और बचा हुआ समय दिखाता है, और «Shut down the PC when done» से इसे रात भर चलने दे सकते हैं (कुछ ड्राइव फ़िल्म वाली डिस्कों के साथ धीमी होती हैं: सीमा ड्राइव की ही है)।
2. किसी वीडियो पर क्लिक करें: उसकी सारी जानकारी दाईं ओर दिखती है। अगर कई चुनें, तो हर एक का सारांश मिलता है।
3. «Add to queue» दबाएँ (या डबल-क्लिक करें): वीडियो अपने-आप वाली सेटिंग्स के साथ टैब में जाता है और ✔ से चिह्नित होता है। सिर्फ़ जोड़े गए वीडियो ही प्रोसेस होते हैं।
4. चाहें तो टैब देखें और PROCESS दबाएँ। आपकी मूल फ़ाइलें कभी नहीं बदलतीं।

VIDEO (वीडियो)
• कोडेक: H.264 (AVC), H.265 (HEVC), H.266 (VVC), AV1, VP9 (वेब के लिए) और, एडिटिंग के लिए, Apple ProRes 422 LT और Avid DNxHR HQ। Passthrough वीडियो को बिना छुए कॉपी करता है। H.266 (VVC) सबसे ज़्यादा कंप्रेस करता है, पर सबसे धीमा भी है, और सिर्फ़ प्रोसेसर से: «Fast» में वीडियो की अवधि का लगभग 2 गुना समय लगता है (डेढ़ घंटे की फ़िल्म, 16 थ्रेड वाले पीसी पर लगभग 3 घंटे); «Medium» में लगभग 5 गुना, और «Slow» में लगभग 20 गुना। ये समय केवल अनुमान हैं: ये हर कंप्यूटर के प्रोसेसर पर बहुत निर्भर करते हैं। जल्दी हो तो H.265 या AV1 बेहतर है।
• किससे एन्कोड करें: प्रोसेसर या NVIDIA या AMD ग्राफ़िक्स कार्ड (शुरू होते समय प्रोग्राम जाँचता है कि आपके पीसी पर कौन से काम करते हैं)। H.266 और ProRes, सिर्फ़ प्रोसेसर से। टैब में चुना गया इंजन अपना रंग दिखाता है (NVIDIA हरा, AMD लाल); लगा हुआ «Auto» शब्द हरे रंग में दिखाता है, और अगर आप उसकी लगाई चीज़ हाथ से बदलें या «Reset» दबाएँ तो बुझ जाता है।
• वीडियो का «Auto» फ़िल्म को मापता है: बैकग्राउंड में कुछ छोटे हिस्सों को तय क्वालिटी पर एन्कोड करके वह बिटरेट लगाता है जो अच्छी तस्वीर के लिए चाहिए (शांत फ़िल्म को कम, ज़्यादा ग्रेन या एक्शन वाली को ज़्यादा)। इसमें कुछ सेकंड लगते हैं; तब तक उसके रिज़ॉल्यूशन वाला बिटरेट रहता है। अगर आप ख़ुद बिटरेट बदलें, तो वह उसे नहीं छूता।
• स्थिर गुणवत्ता (कम = बेहतर) या बिटरेट (तय आकार)। बिटरेट के साथ «Two passes» kbps को बेहतर बाँटता है; ग्राफ़िक्स कार्ड अपना दो-पास तरीका इस्तेमाल करते हैं। ProRes में बिटरेट नहीं होता।
• «Auto» वीडियो के हिसाब से कोडेक, बिटरेट और रिज़ॉल्यूशन चुनता है; अगर वह पहले से अच्छी तरह कंप्रेस है, तो Passthrough छोड़ता है। बिना कुछ छुए फिर से दबाने पर Passthrough पर लौटता है। यह एक शुरुआत है: पसंद न आए तो हाथ से ठीक करें।
• रिज़ॉल्यूशन: मूल जितना या उससे छोटा। डीइंटरलेस: Auto इसे तभी करता है जब वीडियो इंटरलेस्ड हो (DVD, TV)।
• रंग: HDR फ़िल्में (HDR10, HLG) 10 बिट में अपना HDR रखती हैं; «SDR» उन्हें सामान्य स्क्रीनों के लिए बदलता है। कैमरे के log वीडियो के लिए उसका LUT (.cube) चुनें। Dolby Vision: HDR10 परत रखी जाती है।
• ग्राफ़िक्स कार्ड के साथ «Two passes» उसकी अपनी व्यवस्था इस्तेमाल करता है: हर फ़्रेम को एन्कोड करने से पहले उसका विश्लेषण करता है। रंग तभी चालू होता है जब ज़रूरत हो: HDR के साथ, या log वीडियो के साथ (अगर पहचाना न जाए, तो बॉक्स पर टिक करें)।

AUDIO (ऑडियो)
• वीडियो के सभी ट्रैक: आप क्रम (⬆ ⬇), भाषा, शीर्षक, डिफ़ॉल्ट ट्रैक बदल सकते हैं और अनचाहे हटा सकते हैं (डबल-क्लिक)।
• कोडेक: Passthrough (बिना छुए), AC3, E-AC3, DTS, AAC, MP3 (सिर्फ़ स्टीरियो: 5.1 को डाउनमिक्स किया जाता है), FLAC और Opus। «Aften Dolby Digital» (डिफ़ॉल्ट, कोडेक सूची में) AC3 को Aften से बनाता है, जो ज़्यादा डायनामिक रेंज वाली फ़िल्मों में बेहतर रेंज देता है; «AC3 · FFmpeg», FFmpeg से। इसकी सेटिंग्स दूसरे फ़ॉर्मैटों की तरह «⚙ Aften...» से (डिफ़ॉल्ट: block switching और स्थिर पूरी बैंडविड्थ): CBR या VBR, बैंडविड्थ, सटीकता, फ़िल्टर, डायनामिक रेंज (DRC और संवाद स्तर) और एम्प्लीफ़ायर के लिए जानकारी (Dolby Surround EX, Dolby Headphone, Standard या HDCD A/D कनवर्टर, पसंदीदा डाउनमिक्स और उसके स्तर)। हर डिवाइस VBR वाला AC3 नहीं पढ़ता।
• डायनामिक रेंज / कंप्रेशन: स्लाइडर, बीच में बंद। बाईं ओर (1-10) डायनामिक रेंज: ज़्यादा कंट्रास्ट। दाईं ओर (1-10) कंप्रेशन: धीमी आवाज़ें ऊपर जाती हैं (रात में फ़िल्म देखने के लिए)। एक फ़्रंट और सराउंड के लिए, दूसरा सेंटर के लिए। सबवूफ़र को नहीं छूता। यह «Visual / Waves» (Audio टैब) में Presence के दाईं ओर है, जहाँ आप इसे तरंगों पर देखते हैं।
• हर चैनल का वॉल्यूम, डिजिटल स्मूदिंग (80 और 90 के दशक की फ़िल्मों का ज़्यादा ट्रेबल) और 3-बैंड इक्वलाइज़र (फ़्रंट, सेंटर और सराउंड)।
• सुझाया गया क्रम: पहले Presence और/या Dynamic range, फिर बाकी इफ़ेक्ट, और हमेशा आख़िर में Volume per channel: इस तरह हर चैनल का वॉल्यूम बाकी सबके नतीजे पर सेट होता है, ज़्यादा बारीकी से।
• हर «Auto» बाकी इफ़ेक्ट लागू करके ट्रैक को मापता है और अपने कंट्रोल सेट करता है; बिना कुछ छुए फिर से दबाने पर 0 पर लौटता है। इफ़ेक्ट चुने हुए ट्रैक के होते हैं; Passthrough के साथ ट्रैक फिर से अपने ही कोडेक से कंप्रेस होता है।
• TrueHD और FLAC लॉसलेस हैं: kbps की जगह आप 16 या 24 बिट चुनते हैं।
• Double Bass: सबवूफ़र का बेस स्पीकरों पर और स्पीकरों का बेस सबवूफ़र पर कॉपी करता है (सिर्फ़ सबवूफ़र वाले ट्रैकों पर), अपने «Auto» के साथ। इसका «Auto» Double Bass (1-3) लगाता है अगर स्पीकरों में गहरा बेस कम हो या सबवूफ़र कमज़ोर हो; संतुलित हों तो 0। डिफ़ॉल्ट कट: 90 Hz।
• सिंक्रोनाइज़ेशन: ट्रैक की देरी, «Calculate delay» और «Fix by parts» किसी दूसरे ट्रैक (आमतौर पर मूल भाषा वाले) से तुलना करके, Jmg AudioProcesador की तरह। «Add track» जोड़ता है, जैसे, कोई डबिंग जो आपके पास अलग से है।
• «▶ Check synchronization» (Synchronization में): वीडियो अपनी विंडो में, ट्रैक वैसा ही जैसा वह निकलेगा (देरी, टुकड़े और इफ़ेक्ट), आपके चुने बिंदु से या हर टुकड़े से, ताकि आप अपनी आँखों से देख सकें कि होंठ आवाज़ से मिलते हैं या नहीं। उसी पल आप बिना सुधारा ट्रैक या संदर्भ ट्रैक भी सुन सकते हैं। यह वही विंडो है जो Jmg AudioProcesador में है।
• फ़्रेम रेट (Synchronization में): 23.976 वाली फ़िल्म में 25 fps संस्करण के ट्रैक के लिए (या उल्टा), Jmg AudioProcesador की तरह: उसकी सटीक गति बदलता है, पिच बदलकर या बिना, देरी और टुकड़ों से पहले। जब आप किसी दूसरी फ़ाइल से ऐसा ट्रैक जोड़ते हैं जो वीडियो से 4 % छोटा (या लंबा) हो, तो प्रोग्राम उसे पहचानता है, अपने-आप सेट करता है और बताता है। फिर देरी की गणना करें।
• सुनना: Audio के «Visual / Waves» में «▶ Before» या «▶ After» (या तरंगों पर क्लिक करें); ⏸ रोकें (फिर दबाने पर आगे बढ़ता है) और ⏹ रोककर शुरुआत पर लौटाता है। मल्टीचैनल से (AV रिसीवर के लिए) या स्टीरियो में।
• ऑडियो ट्रैक, Jmg AudioProcesador की तरह: प्रोसेस किया गया ट्रैक (इफ़ेक्ट के साथ; सिर्फ़ कोडेक या बिटरेट बदलना नहीं गिना जाता) पहले और डिफ़ॉल्ट के रूप में आता है, शीर्षक «Jmg procesada» के साथ (बदला जा सकता है), और मूल उसके बाद रखा जाता है। «🚫 Remove original» उसे हटाता है (पंक्ति हल्की लाल हो जाती है; फिर दबाने पर लौट आता है); बिना प्रोसेस वाले ट्रैक पर, उसे वीडियो से हटा देता है। «➕ Add track» किसी दूसरी फ़ाइल से ट्रैक लाता है और «➖ Delete track» उसे सूची से हटाता है (मूल फ़ाइल को नहीं छूता)।
• «➕ DTS core» (Audio टैब): DTS-HD ट्रैक (Master Audio या High Resolution) के अंदर उन डिवाइसों के लिए एक सामान्य DTS होता है जो HD नहीं समझते; यह बटन उसे अलग ट्रैक के रूप में भी निकालता है (MKV में), बिना दोबारा एन्कोड किए। फिर दबाने पर: हट जाता है।
• «Information» में माउस का दायाँ बटन: «Copy» और «Select all» (लॉग में भी)। प्रोग्राम खुलने पर Video टैब पूरा दिखता है; बीच की रेखा खींची जा सकती है और याद रखी जाती है।
• PROCESS दबाने पर एक विंडो ज़रूरी बातें दिखाती है (हर वीडियो और जो फ़ाइल निकलेगी, और चेतावनियाँ); «🔍 See everything» सब कुछ दिखाता है (वीडियो, तस्वीर, ट्रिमिंग, हर ट्रैक, सबटाइटल और FFmpeg कमांड) और इसे «📋 Copy all» से कॉपी किया जा सकता है। शुरू करने के लिए «Yes»।

SUBTITLES (सबटाइटल)
• वीडियो के सभी सबटाइटल, क्रम, भाषा, शीर्षक, डिफ़ॉल्ट और forced के साथ। «Add external subtitle» एक SRT, ASS, VTT या SUP जोड़ता है।
• MKV में सभी जाते हैं। MP4 और MOV में टेक्स्ट वाले बदले जाते हैं और इमेज वाले (PGS, DVD) छोड़ दिए जाते हैं, एक सूचना के साथ।
• चुने हुए सबटाइटल का सिंक्रोनाइज़ेशन (Subtitles टैब): फ़्रेम रेट और देरी, ऑडियो की तरह, 23.976 वाली फ़िल्म में 25 fps संस्करण के सबटाइटलों के लिए (या उल्टा)। ये प्रोसेस करते समय लागू होते हैं, इमेज वालों (PGS, DVD) पर भी और टुकड़ों में ट्रिम करते समय भी। वीडियो जोड़ने पर forced सबटाइटल डिफ़ॉल्ट बनता है, और अगर कोई न हो, तो सूची का पहला।

एडवांस्ड विकल्प
• वीडियो · «More options» (Video टैब): विंडो के अंदर ही खुलता है, «Back» के साथ। ऊपर पहले और बाद का फ़्रेम; नीचे पट्टी (क्लिक और ← → तीर = फ़्रेम-दर-फ़्रेम; Shift के साथ, सेकंड-दर-सेकंड), टुकड़ों में ट्रिमिंग (कई टुकड़े एक वीडियो में जुड़ जाते हैं), तस्वीर (चमक, कंट्रास्ट, सैचुरेशन, रंगत, शार्पनेस और नॉइज़ हटाना) और काली पट्टियाँ (वीडियो जोड़ते ही अपने-आप ढूँढी जाती हैं)। Picture में «Auto» फ़िल्म को मापकर मान सुझाता है (फिर दबाएँ = सब वापस 0 पर); अगर नतीजा पसंद न आए, तो हाथ से सुधारें।
• «Play» पट्टी के बिंदु से आवाज़ के साथ वीडियो विंडो खोलता है: मूल या सेटिंग्स के साथ, पहले शामिल ऑडियो ट्रैक के साथ, मल्टीचैनल या स्टीरियो में।
• ऑडियो · «Visual / Waves» (Audio टैब): हर चैनल की पहले और बाद की तरंगें, आपके चुने हिस्से के लिए (पहले 5, 10 या 30 मिनट या पूरी फ़ाइल), Jmg AudioProcesador की तरह। तरंगों पर क्लिक = वहीं से सुनें। अंदर आते ही तरंगें अपने-आप बनती हैं और Presence या हिस्सा बदलने पर फिर से बनती हैं; हर चैनल भरा हुआ बनता है, dBFS में अपने पीक के साथ, और «Zoom» धीमी तरंगों को बड़ा करता है। Presence के दाईं ओर, डायनामिक रेंज / कंप्रेशन: इसके साथ Presence को इतना बढ़ाने की ज़रूरत नहीं। «Detail» (x1-x8) तरंगों को ज़्यादा बारीकी से दिखाता है; पहिये या नीचे की पट्टी से चलें, और चलते समय दृश्य लाल रेखा के साथ चलता है।
• इफ़ेक्ट जुड़ते जाते हैं: «After» में ट्रैक के सभी इफ़ेक्ट होते हैं। Presence (आवाज़, माहौल, इफ़ेक्ट और सबवूफ़र) अपने «Auto» के साथ भी वहीं है। Undo और Redo अब भी नीचे हैं।

OUTPUT
• MKV (सब कुछ लेता है), MP4 (फ़ोन और टीवी के लिए), MOV (ProRes और DNxHR वाला; VP9, MKV या MP4 में जाता है), AVI (पुराने डिवाइसों के लिए: AC3, MP3 या DTS ऑडियो के साथ H.264, बिना सबटाइटल या चैप्टर) या WebM (वेब के लिए: Opus ऑडियो और WebVTT टेक्स्ट सबटाइटल के साथ VP9 या AV1)। मूल के पास वाला फ़ोल्डर या आपका चुना हुआ, नाम में जोड़ा जाने वाला टेक्स्ट, और अगर फ़ाइल पहले से हो तो क्या करें। डिस्क या ISO इमेज की फ़िल्म Videos फ़ोल्डर में जाती है (जब तक आप कोई दूसरा फ़ोल्डर न चुनें)।
• चैप्टर, मेटाडेटा और अटैचमेंट (ASS फ़ॉन्ट और कवर) भी कॉपी होते हैं।
• नीचे की पट्टी प्रगति और बचा हुआ समय दिखाती है। «When done» प्रोग्राम से बाहर निकल सकता है, पीसी को स्लीप में डाल सकता है या बंद कर सकता है।
• कवर: वीडियो वाला, कोई दूसरी इमेज (JPG या PNG) या कोई नहीं। फ़ाइल का नाम वीडियो जैसा होता है, उसमें « (Jmg VideoEncoder)» जोड़ा जाता है (यह जोड़ बदला जा सकता है, और «Name of this video» उसे दूसरा नाम देता है); अगर पहले से हो, तो _1, _2... जुड़ता है। ख़त्म होने पर डेस्टिनेशन फ़ोल्डर खुलता है, अगर पीसी बंद न होने वाला हो। «📤 Extraction...», नाम के दाईं ओर, वीडियो में जो कुछ है उसे एक «(extraction)» फ़ोल्डर में निकालता है, हर चीज़ अपने मूल फ़ॉर्मैट में और बिना फिर से एन्कोड किए: वीडियो, ऑडियो ट्रैक, सबटाइटल, कवर, अटैचमेंट और चैप्टर (हर चीज़ का अपना टिक बॉक्स)। ट्रे आइकन के मेनू से भी («📤 Extraction...») और, प्रोग्राम इंस्टॉल होने पर, Explorer में किसी वीडियो फ़ाइल पर दायाँ क्लिक करके («Extract with Jmg VideoEncoder»; Windows 11 में «Show more options» के अंदर): अगर प्रोग्राम खुला नहीं है, तो सिर्फ़ Extraction विंडो आती है और ख़त्म होने पर बंद हो जाती है। ड्राइव में वीडियो वाली DVD या Blu-ray होने पर, ड्राइव पर दायाँ क्लिक (प्रोग्राम इंस्टॉल होने पर) और ट्रे आइकन का मेनू «Rip» (मुख्य फ़िल्म भाषाएँ और सबटाइटल चुनने के लिए Passthrough में सूची में जाती है: बिना गुणवत्ता खोए MKV मिलती है) और «Create ISO image» देते हैं; ट्रे मेनू में «Create ISO image» डेटा डिस्कों के लिए भी है।
• «🔍 Search online...» (Output → Cover): TMDB पर फ़िल्म खोजता है, उसके पोस्टर दिखाता है ताकि आप एक चुनें, और उसे «शीर्षक (वर्ष)» नाम के साथ कवर बना देता है। अगर वीडियो के पास cover.jpg या folder.jpg हो (जो कई रिपिंग प्रोग्राम, Kodi या Plex बनाते हैं) और वीडियो में कवर न हो, तो वह अपने-आप इस्तेमाल होता है। इसके लिए आपकी अपनी मुफ़्त TMDB key चाहिए: पहली बार प्रोग्राम बताता है कि इसे कैसे पाएँ (themoviedb.org पर खाता → Settings → API)। कनेक्शन न हो तो बस खोज नहीं होती।

ध्यान रखें
• «↶ Undo» और «↷ Redo» (नीचे; Ctrl+Z और Ctrl+Y से भी): आख़िरी 5 कार्यों को एक-एक करके वापस करते और दोहराते हैं (सेटिंग्स, वीडियो जोड़ना या हटाना...)। «Reset» सक्रिय वीडियो के खुले टैब (Video, Audio, Subtitles या Output) की अपने-आप वाली सेटिंग्स वापस लगाता है; «All» के साथ, सब कुछ शून्य से: वीडियो सूची, उनकी जानकारी, उनकी सेटिंग्स और डिफ़ॉल्ट Output (↶ उसे वापस लाता है)। जब «Combine videos», «Check synchronization» या एडवांस्ड विकल्प जैसी कोई विंडो खुली हो, तो मुख्य विंडो के बटन काम नहीं करते: उन विंडो के अपने ↶ ↷ हैं।
• मिनिमाइज़ करने पर प्रोग्राम घड़ी के पास (सिस्टम ट्रे में) एक आइकन बनकर रहता है, जो प्रोसेस की प्रगति दिखाता है: बायाँ क्लिक = विंडो वापस आती है; दायाँ क्लिक = मेनू (प्रोसेस रद्द करें, ख़त्म होने पर क्या करें —कुछ नहीं, बाहर निकलें या पीसी बंद करें—, ख़त्म होने पर फ़ोल्डर खोलें, बाहर निकलें)। Output में इसे बंद किया जा सकता है, ताकि हमेशा की तरह टास्कबार पर मिनिमाइज़ हो। किसी बटन, बॉक्स या स्लाइडर पर माउस रोकने से उसका विवरण दिखता है, जो कुछ सेकंड में अपने-आप चला जाता है।
• एडवांस्ड विकल्प (कोडेक के पास «⚙», Video में और हर Audio ट्रैक पर): हर कोडेक की सबसे ज़रूरी सेटिंग्स, बारीक ट्यूनिंग चाहने वालों के लिए। वीडियो: tune (film, animation, grain...), प्रोफ़ाइल और लेवल, हर X सेकंड पर एक कीफ़्रेम, B-फ़्रेम और रेफ़रेंस फ़्रेम, अनुकूली क्वांटाइज़ेशन, AV1 में कृत्रिम फ़िल्म ग्रेन, NVIDIA के दो पास और AQ, AMD की सबसे ऊँची गुणवत्ता और पूर्व-विश्लेषण, ProRes प्रोफ़ाइल (Proxy से 4444 XQ) और DNxHR प्रोफ़ाइल (LB से 444)। ऑडियो: AC3 और E-AC3 की बिटस्ट्रीम जानकारी (संवाद स्तर, Dolby Surround EX, हेडफ़ोन, HDCD, डाउनमिक्स) और ट्रेबल कट, MP3 और Opus का VBR, FLAC कंप्रेशन। जो न छुआ जाए वह अपने-आप रहता है; हर वीडियो और हर ट्रैक की अपनी सेटिंग्स। ट्रैक सूची में «⚙» = एडवांस्ड विकल्पों के साथ। AC3 और E-AC3 में कमरे का प्रकार (बड़ा या छोटा) और उसका मिक्सिंग स्तर भी है; DTS में ADPCM प्रेडिक्शन। FFmpeg का DTS हमेशा स्थिर बिटरेट पर होता है: 768 या 1536 kbps, मानक वाले (कम पर प्लेयर सिर्फ़ शोर देते हैं)। AC3 (Aften और FFmpeg): 5.1 में 224 से 640 kbps; स्टीरियो में 96 से 640 (डिफ़ॉल्ट 192)। E-AC3: कोई भी बिटरेट, हाथ से लिखा, 5.1 में 192 kbps से (स्टीरियो में 64 से; डिफ़ॉल्ट 192)। Dolby TrueHD, Dolby वालों के बाद आता है।
• सबटाइटल · «Burn into the picture»: चुना हुआ सबटाइटल वीडियो में छाप दिया जाता है; यह किसी भी डिवाइस पर दिखता है, पर फिर हटाया नहीं जा सकता। सिर्फ़ एक, और वीडियो को फिर से एन्कोड करना होगा (अगर वह Passthrough में था, तो H.265 बन जाता है)। टेक्स्ट वाले (SRT, ASS) अंतिम तस्वीर पर बनते हैं; इमेज वाले (PGS, DVD), मूल पर («Black bars» → «Remove them» के साथ, पट्टियों पर जो हो वह कट जाता है)।
• «Edit/Log» जो कुछ होता है सब रखता है; «Show the FFmpeg command» सक्रिय वीडियो का सटीक कमांड दिखाता है।
• शुरू होने पर, दिन में एक बार, प्रोग्राम GitHub पर देखता है कि कोई नया संस्करण है या नहीं और पूछता है कि क्या आप डाउनलोड पेज खोलना चाहते हैं। यह अपने-आप कुछ डाउनलोड या इंस्टॉल नहीं करता।
• हर 45 दिन में, प्रोग्राम खुलने पर, 5 सेकंड के लिए एक संदेश दिखता है जो याद दिलाता है कि आप प्रोजेक्ट का समर्थन कर सकते हैं; यह अपने-आप बंद हो जाता है और, अगर आप समर्थन वाले लिंक पर क्लिक करें (वहाँ या «About» में), तो फिर नहीं आता।
• «⏸ Pause» (PROCESS के पास) बिना कुछ खोए प्रोसेस रोकता है और «▶ Resume» वहीं से आगे बढ़ाता है जहाँ वह था। «When done» प्रोसेस के दौरान बदला जा सकता है।
• Blu-ray: हर ऑडियो ट्रैक और हर सबटाइटल की भाषा डिस्क की प्लेलिस्ट से पढ़ी जाती है (.m2ts फ़ाइलों में यह नहीं होती)।
• जब प्रोग्राम काम कर रहा हो (प्रोसेस, जोड़ना, रिप, निकालना, ISO बनाना...), तब पीसी स्लीप मोड में नहीं जाता; स्क्रीन फिर भी बंद हो सकती है।
• «➖ Delete subtitle» (Subtitles टैब) चुना हुआ सबटाइटल हटाता है, वीडियो वाला या जोड़ा हुआ: वह प्रोसेस की गई फ़ाइल में नहीं होता और मूल को नहीं छुआ जाता।
• «Combine videos» («Add to queue» के पास) कई वीडियो के टुकड़ों को एक में जोड़ता है, पहले वाले के आकार के साथ; «Match color and brightness» हर टुकड़े को मापकर उसे पहले वाले जैसा करता है। तस्वीर और «Start here» / «End here» से हर टुकड़ा बिना अंदाज़े के चिह्नित होता है। यह हर वीडियो के चिह्नित ऑडियो ट्रैक (या «Audio of this part» में चुना गया) और उसके चिह्नित टेक्स्ट सबटाइटल ले जाता है (इमेज वाले जोड़े नहीं जा सकते)। तैयार होने पर नतीजा वीडियो सूची में जाता है, टुकड़ों वाले वीडियो की तरह। हर टुकड़े का वीडियो उसी विंडो में चुना जाता है («Video:» और «➕ Add»)। ← → तीर हर दबाव पर एक फ़्रेम चलाते हैं और, दबाए रखने पर, और तेज़। «Set» लिखी हुई शुरुआत और अंत चुने हुए टुकड़े पर लागू करता है; «↺ Reset» टुकड़ों की सूची ख़ाली करता है; ↶ ↷ (या Ctrl+Z / Ctrl+Y) वापस करते और दोहराते हैं।
• «🎵 To AudioProcesador» (ऊपर, «Create ISO» के बाद): सूची की चुनी हुई फ़ाइलें (या सभी) Jmg AudioProcesador को भेजता है। अगर वह खुला है, तो वे उसकी सूची में जाती हैं; अगर नहीं, तो वह उनके साथ खुलता है। अगर वह न मिले, तो एक बार उसे ढूँढने को कहता है। फिर यह प्रोग्राम बंद हो जाता है (दोनों एक साथ खुले नहीं रहते)।
• हर स्लाइडर कीबोर्ड के तीरों से चलता है (पहले स्लाइडर पर क्लिक करें)। टैब अपने-आप ज़रूरी ऊँचाई ले लेते हैं।

FFMPEG और लाइसेंस
GNU GPL v3 लाइसेंस के तहत FFmpeg (ffmpeg.org, BtbN बिल्ड) का उपयोग करता है।
Jmg VideoEncoder GNU GPL v3 लाइसेंस के तहत मुफ़्त सॉफ़्टवेयर है।
संपर्क: jmgsoftwaremultimedia@gmail.com
प्रोजेक्ट का समर्थन करें: https://www.paypal.com/paypalme/JmgSoftware
Jmg SuiteMultimedia (यह प्रोग्राम और Jmg AudioProcesador 5.1) को बनाने में बहुत बड़ी मेहनत लगी है: लगभग 45 दिन, असली फ़िल्मों पर परीक्षण के साथ। Anthropic की AI, Claude की मदद से विकसित।
"""

if __name__=="__main__":
    try:
        orden_=(sys.argv[1][2:],os.path.abspath(sys.argv[2])) if (len(sys.argv)>2 and sys.argv[1] in ("--extraer","--ripear","--imagen")) else None   # (JMG, 15/16-11) botón derecho del Explorador
        ext_=orden_[1] if (orden_ and orden_[0]=="extraer") else None
        if orden_ and _enviar_orden(*orden_):sys.exit(0)   # ya hay uno abierto: que lo haga él
        archivos=[] if orden_ else [os.path.abspath(a) for a in sys.argv[1:] if os.path.exists(a)]
        srv=_instancia_unica(archivos)
        if srv is None:
            if orden_:_enviar_orden(*orden_)
            sys.exit(0)
        root=TkinterDnD.Tk();root.withdraw()
        cerrar_inicio=None if (ext_ or (orden_ and orden_[0]=="imagen")) else _inicio_abrir(root,"Jmg VideoEncoder",f"v{VERSION_PROG} · Jmg SuiteMultimedia {SUITE_VER}")   # (JMG, 13-11)
        app=VideoEncoderGUI(root)
        if srv:threading.Thread(target=_escuchar_instancias,args=(srv,app),daemon=True).start()
        if ext_:   # solo la ventana de Extracción; al cerrarla (y la cola), el programa se cierra; si se abre el programa entero, se queda
            app._ext_solo=True;root.after(200,lambda:app._ext_recibir(ext_))
        elif orden_ and orden_[0]=="imagen":   # (JMG, 16-11) igual con Crear imagen ISO
            app._isoc_solo=True;root.after(200,lambda:app._disco_imagen(orden_[1]))
        else:
            def _ver_ya():
                root.deiconify();root.lift();root.focus_force()
                if orden_:root.after(350,lambda:app._disco_ripear(orden_[1]))   # (JMG, 16-11) ripear: el programa entero, con la película en la lista
                if archivos:root.after(150,lambda:app._addl(archivos))
            cerrar_inicio(_ver_ya)
            root.after(4000,app._ver_nueva)   # solo al arrancar el programa de verdad (las pruebas no lo llaman)
            root.after(7000,app._apoyo_aviso)   # (JMG, 13-11) el recordatorio de contribuir, cada 45 días
        root.mainloop()
    except Exception as e:
        import traceback
        messagebox.showerror("Error",f"{e}\n\n{traceback.format_exc()}")
