import streamlit as st
import preprocessor, helpers
import matplotlib.pyplot as plt

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("WhatsApp Chat Analyzer")

st.sidebar.markdown("""
### How to Export Your WhatsApp Chat 📤
1. Open **WhatsApp** on your phone.  
2. Go to the **chat** you want to analyze.  
3. Tap the **three dots (⋮) → More → Export Chat**.  
4. Choose **“Without Media”** (faster upload).  
5. Save or share the exported **`.txt` file** to your computer.  
6. Upload the file below 👇
""")

uploaded_file = st.sidebar.file_uploader("📂 Upload your exported WhatsApp chat (.txt)", type=["txt"])

if uploaded_file is not None:
    btyes_data = uploaded_file.getvalue()
    data = btyes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # DISPLAY DATA TO SCREEN
    with st.expander("📂 View Processed Data"):
        st.dataframe(df)

    # FETCH UNIQUE USER
    user_list = df["sender"].unique().tolist()
    user_list.remove("Group Member")
    user_list.sort()
    user_list.insert(0, "Overall")

    st.sidebar.subheader("👤 Select User")
    selected_user = st.sidebar.selectbox("Analyze messages for", user_list)

    if st.sidebar.button("SHOW ANALYSIS"):

        # STATS
        num_messages, words, num_media_messages, links = helpers.fetch_stats(
            selected_user, df
        )

        tab1, tab2, tab3, tab4 , tab5 = st.tabs(["📊 Overview", "⏰ Timeline", "👥 Users", "📖 Words",'😊 Sentiment Analysis'])

        # =============== OVERVIEW TAB =================
        with tab1:
            st.header("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Messages", num_messages)
            col2.metric("Total Words", words)
            col3.metric("Media Shared", num_media_messages)
            col4.metric("Links Shared", links)

        # =============== TIMELINE TAB =================
        with tab2:
            st.header("Monthly Timeline")
            timeline = helpers.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(timeline['time'], timeline['message'], color='green', marker='o')
            plt.xticks(rotation='vertical')
            ax.set_xlabel("Month-Year")
            ax.set_ylabel("Messages")
            ax.set_title("Monthly Timeline")
            st.pyplot(fig)

        # =============== USERS TAB =================
        with tab3:
            if selected_user == 'Overall':
                x, y = helpers.fetch_most_busy_users(df)

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Most Busy Users")
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.bar(x.index, x.values, color='skyblue')
                    ax.set_xlabel("Senders")
                    ax.set_ylabel("Messages")
                    ax.set_title("Most Busy Users")
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

                with col2:
                    st.subheader("Active Users (%)")
                    st.dataframe(y)

        # =============== WORDS TAB =================
        with tab4:
            st.subheader("📖 Word Cloud of Messages")
            df_wc = helpers.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)

            st.subheader("Most Common Words")
            most_common_df = helpers.most_common_words(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(most_common_df['word'], most_common_df['count'], color='skyblue')
            ax.set_xlabel("Words")
            ax.set_ylabel("Frequency")
            ax.set_title("Most Common Words")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        with tab5:
            st.subheader("Sentiment Analysis")

            sentiment_counts, sentiment_df = helpers.sentiment_analysis(selected_user, df)

            col1, col2 = st.columns(2)

            with col1:
                st.write("📊 Sentiment Distribution")
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.pie(
                sentiment_counts.values,
                labels=sentiment_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=['green', 'red', 'gray'])
                ax.axis("equal")
                st.pyplot(fig)

            with col2:
                st.write("📈 Sentiment Over Time")
                sentiment_timeline = sentiment_df.groupby(['date','sentiment']).size().unstack().fillna(0)
                fig, ax = plt.subplots(figsize=(8, 3))
                sentiment_timeline.plot(ax=ax, marker='o')
                plt.xticks(rotation=45)
                ax.set_title("Sentiment Trend Over Time")
                st.pyplot(fig)
    

    
       
