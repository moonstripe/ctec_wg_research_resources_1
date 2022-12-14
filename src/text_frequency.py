"""
    This stand-alone module compiles word frequency lists and displays them as images.

"""

import psycopg2
from psycopg2.extensions import AsIs
import datetime
import time
import json
import re
import nltk
from nltk.stem.snowball import SnowballStemmer 
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
from translate import Translator
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import numpy as np

class TextFrequency:
    def __init__(self, table_name):
        nltk.download('punkt')
        load_dotenv()
        f = open('stopwords.json')
        self.stop_words_arr = json.load(f)
        self.table_name = table_name
        self.db_host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_pass = os.getenv("DB_PASS")
        self.stemmer = SnowballStemmer("russian")
        self.translator = Translator(to_lang="en", from_lang="ru")
        self.all_text = ''
        self.items = []
        self.week_dict = {}
        self.rel_freq = {}
        self.time_values = []
        self.pre_dates = ['2020-09-21','2020-09-28','2020-10-05','2020-10-12','2020-10-19','2020-10-26','2020-11-16','2020-11-30','2020-12-07','2020-12-14','2020-12-28','2021-01-04','2021-01-11','2021-01-18','2021-01-25','2021-02-01','2021-02-08','2021-02-15','2021-02-22','2021-03-01','2021-03-15','2021-03-29','2021-04-05','2021-04-12','2021-04-19','2021-05-03','2021-05-10','2021-05-17','2021-05-24','2021-05-31','2021-06-07','2021-06-14','2021-06-21']
        self.during_dates = ['2021-06-28','2021-07-05','2021-07-12','2021-07-19','2021-08-02','2021-08-09','2021-08-16','2021-08-23','2021-08-30','2021-09-06','2021-09-20','2021-09-27','2021-10-04','2021-10-11','2021-10-18','2021-10-25','2021-11-01','2021-11-08','2021-11-15','2021-11-22','2021-11-29','2021-12-06','2021-12-13','2021-12-20','2021-12-27','2022-01-03','2022-01-10','2022-01-17','2022-01-24','2022-01-31','2022-02-07','2022-02-14','2022-02-21']
        self.post_dates = ['2022-02-28','2022-03-07','2022-03-14','2022-03-21','2022-03-28','2022-04-04','2022-04-11','2022-04-18','2022-04-25','2022-05-02','2022-05-09','2022-05-16','2022-05-23','2022-05-30','2022-06-06','2022-06-13','2022-06-20','2022-06-27','2022-07-04','2022-07-11','2022-07-18','2022-07-25','2022-08-01','2022-08-08','2022-08-15','2022-08-22','2022-08-29','2022-09-05','2022-09-12','2022-09-19','2022-09-26','2022-10-03','2022-10-10']
        self.pre_words = ''
        self.during_words = ''
        self.post_words = ''
        self.dict_of_rel_freqs_per_word = {}

    def get_date_and_text_from_id_from_db(self):
        self.items = []
        """ get date, from_id, and sentiment from table"""
        command = f"""SELECT date, text FROM %s ORDER BY date"""
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
        total = len(self.items)
        temp_duration_arr = []
        for n, i in enumerate(self.items):
            start = datetime.datetime.timestamp(datetime.datetime.now())
            # destructure data
            timestamp = i[0]
            text = i[1]

            # convert timestamp to week
            week_iso = datetime.date.fromtimestamp(timestamp).isocalendar()
            week_str = f'{week_iso.year}-W{week_iso.week}'
            week_timestamp = datetime.datetime.strptime(week_str + "-1", "%Y-W%W-%w")
            week_timestamp_str = week_timestamp.strftime("%Y-%m-%d")
            # if there is no key for week, create empty string for week
            if week_timestamp_str not in list(self.week_dict.keys()):
                self.week_dict[week_timestamp_str] = ""

            # clean text

            # remove text in square brackets
            text = re.sub("[\(\[].*?[\)\]]", "", text)

            words_in_text = text.split(' ')

            new_text = []

            for i in words_in_text:
                if i not in self.stop_words_arr:
                    cleaned_word = re.sub(r'(?:(?!\u0301)[\W\d_])+', ' ', i)
                    cleaned_word = re.sub(r'\s+', ' ', cleaned_word) 
                    stemmed_word = self.stemmer.stem(cleaned_word.lower()).replace(' ', '')
                    if len(stemmed_word) > 3:
                        new_text.append(stemmed_word)

            # remove whitespace
            while("" in new_text):
                new_text.remove("")
            
            # non-cyrillic out
            pattern = re.compile(r'[a-zA-Z]')
            new_text = filter(lambda x: not pattern.search(x), new_text)

            # remove names of respondees
            new_text = filter(lambda x:x[0:2]!='id', new_text)
            new_text = filter(lambda x:x[0:2]!='ид', new_text)

            new_text = ' '.join(new_text)

            # join text to week entry and add to relevant date period
            self.week_dict[week_timestamp_str] = f'{self.week_dict[week_timestamp_str]} {new_text}'

            # pre
            if week_timestamp_str in self.pre_dates:
                self.pre_words = f'{self.pre_words} {new_text}'
            # during
            elif week_timestamp_str in self.during_dates:
                self.during_words = f'{self.during_words} {new_text}'
            # post
            elif week_timestamp_str in self.post_dates:
                self.post_words = f'{self.post_words} {new_text}'

            est_duration = (total * (datetime.datetime.timestamp(datetime.datetime.now()) - start)) - ((n+1) * (datetime.datetime.timestamp(datetime.datetime.now()) - start))
            temp_duration_arr.append(est_duration)

            if (n % 50 == 0):
                average_duration = np.average(temp_duration_arr)

                temp_duration_arr = []
                print(str(datetime.timedelta(seconds=average_duration)))
                

    def most_common_word_per_week(self):
        """
            This function takes the week dict, and produces common words
        """
        all_values = {}

        for k in self.week_dict:
            week_words=word_tokenize(self.week_dict[k], language="russian")
            freq_dist = FreqDist(week_words)
            week_word_freq = freq_dist.most_common(10)

            rel_week_word_freq = []

            total_freq_in_top_n = np.sum([p[1] for p in week_word_freq])
            # total_freq = freq_dist.N()

            
            # construct relative frequencies, while also building the rel_freq_over_time_per_word metric

            for n, i in enumerate(week_word_freq):
                # build the rel_week_word_freq
                relative_frequency = round(i[1]/total_freq_in_top_n, 2)
                rel_week_word_freq.append((i[0], relative_frequency))
            self.time_values.append(k)
            # # english translations
            # eng_week_word_freq = []
            # # in for loop:
            # time.sleep(1)
            # english = self.translator.translate(russian)
            # eng_week_word_freq.append((english, frequency))

            # relative frequency
            all_values[k] = rel_week_word_freq

        self.rel_freq = all_values


    def draw_relative_frequency_chart(self):

        # all words
        # for week in list(self.rel_freq.keys()):
        #     for word in list(zip(*self.rel_freq[week]))[0]:
        #         if word not in list(self.dict_of_rel_freqs_per_word.keys()):
        #             self.dict_of_rel_freqs_per_word[word] = []


        # all time
        # for week in self.time_values:
        #     word_freq_arr = self.rel_freq[week]
        #     word_arr = list(zip(*word_freq_arr))[0]
        #     freq_arr = list(zip(*word_freq_arr))[1]
        #     for word in list(self.dict_of_rel_freqs_per_word.keys()):
        #         if word in word_arr:
        #             i = word_arr.index(word)
        #             self.dict_of_rel_freqs_per_word[word].append(freq_arr[i])
        #         else:
        #             self.dict_of_rel_freqs_per_word[word].append(0)
        # top n words
        top_n = 5

        marker_arr = ['o', 'p', 'P', '*', 'h']

        # init fig
        plt.clf()
        fig, axs = plt.subplots(3, 1, constrained_layout=True)
        fig.set_figwidth(10)
        fig.set_figheight(12)
        fig.set_dpi(80)


        # pre graph
        # word list
        # init the word list
        top_words=word_tokenize(self.pre_words, language="russian")
        top_word_freq = FreqDist(top_words).most_common(top_n)

        # init dict_of_rel...
        self.dict_of_rel_freqs_per_word = {}
        for word in list(zip(*top_word_freq))[0]:
                if word not in list(self.dict_of_rel_freqs_per_word.keys()):
                    self.dict_of_rel_freqs_per_word[word] = []


        for week in self.pre_dates:
            word_freq_arr = self.rel_freq[week]
            word_arr = list(zip(*word_freq_arr))[0]
            freq_arr = list(zip(*word_freq_arr))[1]
            for word in list(self.dict_of_rel_freqs_per_word.keys()):
                if word in word_arr:
                    i = word_arr.index(word)
                    self.dict_of_rel_freqs_per_word[word].append(freq_arr[i])
                else:
                    self.dict_of_rel_freqs_per_word[word].append(0)

        axs[0].set_title('Before')
        for index, i in enumerate(list(self.dict_of_rel_freqs_per_word.keys())):
            print(f'word: {i} \nlength: {len(self.dict_of_rel_freqs_per_word[i])}')
            print(f'length of time_values: {len(self.pre_dates)}')
            print(f'validation = {len(self.pre_dates) == len(self.dict_of_rel_freqs_per_word[i])}')

            axs[0].plot(self.pre_dates, self.dict_of_rel_freqs_per_word[i], label=i, marker=marker_arr[index])

        axs[0].legend(loc="lower left", ncol=5)
        axs[0].set_xlabel('Week')
        axs[0].set_ylabel('Relative Frequency')
        axs[0].tick_params(axis="x", size = 8, labelrotation = 15)
        label_array_pre = self.pre_dates[::10]
        axs[0].set_xticks(label_array_pre)

        # during graph
        top_words=word_tokenize(self.during_words, language="russian")
        top_word_freq = FreqDist(top_words).most_common(top_n)

        # init dict_of_rel...
        self.dict_of_rel_freqs_per_word = {}
        for word in list(zip(*top_word_freq))[0]:
                if word not in list(self.dict_of_rel_freqs_per_word.keys()):
                    self.dict_of_rel_freqs_per_word[word] = []


        for week in self.during_dates:
            word_freq_arr = self.rel_freq[week]
            word_arr = list(zip(*word_freq_arr))[0]
            freq_arr = list(zip(*word_freq_arr))[1]
            for word in list(self.dict_of_rel_freqs_per_word.keys()):
                if word in word_arr:
                    i = word_arr.index(word)
                    self.dict_of_rel_freqs_per_word[word].append(freq_arr[i])
                else:
                    self.dict_of_rel_freqs_per_word[word].append(0)

        # test
        axs[1].set_title('Between')
        for index, i in enumerate(list(self.dict_of_rel_freqs_per_word.keys())):
            print(f'word: {i} \nlength: {len(self.dict_of_rel_freqs_per_word[i])}')
            print(f'length of time_values: {len(self.during_dates)}')
            print(f'validation = {len(self.during_dates) == len(self.dict_of_rel_freqs_per_word[i])}')

            axs[1].plot(self.during_dates, self.dict_of_rel_freqs_per_word[i], label=i, marker=marker_arr[index])
        
        axs[1].legend(loc="lower left", ncol=5)
        axs[1].set_xlabel('Week')
        axs[1].set_ylabel('Relative Frequency')
        axs[1].tick_params(axis="x", size = 8, labelrotation = 15)
        label_array_dur = self.during_dates[::10]
        axs[1].set_xticks(label_array_dur)

        # post graph
        top_words=word_tokenize(self.post_words, language="russian")
        top_word_freq = FreqDist(top_words).most_common(top_n)

        # init dict_of_rel...
        self.dict_of_rel_freqs_per_word = {}
        for word in list(zip(*top_word_freq))[0]:
                if word not in list(self.dict_of_rel_freqs_per_word.keys()):
                    self.dict_of_rel_freqs_per_word[word] = []


        for week in self.post_dates:
            word_freq_arr = self.rel_freq[week]
            word_arr = list(zip(*word_freq_arr))[0]
            freq_arr = list(zip(*word_freq_arr))[1]
            for word in list(self.dict_of_rel_freqs_per_word.keys()):
                if word in word_arr:
                    i = word_arr.index(word)
                    self.dict_of_rel_freqs_per_word[word].append(freq_arr[i])
                else:
                    self.dict_of_rel_freqs_per_word[word].append(0)

        # init graph
        axs[2].set_title('After')
        for index, i in enumerate(list(self.dict_of_rel_freqs_per_word.keys())):
            # test
            print(f'word: {i} \nlength: {len(self.dict_of_rel_freqs_per_word[i])}')
            print(f'length of time_values: {len(self.post_dates)}')
            print(f'validation = {len(self.post_dates) == len(self.dict_of_rel_freqs_per_word[i])}')
            axs[2].plot(self.post_dates, self.dict_of_rel_freqs_per_word[i], label=i, marker=marker_arr[index])
        
        axs[2].legend(loc="lower left", ncol=5)
        axs[2].set_xlabel('Week')
        axs[2].set_ylabel('Relative Frequency')
        axs[2].tick_params(axis="x", size = 8, labelrotation = 15)
        label_array_post = self.post_dates[::10]
        axs[2].set_xticks(label_array_post)

        plt.savefig('images/frequency.png')




    # def draw_wordclouds_from_weekdict(self):
    #     for k in self.week_dict:
    #         wc = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(self.week_dict[k])
            
    #         # hello = wc.to_array()

    #         # print(hello)
            
    #         plt.clf()
    #         plt.figure()
    #         plt.imshow(wc, interpolation="bilinear")
    #         plt.axis("off")
    #         plt.savefig(f'images/wordcloud{k}.png')
    #         plt.close()

    

if __name__ == "__main__":
    t_f = TextFrequency("all_pmcworld")
    t_f.get_date_and_text_from_id_from_db()
    t_f.make_dict_of_weeks()
    t_f.most_common_word_per_week()
    t_f.draw_relative_frequency_chart()
    print('running text_frequency')