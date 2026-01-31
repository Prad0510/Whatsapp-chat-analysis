# helper.py
import pandas as pd
from collections import Counter
import emoji
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

def fetch_stats(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = df.shape[0]
    words = []
    for msg in df["message"]:
        words.extend(msg.split())

    num_media = df[df["message"] == "<Media omitted>"].shape[0]
    num_links = df["message"].str.contains("http").sum()

    return num_messages, len(words), num_media, num_links

def most_busy_users(df: pd.DataFrame, top_n=5):
    x = df["user"].value_counts().head(top_n)
    percent = round((df["user"].value_counts() / df.shape[0]) * 100, 2).reset_index()
    percent.columns = ["user", "percent"]
    return x, percent

def create_wordcloud(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[df["user"] != "group_notification"]
    temp = temp[temp["message"] != "<Media omitted>"]

    text = " ".join(temp["message"].tolist())
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)

    return wc

def most_common_words(selected_user, df: pd.DataFrame, stop_words=None):
    if stop_words is None:
        stop_words = set()

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[df["user"] != "group_notification"]
    temp = temp[temp["message"] != "<Media omitted>"]

    words = []
    for msg in temp["message"]:
        for word in msg.lower().split():
            if word not in stop_words and "http" not in word:
                words.append(word)

    common_df = pd.DataFrame(Counter(words).most_common(20))
    common_df.columns = ["word", "count"]
    return common_df

def emoji_helper(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    emojis = []
    for msg in df["message"]:
        emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_df.columns = ["emoji", "count"]
    return emoji_df

def monthly_timeline(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()
    timeline["time"] = timeline["month"] + "-" + timeline["year"].astype(str)
    return timeline

def daily_timeline(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    daily = df.groupby("date").count()["message"].reset_index()
    return daily

def week_activity_map(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    return df["day_name"].value_counts()

def month_activity_map(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    return df["month"].value_counts()

def activity_heatmap(selected_user, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    heatmap = df.pivot_table(index="day_name", columns="hour", values="message",
                             aggfunc="count").fillna(0)
    # reorder days
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heatmap = heatmap.reindex(order)
    return heatmap
