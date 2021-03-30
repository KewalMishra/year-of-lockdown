import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import pydeck as pdk
from PIL import Image
#import matplotlib.pyplot as plt

st.sidebar.title('Navigation')
st.sidebar.write('Please select a page :point_down:')
add_selectbox = st.sidebar.radio(
    "",
    ("Introduction","Sentiment Analysis", "Pandemic Analysis", "Air Traffic")
)

if add_selectbox=='Introduction':
    st.title('An year in Lockdown: India :flag-in:')

    st.markdown("###")

    st.write(':arrow_right: On 23 March 2020, the Government of India under Prime Minister Narendra Modi ordered a nationwide lockdown for 21 days, limiting movement of the entire 1.38 billion or 138 Crore population of India as a preventive measure against the COVID-19 pandemic in India.')
    ':arrow_right: On 30 May, it was announced that lockdown restrictions were to be lifted from then onwards, while the ongoing lockdown would be further extended till 30 June for only the containment zones. Services would be resumed in a phased manner starting from 8 June. It was termed as "Unlock 1.0".'

    '**This project** aims at investigating the impact of the lockdown over different aspects like: Twitter Sentiment, Virus Spread \
                 data and the Air traffic data.'
    'I built a twitter scraper using Python and used it to scrape Historical tweets from Twitter dating from March of \
                2020 to March of 2021. The criteria for the tweet were that it must contain *"Lockdown" AND "India"*. Approximately 300,000 \
                tweets were scraped from Twitter, all of these tweets were then cleaned and indexed with their polarity and sentiment value. \
                The sentiment value of each tweet can lie anywhere betweeen the range of -1 to 1, where 1 is a positive sentiment and -1 \
                represents negative sentiment.'
    'The air traffic data is publically hosted by the Airport Authority of India. The data can be found here: https://www.aai.aero/en/business-opportunities/aai-traffic-news. The "Traffic News Summary" file contains a summary of all air traffic, passengers and freight \
    for both Domestic and International airports.'
    'The data for the Covid cases is availabke at: https://api.covid19india.org/'
    
    
if add_selectbox=='Sentiment Analysis':
    st.title('Social Media Sentiment Analysis :speech_balloon:')

    @st.cache
    def load_sentiment_data():
        sent_df = pd.read_csv('datasets/Sentiment_scored.csv',parse_dates=['datetime'])
        daily_sent = sent_df.groupby([sent_df['datetime'].dt.date]).mean()
        day_hist_values = np.histogram(sent_df['datetime'].dt.hour, bins=24, range=(0,24))[0]
        ax_perct = sent_df.groupby([sent_df['datetime'].dt.to_period('M'),sent_df['Sentiment']]).size() \
                        .groupby(level=0).apply(lambda x:100 * x / float(x.sum())).reset_index(name='percnt') \
                        .pivot("datetime", "Sentiment", "percnt")
        senti_TS = sent_df.groupby([sent_df['datetime'].dt.to_period('M').astype(str),sent_df['Sentiment']]).size() \
                          .groupby(level=0).apply(lambda x:100 * x / float(x.sum())).reset_index(name='count') \
                                   .pivot("datetime", "Sentiment", "count")
        return sent_df, daily_sent, day_hist_values, ax_perct, senti_TS
    
    data_load_state = st.text('Loading data...')
    sent_df, daily_sent, day_hist_values, ax_perct, senti_TS = load_sentiment_data()
    data_load_state.text('')




    st.markdown('####')
    st.header('Daily Average Sentiment')
    st.markdown('####')
    run = st.button('run animation')
    if run:
        daily_sent_chart = st.line_chart(daily_sent[0:1])
        for i in range(1, len(daily_sent)):
            new_rows = daily_sent[i:i+1]
            daily_sent_chart.add_rows(new_rows)
            time.sleep(0.03) 
    else:
        st.line_chart(daily_sent)

    st.markdown('####')
    st.header('Tweet count distribution throughout a day :clock3:')
    st.markdown('####')   


    st.bar_chart(day_hist_values)

    tweet_cnt_exp = st.beta_expander('Data insight')
    tweet_cnt_exp.write('Twitter users start posting as early as 4 A.M. and the count peaks between 2P.M and 3 P.M., \
    after which there is substantial drop after 5 P.M. which stagnates at night.')

    st.markdown('####')
    st.header('Scraped tweet data distribution :bar_chart:')
    st.markdown('####')   
    image1 = Image.open('datasets/sent_plot1.png')
    st.image(image1)

    #ax_month_hist = pd.to_datetime(sent_df['datetime']).dt.to_period('M').astype(str).hist(figsize=(15, 6))
    #st.pyplot(ax_month_hist.get_figure())


    st.markdown('####')
    st.header('Monthly Sentiment percentage split')
    st.markdown('####')
    #ax_perct_chart = ax_perct.plot(kind='bar', color={"Positive": "mediumseagreen", "Negative": "coral","Neutral":"tab:blue"})
    #patches, labels = ax_perct_chart.get_legend_handles_labels()
    #ax_perct_chart.legend(patches, labels, loc='best')
    #st.pyplot(ax_perct_chart.get_figure())
    image2 = Image.open('datasets/sent_plot2.png')
    st.image(image2)
    perct_splt_exp = st.beta_expander('Data insight')
    perct_splt_exp.write('December 2020 was the most positive month, September 2020 saw the highest weightage of negative sentiment')

    st.markdown('####')
    st.header('How did each Sentiment vary over time :question:')
    st.markdown('####')

    senti = st.selectbox('Select', senti_TS.columns.tolist())

    st.area_chart(senti_TS[senti])

    # show_data = st.checkbox('show data')
    # if show_data:
    #     senti_TS

