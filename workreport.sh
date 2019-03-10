#!/bin/bash

total_minutes=0

for day in *; do
	minutes=`cat $day | uniq | wc -l`
	total_minutes=$((total_minutes+minutes))
	
	day_hours=$((minutes/60))
	day_part_hours=$((minutes%60))
	printf "%s %d:%02d\n" $day $day_hours $day_part_hours
done
printf "TOTAL: %d:%02d" $((total_minutes/60)) $((total_minutes%60))
