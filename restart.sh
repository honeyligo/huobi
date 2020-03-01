#!/bin/bash

ps  -ef | grep  main.py | grep -v grep | awk '{print $2}' | xargs kill -9
sleep 2
nohup /usr/bin/python ./huobi/main.py $1 2>&1 &
