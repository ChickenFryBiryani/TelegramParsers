# ChickenFryBiryani

import os
import json
import datetime
import database_connector

chat_folder_path = "/home/rob/Downloads/Telegram Desktop/ChatExport_2020-10-29/"
remote_telegram_root = "/home/covid19/covid19telegram/"
m_sServerPass = "uvNjdEbsn3t5uyiQkXgw"
local_path = chat_folder_path
m_sServerUser = "covid19"
m_sServerHost = "jaguar.cs.gsu.edu"
telegram_group_id = ""


def getDateString(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d%H%M%S')


def getMediaPath(message):
    if 'photo' in message:
        return str(telegram_group_id) + '/' + chat_folder_path.split('/')[-2].split('_')[1] + '/' + message['photo']
    if 'file' in message:
        return str(telegram_group_id) + '/' + chat_folder_path.split('/')[-2].split('_')[1] + '/' + message['file']
    return ''


def getText(message):
    if 'text' not in message or message['text'] == '':
        return ''
    if type(message['text']) == str:
        return message['text']
    return ' '.join(list(map(lambda x: x.strip() if type(x) == str else x['text'].strip(), message['text'])))


def main():
    global telegram_group_id
    with open(chat_folder_path + 'result.json') as chat_file:
        chat_content = json.load(chat_file)
    if chat_content['type'] != 'public_supergroup':
        print('Not a Group.')
        return
    telegram_group_id = chat_content['id']
    telegram_group_name = chat_content['name']
    telegram_db = database_connector.mySQLTelegramDB()
    search_response = telegram_db.get_group_id_from_telegram_id(telegram_group_id)
    if not search_response:
        return
    if search_response > 0:
        group_id = search_response
    else:
        add_response = telegram_db.add_group(telegram_group_id, telegram_group_name)
        if not add_response:
            return
        group_id = add_response
    from_msg_id = telegram_db.get_last_added_msg_id_in_group(group_id)
    if not from_msg_id:
        return
    pending_msgs = list(filter(lambda x: x['id'] > from_msg_id, chat_content['messages']))
    if len(pending_msgs) == 0:
        print('No new messages.')
        if input('Delete the data in local system?(y/n): ').lower() == 'y':
            os.system('rm -rf {}'.format(chat_folder_path.replace(' ', '\ ')))
        return
    # Add all the new users to group_users table
    from_users = list(set(map(lambda x: (x['from'], x['from_id']) if 'from' in x else (x['actor'], x['actor_id']),
                              pending_msgs)))
    telegram_ids = list(map(lambda x: x[1], from_users))
    user_ids = telegram_db.add_users_if_not_exists(from_users)
    new_msgs = list(map(lambda x: (group_id, 'message' if x['type'] == 'message' else x['action'], str(x['id']),
                                   user_ids[telegram_ids.index(x['from_id'] if 'from_id' in x else x['actor_id'])],
                                   x['reply_to_message_id'] if 'reply_to_message_id' in x else '',
                                   getDateString(x['date']), getText(x), getMediaPath(x)), pending_msgs))
    rows_added = telegram_db.add_group_messages(new_msgs)
    print('Chat posts added: ', rows_added)
    # Copy telegram chat to jaguar
    remote_path = str(telegram_group_id) + '/'
    telegram_db.copy_folder_to_jaguar(chat_folder_path, remote_path)
    if input('Delete the data in local system?(y/n): ').lower() == 'y':
        os.system('rm -rf {}'.format(chat_folder_path.replace(' ', '\ ')))
    return


if __name__ == '__main__':
    main()
