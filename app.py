import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

column_map = {
    "中文": {
        "Title": "职位",
        "Company": "公司",
        "Location": "地点",
        "Posted On": "发布日期",
        "Deadline": "截止时间",
        "Skills": "技能标签",
        "Job Type": "工作类型",
        "Language": "语言要求"
    },
    "English": {
        "职位": "Title",
        "公司": "Company",
        "地点": "Location",
        "发布日期": "Posted On",
        "截止时间": "Deadline",
        "技能标签": "Skills",
        "工作类型": "Job Type",
        "语言要求": "Language"
    }
}

# choose your language
language = st.radio("🌐 选择语言 / Select Language", ["中文", "English"], horizontal=True)

# text dictionary
T = {
    "中文": {
        "title": "JobLens 瑞典招聘信息分析仪 🇸🇪",
        "desc": "输入关键词，获取瑞典招聘数据，并实时展示结果！",
        "input_keyword": "🔍 输入关键词（例如：data scientist）",
        "slider_label": "🎯 最多显示多少条招聘信息",
        "start_button": "开始搜索",
        "start_searching": "正在抓取数据，请稍候...",
        "no_result": "未找到相关职位，请尝试其他关键词。",
        "API_error": "API 请求失败，请稍后再试。",
        "filter_title": "🧩 按标签筛选岗位",
        "skill_label": "选择技能标签：",
        "jobtype_label": "选择工作类型：",
        "lang_label": "选择语言要求：",
        "soon_only": "只看即将截止的职位（🔥3天内）",
        "result_count": "🎯 共找到 {} 个符合条件的岗位",
        "wordcloud_title": "📊 职位名称关键词词云",
        "city_title": "🏙️ 招聘职位最多的城市分布",
        "download_button": "📥 下载岗位数据（CSV）",
        "full_time": "🟩 全职",
        "part_time": "🟧 兼职",
        "internship": "🟦 实习",
        "english": "🟨 英语",
        "swedish": "🟪 瑞典语"
    },
    "English": {
        "title": "JobLens: Swedish Job Analyzer 🇸🇪",
        "desc": "Enter a keyword to fetch and explore job opportunities in Sweden!",
        "input_keyword": "🔍 Enter keyword (e.g., data scientist)",
        "slider_label": "🎯 Max number of jobs to fetch",
        "start_button": "Search",
        "start_searching": "Fetching data, please wait...",
        "no_result": "No relevant jobs found. Try another keyword.",
        "API_error": "API request failed, please try again later.",
        "filter_title": "🧩 Filter by Tags",
        "skill_label": "Select skills:",
        "jobtype_label": "Select job types:",
        "lang_label": "Select language requirements:",
        "soon_only": "Only show positions ending soon (🔥 within 3 days)",
        "result_count": "🎯 Found {} matching positions",
        "wordcloud_title": "📊 Word Cloud of Job Titles",
        "city_title": "🏙️ Top Cities by Job Count",
        "download_button": "📥 Download as CSV",
        "full_time": "🟩 Full-Time",
        "part_time": "🟧 Part-Time",
        "internship": "🟦 Internship",
        "english": "🟨 English",
        "swedish": "🟪 Swedish"
    }
}

# page title and description
st.title(T[language]["title"])
st.write(T[language]["desc"])

# input of user
keyword = st.text_input(T[language]["input_keyword"], "data scientist")  # 创建文本框
limit = st.slider(T[language]["slider_label"], 10, 100, 20)  # 创建滑动条

# --- Automatically load previously saved data when the page loads ---
df = None
if "df" in st.session_state:
    df = st.session_state["df"]

