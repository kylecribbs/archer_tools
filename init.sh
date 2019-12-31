#!/bin/ash
name='Archer Tools'
status start --job-name "$name" --certificate /mnt/secrets/tls.crt \
        --key /mnt/secrets/tls.key
archer_tools --config /mnt/secrets/settings.conf && \
status success --job-name "$name" --certificate /mnt/secrets/tls.crt \
    --key /mnt/secrets/tls.key || \
status failed --job-name "$name" --certificate /mnt/secrets/tls.crt \
    --key /mnt/secrets/tls.key
