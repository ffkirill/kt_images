#!/bin/bash
echo "Started test"

cd ..
source ../.env/bin/activate
set -xv

#echo "Fixtures list"
#python  -m kt_images.manage.load_fixtures --list_all

#echo "JSON Schema"
#python3 -m aiohttp_pydantic.oas kt_images.wsgi:app

#python  -m kt_images.manage.load_fixtures --list_all
#python  -m kt_images.manage.load_fixtures --apply_all # Dangerous!

#python -m kt_images &
#sleep 30s

curl -i "http://localhost:8080/images" 

curl -i "http://localhost:8080/images" -H "Content-Type: application/json" -X POST --data '{"filename": "example.jpg", "tags": ["example_1", "jpeg", "canon"]}'

curl -i "http://localhost:8080/images?tag=canon" -X GET 

curl -i "http://localhost:8080/images?tags_all=canon&tags_all=jpeg" -X GET 

curl -i "http://localhost:8080/images?tags_any=canon&tags_any=nikon" -X GET 

curl -i "http://localhost:8080/images?tag=canon2" -X GET  

curl -i "http://localhost:8080/images/1" -X GET  

curl -i "http://localhost:8080/images/1/attachment/example.jpg" -X POST -F 'image=@"/home/kgolubev/Documents/example.jpg"'

curl -i "http://localhost:8080/images/1/attachment/example.jpg"

#fg 1
