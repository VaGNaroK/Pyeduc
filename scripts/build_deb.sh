#!/bin/bash
VERSION="1.0.0"
DIR_NAME="pyeduc_${VERSION}_amd64"

# Criar estrutura
mkdir -p ${DIR_NAME}/DEBIAN
mkdir -p ${DIR_NAME}/usr/bin
mkdir -p ${DIR_NAME}/opt/pyeduc
mkdir -p ${DIR_NAME}/usr/share/applications

# Criar DEBIAN/control
cat << EOF > ${DIR_NAME}/DEBIAN/control
Package: pyeduc
Version: ${VERSION}
Architecture: amd64
Maintainer: Pyeduc Team <contato@pyeduc.org>
Description: App Educacional Python com Flet.
Depends: libgtk-3-0, libmpv1, libgstreamer1.0-0, libgstreamer-plugins-base1.0-0
EOF

# Copiar binarios gerados pelo flet
cp -r build/linux/* ${DIR_NAME}/opt/pyeduc/

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
