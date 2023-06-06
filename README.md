# tg cloud storage bot

### tg: @angrydish
used: aiogram=2.25.1

to store a token you need to create a .env file in root directory and write your token

```TOKEN_TG_BOT=abcdef12355323```

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