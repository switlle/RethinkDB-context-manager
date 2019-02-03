#!/bin/bash
remoteHost="uwsgi.loc:5000"
url="api/new"
#user="api"
#passwd="1245"
# Формируем JSON
login="rocha"
name="Busan"
passw="root"
phone="79005006826"
email="mail@mail.ru"
#gender=None

INFO=$(\
printf "{\n"
printf "\t\"method\": \"stats\",\n"
printf "\t\"jsonrpc\": \"2.0\",\n"
printf "\t\"login\": \"$login\",\n"
printf "\t\"name\": \"$name\",\n"
printf "\t\"passw\": \"$passw\",\n"
printf "\t\"phone\": \"$phone\",\n"
printf "\t\"email\": \"$email\"\n"
#printf "\t\"gender\": \"$gender\"\n"
printf "}\n")

echo $INFO
# Отправляем JSON на REST API сервер
#curl -s -u $user:$passwd -j --ssl -H "Content-Type: application/json" -X POST -d "$INFO" $remoteHost/$url
#curl -v -u $user:$passwd -j -H "Content-Type: application/json" -X POST -d "$INFO" $remoteHost/$url
curl -v -j -H "Content-Type: application/json" -X POST -d "$INFO" $remoteHost/$url

# curl -s -H "Content-Type: application/json" -X POST -d '{ "method": "stats", "jsonrpc": "2.0", "login": "Test", "name": "Susan", "passw": "root", "phone": "79005006826", "email": "mail@mail.ru", "gender": "None"}' http://uwsgi.loc:5000/api/new
