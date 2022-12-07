import psycopg2
from psycopg2.extensions import AsIs
import os
from dotenv import load_dotenv

class db:
    """
        This module helps organize and implement interactivity with the PostgreSQL database.
    """
    def __init__(self, **kwargs):
        load_dotenv()
        if (len(kwargs.keys()) < 2):
            self.db_host = os.getenv("DB_HOST")
            self.db_name = os.getenv("DB_NAME")
            self.db_user = os.getenv("DB_USER")
            self.db_pass = os.getenv("DB_PASS")
        if (len(list(kwargs.keys())) == 4):
            self.db_host = kwargs['db_host']
            self.db_name = kwargs['db_name']
            self.db_user = kwargs['db_user']
            self.db_pass = kwargs['db_pass']

        self.conn = None
        print('table name', kwargs['table_name'])
        self.table_name = kwargs['table_name']

    def drop_and_create(self):
        self.drop_tables()
        self.create_tables()
        print(f"database {self.table_name} initialized")

    def test_local_connection(self):
        print("Starting Local DB Test:\n")
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            # create a cursor
            cur = self.conn.cursor()

            # execute a statement
            print("Local DB Test: Successful")
            print('PostgreSQL database version:')
            cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            print(db_version[0], "\n")

            print('Printing local tables:')
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
            tables = cur.fetchall()
            for i in tables:
                print(i[0])

            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close() 
            
    def create_tables(self):
        """ create tables in the PostgreSQL database"""
        if self.table_name == "groups":
            command = f"""CREATE TABLE %s (
                    id SERIAL PRIMARY KEY,
                    local_id INTEGER,
                    name VARCHAR(255),
                    members INTEGER
                )
                """
        elif self.table_name == "posts" or self.table_name == "comments":
            command = f"""CREATE TABLE %s (
                    id SERIAL PRIMARY KEY,
                    local_id INTEGER,
                    date INTEGER,
                    text VARCHAR(25000),
                    parent INTEGER,
                    likes INTEGER,
                    from_id INTEGER,
                    neutral REAL,
                    positive REAL,
                    negative REAL,
                    argmax INTEGER
                )
                """            
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (AsIs(self.table_name),))
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()

            print('added new table')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()

    def drop_tables(self):
        """ drop tables in the PostgreSQL database"""
        command = f"""DROP TABLE IF EXISTS %s"""
            
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (AsIs(self.table_name),))
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()

            print('succesfully dropped table')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()
              
    def backup_table(self, new_table_name, old_table_name):
        """ backup tables in the PostgreSQL database"""
        command = f"""CREATE TABLE %s AS TABLE %s"""
            
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (AsIs(new_table_name), AsIs(old_table_name),))
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()

            print('succesfully backed up table')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()   

            
    def combine_posts_and_comments_into_all(self):
        """ combine tables posts and comments in the PostgreSQL database"""
        command = f"""
            CREATE TABLE %s AS
                (
                    SELECT * FROM posts WHERE argmax >= 0
                    UNION
                    SELECT * FROM comments WHERE argmax >= 0
                );
        """

        try:
            self.conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (AsIs(self.table_name),))
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()

            print('succesfully combined tables')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close() 


    def insert_group(self, name, id):
        """ add new group to group table"""
        command = f"""INSERT INTO groups(name, local_id)
                VALUES (%s,%s) RETURNING local_id"""
            
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (name, id,))
            id_of_new_row = cur.fetchone()[0]
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()      

            return id_of_new_row      

    def insert_post(self, id, date, text, parent, likes, from_id):
        """ add new post to posts table"""
        command = f"""INSERT INTO posts(local_id, date, text, parent, likes, from_id)
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING local_id"""
            
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (id, date, text, parent, likes, from_id,))
            id_of_new_row = cur.fetchone()[0]
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()      

            return id_of_new_row  

    def insert_comment(self, id, date, text, parent, likes, from_id):
        """ add new group to comments table"""
        command = f"""INSERT INTO comments(local_id, date, text, parent, likes, from_id)
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING local_id"""
            
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (id, date, text, parent, likes, from_id,))
            id_of_new_row = cur.fetchone()[0]
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()

            return id_of_new_row
    
    def get_all(self):
        """ get all posts from posts table"""
        command = f"""SELECT * FROM %s"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass
            )
            cur = self.conn.cursor()
            cur.execute(command, (AsIs(self.table_name),))
            items = cur.fetchall()
            cur.close()
            self.conn.commit()

            return items
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()  

    def add_sentiment_to_db(self, id, neutral, positive, negative, argmax):
        """ update values with sentiment """
        command = f"""UPDATE %s 
                    SET neutral = %s,
                        positive = %s,
                        negative = %s,
                        argmax = %s
                    WHERE id = %s 
                    RETURNING local_id"""
            
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass)

            cur = self.conn.cursor()
            # create table one by one
            cur.execute(command, (AsIs(self.table_name), neutral, positive, negative, argmax, id,))
            id_of_new_row = cur.fetchone()[0]
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()

            return id_of_new_row

 

if __name__ == '__main__':
    database = db(table_name="posts")

    database.drop_tables()
    database.create_tables()