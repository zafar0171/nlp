import pymysql
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import pandas as pd
#from helper_functions import send_email_new
import datetime,time
# type: ignore

def get_connection():
    try:
        connection = pymysql.connect(
        user="root",
        password="Thermodynamics@1",
        host="localhost",    
        database="stocks", 
        )
        
        print("Connection to MySQL database was successful")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Function to fetch and parse the news
def fetch_news(rss_url):
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    
    headlines = []
    urls = []
  
    for item in root.findall('./channel/item'):
        headline = item.find('title').text
        url = item.find('link').text
        headlines.append(headline)
        urls.append(url)
    
    return headlines, urls


#--------------------------------------------------------------------------------------------------------------------------------------------------------
                                                                        #Part-1


rss_url = 'https://news.google.com/news/rss/headlines/section/topic/BUSINESS.IN'
headlines, urls = fetch_news(rss_url)

data = {'Headline': headlines, 'URL': urls,"updated_at": time.strftime("%H:%M:%S", time.localtime()),"insertion_date": datetime.date.today()}

#data = {'Headline': headlines, 'URL': urls}
df = pd.DataFrame(data)

#print(df)
print("step-1:- news headline successfully fetched")

stocksTupleList = list(df.itertuples(index=False, name=None))
#Data insertion
mydb = get_connection()
if mydb:
    mycursor = mydb.cursor()

    query = """INSERT IGNORE INTO goog_rss (Headline, url,updated_at,insertion_date) VALUES (%s, %s, %s, %s)"""                 #Ignore: To ignore dupicate values 
    mycursor.executemany(query, stocksTupleList)
    mydb.commit()
    mycursor.close()
    mydb.close()
    print("Step-2:- Data successfully inserted in goog_news database")
else:
    print("Failed to connect to MySQL database")

#--------------------------------------------------------------------------------------------------------------------------------------------------------
                                                                        #Part-2


sen = []
news = []
org = []

for text in df.Headline:
    x = text.rsplit("|", maxsplit=1)
    
    if len(x) == 2:
        new = x[1].lstrip().rsplit('-', maxsplit=1)
        new[0] = new[0].strip()
        
        if len(new) > 1:
            new[1] = new[1].strip()
            org.append(new[1])
        else:
            org.append('')  # Handle case where there's no second part
        
        sen.append(x[0])
        
        if len(new) > 1 and new[0] == new[1]:
            print(f"{new[0]}, {new[1]} are the same, inserting NaN instead of {new[0]}")
            news.append('NaN')
        else:
            if len(new[0]) > 24:
                print(f"{new[0]} exceeded the character limit")
                news.append('NaN')
            else:
                news.append(new[0])
            
    else:
        e = x[0].lstrip().rsplit('-', maxsplit=1)
        sen.append(e[0])
        news.append('NaN')
        if len(e) > 1:
            org.append(e[1])
        else:
            org.append('')  # Handle case where there's no second part
            
org = [i.strip() for i in org]
sen = [i.strip() for i in sen]
new_df = pd.DataFrame({'headline':sen,'news_category':news,'org':org})
print("Step-3:- Headline successfully trimmed, organistaion and news category part has bee extracted")
#new_df.head(10)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
                                                                        #Part-3

#Heuristic Approach

import spacy
from spacy.matcher import Matcher

# Load the pre-trained model
nlp = spacy.load("en_core_web_trf")

# categories and keywords with respective synonyms
positive_keywords = ["approves", "investment", "expansion", "success", "high", "best ever", "fly high", "jump", "rallied", "surge", "increase", "rise", "gain", "soar", "profit"]
negative_keywords = ["loser", "fall", "decline", "drop", "decrease", "plunge", "slump", "crash", "fraud"]
sectorial_keywords = ["energy stocks", "aviation", "renewable energy"]
recommendation_keywords = ["Planning to buy", "brokerages views", "recommendations"]
deal_keywords = ["raising", "investment target", "IPO", "stake", "valuation"]

#matcher object
matcher = Matcher(nlp.vocab)

#patterns for specific phrases including entities
patterns = [
    [{"ENT_TYPE": "PERSON"}, {"LOWER": "of"}, {"ENT_TYPE": "ORG"}, {"LOWER": "top"}, {"LOWER": "picks"}],
    [{"ENT_TYPE": "PERSON"}, {"LOWER": "suggested"}, {"LOWER": "this"}],
    [{"LOWER": "breakout"}, {"LOWER": "stock"}],
    [{"LOWER": "price"}, {"LOWER": "volume"}, {"LOWER": "breakouts"}],
    [{"ENT_TYPE": "PERSON"}, {"LOWER": "recommends"}, {"LOWER": "this"}]
]

for pattern in patterns:
    matcher.add("TOP_PICK_PATTERNS", [pattern])


def classify_headline(headline):
    doc = nlp(headline)
    matches = matcher(doc)
    
    if matches:
        return "Top Picks"
    
    category = None
   # Dependency parsing and context check
    for token in doc:
        if token.lemma_ in positive_keywords and any([ent.label_ == "ORG" for ent in doc.ents]):
            category = "Positive News"
        elif token.lemma_ in negative_keywords and any([ent.label_ == "ORG" for ent in doc.ents]):
            category = "Negative News"
        elif token.lemma_ in sectorial_keywords:
            category = "Sectorial News"
        elif token.lemma_ in recommendation_keywords:
            category = "Stock Recommendations"
        elif token.lemma_ in deal_keywords:
            category = "Deals"
    
    return category

#  headline processing and classification
alerts = []
for headline in new_df.headline:
    category = classify_headline(headline)
    if category:
        alerts.append((headline, category))

for alert in alerts:
    print(f"Category: {alert[1]}\nHeadline: {alert[0]}\n")


#--------------------------------------------------------------------------------------------------------------------------------------------------------
                                                                        #Part-4
## FLAG -- Need improvement
for i in range(len(alerts)):
    doc = nlp(alerts[i][0])
    print(alerts[i][0])
    spacy.displacy.render(doc, style = 'ent')


latest_news = [i[0] for i in alerts]
company = []
for i in range(len(alerts)):
    doc = nlp(alerts[i][0])
    print(alerts[i][0])
    for ent in doc.ents:
        if ent.label_ == "ORG":
            company.append(ent)
            print(doc)
        else:
           pass
    print(doc) 
    company.append(ent)
    if doc.ents == "ORG":
        company.append(doc.ents)
print("Companies in focus: \n",company)
print(latest_news)
#body = pd.DataFrame({"news":latest_news,}).to_string(index = False,justify = 'center')
#send_email_new('Stocks in news', body , 'mdmodassir3889@gmail.com', 'plain')


#send_email1('subject', 'messageBody', 'mdmodassir3889@gmail.com', 'text')
#
# messgae_body = 