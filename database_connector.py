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

    def get_channel_id_from_telegram_id(self, telegram_id):
        if not self.get_db_connection():
            return False
        query = "SELECT channel_id FROM channel_list WHERE channel_telegram_id = '{}';".format(telegram_id)
        self.telegram_cursor.execute(query)
        count = self.telegram_cursor.fetchone()
        if not count:
            self.close_db_connection()
            return -1
        channel_id = count[0]
        self.close_db_connection()
        return channel_id

    def get_group_id_from_telegram_id(self, telegram_id):
        if not self.get_db_connection():
            return False
        query = "SELECT group_id FROM group_list WHERE group_telegram_id = '{}';".format(telegram_id)
        self.telegram_cursor.execute(query)
        count = self.telegram_cursor.fetchone()
        if not count:
            self.close_db_connection()
            return -1
        channel_id = count[0]
        self.close_db_connection()
        return channel_id

    def add_channel(self, telegram_id, telegram_name):
        if not self.get_db_connection():
            return False
        qry = "INSERT INTO channel_list (channel_name, channel_telegram_id) VALUES ('{}', '{}');".format(telegram_name,
                                                                                                         telegram_id)
        self.telegram_cursor.execute(qry)
        if self.telegram_cursor.rowcount == 1:
            channel_id = int(self.telegram_cursor.lastrowid)
            self.telegram_conn.commit()
            self.close_db_connection()
            return channel_id
        self.telegram_conn.rollback()
        self.close_db_connection()
        return False

    def add_group(self, telegram_id, telegram_name):
        if not self.get_db_connection():
            return False
        qry = "INSERT INTO group_list (group_name, group_telegram_id) VALUES ('{}', '{}');".format(telegram_name,
                                                                                                   telegram_id)
        self.telegram_cursor.execute(qry)
        if self.telegram_cursor.rowcount == 1:
            group_id = int(self.telegram_cursor.lastrowid)
            self.telegram_conn.commit()
            self.close_db_connection()
            return group_id
        self.telegram_conn.rollback()
        self.close_db_connection()
        return False

    def add_users_if_not_exists(self, users_info):
        if not self.get_db_connection():
            return False
        query = "INSERT INTO group_users (user_name, user_telegram_id) WITH temp(user_name, user_telegram_id) AS " \
                "(VALUES {}) SELECT temp.user_name, temp.user_telegram_id FROM temp LEFT JOIN group_users ON " \
                "group_users.user_telegram_id = temp.user_telegram_id " \
                "WHERE group_users.user_telegram_id IS NULL".format(str(tuple(users_info))[1:-1])
        self.telegram_cursor.execute(query)
        new_user_count = self.telegram_cursor.rowcount
        self.telegram_conn.commit()
        print('New users added:', new_user_count)
        id_query = "SELECT user_id FROM group_users where user_telegram_id in {};".format(str(tuple(map(lambda x: x[1],
                                                                                                        users_info))))
        self.telegram_cursor.execute(id_query)
        user_ids = list(map(lambda x: x[0], self.telegram_cursor.fetchall()))
        self.close_db_connection()
        return user_ids

    def get_last_added_msg_id_in_channel(self, channel_id):
        if not self.get_db_connection():
            return False
        query = "SELECT message_telegram_id FROM channel_messages WHERE channel_id = {} ORDER BY message_id DESC " \
                "LIMIT 1;".format(channel_id)
        self.telegram_cursor.execute(query)
        result = self.telegram_cursor.fetchall()
        if len(result) == 1:
            return_val = int(result[0][0])
        else:
            return_val = -1
        self.close_db_connection()
        return return_val

    def get_last_added_msg_id_in_group(self, group_id):
        if not self.get_db_connection():
            return False
        query = "SELECT message_telegram_id FROM group_messages WHERE group_id = {} ORDER BY message_id DESC " \
                "LIMIT 1;".format(group_id)
        self.telegram_cursor.execute(query)
        result = self.telegram_cursor.fetchall()
        if len(result) == 1:
            return_val = int(result[0][0])
        else:
            return_val = -1
        self.close_db_connection()
        return return_val

    def add_channel_messages(self, message_list):
        if not self.get_db_connection():
            return False
        query = """INSERT INTO channel_messages (channel_id, message_type, message_telegram_id, posted_date, 
        message_text, media_path) VALUES (%s, %s, %s, %s, %s, %s)"""
        self.telegram_cursor.executemany(query, message_list)
        rows_inserted = self.telegram_cursor.rowcount
        self.telegram_conn.commit()
        self.close_db_connection()
        return rows_inserted

    def add_group_messages(self, message_list):
        if not self.get_db_connection():
            return False
        query = """INSERT INTO group_messages (group_id, message_type, message_telegram_id, user_id, 
        reply_to_message_telegram_id, posted_date, message_text, media_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        self.telegram_cursor.executemany(query, message_list)
        rows_inserted = self.telegram_cursor.rowcount
        self.telegram_conn.commit()
        self.close_db_connection()
        return rows_inserted

    def copy_folder_to_jaguar(self, local_path, remote_path, is_group):
        # check if the folder exists in jaguar. if not create
        folder = "groups/" if is_group else "channels/"
        cd = "sshpass -p '{}' rsync -ave ssh -r {} {}@{}:{}".format(self.m_sServerPasswd, local_path.replace(' ', "\ "),
                                                                    self.m_sServerUser, self.m_sServerHost,
                                                                    self.telegram_data_root + folder + remote_path)
        os.system(cd)
