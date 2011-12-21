#!/bin/bash

if [ ! -d "logs" ]; then
	mkdir logs
fi

if [ ! -d "db" ]; then
	mkdir db
fi

if [ -e "db/mongod.lock" ]; then
	echo "db/mongod.lock exists; delete that file then retry."
	exit 1
fi

mongod --fork --logpath logs/mongo.log --dbpath db/ --rest