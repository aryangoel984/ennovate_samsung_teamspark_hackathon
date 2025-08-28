#!/usr/bin/env bash
SESSION=$1
ACTION=$2
STATE=$3
LOG="../raw/${SESSION}_action_log.csv"

if [ ! -f "$LOG" ]; then
    echo "session_id,action,start_epoch,end_epoch" > $LOG
fi

if [ "$STATE" = "start" ]; then
    echo "$SESSION,$ACTION,$(date +%s)," >> $LOG
elif [ "$STATE" = "stop" ]; then
    # update last row’s end_epoch
    tmpfile=$(mktemp)
    awk -F',' -v ts=$(date +%s) 'BEGIN{OFS=","}
        NR==FNR {last=$0; next}
        {print} 
        END {split(last,a,","); if(length(a)==4 && a[4]=="") {a[4]=ts; print a[1]","a[2]","a[3]","a[4]}}' $LOG $LOG > $tmpfile
    mv $tmpfile $LOG
fi
