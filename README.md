# TelegramParsers

# Introduction:

This repository is developed to parse the telegram data exported in JSON format from the Telegram desktop app.

# Requirements and Steps:

* Install git and clone the repository.
* Install pip ($sudo apt install python3-pip)
* Install mysql connector ($pip3 install mysql-connector)
* Install sshpass ($sudo apt install sshpass)

# How to use:

* For any channel or group, Download the entire chat history once before downloading the weekly chats. If we parse a chat once to our database, then the code will parse messages only from the last parsed messages. So we have to download the chat in chronological order.
* Do not change the folder name of the exported chat.
* Download as many channels or groups as you want.
* You can download the same chat(channel or group) multiple times, the code will handle the duplicates.
* Just run channel_parser.py and group_parser.py. (order doesn’t matter)
* Ideally, all the folders from the ‘Telegram Desktop’ folder should be deleted in the local system. If not look for the appropriate error. (if you can’t resolve it, manually delete the folder and restart the parsers. It will miss some messages.)
* Install cron job to run both the parsers automatically on daily basis.
* * $crontab -e
* * 0 4 * * * cd /home/rob/PycharmProjects/TelegramParsers && sh telegram_script.sh 
* * This will run the parsers daily at 4 AM.

# Developer Reference:

Channel Parser:
* Lists all the folders sorted on the creation date.
* Loads the JSON file. Skips if not channel.
* Checks if the channel is already in the database and inserts if new.
* Extracts last parsed message_id (telegram id, unique, always increasing in a channel/group)
* Checks if there are new messages in the channel JSON.
* Extracts all the useful data and inserts it into the database.
* Then renames the json file to date at with it was generated.
* Copies all new files to jaguar using rsync.
* Delete the local copy when the above steps are successful.

Group Parser:
* Lists all the folders sorted on the creation date.
* Loads the JSON file. Skips if not group.
* Checks if the group is already in the database and inserts if new.
* Extracts all the usernames and their telegram ids.
* Inserts them if not exists into our database.
* Extracts last parsed message_id (telegram id, unique, always increasing in a channel/group)
* Checks if there are new messages in the group JSON.
* Extracts all the useful data and inserts it into the database with batch size of 10000.
* Then renames the json file to date at with it was generated.
* Copies all new files to jaguar using rsync.
* Delete the local copy when the above steps are successful.
