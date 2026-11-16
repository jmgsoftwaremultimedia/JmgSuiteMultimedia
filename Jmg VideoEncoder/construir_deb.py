# -*- coding: utf-8 -*-
"""Crea el paquete de Linux (.deb) de Jmg VideoEncoder a partir de main.pyw, sin necesitar Linux.
Lo lanza construir_deb.bat. La version se lee de construir.bat (set "VER=...") para que siempre coincida
con el instalador de Windows. Resultado: salida\\jmg-videoencoder_<version>_all.deb

En Linux el programa usa el FFmpeg del sistema (paquete ffmpeg, que trae tambien ffplay para reproducir)."""
import os, re, io, sys, time, gzip, tarfile, hashlib

AQUI = os.path.dirname(os.path.abspath(__file__))
PKG = "jmg-videoencoder"
APP = "/usr/share/" + PKG
MAIL = "jmgsoftwaremultimedia@gmail.com"


def leer(nombre):
    with open(os.path.join(AQUI, nombre), "rb") as f:
        return f.read()


def version():
    m = re.search(r'set "VER=([0-9][0-9.]*)"', leer("construir.bat").decode("utf-8", "ignore"))
    if not m:
        sys.exit("[ERROR] No se encuentra la version en construir.bat (set \"VER=...\")")
    return m.group(1)


def iconos_png():
    """PNG de cada tamaño guardados dentro de VideoEncoder.ico -> {lado: bytes}"""
    ico = leer("VideoEncoder.ico")
    n = int.from_bytes(ico[4:6], "little")
    out = {}
    for i in range(n):
        e = ico[6 + 16 * i:22 + 16 * i]
        lado = e[0] or 256
        tam = int.from_bytes(e[8:12], "little"); pos = int.from_bytes(e[12:16], "little")
        dato = ico[pos:pos + tam]
        if dato[:8] == b"\x89PNG\r\n\x1a\n":
            out[lado] = dato
    if 256 not in out:
        sys.exit("[ERROR] VideoEncoder.ico no trae el icono PNG de 256x256")
    return out


def tar_gz(entradas):
    """entradas: lista de (ruta, bytes o None si es carpeta, permisos). Todo de root, como en un paquete normal."""
    buf = io.BytesIO(); ahora = int(time.time())
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT, compresslevel=9) as t:
        for ruta, dato, modo in entradas:
            ti = tarfile.TarInfo("./" + ruta.strip("/") if ruta.strip("/") else ".")
            ti.uid = ti.gid = 0; ti.uname = ti.gname = "root"; ti.mtime = ahora; ti.mode = modo
            if dato is None:
                ti.type = tarfile.DIRTYPE; t.addfile(ti)
            else:
                ti.size = len(dato); t.addfile(ti, io.BytesIO(dato))
    return buf.getvalue()


def ar(miembros):
    """formato «ar» de los .deb: debian-binary, control.tar.gz, data.tar.gz (en ese orden)"""
    out = [b"!<arch>\n"]; ahora = int(time.time())
    for nombre, dato in miembros:
        cab = "%-16s%-12d%-6d%-6d%-8s%-10d`\n" % (nombre, ahora, 0, 0, "100644", len(dato))
        out += [cab.encode("ascii"), dato, b"\n" if len(dato) % 2 else b""]
    return b"".join(out)


