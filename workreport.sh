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

total_minutes=0

for day in *; do
	minutes=`cat $day | uniq | wc -l`
	total_minutes=$((total_minutes+minutes))
	
	day_hours=$((minutes/60))
	day_part_hours=$((minutes%60))
	printf "%s %d:%02d\n" $day $day_hours $day_part_hours
done
printf "TOTAL: %d:%02d" $((total_minutes/60)) $((total_minutes%60))
