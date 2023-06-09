# tg cloud storage bot

### tg: @angrydish
used: aiogram=2.25.1


---
to store a token you need to create a .env file in root directory and write your token

```TOKEN_TG_BOT=abcdef12355323```

---
to upload a file you just simply need to attach and send a file (documents, videos and non-compressed photos are allowed)

list of commands:
```commandline
/login - log in to user account
/logout - log out of user account
/register - register an account
/list - list all files, that user have
/search - search file by it's filename, e.g. hashcat = /search hash
/sort - sort files in descending order
/get <number> - download a file by it's number, numbers are given in /list output
```

---

Building in docker is pretty simple, all you need is to make same things as for building not for docker, and then type
```commandline
docker compose up --build -d
```
Telegram token must still be stored in .env file, as docker copies it inside itself

To edit configuration parameters for database, edit db/config.db file and write you credentials, also docker-compose.yml file must be edited