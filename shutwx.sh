#! /usr/bin/bash
thdid=`ps aux|grep 'python weixinServer'|grep -v grep|grep -v 'sudo'|cut -d ' ' -f6`
echo $thdid
sudo kill -9 $thdid