# --- When clicking the button ---
if st.button(T[language]["start_button"]):
    with st.spinner(T[language]["start_searching"]):
        # Constructing the API request address
        url = f"https://jobsearch.api.jobtechdev.se/search?q={keyword}&limit={limit}"
        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Extracting useful fields
            jobs = data.get("hits", [])
            if not jobs:
                st.warning(T[language]["no_result"])
            else:
                job_list = []
                for job in jobs:
                    desc_text = job.get("description", {}).get("text", "").lower()

                    # initial label list
                    skills = []
                    job_type = ""
                    job_language = ""

                    # Skill Matching
                    for skill in ["python", "sql", "excel", "java", "machine learning", "aws", "r", "docker"]:
                        if skill in desc_text:
                            skills.append(skill.upper())

                    # Work type Matchin
                    if "full-time" in desc_text or "heltid" in desc_text:
                        job_type = T[language]["full_time"]
                    elif "part-time" in desc_text or "deltid" in desc_text:
                        job_type = T[language]["part_time"]
                    elif "internship" in desc_text or "praktik" in desc_text:
                        job_type = T[language]["internship"]

                    # Job language requirement
                    if "english" in desc_text:
                        job_language = T[language]["english"]
                    elif "swedish" in desc_text or "svenska" in desc_text:
                        job_language = T[language]["swedish"]

                    # get publication and application list
                    published_raw = job.get("publication_date")
                    deadline_raw = job.get("application_deadline")

                    # initial string
                    published = ""
                    deadline = ""

                    # publication time：only date
                    if published_raw:
                        try:
                            dt_pub = datetime.fromisoformat(published_raw)
                            published = dt_pub.strftime("%Y-%m-%d")
                        except:
                            published = ""

                    # deadline：date and time
                    if deadline_raw:
                        try:
                            dt_deadline = datetime.fromisoformat(deadline_raw)
                            deadline = dt_deadline.strftime("%Y-%m-%d %H:%M")
                        except:
                            deadline = ""

                    # 组织信息
                    job_info = {
                        "职位": job.get("headline"),
                        "公司": job.get("employer", {}).get("name"),
                        "地点": job.get("workplace_address", {}).get("municipality"),
                        "发布日期": published,
                        "截止时间": deadline,
                        "链接": job.get("webpage_url"),
                        "技能标签": ", ".join(skills),
                        "工作类型": job_type,
                        "语言要求": job_language
                    }

                    job_list.append(job_info)

                # transfer toDataFrame
                df = pd.DataFrame(job_list)
                st.session_state["df"] = df  # save the data

                # 显示表格
                #st.success(f"共找到 {len(df)} 个职位：")
                #st.dataframe(df)
        else:
            st.error(T[language]["API_error"])

if df is not None and not df.empty:
    # Filter jobs by tag
    st.subheader(T[language]["filter_title"])

    skill_options = sorted(set(skill for s in df["技能标签"] for skill in s.split(", ") if s))
    selected_skills = st.multiselect(T[language]["skill_label"], skill_options)

    job_type_options = df["工作类型"].dropna().unique().tolist()
    selected_job_types = st.multiselect(T[language]["jobtype_label"], job_type_options)

    language_options = df["语言要求"].dropna().unique().tolist()
    selected_languages = st.multiselect(T[language]["lang_label"], language_options)

    filtered_df = df.copy()

    if selected_skills:
        filtered_df = filtered_df[filtered_df["技能标签"].apply(
            lambda tags: all(skill in tags.split(", ") for skill in selected_skills))]

    if selected_job_types:
        filtered_df = filtered_df[filtered_df["工作类型"].isin(selected_job_types)]

    if selected_languages:
        filtered_df = filtered_df[filtered_df["语言要求"].isin(selected_languages)]

    if st.checkbox(T[language]["soon_only"]):
        filtered_df = filtered_df[filtered_df["截止时间"].str.contains("🔥")]


    filtered_df = filtered_df.sort_values(by="发布日期", ascending=False)

    st.write(T[language]["result_count"].format(len(filtered_df)))

    # Convert the job title column into a markdown hyperlink with a link
    filtered_df["职位"] = filtered_df.apply(
        lambda row: f"[{row['职位']}]({row['链接']})" if pd.notna(row["链接"]) else row["职位"],
        axis=1
    )

    # Remove the original "Link" column
    filtered_df.drop(columns=["链接"], inplace=True)

    # change column name according to web language
    filtered_df.rename(columns=column_map[language], inplace=True)

    # show the column
    st.markdown(filtered_df.to_markdown(index=False), unsafe_allow_html=True)

    # CSV 下载按钮
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(T[language]["download_button"], csv, file_name="jobs.csv", mime="text/csv")

    # Word Cloud
    if not df.empty:
        st.subheader(T[language]["wordcloud_title"])

        # concat the job title
        text = " ".join(df["职位"].dropna().astype(str))

        stopwords = set(["for", "and", "to", "with", "of", "in", "the", "a", "on", "as"])
        wordcloud = WordCloud(width=800, height=400, background_color="white", stopwords=stopwords).generate(text)

        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

    # City distribution map
    if not df.empty:
        st.subheader(T[language]["city_title"])

        city_counts = df["地点"].value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=city_counts.values, y=city_counts.index, ax=ax)
        ax.set_xlabel("Number of Positions")
        ax.set_ylabel("City")
        st.pyplot(fig)