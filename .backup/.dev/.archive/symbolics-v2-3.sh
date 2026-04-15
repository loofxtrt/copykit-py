#!/usr/bin/bash

COPYDB=/mnt/seagate/symlinks/copydb
WHITE_SUR=$COPYDB/original-unzipped/WhiteSur-dark
FLUENT=$COPYDB/original-unzipped/Fluent-dark

COPYCAT=/mnt/seagate/symlinks/kde-user-icons/copycat # esse é o local, não o do repo
SIMPLIFIED=$COPYCAT/all/simplified

AUDIO_HIGH="$FLUENT/22/panel/audio-volume-high-panel.svg"
AUDIO_MEDIUM="$FLUENT/22/panel/audio-volume-medium-panel.svg"
AUDIO_LOW="$FLUENT/22/panel/audio-volume-low-panel.svg"
AUDIO_MUTED="$FLUENT/22/panel/audio-volume-muted-blocking-panel.svg"

# FIXME: variantes day do redshift são symlinks, mas não devem ser puladas
# ao menos uma deve ser realmente substituída (o status-day, o symbolic deve ser o link)

# FIXME: provavelmente esses ícones (do fluent e whitesur) são branco puro
# em vez de cores que se adaptam ao color scheme

# whole_sections() {
#     cp -rT "$FLUENT/16/actions" "$COPYCAT/actions/16"
#     cp -rT "$FLUENT/symbolic/actions" "$COPYCAT/actions/symbolic"

#     # FIXME: os apps tem o símbolo de help e o de system que o menu usa
#     # então eles sobreescrever os de 22
#     cp -rT "$FLUENT/symbolic/apps" "$COPYCAT/apps/symbolic"

#     cp -rT "$FLUENT/22/categories" "$COPYCAT/categories/symbolic"

#     cp -rT "$FLUENT/22/devices" "$COPYCAT/devices/symbolic"

#     cp -rT "$FLUENT/16/devices" "$COPYCAT/devices/16"
#     cp -rT "$FLUENT/22/devices" "$COPYCAT/devices/22"
#     cp -rT "$FLUENT/24/devices" "$COPYCAT/devices/24"

#     cp -rT "$FLUENT/symbolic/status" "$COPYCAT/status/symbolic"
# }

# whole_sections() {
#     cp -rT "$FLUENT/16/actions" "$COPYCAT/actions/16"
#     cp -rT "$FLUENT/16/devices" "$COPYCAT/devices/16"
#     cp -rT "$FLUENT/16/places" "$COPYCAT/places/16"
    
#     cp -rT "$FLUENT/22/actions" "$COPYCAT/actions/22"
#     cp -rT "$FLUENT/22/categories" "$COPYCAT/categories/22"
#     cp -rT "$FLUENT/22/devices" "$COPYCAT/devices/22"
#     cp -rT "$FLUENT/22/places" "$COPYCAT/places/22"

#     cp -rT "$FLUENT/24/actions" "$COPYCAT/actions/24"
#     cp -rT "$FLUENT/24/devices" "$COPYCAT/devices/24"
#     cp -rT "$FLUENT/24/places" "$COPYCAT/places/24"

#     cp -rT "$FLUENT/32/actions" "$COPYCAT/actions/32"
#     cp -rT "$FLUENT/32/devices" "$COPYCAT/devices/32"
#     cp -rT "$FLUENT/32/status" "$COPYCAT/status/32"

#     cp -rT "$FLUENT/symbolic/actions" "$COPYCAT/actions/symbolic"
#     cp -rT "$FLUENT/symbolic/apps" "$COPYCAT/apps/symbolic"
#     cp -rT "$FLUENT/symbolic/categories" "$COPYCAT/categories/symbolic"
#     cp -rT "$FLUENT/symbolic/devices" "$COPYCAT/devices/symbolic"
#     cp -rT "$FLUENT/symbolic/mimetypes" "$COPYCAT/mimetypes/symbolic"
#     cp -rT "$FLUENT/symbolic/places" "$COPYCAT/places/symbolic"
#     cp -rT "$FLUENT/symbolic/status" "$COPYCAT/status/symbolic"
# }

audio() {
    local src="$1"
    local name="$2"

    for size in 22 24; do
        local dst="$COPYCAT/panel/$size/$name.svg"

        # pular se for symlink
        if [[ -L "$dst" ]]; then
            echo "symlink pulado"
            continue
        fi

        cp "$src" "$dst"
        echo "ícone substituído"
    done
}

redshift() {
    local prefix="$WHITE_SUR/status/22"
    
    local status_on="$prefix/redshift-status-on.svg"
    local status_day="$prefix/redshift-status-day.svg"
    local status_off="$prefix/redshift-status-off.svg"

    local off_variants=(
        "redshift-status-off"
        "redshift-status-off-symbolic"
    )

    local on_variants=(
        "redshift-status-on"
        "redshift-status-on-symbolic"
    )

    local day_variants=(
        "redshift-status-day"
        "redshift-status-day-symbolic"
    )

    replace_variants() {
        local -n variants="$1"
        local src="$2"

        for v in "${variants[@]}"; do
            local dst="$COPYCAT/panel/24/$v.svg"

            # pular se for symlink
            if [[ -L "$dst" ]]; then
                echo "symlink pulado"
                continue
            fi
        
            cp "$src" "$dst"
            echo "ícone substituído"
        done
    }

    replace_variants off_variants "$status_off"
    replace_variants on_variants "$status_on"
    replace_variants day_variants "$status_day"
}

network() {
    local src="$FLUENT/22/panel/network-wired.svg"
    local destinations=(
        "$COPYCAT/panel/16/network-wired.svg"
        "$COPYCAT/panel/22/network-wired.svg"
        "$COPYCAT/panel/24/network-wired.svg"
        "$COPYCAT/devices/symbolic/network-wired-symbolic.svg"
        "$COPYCAT/status/symbolic/com.system76.CosmicAppletNetwork-symbolic.svg"
    )

    for dst in "${destinations[@]}"; do
        cp "$src" "$dst"
    done
}

desktop() {
    local destinations=(
        "$COPYCAT/apps/symbolic/preferences-desktop-symbolic.svg"
        "$COPYCAT/places/symbolic/user-desktop-symbolic.svg"
    )

    for dst in "${destinations[@]}"; do
        cp "$WHITE_SUR/actions@2x/32/user-desktop-symbolic.svg" "$dst"
    done
}

whole_sections
# redshift
# network
# desktop
# audio "$AUDIO_HIGH"   "audio-volume-high"
# audio "$AUDIO_HIGH"   "audio-on"
# audio "$AUDIO_MEDIUM" "audio-volume-medium"
# audio "$AUDIO_LOW"    "audio-volume-low"
# audio "$AUDIO_MUTED"  "audio-volume-muted"