def main():
    ver = version()
    if not os.path.isfile(os.path.join(AQUI, "main.pyw")):
        sys.exit("[ERROR] Falta main.pyw en esta carpeta")
    prog = leer("main.pyw")
    compile(prog, "main.pyw", "exec")          # si el programa tuviera un error de sintaxis, no se empaqueta
    pngs = iconos_png()

    lanzador = ('#!/bin/sh\n'
                '# Jmg VideoEncoder (Jmg Software)\n'
                'exec python3 %s/main.pyw "$@"\n' % APP).encode()
    escritorio = ("[Desktop Entry]\n"
                  "Type=Application\n"
                  "Version=1.0\n"
                  "Name=Jmg VideoEncoder\n"
                  "GenericName=Video encoder\n"
                  "GenericName[es]=Codificador de vídeo\n"
                  "Comment=Compress and convert videos with FFmpeg (H.264, H.265, AV1, VP9, ProRes, DNxHR), with its audio and subtitles\n"
                  "Comment[es]=Comprime y convierte vídeos con FFmpeg (H.264, H.265, AV1, VP9, ProRes, DNxHR), con su audio y sus subtítulos\n"
                  "Exec=%s %%F\n"
                  "Icon=%s\n"
                  "Terminal=false\n"
                  "Categories=AudioVideo;Video;AudioVideoEditing;\n"
                  "Keywords=video;encoder;ffmpeg;h264;hevc;av1;mkv;\n"
                  "MimeType=video/x-matroska;video/mp4;video/x-msvideo;video/quicktime;video/mp2t;video/webm;video/mpeg;video/x-flv;\n"
                  % (PKG, PKG)).encode()
    anio = time.strftime("%Y")
    derechos = ("Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\n"
                "Upstream-Name: Jmg VideoEncoder\n"
                "Upstream-Contact: JMG <%s>\n\n"
                "Files: *\n"
                "Copyright: %s JMG (Jmg Software)\n"
                "License: GPL-3+\n"
                " Jmg VideoEncoder es software libre bajo la licencia GNU GPL v3.\n"
                " «Jmg VideoEncoder» y el logo Jmg Software son de su autor: las versiones\n"
                " modificadas deben usar otro nombre.\n"
                " .\n"
                " En sistemas Debian el texto completo de la licencia esta en\n"
                " /usr/share/common-licenses/GPL-3.\n" % (MAIL, anio)).encode()

    # historial de cambios (formato Debian, comprimido) y pagina de manual: Debian los pide en todo paquete
    fecha = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    cambios = ("%s (%s) unstable; urgency=medium\n\n"
               "  * Version %s de Jmg VideoEncoder. Novedades en el LEEME.txt.\n\n"
               " -- JMG <%s>  %s\n" % (PKG, ver, ver, MAIL, fecha)).encode()
    manual = (".TH JMG-VIDEOENCODER 1 \"%s\" \"%s\" \"Jmg VideoEncoder\"\n"
              ".SH NAME\n%s \\- video encoder with FFmpeg\n"
              ".SH SYNOPSIS\n.B %s\n[\\fIFILE\\fR...]\n"
              ".SH DESCRIPTION\nGraphical tool to compress and convert videos with FFmpeg, with their audio tracks,\n"
              "subtitles and covers. The original files are never modified.\n"
              "Files given on the command line are added to the file list.\n"
              ".SH FILES\n.I ~/.config/jmg-videoencoder/\nSettings and presets.\n"
              ".SH AUTHOR\nJMG <%s>\n" % (time.strftime("%Y-%m-%d"), ver, PKG, PKG, MAIL)).encode()
    gz = lambda b: gzip.compress(b, compresslevel=9, mtime=0)

    dirs = ["usr", "usr/bin", "usr/share", APP[1:], "usr/share/applications", "usr/share/pixmaps",
            "usr/share/doc", "usr/share/doc/" + PKG, "usr/share/icons", "usr/share/icons/hicolor",
            "usr/share/man", "usr/share/man/man1", APP[1:] + "/bin"]
    archivos = [(APP[1:] + "/main.pyw", prog, 0o644),
                (APP[1:] + "/VideoEncoder.png", pngs[256], 0o644),
                ("usr/bin/" + PKG, lanzador, 0o755),
                ("usr/share/applications/%s.desktop" % PKG, escritorio, 0o644),
                ("usr/share/pixmaps/%s.png" % PKG, pngs[256], 0o644),
                ("usr/share/doc/%s/copyright" % PKG, derechos, 0o644),
                ("usr/share/doc/%s/LEEME.txt" % PKG, leer("LEEME.txt").replace(b"\r\n", b"\n"), 0o644),
                ("usr/share/doc/%s/changelog.gz" % PKG, gz(cambios), 0o644),
                ("usr/share/man/man1/%s.1.gz" % PKG, gz(manual), 0o644)]
    for lado in sorted(pngs):
        d = "usr/share/icons/hicolor/%dx%d" % (lado, lado)
        dirs += [d, d + "/apps"]
        archivos.append((d + "/apps/%s.png" % PKG, pngs[lado], 0o644))

    data = tar_gz([("", None, 0o755)] + [(d, None, 0o755) for d in dirs] + archivos)
    kb = (sum(len(a[1]) for a in archivos) + 1023) // 1024
    md5 = "".join("%s  %s\n" % (hashlib.md5(a[1]).hexdigest(), a[0]) for a in archivos).encode()
    control = ("Package: %s\n"
               "Version: %s\n"
               "Section: video\n"
               "Priority: optional\n"
               "Architecture: all\n"
               "Depends: python3 (>= 3.10), python3-tk, ffmpeg (>= 7:5)\n"
               "Recommends: fonts-symbola, fonts-noto-cjk, xdg-utils\n"
               "Installed-Size: %d\n"
               "Maintainer: JMG <%s>\n"
               "Description: codificador de video / video encoder\n"
               " Jmg VideoEncoder comprime y convierte videos con FFmpeg (H.264, H.265,\n"
               " H.266, AV1, VP9, ProRes y DNxHR, por procesador o tarjeta grafica), con sus pistas de\n"
               " audio, subtitulos y portada: recorte por tramos, imagen, bandas negras,\n"
               " sincronizacion del audio y los subtitulos. Los originales no se tocan.\n"
               " .\n"
               " Compresses and converts videos with FFmpeg, with their audio tracks,\n"
               " subtitles and cover. The originals are never modified.\n" % (PKG, ver, kb, MAIL)).encode()
    tras = (b"#!/bin/sh\nset -e\n"
            b"if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q /usr/share/applications || true; fi\n"
            b"if command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -q -t /usr/share/icons/hicolor || true; fi\n"
            b"exit 0\n")
    ctl = tar_gz([("", None, 0o755), ("control", control, 0o644), ("md5sums", md5, 0o644),
                  ("postinst", tras, 0o755), ("postrm", tras, 0o755)])

    sal = os.path.join(AQUI, "salida"); os.makedirs(sal, exist_ok=True)
    deb = os.path.join(sal, "%s_%s_all.deb" % (PKG, ver))
    with open(deb, "wb") as f:
        f.write(ar([("debian-binary", b"2.0\n"), ("control.tar.gz", ctl), ("data.tar.gz", data)]))
    print("  LISTO: salida\\%s (%d KB)" % (os.path.basename(deb), os.path.getsize(deb) // 1024))
    print("  En Linux: sudo apt install ./%s" % os.path.basename(deb))


if __name__ == "__main__":
    main()
