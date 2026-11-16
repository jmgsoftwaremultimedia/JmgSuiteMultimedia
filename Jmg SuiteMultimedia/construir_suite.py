# -*- coding: utf-8 -*-
"""Construye Jmg SuiteMultimedia: Jmg AudioProcesador y Jmg VideoEncoder con un solo FFmpeg.
Resultado en «salida»: JmgSuiteMultimedia_<ver>_setup.exe, JmgSuiteMultimedia_<ver>_portable.zip y los .deb de Linux de los dos.
Los programas están en las carpetas de al lado («Jmg AudioProcesador 5.1» y «Jmg VideoEncoder»); FFmpeg se coge del «bin» del AudioProcesador."""
import os, sys, re, glob, shutil, zipfile, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
AP = os.path.join(RAIZ, "Jmg AudioProcesador 5.1"); VE = os.path.join(RAIZ, "Jmg VideoEncoder")
VER = re.search(r'#define MyAppVersion "([^"]+)"', open(os.path.join(AQUI, "suite.iss"), encoding="utf-8").read()).group(1)
DIST = os.path.join(AQUI, "dist"); BUILD = os.path.join(AQUI, "build"); SAL = os.path.join(AQUI, "salida"); JS = os.path.join(DIST, "Jmg Software")
PROGS = [("Jmg AudioProcesador", AP, "AudioProcesador.ico"), ("Jmg VideoEncoder", VE, "VideoEncoder.ico")]
def paso(t): print("\n" + t, flush=True)
def falta(p):
    if not os.path.exists(p): sys.exit("[ERROR] Falta " + p)
def iscc():
    for b in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.path.join(os.environ.get("LocalAppData", ""), "Programs")):
        for v in ("6", "7"):
            p = os.path.join(b or "", "Inno Setup " + v, "ISCC.exe")
            if b and os.path.isfile(p): return p
    return shutil.which("ISCC.exe")
