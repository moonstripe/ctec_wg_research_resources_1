"""
    This stand-alone module checks for the frequency of particular accounts.

    TODO: I want a dict of weeks, each week having a frequency dict of accounts and posts originating from that account.
"""

import psycopg2
from psycopg2.extensions import AsIs
import datetime
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from dotenv import load_dotenv
import os

class AccountChecker:
    def __init__(self, table_name):
        load_dotenv()
        self.table_name = table_name
        self.db_host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_pass = os.getenv("DB_PASS")
        self.items = []
        self.week_dict = {}

    def get_date_and_from_id_from_db(self):
        self.items = []
        """ get date, from_id, and sentiment from table"""
        command = f"""SELECT date, from_id, positive, negative FROM %s ORDER BY date"""
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
            
            self.items = items

            return items
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close() 

    def make_dict_of_weeks(self):
        self.week_dict = {}
        for i in self.items:
            # destructure data
            timestamp = i[0]
            account_id = i[1]
            positive = i[2]
            negative = i[3]


            # convert timestamp to week
            week_iso = datetime.date.fromtimestamp(timestamp).isocalendar()
            week_str = f'{week_iso.year}-W{week_iso.week}'
            week_timestamp = datetime.datetime.strptime(week_str + "-1", "%Y-W%W-%w")
            week_timestamp_str = week_timestamp.strftime("%Y-%m-%d")
            # if there is no key for week, create entry for week
            if week_timestamp_str not in list(self.week_dict.keys()):
                self.week_dict[week_timestamp_str] = {}

            # if there is no key for account id in said week, create list for account id
            if account_id not in list(self.week_dict[week_timestamp_str].keys()):
                self.week_dict[week_timestamp_str][account_id] = []

            # add adjusted_sentiment to list
            self.week_dict[week_timestamp_str][account_id].append(positive-negative)
            

        for i in self.week_dict:
            for j in self.week_dict[i]:
                self.week_dict[i][j] = np.average(self.week_dict[i][j])
        
        # print(self.week_dict)
        return 

if __name__ == "__main__":
    a_c = AccountChecker("all_pmcworld")
    items = a_c.get_date_and_from_id_from_db()
    a_c.make_dict_of_weeks()

    pre_dates = ['2020-09-21','2020-09-28','2020-10-05','2020-10-12','2020-10-19','2020-10-26','2020-11-16','2020-11-30','2020-12-07','2020-12-14','2020-12-28','2021-01-04','2021-01-11','2021-01-18','2021-01-25','2021-02-01','2021-02-08','2021-02-15','2021-02-22','2021-03-01','2021-03-15','2021-03-29','2021-04-05','2021-04-12','2021-04-19','2021-05-03','2021-05-10','2021-05-17','2021-05-24','2021-05-31','2021-06-07','2021-06-14','2021-06-21']
    during_dates = ['2021-06-28','2021-07-05','2021-07-12','2021-07-19','2021-08-02','2021-08-09','2021-08-16','2021-08-23','2021-08-30','2021-09-06','2021-09-20','2021-09-27','2021-10-04','2021-10-11','2021-10-18','2021-10-25','2021-11-01','2021-11-08','2021-11-15','2021-11-22','2021-11-29','2021-12-06','2021-12-13','2021-12-20','2021-12-27','2022-01-03','2022-01-10','2022-01-17','2022-01-24','2022-01-31','2022-02-07','2022-02-14','2022-02-21']
    post_dates = ['2022-02-28','2022-03-07','2022-03-14','2022-03-21','2022-03-28','2022-04-04','2022-04-11','2022-04-18','2022-04-25','2022-05-02','2022-05-09','2022-05-16','2022-05-23','2022-05-30','2022-06-06','2022-06-13','2022-06-20','2022-06-27','2022-07-04','2022-07-11','2022-07-18','2022-07-25','2022-08-01','2022-08-08','2022-08-15','2022-08-22','2022-08-29','2022-09-05','2022-09-12','2022-09-19','2022-09-26','2022-10-03','2022-10-10']

    pre_list, during_list, post_list = [], [], []

    for i, e in enumerate(pre_dates):
        pre_list = pre_list + list(a_c.week_dict[pre_dates[i]].values())
        during_list = during_list + list(a_c.week_dict[during_dates[i]].values())
        post_list = post_list + list(a_c.week_dict[post_dates[i]].values())

    # print(pre_list)

    # pre_data = [ i/max(pre_list) for i in pre_list ]
    # during_data = [ i/max(during_list) for i in during_list ]
    # post_data = [ i/max(post_list) for i in post_list ]

    # print(pre_data, "\n", during_data, "\n", post_data)

    pre_post_list = [*pre_list, *post_list]

    pre_post_hist = np.histogram(pre_post_list, bins=100)
    during_hist = np.histogram(during_list, bins=100)

    print(sum(pre_post_hist[0]))
    print(sum(during_hist[0]))


    pre_post_hist_dist = stats.rv_histogram(pre_post_hist)
    dur_hist_dist = stats.rv_histogram(during_hist)



    # b = 100

    # plt.clf()
    # plt.title("Pre Frequency of Average Sentiments per Account")
    # plt.hist(pre_list, bins=b)
    # plt.savefig("images/pre_hist.png")

    # plt.clf()
    # plt.title("During Frequency of Average Sentiments per Account")
    # plt.hist(during_list, bins=b)
    # plt.savefig("images/during_hist.png")

    # plt.clf()
    # plt.title("Post Frequency of Average Sentiments per Account")
    # plt.hist(post_list, bins=b)
    # plt.savefig("images/post_hist.png")

    plt.clf()
    X = np.linspace(-1.0, 1.0, 100)
    plt.title("PDF from Template")
    plt.plot(X, pre_post_hist_dist.pdf(X), label='PDF')
    plt.savefig("images/pre_post_test.png")

    plt.clf()
    X = np.linspace(-1.0, 1.0, 100)
    plt.title("PDF from Template")
    plt.plot(X, dur_hist_dist.pdf(X), label='PDF')
    plt.savefig("images/dur_test.png")


    # print(items)