import os
from datetime import datetime as dt
from requests import request
from dotenv import load_dotenv
import logging
from db import db

class PostsCollection:
    def __init__(self, parent: int):
        self.parent: int = parent
        self.posts = []

        # init databases

        p_db = db(table_name="posts")
        p_db.drop_and_create()
        c_db = db(table_name="comments")
        c_db.drop_and_create()

        self.posts_db = p_db
        self.comments_db = c_db

    def id_to_posts(self, counter=0, arr=[]):
        if len(self.posts) > 0:
            logging.info(f"Post list already pulled for id: {self.parent}.")
            return 

        base = "https://api.vk.com/method/wall.get?v=5.131"
        params = f"&owner_id=-{str(self.parent)}&count={100}&offset={counter}&access_token={os.getenv('VK_APP_TOKEN')}"
        
        try:
            res = request("POST", base+params).json()
        except Exception as e:
            logging.critical(e)

        if 'response' not in list(res.keys()):
            logging.error(f'hidden member list for parent: {self.parent}')
            return []

        new_count = counter + len(res['response']['items'])
        logging.info(f"\t We have made it through {new_count} out of {res['response']['count']} ({str(round(new_count/res['response']['count'], 4)*100)}%) of all posts in {self.parent}.")

 
        if len(res['response']['items']) < 100:
            self.posts = arr + res['response']['items']
            return self.posts

        return self.id_to_posts(new_count, arr+res['response']['items'])

    def thread_untangler(self, start_comment_id, counter=0, arr=[]):
        base = "https://api.vk.com/method/wall.getComments?v=5.131"
        params = f"&owner_id=-{str(self.parent)}&comment_id={start_comment_id}&count={100}&offset={counter}&need_likes=1&access_token={os.getenv('VK_APP_TOKEN')}"
        
        try:
            res = request("POST", base+params).json()
        except Exception as e:
            logging.critical(e)

        if 'response' not in list(res.keys()):
            logging.error(f'hidden member list for self.parent: {self.parent}')
            return []


        new_count = counter + len(res['response']['items'])
        logging.info(f"\t We have made it through {new_count} out of {res['response']['count']} ({str(round(new_count/res['response']['count'], 4)*100)}%) of all thread comments in {start_comment_id}.")

 
        if len(res['response']['items']) < 100:
            new_arr = arr + res['response']['items']
            return new_arr

        return self.thread_untangler(start_comment_id, new_count, arr+res['response']['items'])

    def single_post_to_comments(self, post_id, counter=0, arr=[]):
        # if self.parent != 0:
        #     logging.info(f"ID has already been pulled for group_name, {self.group_name}.")
        #     return 


        base = "https://api.vk.com/method/wall.getComments?v=5.131"
        params = f"&owner_id=-{str(self.parent)}&post_id={post_id}&count={100}&offset={counter}&need_likes=1&access_token={os.getenv('VK_APP_TOKEN')}"
        
        try:
            res = request("POST", base+params).json()
        except Exception as e:
            logging.critical(e)

        if 'error' in res.keys():
            print(res['error'])

        if counter == 0:
            logging.info(f"We identified {res['response']['count']} comments in the thread.")

        
        if len(res['response']['items']) > 0:
            for e in res['response']['items']:
                if len(e['text']) > 0:
                    self.save_comment_to_db(e, post_id)

                if e['thread']['count'] > 0:
                    logging.info(f"We identified {e['thread']['count']} comments in the thread.")
                    thread = self.thread_untangler(e['id'], 0, [])
                    for j in thread:
                        if len(j['text']) > 0:
                            self.save_comment_to_db(j, post_id)

            new_count = counter + len(res['response']['items'])
            logging.info(f"\t We have made it through {new_count} out of {res['response']['count']} ({str(round(new_count/res['response']['count'], 4)*100)}%) of all comments in {post_id}.")


        if len(res['response']['items']) < 100:
            new_arr = arr + res['response']['items']
            return new_arr

        return self.single_post_to_comments(post_id, new_count, arr+res['response']['items'])

    def save_post_to_db(self, post):
        
        id = self.posts_db.insert_post(
            post['id'], 
            post['date'], 
            post['text'] if len(post['text']) > 0 else '',
            post['owner_id'],
            post['likes']['count'],
            post['from_id'] if 'from_id' in list(post.keys()) else 0
            )
        logging.info(f'Saved post {self.parent} to DB with ID {id}')
        return

    def save_comment_to_db(self, comment, parent_id):

        id = self.comments_db.insert_comment(
            comment['id'], 
            comment['date'], 
            comment['text'] if len(comment['text']) > 0 else '',
            comment['parents_stack'][0] if len(comment['parents_stack']) > 0 else parent_id,
            comment['likes']['count'] if 'likes' in comment.keys() and 'count' in comment['likes'].keys() else -1,
            comment['from_id'] if 'from_id' in list(comment.keys()) else 0
            )
        logging.info(f"Saved comments from parent {comment['parents_stack'][0] if len(comment['parents_stack']) > 0 else parent_id} to DB with ID {id}")
        return

if __name__ == "__main__":
    load_dotenv()
    pmcposts = PostsCollection(188474281)
    pmcposts.id_to_posts()

    print(len(pmcposts.posts))

    for i, e in enumerate(pmcposts.posts):
        pmcposts.save_post_to_db(e)
        pmcposts.single_post_to_comments(e['id'])
        logging.info(f"Total Progress: {i} posts / {len(pmcposts.posts)} {round(100*(i/len(pmcposts.posts)), 2)}%")
    