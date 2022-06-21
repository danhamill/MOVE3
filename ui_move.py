import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import altair as alt
from core.move3 import MOVE3
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

st.title('USGS MOVE.3 Record Extension Example')

DATE_COLUMN = 'date/time'
DATA_URLS = {'long':'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Etowah.csv',
             'short': "https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Suwanee.csv"}

def merge_flow_data(short_data, long_data):
    #Merge short and long data for chart plotting
    short_data.loc[:,'Record_Type'] = 'Short Record'
    long_data.loc[:, 'Record_Type'] = 'Long Record'
    merge = pd.concat([long_data, short_data])
    merge.loc[:,'WY'] = pd.to_datetime(merge.WY, format = '%Y')
    return merge

@st.cache(allow_output_mutation=True)
def load_data_short(fpath):
    data = pd.read_csv(fpath,  header=None, names = ['WY','flow'])
    return data

@st.cache(allow_output_mutation=True)
def load_data_long(fpath):
    data = pd.read_csv(fpath, header=None, names = ['WY','flow'])
    return data

data_load_state = st.text('Loading data...')
short_data = load_data_short(DATA_URLS['short'])
long_data = load_data_long(DATA_URLS['long'])
data_load_state.text("Done! (using st.cache)")

col1, col2 = st.columns(2)
if col1.checkbox('Show short record'):
    col1.subheader('Short record (Suwanee)')
    col1.write(short_data)

if col2.checkbox('Show long record'):
    col2.subheader('Long record (Etowah)')
    col2.write(long_data)

merge = merge_flow_data(short_data, long_data)
merge.columns = ['WY','FLOW','Record_Type']

selection= alt.selection_multi(fields=['Record_Type'], bind='legend')

c = alt.Chart(merge).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'), 
    tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_selection(selection)

st.altair_chart(c,use_container_width=True)

res = MOVE3(merge)
res.calculate()

move_stats = {'y_bar1': res.ybar1,
            'x_bar1' : res.xbar1,
            'x_bar2': res.xbar2,
            'var_y1': res.s_sq_y1,
            'var_x1': res.s_sq_x1,
            'var_x2': res.s_sq_x2,
            'mu_hat_y': res.mu_hat_y,
            'sigma_hat_y':res.sigma_hat_y_sq,
            'beta_hat': res.beta_hat,
            'alpha_sq': res.alpha_sq,
            'n1':res.n1,
            'n2':res.n2,
            'A': res.A,
            'B': res.B,
            'C': res.C,
            'p_hat': res.p_hat}

stats_mean = {'ne': res.ne_mean,
              'a': res.a_mean,
              'b':res.b_mean}

stats_var = {'ne': res.ne_var,
             'a': res.a_var,
             'b':res.b_var}

stats_n2 = {'ne': res.n2,
            'a': res.a_n2,
            'b':res.b_n2,
            }

con_df = pd.DataFrame(data = {'WY': res.concurrent_years, 
                                        'Short Record': 10**res.con_short_record,
                                        'Long Record':  10**res.con_long_record}).set_index('WY')

con_df_log = pd.DataFrame(data = {'WY': res.concurrent_years, 
                                        'Short Record': res.con_short_record,
                                        'Long Record':  res.con_long_record}).set_index('WY')




linear_model = LinearRegression().fit(con_df_log[['Long Record']], con_df_log[['Short Record']])

con_slope = float(np.round(linear_model.coef_,4))
con_int = float(np.round(10**linear_model.intercept_,4))
y_pred = linear_model.predict(con_df_log[['Long Record']])
r_sqd = np.round(r2_score( con_df_log[['Short Record']], y_pred),3)

col1, col2 = st.columns(2)
eqn = fr"y ={con_int}x^{chr(123)}{con_slope}{chr(125)} "
col1.latex(eqn)
col2.latex(rf"R^{2} = {r_sqd}")


con_chart = alt.Chart(con_df.reset_index()).mark_circle().encode(
        x = alt.X('Long Record',  axis = alt.Axis(title = 'Annual Peak Flow, Etowah'), scale = alt.Scale(type='log')),
        y = alt.Y('Short Record', axis = alt.Axis(title = 'Annual Peak Flow, Suwanee'), scale = alt.Scale(type='log')),
        tooltip = [alt.Tooltip('WY:T', format='%Y')]
    )

