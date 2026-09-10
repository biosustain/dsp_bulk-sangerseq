#!/usr/bin/env bash
#
# Open the Indigo visualisation of every mutation called for one sample.
#
# Usage:
#   util/open_indigo_visualisations.sh sample_1 [results_combined.csv]
#
# Each row of the results CSV carries one variant and one visualisation URL,
# and a single sample can run to hundreds of variants. The URLs are therefore
# opened in batches of BATCH_SIZE, confirming with the caller between batches
# so a sample never dumps hundreds of tabs into the browser at once.

set -euo pipefail

readonly BROWSER="Google Chrome"
readonly INDIGO_URL_COLUMN=14
readonly SAMPLE_NAME_COLUMN=1
readonly BATCH_SIZE=25

sample_name=${1:-}
results_csv=${2:-outdir/results_combined.csv}

if [[ -z $sample_name ]]; then
    echo "usage: $0 <sample_name> [results_csv]" >&2
    exit 2
fi

if [[ ! -f $results_csv ]]; then
    echo "$0: no such results CSV: $results_csv" >&2
    exit 1
fi

# The ?variants-table=N query selects which mutation the viewer highlights, so
# it has to reach the browser intact. Neither `open` nor Chrome's own command
# line preserves it: both resolve a file:// URL to a bare path, drop the query,
# then fail to find that file. AppleScript's `open location` takes the URL as a
# URL and is the only route tested here that keeps the query.
open_urls_in_browser() {
    osascript \
        -e 'on run argv' \
        -e "tell application \"$BROWSER\"" \
        -e 'activate' \
        -e 'repeat with target_url in argv' \
        -e 'open location (target_url as text)' \
        -e 'end repeat' \
        -e 'end tell' \
        -e 'end run' \
        -- "$@"
}

# A bare Enter continues, so walking through every batch costs one keypress.
# Reads from stdin rather than /dev/tty so the script stays scriptable, and an
# EOF (no answer available at all) still counts as "stop" rather than as a
# default "yes" -- a non-interactive caller should not open hundreds of tabs.
confirm_next_batch() {
    local remaining=$1
    local next_batch_size=$(( remaining < BATCH_SIZE ? remaining : BATCH_SIZE ))
    local answer=""

    read -r -p "Open the next $next_batch_size? ($remaining left) [Y/n] " answer \
        || return 1

    [[ -z $answer || $answer == [yY] || $answer == [yY][eE][sS] ]]
}

urls=$(
    awk -F, \
        -v sample="$sample_name" \
        -v sample_column="$SAMPLE_NAME_COLUMN" \
        -v url_column="$INDIGO_URL_COLUMN" \
        'NR > 1 && $sample_column == sample && $url_column != "" { print $url_column }' \
        "$results_csv"
)

if [[ -z $urls ]]; then
    echo "$0: no visualisations for sample '$sample_name' in $results_csv" >&2
    exit 1
fi

url_list=()
while IFS= read -r url; do
    url_list+=("$url")
done <<<"$urls"

total_count=${#url_list[@]}
opened_count=0

echo "$sample_name has $total_count visualisation(s), opening $BATCH_SIZE at a time."

while (( opened_count < total_count )); do
    batch=("${url_list[@]:opened_count:BATCH_SIZE}")

    echo "Opening $((opened_count + 1))-$((opened_count + ${#batch[@]})) of $total_count..."
    open_urls_in_browser "${batch[@]}"

    opened_count=$(( opened_count + ${#batch[@]} ))
    remaining_count=$(( total_count - opened_count ))

    if (( remaining_count == 0 )); then
        echo "Opened all $total_count visualisation(s) for $sample_name."
        break
    fi

    if ! confirm_next_batch "$remaining_count"; then
        echo "Stopped after $opened_count of $total_count; $remaining_count not opened."
        break
    fi
done
