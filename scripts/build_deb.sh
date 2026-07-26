#!/bin/bash
VERSION="1.0.0"
DIR_NAME="pyeduc_${VERSION}_amd64"

# Criar estrutura
mkdir -p ${DIR_NAME}/DEBIAN
mkdir -p ${DIR_NAME}/usr/bin
mkdir -p ${DIR_NAME}/opt/pyeduc
mkdir -p ${DIR_NAME}/usr/share/applications

# Criar DEBIAN/control com suporte a distros modernas (Ubuntu 24.04 / Mint 22 utilizam libmpv2 ou mpv)
cat << EOF > ${DIR_NAME}/DEBIAN/control
Package: pyeduc
Version: ${VERSION}
Architecture: amd64
Maintainer: Pyeduc Team <contato@pyeduc.org>
Description: App Educacional Python com Flet.
Depends: libgtk-3-0, libmpv2 | libmpv1 | mpv | libmpv-dev, libgstreamer1.0-0, libgstreamer-plugins-base1.0-0
EOF

# Criar DEBIAN/postinst para automação do symlink libmpv.so.1 em distros modernas
cat << 'EOF' > ${DIR_NAME}/DEBIAN/postinst
#!/bin/sh
set -e

if [ ! -f /usr/lib/x86_64-linux-gnu/libmpv.so.1 ] && [ ! -f /usr/lib/libmpv.so.1 ]; then
    if [ -f /usr/lib/x86_64-linux-gnu/libmpv.so.2 ]; then
        ln -sf /usr/lib/x86_64-linux-gnu/libmpv.so.2 /usr/lib/x86_64-linux-gnu/libmpv.so.1
    elif [ -f /usr/lib/x86_64-linux-gnu/libmpv.so ]; then
        ln -sf /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/x86_64-linux-gnu/libmpv.so.1
    fi
fi

if command -v ldconfig >/dev/null 2>&1; then
    ldconfig || true
fi

exit 0
EOF
chmod +x ${DIR_NAME}/DEBIAN/postinst

# Criar DEBIAN/postrm para remoção limpa do symlink ao desinstalar
cat << 'EOF' > ${DIR_NAME}/DEBIAN/postrm
#!/bin/sh
set -e

if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    if [ -L /usr/lib/x86_64-linux-gnu/libmpv.so.1 ]; then
        rm -f /usr/lib/x86_64-linux-gnu/libmpv.so.1
    fi
fi

exit 0
EOF
chmod +x ${DIR_NAME}/DEBIAN/postrm

# Copiar binarios gerados pelo flet
cp -r build/linux/* ${DIR_NAME}/opt/pyeduc/

# Copiar ícone do projeto para o sistema de ícones do Linux
mkdir -p ${DIR_NAME}/usr/share/icons/hicolor/scalable/apps
mkdir -p ${DIR_NAME}/usr/share/pixmaps
cp content/icons/pyeduc.svg ${DIR_NAME}/usr/share/icons/hicolor/scalable/apps/pyeduc.svg
cp content/icons/pyeduc.svg ${DIR_NAME}/usr/share/pixmaps/pyeduc.svg

# Criar link simbolico no bin
ln -s /opt/pyeduc/pyeduc ${DIR_NAME}/usr/bin/pyeduc

# Criar arquivo .desktop
cat << EOF > ${DIR_NAME}/usr/share/applications/pyeduc.desktop
[Desktop Entry]
Name=Pyeduc
Exec=/usr/bin/pyeduc
Icon=pyeduc
Type=Application
Categories=Education;Development;
EOF

# Construir o .deb
dpkg-deb --build ${DIR_NAME}
mv ${DIR_NAME}.deb pyeduc_amd64.deb
