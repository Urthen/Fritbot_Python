#!/bin/bash

if [ ! -d "logs" ]; then
	mkdir logs
fi

if [ -z $1 ]; then
	twistd -y startup.tac
else
	twistd -ny startup.tac
fi