if add_selectbox=='Pandemic Analysis':
    st.title('Pandemic Analysis :mask:')

    @st.cache
    def load_pandemic_data():
        case_time_series ="https://api.covid19india.org/csv/latest/case_time_series.csv"
        states ="https://api.covid19india.org/csv/latest/states.csv"
        state_wise ="https://api.covid19india.org/csv/latest/state_wise.csv"
        case_time_series = pd.read_csv(case_time_series ,parse_dates=['Date_YMD'])
        state_wise = pd.read_csv(state_wise)
        states = pd.read_csv(states,parse_dates=['Date'])
        return case_time_series,states,state_wise


    data_load_state = st.text('Loading data...')
    case_time_series,states,state_wise = load_pandemic_data()
    data_load_state.text('')
    last_update_date = st.write('Last data update:',case_time_series.Date_YMD.max().date())

    state_wise = state_wise[['State', 'Confirmed', 'Recovered', 'Deaths', 'Active']]

    states = states[(states.State != 'India')&(states.State != 'State Unassigned')]
    states.drop('Other',axis=1,inplace=True)

    daily_df = case_time_series[['Date_YMD','Daily Confirmed','Daily Recovered','Daily Deceased']] \
    .rename(columns={'Date_YMD':'index'}).set_index('index')
    total_df = case_time_series[['Date_YMD','Total Confirmed','Total Recovered','Total Deceased']] \
    .rename(columns={'Date_YMD':'index'}).set_index('index')

    st.markdown('##')
    st.header('Time Series plot of Covid-19 cases (nation-level) :chart_with_upwards_trend:')
    st.markdown('####')

    st.write('Select plot aggregation :arrow_heading_down:')
    trend_plot = st.selectbox('',['Daily Trend','Cumulative Trend'])
    run = st.button('run animation')
    if trend_plot == 'Daily Trend':
        if run:
            daily_chart = st.line_chart(daily_df[0:1])
            for i in range(1, len(daily_df)):
                new_rows = daily_df[i:i+1]
                daily_chart.add_rows(new_rows)
                time.sleep(0.03) 
        else:
            st.line_chart(daily_df)

    if trend_plot == 'Cumulative Trend':
        if run:
            total_chart = st.area_chart(total_df[0:1])
            for i in range(1, len(total_df)):
                new_rows = total_df[i:i+1]
                total_chart.add_rows(new_rows)
                time.sleep(0.03)        
        else:
            st.area_chart(total_df)

    st.markdown('###')
    st.header('State level analysis')
    st.markdown('####')
    left_column, right_column = st.beta_columns(2)
    plot_data = right_column.radio('Select data',states.columns.tolist()[-4:])
    state_select = left_column.multiselect("Select states", states.State.unique().tolist(), ["Maharashtra", "Kerala"])
    if not state_select:
        st.error("Please select at least one state.")
    else:
        state_level_chart = st.area_chart()
        for stt in state_select:  
            state_level_chart.add_rows(states[states.State==stt][['Date',plot_data]] \
                                       .rename(columns={'Date':'index',plot_data:stt}).set_index('index'))

    st.markdown('###')        
    st.header('Map Visualtization :earth_asia:')
    st.markdown('###')        

    state_wise = state_wise[(state_wise.State != 'Total')&(state_wise.State != 'State Unassigned')]
    coord_data = pd.read_csv('datasets/states_coords.csv')
    coord_data = coord_data[['State','lon','lat']]
    state_wise = pd.merge(state_wise,coord_data, on='State', how='left')
    state_wise_mod = state_wise.copy()
    state_wise_mod['Confirmed_scaled'] = state_wise_mod.Confirmed/500
    state_wise_mod = state_wise_mod[['lon','lat','Confirmed_scaled']].reset_index(drop=True)

    #view (location, zoom level, etc.)
    view = pdk.ViewState(latitude=23.8343419, longitude=77.5640719, pitch=40, zoom=4)

    # layer
    column_layer = pdk.Layer('ColumnLayer',
                             data=state_wise_mod,
                             get_position=['lon', 'lat'],
                             get_elevation='Confirmed_scaled',
                             elevation_scale=100,
                             radius=10000,
                             get_fill_color=[255, 165, 0, 80],
                             pickable=True,
                             auto_highlight=True)

    # render map
    # with no map_style, map goes to default
    st.pydeck_chart(pdk.Deck(layers=column_layer, 
                                initial_view_state=view))

    map_exp = st.beta_expander('Data insight')
    map_exp.write('The height of column is proportional to the *Total Confirmed Cases* count of that location.')
    show_data = st.checkbox('show data')
    if show_data:
        st.table(state_wise)


    
