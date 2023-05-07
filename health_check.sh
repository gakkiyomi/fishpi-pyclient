#!/bin/bash
while true
do
    count=`ps -ef | grep main.py | grep -v "grep" | wc -l`
    if [[ $count == 0 ]];then
        echo "自动重启中"
        sh pwl_start
        echo "脚本重启成功"
    else
        echo "脚本状态正常"
    fi
    sleep 5
done
