import pandas as pd
import numpy as np
from core.move3 import MOVE3
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import altair as alt
alt.renderers.enable('altair_viewer')


DATA_URLS = {'long':'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Etowah.csv',
             'short': 'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Suwanee.csv'}

def merge_flow_data(short_data, long_data):
    #Merge short and long data for chart plotting
    short_data.loc[:,'Record_Type'] = 'Short Record'
    long_data.loc[:, 'Record_Type'] = 'Long Record'
    merge = pd.concat([long_data, short_data])
    merge.loc[:,'WY'] = pd.to_datetime(merge.WY, format = '%Y')
    return merge

def load_data(fpath):
    data = pd.read_csv(fpath, header=None, names = ['WY','FLOW'])
    return data

def main():
    short_data = load_data(DATA_URLS['short'])
    long_data = load_data(DATA_URLS['long'])


    merge = merge_flow_data(short_data, long_data)

    res = MOVE3(merge)
    res.calculate()


    con_df = pd.DataFrame(data = {
        'WY': res.concurrent_years, 
        'Short Record': 10**res.con_short_record,
                                            'Long Record':  10**res.con_long_record}).set_index('WY')

    con_df_log = pd.DataFrame(data = {'WY': res.concurrent_years, 
                                            'Short Record': res.con_short_record,
                                            'Long Record':  res.con_long_record}).set_index('WY')

    con_chart = alt.Chart(con_df).mark_circle().encode(
            y = alt.Y('Short Record', axis = alt.Axis(title = 'Annual Peak Flow, Long Record'), scale = alt.Scale(type='log')),
            x = alt.X('Long Record', axis = alt.Axis(title = 'Annual Peak Flow, Short Record'), scale = alt.Scale(type='log'))
        )

    linear_model = LinearRegression().fit(con_df_log[['Long Record']], con_df_log[['Short Record']])

    con_slope = linear_model.coef_
    con_int = linear_model.intercept_
    y_pred = linear_model.predict(con_df_log[['Long Record']])
    r_sqd = r2_score( con_df_log[['Short Record']], y_pred)




    c = alt.Chart(con_df).mark_circle().encode(
        x = alt.X('Short Record', axis = alt.Axis(title = 'Annual Peak Flow, Long Record'), scale = alt.Scale(type='log')),
        y = alt.X('Long Record', axis = alt.Axis(title = 'Annual Peak Flow, Short Record'), scale = alt.Scale(type='log'))
    )

    extend_df = pd.DataFrame(data = {'WY': pd.to_datetime(res.extended_short_years_var, format = '%Y'),
                                     'FLOW': res.extended_short_record_var,
                                     'Record_Type':'Extended Sort Record'})
                                     
    extend_chart = alt.Chart(extend_df).mark_circle().encode(
        x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
        y = alt.Y('FLOW'),
        color = alt.Color('Record_Type'), 
        tooltip = ['WY','FLOW','Record_Type']
    )



if __name__ == '__main__':
    main()