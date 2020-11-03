# ChickenFryBiryani

import os
import json
import datetime
import database_connector

chat_folder_path = "/home/rob/Downloads/Telegram Desktop/ChatExport_2020-10-27/"
remote_telegram_root = "/home/covid19/covid19telegram/"
m_sServerPass = "uvNjdEbsn3t5uyiQkXgw"
local_path = chat_folder_path
m_sServerUser = "covid19"
m_sServerHost = "jaguar.cs.gsu.edu"
telegram_channel_id = ""


def decodeStr(string):
    return string


def getDateString(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d%H%M%S')


def getMediaPath(message):
    if 'photo' in message:
        return str(telegram_channel_id) + '/' + chat_folder_path.split('/')[-2].split('_')[1] + '/' + message['photo']
    if 'file' in message:
        return str(telegram_channel_id) + '/' + chat_folder_path.split('/')[-2].split('_')[1] + '/' + message['file']
    return ''


def getText(message):
    if 'text' not in message or message['text'] == '':
        return ''
    if type(message['text']) == str:
        return decodeStr(message['text'])
    return ' '.join(list(map(lambda x: decodeStr(x).strip() if type(x) == str else decodeStr(x['text']).strip(),
                             message['text'])))


def main():
    global telegram_channel_id
    with open(chat_folder_path + 'result.json') as chat_file:
        chat_content = json.load(chat_file)
    if chat_content['type'] != 'public_channel':
        print('Not a channel.')
        return
    telegram_channel_id = chat_content['id']
    telegram_channel_name = decodeStr(chat_content['name'])
    telegram_db = database_connector.mySQLTelegramDB()
    search_response = telegram_db.get_id_from_telegram_id(False, telegram_channel_id)
    if not search_response:
        return
    if search_response > 0:
        channel_id = search_response
    else:
        add_response = telegram_db.add_group_channel(False, telegram_channel_id, telegram_channel_name)
        if not add_response:
            return
        channel_id = add_response
    from_msg_id = telegram_db.get_last_added_msg_id(channel_id)
    if not from_msg_id:
        return
    pending_msgs = list(filter(lambda x: x['id'] >= from_msg_id and x['type'] == 'message', chat_content['messages']))
    insert_msgs = list(map(lambda x: (channel_id, 'message', str(x['id']), getDateString(x['date']),
                                      getText(x), getMediaPath(x)), pending_msgs))
    rows_added = telegram_db.add_channel_chat_posts(insert_msgs)
    print('Chat posts added: ', rows_added)
    # Copy telegram chat to jaguar
    remote_path = str(telegram_channel_id) + '/'
    telegram_db.copy_folder_to_jaguar(chat_folder_path, remote_path)
    if input('Delete the data in local system?(y/n): ').lower() == 'y':
        os.system('rm -rf {}'.format(chat_folder_path))
    return


if __name__ == '__main__':
    main()
