from urlextract import URLExtract
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download("vader_lexicon")



def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df["sender"] == selected_user]
    # NUMBER OF MESSAGES
    num_messages = df.shape[0]

    # TOTAL NUMBER OF WORDS
    words = []
    for message in df["message"]:
        words.extend(message.split())

    # TOTAL NUMBER OF MEDIA
    num_media_messages = df[df["message"] == "<Media omitted>"].shape[0]

    # TOTAL NUMBER OF LINKS
    extractor = URLExtract()
    links = []
    for message in df["message"]:
        links.extend(extractor.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def fetch_most_busy_users(df):
    # BUSIEST USER
    x = df["sender"].value_counts().head()

    # ACTIVE USERS
    y = (
        round((df["sender"].value_counts() / df.shape[0]) * 100, 2)
        .reset_index()
        .rename(columns={"index": "sender", "name": "percent"})
    )
    return x, y


def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df["sender"] == selected_user]
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color="white")

    df_wc = wc.generate(df["message"].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    f = open("stop_hinglish.txt", "r")
    stop_words = f.read()

    if selected_user != "Overall":
        df = df[df["sender"] == selected_user]

    # remove group member
    temp = df[df["sender"] != "Group Member"]
    # remove media omitted
    temp = temp[temp["message"] != "<Media omitted>"]

    words = []
    for message in temp["message"]:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    most_common_df.columns = ["word", "count"]

    return most_common_df


def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["sender"] == selected_user]

    timeline = (
        df.groupby(["year", "month_number", "month_name"])
        .count()["message"]
        .reset_index()
    )

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline["month_name"][i] + "-" + str(timeline["year"][i]))
    
    timeline['time'] = time

    return timeline

def sentiment_analysis(selected_user, df):
    sid = SentimentIntensityAnalyzer()

    if selected_user != "Overall":
        df = df[df['sender'] == selected_user]

    sentiments = df['message'].apply(lambda x: sid.polarity_scores(str(x)))
    sentiment_df = pd.DataFrame(list(sentiments))

    df = df.join(sentiment_df)
    df['sentiment'] = df['compound'].apply(
        lambda x: 'Positive' if x > 0.05 else ('Negative' if x < -0.05 else 'Neutral')
    )

    sentiment_counts = df['sentiment'].value_counts(normalize=True) * 100
    return sentiment_counts, df