con_df.loc[:,'xrange'] = np.linspace(3000,30000, con_df.shape[0])
con_df.loc[:,'yrange'] = con_int*con_df.xrange**(con_slope)


con_chart2 = alt.Chart(con_df.reset_index()).mark_line(color='black').encode(
        x = alt.X('xrange', axis = alt.Axis(title = 'Annual Peak Flow, Etowah'),  scale = alt.Scale(domain = [3000,30000],type='log')),
        y = alt.Y('yrange', axis = alt.Axis(title = 'Annual Peak Flow, Suwanee'),  scale = alt.Scale(type='log'))
    )

con_merge = alt.layer( con_chart2, con_chart)


st.altair_chart(con_merge, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
if col1.checkbox("Show MOVE.3 Parameters"):

    stat_df_move = pd.DataFrame.from_dict(move_stats, orient='index', columns = ['Parameter'])
    col1.write(stat_df_move)

if col2.checkbox("ne extension (variance)"):

    stat_df_var = pd.DataFrame.from_dict(stats_var, orient='index', columns = ['Parameter'])
    col2.write(stat_df_var)

if col3.checkbox("ne extension (mean)"):
    stat_df_mean = pd.DataFrame.from_dict(stats_mean, orient='index', columns = ['Parameter'])
    col3.write(stat_df_mean)

if col4.checkbox('n2 extension'):
    stat_df_n2 = pd.DataFrame.from_dict(stats_n2, orient='index', columns = ['Parameter'])
    col4.write(stat_df_n2)

extend_df_var = pd.DataFrame(data = {'WY': pd.to_datetime(res.extended_short_years_var, format = '%Y'),
                                    'FLOW': res.extended_short_record_var,
                                    'Record_Type':'Extended Short Record (variance)'})
                                    
extend_df_mean = pd.DataFrame(data = {'WY': pd.to_datetime(res.extended_short_years_mean, format = '%Y'),
                                    'FLOW': res.extended_short_record_mean,
                                    'Record_Type':'Extended Short Record (mean)'})

extend_df_n2 = pd.DataFrame(data = {'WY': pd.to_datetime(res.extended_short_years_n2, format = '%Y'),
                                    'FLOW': res.extended_short_record_n2,
                                    'Record_Type':'Extended Short Record (n2)'})

extend_chart_mean = alt.Chart(extend_df_mean).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2)), 
    # tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type']
)

extend_chart_var = alt.Chart(extend_df_var).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2)), 
    # tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type']
)

extend_chart_n2 = alt.Chart(extend_df_n2).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW', scale = alt.Scale(type='log')),
    color = alt.Color('Record_Type'),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2)), 
    # tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type']
)

merge_chart_mean= alt.layer(c, extend_chart_mean).add_selection(
    selection
)

mearge_chart_var = alt.layer(c, extend_chart_var).add_selection(
    selection
)

mearge_chart_n2 = alt.layer(c, extend_chart_n2).add_selection(
    selection
)

if st.checkbox('Show Mean Extension Plot'):
    st.write('Mean Based Extension')
    st.latex(res.mean_extension_equation)
    st.altair_chart(merge_chart_mean, use_container_width=True)

if st.checkbox('Show Variance Extension Plot'):
    st.write('Variance Based Extension')
    st.latex(res.var_extension_equation)
    st.altair_chart(mearge_chart_var, use_container_width = True)

if st.checkbox('Show n2 Extension Plot'):
    st.write('Variance Based Extension')
    st.latex(res.n2_extension_equation)
    st.altair_chart(mearge_chart_n2, use_container_width = True)

if st.checkbox("Show Extended Dataset (mean)"):
    st.write(extend_df_mean)
if st.checkbox("Show Extended Dataset (variance)"):
    st.write(extend_df_var)

if st.checkbox("Show Extended Dataset (n2)"):
    st.write(extend_df_n2)
