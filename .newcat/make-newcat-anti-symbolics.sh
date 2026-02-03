#!/usr/bin/env bash

KORA="/mnt/seagate/symlinks/kde-user-icons/kora/"
FLUENT="/mnt/seagate/symlinks/kde-user-icons/Fluent"
NEWCAT="/mnt/seagate/temporario/newcat-3"

#rm -rf "$NEWCAT/16"
rm -rf "$NEWCAT/16@2x"
rm -rf "$NEWCAT/16@3x"

#rm -rf "$NEWCAT/22"
rm -rf "$NEWCAT/22@2x"
rm -rf "$NEWCAT/22@3x"

#rm -rf "$NEWCAT/24"
rm -rf "$NEWCAT/24@2x"
rm -rf "$NEWCAT/24@3x"

#rm -rf "$NEWCAT/32"
rm -rf "$NEWCAT/32@2x"
rm -rf "$NEWCAT/32@3x"

rm -rf "$NEWCAT/256"
rm -rf "$NEWCAT/256@2x"
rm -rf "$NEWCAT/256@3x"

rm -rf "$NEWCAT/scalable@2x"
rm -rf "$NEWCAT/scalable@3x"

mkdir -p "$NEWCAT/16"
mkdir -p "$NEWCAT/22"
mkdir -p "$NEWCAT/24"
mkdir -p "$NEWCAT/32"

# corrigir o que é symlink no fluent original, fazendo uma cópia real deles
cp -r "$FLUENT/16/panel" "$NEWCAT/16/panel"
cp -r "$FLUENT/16/mimetypes" "$NEWCAT/16/mimetypes"
cp -r "$FLUENT/16/status" "$NEWCAT/16/status"

cp -r "$FLUENT/22/emblems" "$NEWCAT/22/emblems"
cp -r "$FLUENT/22/mimetypes" "$NEWCAT/22/mimetypes"
cp -r "$FLUENT/22/panel" "$NEWCAT/22/panel"

cp -r "$FLUENT/24/animations" "$NEWCAT/24/animations"
cp -r "$FLUENT/24/panel" "$NEWCAT/24/panel"

cp -r "$FLUENT/32/categories" "$NEWCAT/32/categories"

# remover os places simbólicos
rm -rf "$NEWCAT/16/places"
rm -rf "$NEWCAT/22/places"
rm -rf "$NEWCAT/24/places"
rm -rf "$NEWCAT/22/places"
rm -rf "$NEWCAT/symbolic/places"

# copiar os scalables do kora pra substituir os originais do fluent
rm -rf "$NEWCAT/scalable/places"
rm -rf "$NEWCAT/scalable/apps"
rm -rf "$NEWCAT/scalable/devices"
rm -rf "$NEWCAT/scalable/mimetypes"

cp -r "$KORA/places/scalable" "$NEWCAT/scalable/places"
cp -r "$KORA/apps/scalable" "$NEWCAT/scalable/apps"
cp -r "$KORA/devices/scalable" "$NEWCAT/scalable/devices"
cp -r "$KORA/mimetypes/scalable" "$NEWCAT/scalable/mimetypes"

# aplicação
rm -rf /mnt/seagate/symlinks/kde-user-icons/newcat
cp -aT "$NEWCAT" /mnt/seagate/symlinks/kde-user-icons/newcat