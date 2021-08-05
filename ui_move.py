import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from core.move3 import MOVE3
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

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

res = MOVE3(merge)
res.calculate()

stats = {'y_bar1': res.ybar1,
         'x_bar1' : res.xbar1,
         'x_bar2': res.xbar2,
         'var_y1': res.s_sq_y1,
         'var_x1': res.s_sq_x1,
         'var_x2': res.s_sq_x2,
         'mu_hat_y': res.mu_hat_y,
         'beta_hat': res.beta_hat,
         'alpha_sq': res.alpha_sq,
         'n1':res.n1,
         'n2':res.n2,
         'A': res.A,
         'B': res.B,
         'C': res.C,
         'ne': res.ne_int,
         'p_hat': res.p_hat}


con_df = pd.DataFrame(data = {'WY': res.concurrent_years, 
                                        'Short Record': 10**res.con_short_record,
                                        'Long Record':  10**res.con_long_record}).set_index('WY')

con_df_log = pd.DataFrame(data = {'WY': res.concurrent_years, 
                                        'Short Record': res.con_short_record,
                                        'Long Record':  res.con_long_record}).set_index('WY')

con_chart = alt.Chart(con_df.reset_index()).mark_circle().encode(
        x = alt.X('Long Record', axis = alt.Axis(title = 'Annual Peak Flow, Long Record'), scale = alt.Scale(type='log')),
        y = alt.Y('Short Record', axis = alt.Axis(title = 'Annual Peak Flow, Short Record'), scale = alt.Scale(type='log')),
        tooltip = ['WY']
    )


linear_model = LinearRegression().fit(con_df_log[['Long Record']], con_df_log[['Short Record']])

con_slope = float(np.round(linear_model.coef_,4))
con_int = float(np.round(10**linear_model.intercept_,4))
print(con_int)
y_pred = linear_model.predict(con_df_log[['Long Record']])
r_sqd = np.round(r2_score( con_df_log[['Short Record']], y_pred),3)

eqn = f"y ={con_int}x^{con_slope} "
print(eqn)
st.write(eqn)
st.latex(rf"R^{2} = {r_sqd}")


st.altair_chart(con_chart, use_container_width=True)

if st.checkbox("Show Move 3 Statistics"):

    stat_df = pd.DataFrame.from_dict(stats, orient='index', columns = ['Parameter'])
    st.write(stat_df)


extend_df = pd.DataFrame(data = {'WY': pd.to_datetime(res.extended_short_years, format = '%Y'),
                                    'FLOW': res.extended_short_record,
                                    'Record_Type':'Extended Sort Record'})
extend_chart = alt.Chart(extend_df).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'), 
    tooltip = ['WY','FLOW','Record_Type']
)

merge_chart= alt.layer(c, extend_chart)
st.altair_chart(merge_chart, use_container_width=True)

# c1 = alt.Chart()




# extended_record = pd.DataFrame(data = {'WY':out[1], 'FLOW':out[0]})

# st.write(extended_record)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# st.map(filtered_data)