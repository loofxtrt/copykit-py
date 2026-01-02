#!/usr/bin/bash

WHITE_SUR=/mnt/seagate/symlinks/copykit-data/data/original-unzipped/WhiteSur-dark
FLUENT=/mnt/seagate/symlinks/copykit-data/data/original-unzipped/Fluent-dark

COPYCAT=/mnt/seagate/symlinks/kde-user-icons/copycat # esse é o local, não o do repo
SIMPLIFIED=$COPYCAT/all/simplified


redshift() {
    local prefix="$WHITE_SUR/status/22"
    
    local status_on="$prefix/redshift-status-on.svg"
    local status_day="$prefix/redshift-status-on.svg"
    local status_off="$prefix/redshift-status-off.svg"

    local off_variants=(
        "redshift-status-off"
        "redshift-status-off-symbolic"
    )

    local on_variants=(
        "redshift-status-on"
        "redshift-status-on-symbolic"
    )

    local day_variantts=(
        "redshift-status-day"
        "redshift-status-day-symbolic"
    )

    for v in "${off_variants[@]}"; do
        local src="$status_off"
        local dst="$COPYCAT/panel/24/$v.svg"
        
        if [[ -L "$path" ]]; then
            continue
        fi
        
        cp "$src" "$dst"
    done
}



















# script do copykit-ts
# # copia o arquivo pro diretório simplified
# cp "$WHITE_SUR/actions@2x/32/user-desktop-symbolic.svg"     "$SIMPLIFIED/desktop.svg"
# cp "$FLUENT/22/panel/audio-volume-high-panel.svg"           "$SIMPLIFIED/audio-volume-high.svg"
# cp "$FLUENT/22/panel/audio-volume-medium-panel.svg"         "$SIMPLIFIED/audio-volume-medium.svg"
# cp "$FLUENT/22/panel/audio-volume-low-panel.svg"            "$SIMPLIFIED/audio-volume-low.svg"
# cp "$FLUENT/22/panel/audio-volume-muted-blocking-panel.svg" "$SIMPLIFIED/audio-volume-muted.svg"

# # *** ANOTAÇÕES
# # ícones que aparecem na taskbar:
# #   áudio: panel/22
# #   desktop: places/symbolic
# # editados:
# #   obs tray (ícone normal do obs modificado, ainda não tem dinamismo na cor)

# # DESKTOP
# LINK=$COPYCAT/apps/symbolic/preferences-desktop-symbolic.svg
# rm -f "$LINK" # remove o arquivo antigo ou symlink
# ln -s ../../all/simplified/desktop.svg "$LINK" # cria o symlink relativo

# LINK=$COPYCAT/places/symbolic/user-desktop-symbolic.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/desktop.svg "$LINK"

# # OBS
# TARGETS_OBS=(
#     "$COPYCAT/panel/16/obs-tray.svg"
#     "$COPYCAT/panel/22/obs-tray.svg"
#     "$COPYCAT/panel/24/obs-tray.svg"
# )

# TARGETS_OBS_ACTIVE=(
#     "$COPYCAT/panel/16/obs-tray-active.svg"
#     "$COPYCAT/panel/22/obs-tray-active.svg"
#     "$COPYCAT/panel/24/obs-tray-active.svg"
# )

# for T in "${TARGETS_OBS[@]}"; do
#     LINK=${T}
#     rm -f "$LINK"
#     ln -s ../../all/simplified/obs-tray.svg "$LINK"
# done

# for T in "${TARGETS_OBS_ACTIVE[@]}"; do
#     LINK=${T}
#     rm -f "$LINK"
#     ln -s ../../all/simplified/obs-tray-active.svg "$LINK"
# done

# # AUDIO
# ## HIGH
# LINK=$COPYCAT/panel/24/audio-volume-high.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-high.svg "$LINK"

# LINK=$COPYCAT/panel/24/audio-on.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-high.svg "$LINK"

# LINK=$COPYCAT/panel/22/audio-volume-high.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-high.svg "$LINK"

# LINK=$COPYCAT/panel/22/audio-on.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-high.svg "$LINK"

# ## LOW
# LINK=$COPYCAT/panel/24/audio-volume-low.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-low.svg "$LINK"

# LINK=$COPYCAT/panel/22/audio-volume-low.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-low.svg "$LINK"

# ## MEDIUM
# LINK=$COPYCAT/panel/24/audio-volume-medium.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-medium.svg "$LINK"

# LINK=$COPYCAT/panel/22/audio-volume-medium.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-medium.svg "$LINK"

# ## MUTED
# LINK=$COPYCAT/panel/24/audio-volume-muted.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-muted.svg "$LINK"

# LINK=$COPYCAT/panel/22/audio-volume-muted.svg
# rm -f "$LINK"
# ln -s ../../all/simplified/audio-volume-muted.svg "$LINK"