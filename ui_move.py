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
    tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type']
)

st.altair_chart(c,use_container_width=True)

res = MOVE3(merge)
res.calculate()

stats_mean = {'y_bar1': res.ybar1,
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
            'ne': res.ne_n1_mean_int,
            'p_hat': res.p_hat}
stats_var = {'y_bar1': res.ybar1,
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
            'ne': res.ne_n1_var_int,
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
        tooltip = [alt.Tooltip('WY:T', format='%Y')]
    )


linear_model = LinearRegression().fit(con_df_log[['Long Record']], con_df_log[['Short Record']])

con_slope = float(np.round(linear_model.coef_,4))
con_int = float(np.round(10**linear_model.intercept_,4))
y_pred = linear_model.predict(con_df_log[['Long Record']])
r_sqd = np.round(r2_score( con_df_log[['Short Record']], y_pred),3)

col1, col2 = st.beta_columns(2)
eqn = fr"y ={con_int}x^{chr(123)}{con_slope}{chr(125)} "
col1.latex(eqn)
col2.latex(rf"R^{2} = {r_sqd}")


st.altair_chart(con_chart, use_container_width=True)

col1, col2 = st.beta_columns(2)
if col1.checkbox("Show MOVE.3 Statistics (mean)"):

    stat_df_mean = pd.DataFrame.from_dict(stats_mean, orient='index', columns = ['Parameter'])
    col1.write(stat_df_mean)
if col2.checkbox("Show MOVE.3 Statistics (variance)"):

    stat_df_var = pd.DataFrame.from_dict(stats_var, orient='index', columns = ['Parameter'])
    col2.write(stat_df_var)

extend_df_var = pd.DataFrame(data = {'WY': pd.to_datetime(res.extended_short_years_var, format = '%Y'),
                                    'FLOW': res.extended_short_record_var,
                                    'Record_Type':'Extended Short Record (variance)'})
extend_df_mean = pd.DataFrame(data = {'WY': pd.to_datetime(res.extended_short_years_mean, format = '%Y'),
                                    'FLOW': res.extended_short_record_mean,
                                    'Record_Type':'Extended Short Record (mean)'})

extend_chart_mean = alt.Chart(extend_df_mean).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'), 
    tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type']
)

extend_chart_var = alt.Chart(extend_df_var).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'), 
    tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type']
)
merge_chart_mean= alt.layer(c, extend_chart_mean)
mearge_chart_var = alt.layer(c, extend_chart_var)

if st.checkbox('Show Mean Extension Plot'):
    st.write('Mean Based Extension')
    st.latex(res.mean_extension_equation)
    st.altair_chart(merge_chart_mean, use_container_width=True)
if st.checkbox('Show Variance Extension Plot'):
    st.write('Variance Based Extension')
    st.latex(res.var_extension_equation)
    st.altair_chart(mearge_chart_var, use_container_width = True)

if st.checkbox("Show Extended Dataset (mean)"):
    st.write(extend_df_mean)
if st.checkbox("Show Extended Dataset (variance)"):
    st.write(extend_df_var)