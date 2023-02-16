# Wagner Group Research Repository

![Middlebury Logo](https://avatars.githubusercontent.com/u/65674242?s=200&v=4)

*This project was conducted by a team of researchers working at the Center on [Terrorism, Extremism, and Counter Terrorism](https://www.middlebury.edu/institute/tags/ctec) at the [Middlebury Institute of International Studies at Monterey](https://www.middlebury.edu/institute/).*

## Introduction
These resources were developed in order to perform research into the Wagner Group in Russia. They serve as a means of replicating the data found in the corresponding paper.

### Table of Contents
- [Wagner Group Research Repository](#wagner-group-research-repository)
  - [Introduction](#introduction)
    - [Table of Contents](#table-of-contents)
  - [Guide to Included Scripts](#guide-to-included-scripts)
  - [Guide to Included Images](#guide-to-included-images)
  - [Usage](#usage)

## Guide to Included Scripts

All important Python scripts are included in `src/`.

```
...
├─ src/
│  ├─ db.py <- storing and pulling from the database
│  ├─ establishing_timeline.py <- plotting Graph 1
│  ├─ groups.py <- storing information in groups table
│  ├─ main.py <- main controller
│  ├─ posts.py <- controller for navigating VK API related to posts and comments
│  ├─ sentiment_analyzer.py <- controller for sentiment analysis model
│  ├─ text_frequency.py <- plotting Graph 2
...
```

## Guide to Included Images

As part of our exploratory analysis of VK communities related to Wagner, we recorded some screenshots, as well as a link to the context. 
- **1.png:** [Comment about moderating the group because there are too many Nazies among members](https://vk.com/wall-196348570_94318?reply=94401)
- **2.png:** [Mother who is proud of her deceased son who fought for Wagner](https://vk.com/wall-160233565_172542?reply=172914&thread=172858)
- **3.png:** [Сима-ленд - Sima-Land Russian online retail shop, allegedly related to Wagner. Post is about Wagner-support flash mob in the company’s headquarters](https://vk.com/wall-160233565_172542) 
- **4.png:** [Every country has its own values meme](https://vk.com/wall-160233565_172542?reply=172775&thread=172559)
- **5.png:** [Вы лучшие - you’re the best](https://vk.com/wall-196348570_138906?reply=138920)
- **6.png:** [Красавцы - literally handsome, meaning “well done,” a poem to Wagner](https://vk.com/wall-196348570_138906?reply=138977)
- **7.png:** [Cat in the barracks - positive image creation](https://vk.com/wall-196348570_137730)
- **8.png:** [Another Cat](https://vk.com/wall-196348570_136890)
- **9.png:** [Wagner celebrates the end of the operation “Barkhane” in Mali](https://vk.com/wall-196348570_107266)
- **10.png:** [Wagner statistics: 2000+ photos with saved children, 500 rescued animals, prisoner amnesty](https://vk.com/wall-196348570_107080)
- **11.png:** [ЗП - paycheck - Complaint about not being paid](https://vk.com/wall-188474281_159535?reply=159952)

## Usage

In order to replicate the results in the paper, you will need to install all necessary dependencies. These dependencies have been helpfully summarized in `requirements.txt`. (The following instructions assume you've initialized a PostgreSQL database to store all of the content. Official instructions on using PostgreSQL can be found [here](https://www.postgresql.org/docs/current/tutorial.html).)

<br/>

1. Clone the repository by opening a Terminal window and entering:

```
$ git clone https://github.com/moonstripe/ctec_wg_research_resources_1.git
```

2. Change directory into the cloned repository and initialize your virtual environment with the following command:

```
$ cd ctec_wg_research_resources_1
$ python3 -m venv venv
```

3. Activate your new virtual environment by entering:
   
```
$ source venv/bin/activate
```

4. Install the dependencies from the requirements file:

```
$ pip install -r requirements.txt
```

5. Create and populate a .env file with your VK access token, and database information.

```
$ touch .env
$ echo "VK_APP_TOKEN={your access token}" > .env
$ echo "DB_HOST={your database host}" >> .env
$ echo "DB_NAME={your database name}" >> .env
$ echo "DB_USER={your database username}" >> .env
$ echo "DB_PASS={your database password}" >> .env
```

6. To pull all post from a group, edit the `main.py` script under the `if __name__ == "__main__":` guard, replacing the value with the name of the VK group you're interested in. The script will pull a lot of data, and then apply an intensive sentiment analysis model to it. Make sure your computer can handle such operations.

7. Pull information from the database using SQL commands or psql. 