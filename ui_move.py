import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from core.MOVE import comp_extended_record


st.title('MOVE.3 Record Extnsion')

DATE_COLUMN = 'date/time'
DATA_URLS = {'long':'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Etowah.csv',
             'short': 'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Suwanee.csv'}


@st.cache(allow_output_mutation=True)
def load_data(fpath):
    data = pd.read_csv(fpath, header=None, names = ['WY','FLOW'])
    return data

data_load_state = st.text('Loading data...')
short_data = load_data(DATA_URLS['short'])
long_data = load_data(DATA_URLS['long'])
data_load_state.text("Done! (using st.cache)")

#Merge short and long data for chart plotting
short_data.loc[:,'Record_Type'] = 'Short Record'
long_data.loc[:, 'Record_Type'] = 'Long Record'
merge = pd.concat([long_data, short_data])

merge.loc[:,'WY'] = pd.to_datetime(merge.WY, format = '%Y')

c = alt.Chart(merge).mark_circle().encode(
    x = alt.X('WY:T'),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'), 
    tooltip = ['WY','FLOW','Record_Type']
)

st.altair_chart(c,use_container_width=True)

if st.checkbox('Show short data'):
    st.subheader('Short data')
    st.write(short_data)

if st.checkbox('Show long data'):
    st.subheader('Long data')
    st.write(short_data)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# st.map(filtered_data)