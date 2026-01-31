# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from preprocess import preprocess
import helper

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("WhatsApp Chat Analyzer – CampusX Style")

uploaded_file = st.file_uploader("Upload WhatsApp chat (.txt)", type=["txt"])

if uploaded_file is not None:
    raw_data = uploaded_file.read().decode("utf-8")
    df = preprocess(raw_data)

    st.subheader("Sample parsed data")
    st.dataframe(df.head())

    # user list for dropdown
    users = df["user"].unique().tolist()
    if "group_notification" in users:
        users.remove("group_notification")
    users.sort()
    users.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", users)
    if st.sidebar.button("Show Analysis"):
        # 1. Top stats
        num_messages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.header("Top Statistics")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total messages", num_messages)
        with c2:
            st.metric("Total words", num_words)
        with c3:
            st.metric("Media shared", num_media)
        with c4:
            st.metric("Links shared", num_links)

        # 2. Monthly timeline
        st.header("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["time"], timeline["message"], color="green")
        plt.xticks(rotation=90)
        st.pyplot(fig)

        # 3. Daily timeline
        st.header("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig2, ax2 = plt.subplots()
        ax2.plot(daily_timeline["date"], daily_timeline["message"], color="black")
        plt.xticks(rotation=90)
        st.pyplot(fig2)

        # 4. Activity map
        st.header("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig3, ax3 = plt.subplots()
            ax3.bar(busy_day.index, busy_day.values, color="purple")
            plt.xticks(rotation=90)
            st.pyplot(fig3)

        with col2:
            st.subheader("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig4, ax4 = plt.subplots()
            ax4.bar(busy_month.index, busy_month.values, color="orange")
            plt.xticks(rotation=90)
            st.pyplot(fig4)

        # 5. Heatmap: day vs hour
        st.header("Weekly Activity Heatmap")
        heatmap = helper.activity_heatmap(selected_user, df)
        fig5, ax5 = plt.subplots(figsize=(10,4))
        sns.heatmap(heatmap, cmap="YlOrRd", ax=ax5)
        st.pyplot(fig5)

        # 6. Busy users (only for overall)
        if selected_user == "Overall":
            st.header("Most Busy Users")
            x, percent_df = helper.most_busy_users(df)
            fig6, ax6 = plt.subplots()
            ax6.bar(x.index, x.values, color="red")
            plt.xticks(rotation=90)
            st.pyplot(fig6)
            st.dataframe(percent_df)

        # 7. WordCloud
        st.header("Word Cloud")
        wc = helper.create_wordcloud(selected_user, df)
        fig7, ax7 = plt.subplots()
        ax7.imshow(wc)
        ax7.axis("off")
        st.pyplot(fig7)

        # 8. Most common words
        st.header("Most Common Words")
        stop_words = set(["the","a","an","is","are","to","of","and","for","in","on",
                          "this","that","with","as","be","by","or","it","at","from",
                          "you","your","https","media","omitted"])
        common_df = helper.most_common_words(selected_user, df, stop_words)
        fig8, ax8 = plt.subplots()
        ax8.barh(common_df["word"], common_df["count"], color="teal")
        plt.gca().invert_yaxis()
        st.pyplot(fig8)

        # 9. Emoji analysis
        st.header("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col_emoji1, col_emoji2 = st.columns(2)
        with col_emoji1:
            st.dataframe(emoji_df.head(20))
        with col_emoji2:
            if not emoji_df.empty:
                fig9, ax9 = plt.subplots()
                ax9.pie(emoji_df["count"].head(10),
                        labels=emoji_df["emoji"].head(10),
                        autopct="%0.2f")
                st.pyplot(fig9)
