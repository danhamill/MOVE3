import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from core.MOVE import comp_extended_record


st.title('MOVE.3 Record Extension')

DATE_COLUMN = 'date/time'
DATA_URLS = {'long':'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Etowah.csv',
             'short': 'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Suwanee.csv'}

def merge_flow_data(short_data, long_data):
    #Merge short and long data for chart plotting
    short_data.loc[:,'Record_Type'] = 'Short Record'
    long_data.loc[:, 'Record_Type'] = 'Long Record'
    merge = pd.concat([long_data, short_data])
    merge.loc[:,'WY'] = pd.to_datetime(merge.WY, format = '%Y')
    return merge



@st.cache(allow_output_mutation=True)
def load_data(fpath):
    data = pd.read_csv(fpath, header=None, names = ['WY','FLOW'])
    return data



data_load_state = st.text('Loading data...')
short_data = load_data(DATA_URLS['short'])
long_data = load_data(DATA_URLS['long'])
data_load_state.text("Done! (using st.cache)")

col1, col2 = st.beta_columns(2)
if col1.checkbox('Show short data'):
    col1.subheader('Short data')
    col1.write(short_data)

if col2.checkbox('Show long data'):
    col2.subheader('Long data')
    col2.write(long_data)

merge = merge_flow_data(short_data, long_data)

c = alt.Chart(merge).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'), 
    tooltip = ['WY','FLOW','Record_Type']
)

st.altair_chart(c,use_container_width=True)


short_years = list(short_data.WY)
short_record = list(short_data.FLOW)
long_years = list(long_data.WY)
long_record = list(long_data.FLOW)

out = comp_extended_record(short_years, short_record, long_years, long_record)

extended_record = pd.DataFrame(data = {'WY':out[1], 'FLOW':out[0]})

st.write(extended_record)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# st.map(filtered_data)