#!/bin/bash

if [ ! -d "logs" ]; then
	mkdir logs
fi

if [ ! -d "db" ]; then
	mkdir db
fi

mongod --fork --logpath logs/mongo.log --dbpath db/ --rest