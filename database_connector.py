# ChickenFryBiryani
import os
import time
import mysql
import mysql.connector
import codecs
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)


class mySQLTelegramDB:
    def __init__(self):
        self.m_sServerHost = "jaguar.cs.gsu.edu"
        self.m_sServerUser = "covid19"
        self.m_sServerPasswd = "uvNjdEbsn3t5uyiQkXgw"
        self.m_sServerDatabaseUser = "telegram_admin"
        self.m_sServerDatabasePasswd = "wowiNrNaTjObof5n6YGm"
        self.m_sServerDatabase = "telegram"
        self.m_sServerPort = "3306"
        self.telegram_conn = None
        self.telegram_cursor = None
        self.telegram_data_root = "/home/covid19/covid19telegram/"

    def get_db_connection(self):
        retries = 5
        while retries != 0:
            try:
                self.telegram_conn = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser,
                                                        passwd=self.m_sServerDatabasePasswd, charset="utf8mb4",
                                                        database=self.m_sServerDatabase, port=self.m_sServerPort)
                self.telegram_cursor = self.telegram_conn.cursor()
                return True
            except:
                time.sleep(5)
                retries -= 1
        print('Jaguar Connectivity issues.')
        return False

    def close_db_connection(self):
        # if self.telegram_cursor:
        #     self.telegram_cursor.close()
        if self.telegram_conn:
            self.telegram_conn.close()

    def get_id_from_telegram_id(self, isGroup, telegram_id):
        if not self.get_db_connection():
            return False
        g_type = 'group' if isGroup else 'channel'
        query = "SELECT group_channel_id FROM groups_channels WHERE group_or_channel = '{}' AND " \
                "telegram_id_of_gp_or_ch = '{}';".format(g_type, telegram_id)
        self.telegram_cursor.execute(query)
        count = self.telegram_cursor.fetchone()
        if not count:
            self.close_db_connection()
            return -1
        result_id = count[0]
        self.close_db_connection()
        return result_id

    def add_group_channel(self, isGroup, telegram_id, telegram_name):
        # False: Not added
        # >0 : id
        if not self.get_db_connection():
            return False
        g_type = 'group' if isGroup else 'channel'
        qry = "INSERT INTO groups_channels (group_or_channel_name, group_or_channel, telegram_id_of_gp_or_ch) VALUES " \
              "('{}', '{}', '{}');".format(telegram_name, g_type, telegram_id)
        self.telegram_cursor.execute(qry)
        if self.telegram_cursor.rowcount == 1:
            return_id = int(self.telegram_cursor.lastrowid)
            self.telegram_conn.commit()
            self.close_db_connection()
            return return_id
        self.telegram_conn.rollback()
        self.close_db_connection()
        return False

    def get_last_added_msg_id(self, channel_or_group_id):
        if not self.get_db_connection():
            return False
        query = "SELECT telegram_post_id FROM chat_posts WHERE group_channel_id = '{}' ORDER BY " \
                "post_id DESC LIMIT 1".format(channel_or_group_id)
        self.telegram_cursor.execute(query)
        if self.telegram_cursor.rowcount == 1:
            return_val = int(self.telegram_cursor.fetchone())
        else:
            return_val = -1
        self.close_db_connection()
        return return_val

    def add_channel_chat_posts(self, message_list):
        if not self.get_db_connection():
            return False
        query = """INSERT INTO chat_posts (group_channel_id, post_type, telegram_post_id, post_date, post_text, 
        media_path) VALUES (%s, %s, %s, %s, %s, %s)"""
        self.telegram_cursor.executemany(query, message_list)
        rows_inserted = self.telegram_cursor.rowcount
        self.telegram_conn.commit()
        self.close_db_connection()
        return rows_inserted

    def copy_folder_to_jaguar(self, local_path, remote_path):
        # check if the folder exists in jaguar. if not create
        cd = "sshpass -p '{}' rsync -ave ssh -r {} {}@{}:{}".format(self.m_sServerPasswd, local_path.replace(' ', "\ "),
                                                                    self.m_sServerUser, self.m_sServerHost,
                                                                    self.telegram_data_root + remote_path)
        os.system(cd)
