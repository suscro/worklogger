#!/bin/bash

#   Copyright 2019 Suscro
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

MONTH="$(printf "%d" $( echo "${1:-$( date +%m )}" | bc))"
YEAR="${2:-$( date +%Y )}"

dir="$HOME/.worklog/$YEAR/$MONTH"

if [[ ! -d "$dir" ]]; then
    echo "TOTAL: 0"
    exit
fi

cd "$dir"

echo "$YEAR-$(printf "%02d" $MONTH)"
echo
total_minutes=0
days=0
for day in $(ls | sort -n); do
    dayOfWeek="$( date -d "$YEAR-$MONTH-$day" +%u)"
    if (( dayOfWeek != 6 )) && (( dayOfWeek != 7 )); then
        days=$(( days + 1 ))
    fi
	minutes=`cat $day | uniq | wc -l`
	total_minutes=$((total_minutes+minutes))
	
	day_hours=$((minutes/60))
	day_part_hours=$((minutes%60))
	printf "%2d%3d:%02d\n" $day $day_hours $day_part_hours
done
printf "TOTAL: %4d:%02d\n" $((total_minutes/60)) $((total_minutes%60))
delta=$(( total_minutes - (days * 8 * 60) ))
prefix=""
if (( delta < 0 )); then
    delta=$(( -delta ))
    prefix="-"
fi
printf "    Δ: %4s:%02d\n" "${prefix}$(( delta / 60 ))" $(( delta % 60))
