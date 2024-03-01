#!/bin/sh

tracker_list=$(curl -Ns https://ngosang.github.io/trackerslist/trackers_all_http.txt | awk '$0' | tr '\n\n' ',')

chrome --allow-overwrite=true --auto-file-renaming=true --bt-detach-seed-only=true --bt-enable-lpd=true --bt-max-peers=0 \
       --bt-remove-unselected-file=true --bt-tracker="[$tracker_list]" --check-certificate=false --check-integrity=true \
       --content-disposition-default-utf8=true --continue=true --daemon=true --disable-ipv6=true --disk-cache=1024M \
       --enable-rpc=true --follow-torrent=mem --force-save=true --http-accept-gzip=true --max-concurrent-downloads=1000 \
       --max-connection-per-server=16 --max-file-not-found=0 --max-overall-upload-limit=0 --max-tries=20 --max-upload-limit=0 \
       --min-split-size=1024M --optimize-concurrent-downloads=true --peer-agent=qBittorrent/4.6.2 --peer-id-prefix=-qB4620- \
       --quiet=true --reuse-uri=true --rpc-max-request-size=1024M --seed-ratio=0 --split=16 --summary-interval=0 --user-agent=Wget/1.12 

firefox -d --profile="$(pwd)"