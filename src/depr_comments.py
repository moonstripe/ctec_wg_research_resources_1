import os
from time import time
from requests import post, request
from dotenv import load_dotenv
import logging
from db import db

# dep

class Comments:
    def __init__(self, parent: int):
        self.parent: int = parent
        self.comments = []

    def thread_untangler(self, start_comment_id, counter=0, arr=[]):
        base = "https://api.vk.com/method/wall.getComments?v=5.131"
        params = f"&owner_id=-{str(self.parent)}&comment_id={start_comment_id}&count={10}&offset={counter}&access_token={os.getenv('VK_APP_TOKEN')}"
        res = request("POST", base+params).json()

        if 'response' not in list(res.keys()):
            logging.error(f'hidden member list for self.parent: {self.parent}')
            return []

        print(res['response'])

        new_count = counter + len(res['response']['items'])
        logging.info(f"\t We have made it through {new_count} out of {res['response']['count']} ({str(round(new_count/res['response']['count'], 4)*100)}%) of all thread comments in {start_comment_id}.")

 
        if len(res['response']['items']) < 10:
            arr = arr + res['response']['items']
            return arr

        return self.thread_untangler(start_comment_id, new_count, arr+res['response']['items'])

    def single_post_to_comments(self, counter=0, arr=[]):
        # if self.parent != 0:
        #     logging.info(f"ID has already been pulled for group_name, {self.group_name}.")
        #     return 


        base = "https://api.vk.com/method/wall.getComments?v=5.131"
        params = f"&owner_id={str(self.parent)}&post_id={self.parent}&count={100}&offset={counter}&access_token={os.getenv('VK_APP_TOKEN')}"
        res = request("POST", base+params).json()


        for i, e in enumerate(res['response']['items']):
            if e['thread']['count'] > 0:
                logging.info(f"We identified {e['thread']['count']} comments in the thread.")
                thread = self.thread_untangler(e['id'], 0, [])
                for i in thread:
                    self.save_to_db(i)


        return

    def save_to_db(self, comment):
        database = db(table_name='posts')

    

        id = database.insert_comment(
            comment['id'], 
            comment['date'], 
            comment['text'] if len(comment['text']) > 0 else '',
            comment['owner_id'],
            comment['likes']['count'] if 'likes' in comment.keys() and 'count' in comment['likes'].keys() else -1
            )
        logging.info(f'Saved comments from post {self.parent} to DB with ID {id}')
        return

if __name__ == "__main__":
    logging.basicConfig(filename='posts.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')
    load_dotenv()
    data = db(table_name='posts')
    posts = data.get_all(table_name='posts')
    for i, e in enumerate(posts):
        postId = e[1]
        comments = Comments(postId)
        comments.single_post_to_comments()

