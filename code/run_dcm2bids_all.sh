#!/bin/bash
for d in ~/adni/ad_dicom/ADNI/*/ ~/adni/cn_dicom/ADNI/*/; do
    sid=$(basename "$d")
    label=$(echo "$sid" | tr -d '_')
    if [ -d ~/adni/bids/sub-$label ]; then
        echo "=== SKIP $sid (already done) ==="
        continue
    fi
    echo "=== CONVERT $sid -> sub-$label ==="
    dcm2bids -d "$d" -p "$label" -c ~/adni/dcm2bids_config.json -o ~/adni/bids
done
echo "=== ALL CONVERSIONS DONE ==="
