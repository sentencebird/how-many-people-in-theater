import streamlit as st
import datetime
import constant
from function import *

st.set_page_config(page_title='How many people in theater', layout='wide')

@st.cache(suppress_st_warning=True, show_spinner=False, allow_output_mutation=True)
def set_data(theater_url, date, people_per_time):
    base_url = 'https://tjoy.jp'
    
    with st.spinner('アクセス中...'):
        driver = get_driver(theater_url)
        _ = [tag.find_element_by_tag_name('button').click() for tag in driver.find_elements_by_class_name('modal') if '閉じる' in tag.text]

        click_date_button(driver, date)
        time.sleep(1)        
        driver.find_elements_by_css_selector('.btn.js-show-hidden.close-all')[0].click() # 全部表示  

    with st.spinner('スクリーンの人数を計算中...'):
        bar = st.progress(0)
        screen_tags = driver.find_elements_by_class_name('schedule-box-body')
        n_screens = len(screen_tags)
        for i, tag in enumerate(screen_tags, 1):
            bar.progress(i / n_screens)
            try: 
                url = base_url + tag.get_attribute('onclick').split('location.href =')[-1].replace("'", '')
                if 'javascript:void(0);' in url: continue
                soup = get_soup(url, useragents=constant.useragents)
                start_time, end_time = soup.select_one('.movie-date').text.split('）')[-1].split('～')
                n_people = len(soup.select('area.sold-out'))
                people_per_time[start_time.strip()] += n_people
                people_per_time[end_time.strip()] += n_people
            except: continue
    return people_per_time

# ページ
_left, center, _right = st.beta_columns([1, 1, 1])
with center:
    st.title('上映開始と終了時刻の人数')
    # 入力
    theater = st.selectbox('上映館',(['---'] + list(constant.theaters.keys())))
    if theater == '---': st.stop()
    theater_url = constant.theaters[theater]
    a_tag = f'[{theater}]({theater_url})'
    st.markdown(a_tag, unsafe_allow_html=True)    

    dates = date_list(6)
    date = st.selectbox('上映日', (['---'] + dates))
    if date == '---': st.stop()

    # スクレイピング 
    data = set_data(theater_url, date, constant.per_5_mins)
    
    # グラフ表示
    with st.spinner('グラフ表示'):
        times = list(data.keys())
        fig, ax = plt.subplots(figsize=(20, 5))        
        ax.tick_params(axis='x')
        ax.tick_params(axis='y')
        xlabels = [time if ':00' in time else '' for time in data.keys()]
        ax.bar(data.keys(), list(data.values()), tick_label=xlabels)
st.pyplot(fig)
