import streamlit as st
import datetime
import constant
from function import *

st.title('How many people in theater')

@st.cache(suppress_st_warning=True, show_spinner=False, allow_output_mutation=True)
def set_data(theater_url, date):
    base_url = 'https://tjoy.jp'
    people_per_time = constant.per_5_mins
    
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

# 入力
theater = st.selectbox('上映館',(['---'] + list(constant.theaters.keys())))
if theater == '---': st.stop()
theater_url = constant.theaters[theater]    
    
dates = date_list(6)
date = st.selectbox('上映日', (['---'] + dates))
if date == '---': st.stop()

# スクレイピング 
data = set_data(theater_url, date)
    
# グラフ表示
with st.spinner('グラフ表示'):
    times = list(data.keys())
    start_time = st.selectbox('表示開始', (times), index=times.index('12:00'))
    end_time = st.selectbox('表示終了', (times), index=times.index('15:00'))
    start_idx, end_idx = times.index(start_time), times.index(end_time)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.tick_params(axis='x', labelrotation=45, labelsize=6)
    ax.bar(times[start_idx:end_idx], list(data.values())[start_idx:end_idx])
    st.write(fig)