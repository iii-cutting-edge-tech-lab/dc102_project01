#!/bin/bash
if [ `docker ps | grep  jupyter.vcloudlab.pro | wc -l`  = 1 ]
then
        docker stop jupyter.vcloudlab.pro
        docker rm  jupyter.vcloudlab.pro
fi