if add_selectbox=='Air Traffic':
    st.title('Air Traffic Analysis :airplane:')

    @st.cache
    def load_air_traffic_data():
        dom = pd.read_csv('datasets/dom_air_traffic.csv',parse_dates=['Month']).set_index('Month')
        intn = pd.read_csv('datasets/intn_air_traffic.csv',parse_dates=['Month']).set_index('Month')
        return dom,intn


    data_load_state = st.text('Loading data...')
    dom,intn = load_air_traffic_data()
    data_load_state.text('')

    left_column, right_column = st.beta_columns(2)
    agg_lvl = left_column.radio('Select data aggregation',['All','Domestic','International'])
    data_type = right_column.radio('Select Data',dom.columns.tolist())

    if agg_lvl == 'All':    
        chart_data = dom + intn
    elif agg_lvl == 'Domestic':
        chart_data = dom
    elif agg_lvl == 'International':
        chart_data = intn
    st.area_chart(chart_data[data_type])

    data_btn = st.checkbox('Show data')
    if data_btn:
        st.dataframe(chart_data)
    st.subheader('Data Metrics:')
    st.write('1. Aircraft Movement (**in Thousands**): all operational airports taken together handled aircraft \
                  movements (excluding General Aviation Movements).')
    st.write('2. Passengers (**in Millions**)')
    st.write('3. Freight (**in Tonnes**)')
    
        
    


