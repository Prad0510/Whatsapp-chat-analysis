# preprocess.py
import re
import pandas as pd

def preprocess(data: str) -> pd.DataFrame:
    """
    Takes raw WhatsApp chat text and returns a cleaned DataFrame
    with columns: datetime, date, year, month, day_name, hour, user, message.
    Supports 24-hr export format like: 07/01/25, 19:04 - Name: msg
    """

    # Pattern for messages: "dd/mm/yy, hh:mm - user: message"
    message_pattern = r'^(\d{1,2})\/(\d{1,2})\/(\d{2}), (\d{1,2}:\d{2}) - (.*)'
    message_regex = re.compile(message_pattern)

    messages = []
    dates = []

    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue

        if message_regex.match(line):
            # new message
            date_part = line.split(" - ")[0]
            msg_part = " - ".join(line.split(" - ")[1:])
            dates.append(date_part)
            messages.append(msg_part)
        else:
            # continuation of previous message
            if len(messages) > 0:
                messages[-1] += "\n" + line

    # Extract user and message text
    users = []
    msg_texts = []
    for m in messages:
        entry = m.split(": ", 1)
        if len(entry) == 2:
            user, msg = entry[0], entry[1]
        else:
            user, msg = "group_notification", m
        users.append(user)
        msg_texts.append(msg)

    df = pd.DataFrame({"message_date": dates, "user": users, "message": msg_texts})

    # Convert date string to datetime
    # Adjust format if your export is different (e.g. 12-09-25 instead of 12/09/25)
    df["message_date"] = pd.to_datetime(df["message_date"], format="%d/%m/%y, %H:%M")

    df.rename(columns={"message_date": "datetime"}, inplace=True)
    df["date"] = df["datetime"].dt.date
    df["year"] = df["datetime"].dt.year
    df["month_num"] = df["datetime"].dt.month
    df["month"] = df["datetime"].dt.month_name()
    df["day_name"] = df["datetime"].dt.day_name()
    df["hour"] = df["datetime"].dt.hour

    return df
