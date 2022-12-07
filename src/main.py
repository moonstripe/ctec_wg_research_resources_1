import os
import time
from datetime import datetime as dt, timedelta
from dotenv import load_dotenv
from posts import PostsCollection
from sentiment_analyzer import DoubleRubertAnalyzer
from groups import Group
from db import db
import logging

class CommentReader:
    def __init__(self, group_name):
        self.group_name = group_name
        logging.basicConfig(filename=f"/var/log/ctec-wag-main-{dt.now().strftime('%-m%d%Y%H:%M')}.log", encoding='utf-8', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
        load_dotenv()
        logging.info(f"Initialized comment reader.")

    def backup_databases(self):
        # TODO

        groups_db = db(table_name="groups")
        groups_db.backup_table(new_table_name=f"groups{dt.now().strftime('%-m%d%Y%H%M')}", old_table_name="groups")

        posts_db = db(table_name="posts")
        posts_db.backup_table(new_table_name=f"posts{self.group_name}{dt.now().strftime('%-m%d%Y%H%M')}", old_table_name="posts")

        comments_db = db(table_name="comments")
        comments_db.backup_table(new_table_name=f"comments{self.group_name}{dt.now().strftime('%-m%d%Y%H%M')}", old_table_name="comments")

        combiner = db(table_name=f"all_{self.group_name}")
        combiner.drop_tables()
        combiner.combine_posts_and_comments_into_all()

        logging.info(f"Finished backing up databases.")

        return

    def build_database(self):
        start_time = time.time()
        group_test = Group(self.group_name)

        id = group_test.run()

        posts_collection = PostsCollection(id)
        posts_collection.id_to_posts()

        print(len(posts_collection.posts))

        for i, e in enumerate(posts_collection.posts):
            posts_collection.save_post_to_db(e)
            posts_collection.single_post_to_comments(e['id'])
            logging.info(f"Total Progress: {i+1} posts / {len(posts_collection.posts)} {round(((i+1)/len(posts_collection.posts))*100, 2)}%")
        
        
        duration = str(timedelta(seconds=(time.time() - start_time)))

        logging.info(f"Finished building database for {self.group_name}. \n\n\tDuration: {duration} ")

    def sentiment_analysis(self):
        start_time = time.time()
        posts_db = db(table_name="posts")

        posts = posts_db.get_all()

        analyzer = DoubleRubertAnalyzer()

        for i, e in enumerate(posts):
            id = e[0]
            text = e[3]

            analyzer.set_text(text)
            # 11/24 trying s_predict instead
            sentiment = analyzer.s_predict()

            neu = sentiment[0][0]
            pos = sentiment[0][1]
            neg = sentiment[0][2]
            argmax = sentiment[1]
            
            posts_db.add_sentiment_to_db(id, neu, pos, neg, argmax)

            logging.info(f"Total Progress: {i+1} posts / {len(posts)} {round(((i+1)/len(posts))*100, 2)}%")

        logging.info(f"Finished posts analysis")


        comments_db = db(table_name="comments")

        comments = comments_db.get_all()

        for i, e in enumerate(comments):
            id = e[0]
            text = e[3]

            analyzer.set_text(text)
            sentiment = analyzer.s_predict()

            neu = sentiment[0][0]
            pos = sentiment[0][1]
            neg = sentiment[0][2]
            argmax = sentiment[1]
            
            comments_db.add_sentiment_to_db(id, neu, pos, neg, argmax)
            logging.info(f"Total Progress: {i+1} comments / {len(comments)} {round(((i+1)/len(comments))*100, 2)}%")

        logging.info(f"Finished comments analysis")

        duration = str(timedelta(seconds=(time.time() - start_time)))

        logging.info(f"Finished sentiment analysis for {self.group_name}. \n\n\tDuration: {duration} ")

if __name__ == "__main__":
    group_list = ['pmcworld']

    for i in group_list:
        reader = CommentReader(i)

        reader.build_database()
        reader.sentiment_analysis()
        reader.backup_databases()