import re
import pandas as pd

def preprocess(data):

    # Regex pattern to extract messages
    pattern = r'^(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}),\s(\d{1,2}:\d{2}\s?[APap][Mm])\s-\s([^:]+?):\s(.*)'

    matches = re.findall(pattern, data, flags=re.MULTILINE)

    #print("Total messages parsed:", len(matches))

    # create dataframe with columns
    df = pd.DataFrame(matches, columns=["date", "time", "sender", "message"])

    # ✅ Replace numbers with "Group Notification"
    df["sender"] = df["sender"].apply(lambda x: "Group Member" if re.match(r"^\+?\d[\d\s-]+$", x) else x)

    # Fix weird spaces in time (WhatsApp sometimes has U+202F narrow space)
    df['time'] = df['time'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Extract date parts
    df['year'] = pd.to_datetime(df['date'], dayfirst=True).dt.year
    df['month_name'] = pd.to_datetime(df['date'], dayfirst=True).dt.month_name()
    df['day'] = pd.to_datetime(df['date'], dayfirst=True).dt.day
    df['month_number'] = pd.to_datetime(df['date'],dayfirst=True).dt.month


    # Extract time parts
    time_parsed = pd.to_datetime(df['time'], format='%I:%M %p', errors='coerce')
    df['hour_am_pm'] = time_parsed.dt.strftime('%I %p')  # 12-hour formatted hour (AM/PM)
    df['minute'] = pd.to_datetime(df['time'], format='%I:%M %p', errors='coerce').dt.minute

    return df