def main():
    py = sys.executable
    print("  Jmg SuiteMultimedia " + VER + "  -  instalador, portable y paquetes de Linux")
    for nom, carp, ico in PROGS:
        for f in ("main.pyw", ico, "version_info.txt", "construir_deb.py"): falta(os.path.join(carp, f))
    for f in ("ffmpeg.exe", "ffprobe.exe", "ffplay.exe", "LICENSE.txt", "voz.rnnn", "aften.exe", "aften_LICENSE.txt"): falta(os.path.join(AP, "bin", f))
    for f in ("lanzador.pyw", "imagenes.py"): falta(os.path.join(AQUI, "lanzador", f))   # (JMG, 13-11) el lanzador de la suite   # Aften: el AC3 de EncWAVtoAC3 (JMG, 8-11)
    paso("[1/6] Instalando / actualizando PyInstaller y tkinterdnd2...")
    subprocess.check_call([py, "-m", "pip", "install", "--upgrade", "--quiet", "pyinstaller", "tkinterdnd2"])
    for d in (DIST, BUILD): shutil.rmtree(d, ignore_errors=True)
    for i, (nom, carp, ico) in enumerate(PROGS, 2):
        paso(f"[{i}/6] Creando {nom} (tarda un par de minutos)...")
        subprocess.check_call([py, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--onedir", "--name", nom,
                               "--icon", os.path.join(carp, ico), "--add-data", os.path.join(carp, ico) + ";.", "--collect-all", "tkinterdnd2",
                               "--version-file", os.path.join(carp, "version_info.txt"), "--distpath", JS, "--workpath", os.path.join(BUILD, nom),
                               "--specpath", BUILD, os.path.join(carp, "main.pyw")])
        if os.path.isfile(os.path.join(carp, "LEEME.txt")): shutil.copy2(os.path.join(carp, "LEEME.txt"), os.path.join(JS, nom, "LEEME.txt"))
    paso("[3b/6] Creando el lanzador «Jmg SuiteMultimedia» (elegir uno de los dos programas)...")   # (JMG, 13-11)
    os.makedirs(BUILD, exist_ok=True); vi = os.path.join(BUILD, "version_suite.txt"); n_ = VER.split(".") + ["0"] * 4
    open(vi, "w", encoding="utf-8").write(open(os.path.join(VE, "version_info.txt"), encoding="utf-8").read()
        .replace("Jmg VideoEncoder", "Jmg SuiteMultimedia").replace(re.search(r"filevers=\([^)]*\)", open(os.path.join(VE, "version_info.txt"), encoding="utf-8").read()).group(0), "filevers=(" + ",".join(n_[:4]) + ")")
        .replace(re.search(r"prodvers=\([^)]*\)", open(os.path.join(VE, "version_info.txt"), encoding="utf-8").read()).group(0), "prodvers=(" + ",".join(n_[:4]) + ")")
        .replace(re.search(r"u'FileVersion',u'[^']*'", open(os.path.join(VE, "version_info.txt"), encoding="utf-8").read()).group(0), "u'FileVersion',u'" + ".".join(n_[:4]) + "'")
        .replace(re.search(r"u'ProductVersion',u'[^']*'", open(os.path.join(VE, "version_info.txt"), encoding="utf-8").read()).group(0), "u'ProductVersion',u'" + VER + "'"))
    subprocess.check_call([py, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--onedir", "--name", "Jmg SuiteMultimedia",
                           "--icon", os.path.join(AQUI, "JmgSuite.ico"), "--add-data", os.path.join(AQUI, "JmgSuite.ico") + ";.",
                           "--paths", os.path.join(AQUI, "lanzador"), "--version-file", vi, "--distpath", JS, "--workpath", os.path.join(BUILD, "lanzador"),
                           "--specpath", BUILD, os.path.join(AQUI, "lanzador", "lanzador.pyw")])
    paso("[4/6] FFmpeg común (una sola vez) y los demás archivos...")
    b = os.path.join(JS, "bin"); os.makedirs(b)
    for f in ("ffmpeg.exe", "ffprobe.exe", "ffplay.exe", "LICENSE.txt", "aften.exe", "aften_LICENSE.txt"): shutil.copy2(os.path.join(AP, "bin", f), b)
    vb = os.path.join(JS, "Jmg AudioProcesador", "bin"); os.makedirs(vb, exist_ok=True)
    shutil.copy2(os.path.join(AP, "bin", "voz.rnnn"), vb)   # el modelo de voz de «Central solo voz» se queda con el AudioProcesador
    shutil.copy2(os.path.join(AP, "bin", "LICENSE.txt"), os.path.join(JS, "LICENSE.txt"))
    # (JMG, 20-11) el instalador en español: un resumen en español delante del texto oficial (en inglés) de la GPL v3
    open(os.path.join(BUILD, "LICENCIA_es.txt"), "w", encoding="utf-8-sig").write(open(os.path.join(AQUI, "licencia_resumen_es.txt"), encoding="utf-8").read() + open(os.path.join(AP, "bin", "LICENSE.txt"), encoding="utf-8").read())
    shutil.copy2(os.path.join(AQUI, "LEEME.txt"), os.path.join(JS, "LEEME.txt"))
    os.makedirs(SAL, exist_ok=True)
    paso("[5/6] Creando la versión portable (.zip)...")
    z = os.path.join(SAL, f"JmgSuiteMultimedia_{VER}_portable.zip")
    if os.path.exists(z): os.remove(z)
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for r, _, fs in os.walk(JS):
            for f in fs:
                p = os.path.join(r, f); zf.write(p, os.path.relpath(p, DIST))
    paso("[6/6] Instalador (Inno Setup) y paquetes de Linux (.deb)...")
    i = iscc()
    if i: subprocess.check_call([i, "/Q", os.path.join(AQUI, "suite.iss")])
    else: print("[AVISO] No se encuentra Inno Setup (6 o 7): el portable ya está; para el instalador abre suite.iss con Inno Setup y pulsa Compile.")
    for nom, carp, _ in PROGS:
        subprocess.check_call([py, os.path.join(carp, "construir_deb.py")], cwd=carp)
        debs = sorted(glob.glob(os.path.join(carp, "salida", "*.deb")), key=os.path.getmtime)
        if debs: shutil.copy2(debs[-1], SAL)
    shutil.rmtree(BUILD, ignore_errors=True); shutil.rmtree(DIST, ignore_errors=True)
    print("\n  LISTO. Mira la carpeta «salida»:")
    for f in sorted(os.listdir(SAL)): print("    - " + f)
if __name__ == "__main__":
    main()
