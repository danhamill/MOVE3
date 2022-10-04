import pandas as pd
import numpy as np
import altair as alt
from altair_saver import save
from core.move3 import MOVE3
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def getData(excelFile, sheet_name, record_type):
    isb = pd.read_excel(excelFile, sheet_name = sheet_name)
    isb = isb.set_index('Year')
    isb = isb[[i for i in isb.columns if 'Day' in i]].stack()
    isb.index.names = ['WY','n-day']
    isb.name = 'FLOW'
    isb = isb.reset_index()
    isb.loc[:,'Record_Type'] = record_type
    return isb

def getMOVE(merge, nDay):

    selection= alt.selection_multi(fields=['Record_Type'], bind='legend')
    c = alt.Chart(merge).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'), 
    tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_selection(selection)

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
                'b':res.b_mean,
                'x_bar':res.xe_bar_mean}

    stats_var = {'ne': res.ne_var,
                'a': res.a_var,
                'b':res.b_var,
                'x_bar':res.xe_bar_var}

    stats_n2 = {'ne': res.n2,
                'a': res.a_n2,
                'b':res.b_n2,
                'x_bar': res.xe_bar_n2
                }

    con_df = pd.DataFrame(data = {'WY': res.concurrent_years, 
                                            'Short Record': 10**res.con_short_record,
                                            'Long Record':  10**res.con_long_record}).set_index('WY')

    con_df_log = pd.DataFrame(data = {'WY': res.concurrent_years, 
                                            'Short Record': res.con_short_record,
                                            'Long Record':  res.con_long_record}).set_index('WY')

    con_chart = alt.Chart(con_df.reset_index()).mark_circle().encode(
            x = alt.X('Long Record', axis = alt.Axis(title = f'Annual Maximum {nDay} Flow (cfs), Kern Bakersfield'), scale = alt.Scale(domain = [100, 100000], type='log')),
            y = alt.Y('Short Record', axis = alt.Axis(title = f'Annual Maximum {nDay} Flow (cfs), Isabella'), scale = alt.Scale(type='log')),
            tooltip = [alt.Tooltip('WY:T', format='%Y')]
        )

    con_df.loc[:,'xrange'] = np.linspace(100,100000, con_df.shape[0])
    con_df.loc[:,'yrange'] = 1.2594*con_df.xrange**(0.9641)


    con_chart2 = alt.Chart(con_df.reset_index()).mark_line(color='black').encode(
            x = alt.X('xrange', axis = alt.Axis(title = f'Annual Maximum {nDay} Flow (cfs), Kern Bakersfield'), scale = alt.Scale(domain = [100, 100000],type='log')),
            y = alt.Y('yrange', axis = alt.Axis(title = f'Annual Maximum {nDay} Flow (cfs), Isabella'), scale = alt.Scale(type='log'))
        )

    con_merge = alt.layer( con_chart2, con_chart)

    # save(con_merge, r'output\scatter_compariton.svg', method= 'selenium', scale_factor =3)


    linear_model = LinearRegression().fit(con_df_log[['Long Record']], con_df_log[['Short Record']])

    con_slope = float(np.round(linear_model.coef_,4))
    con_int = float(np.round(10**linear_model.intercept_,4))
    y_pred = linear_model.predict(con_df_log[['Long Record']])
    r_sqd = np.round(r2_score( con_df_log[['Short Record']], y_pred),3)

    
    eqn = fr"y ={con_int}x^{chr(123)}{con_slope}{chr(125)} "

    stat_concurrent = pd.DataFrame(index = [nDay], data = {'equation': eqn, 'rSqd': r_sqd})

    stat_df_move = pd.DataFrame.from_dict(move_stats, orient='index', columns = [nDay])


    stat_df_var = pd.DataFrame.from_dict(stats_var, orient='index', columns = [nDay])



    stat_df_mean = pd.DataFrame.from_dict(stats_mean, orient='index', columns = [nDay])


    stat_df_n2 = pd.DataFrame.from_dict(stats_n2, orient='index', columns = [nDay])


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
    # save(mearge_chart_n2, r'output\extended_record.svg', method= 'selenium', scale_factor =3)

    e = pd.concat([extend_df_var, extend_df_mean, extend_df_n2])
    e.loc[:,'n-day'] = nDay
    return stat_concurrent, stat_df_move, stat_df_mean, stat_df_var, stat_df_n2, e, con_merge


excelFile = r'C:\workspace\Isabella_Dam\flow_data\ssp\ISB_WCM_RainFlood_Durations.xlsx'

isb = getData(excelFile, 'ISB', 'Short Record')
krn = getData(excelFile, 'KERN', 'Long Record')

df = pd.concat([isb,krn])
df.loc[:,'WY'] = pd.to_datetime(df.loc[:,'WY'].astype(str) + '-01-06', format = '%Y-%d-%m')


concurrent_stats = pd.DataFrame()
move_stats = pd.DataFrame()
mean_stats = pd.DataFrame()
var_stats = pd.DataFrame()
n2_stats = pd.DataFrame()
all_data = pd.DataFrame()
charts = {}

for nDay, merge in df.groupby('n-day'):
    
    nday_parts = nDay.split('-')
    nday_parts[0] = nday_parts[0].zfill(2)
    nDay = '-'.join(nday_parts)

    stat_concurrent, stat_df_move, stat_df_mean, stat_df_var, stat_df_n2, extendedData, con_merge = getMOVE(merge, nDay)
    
    concurrent_stats = pd.concat([concurrent_stats, stat_concurrent])
    move_stats = pd.concat([move_stats, stat_df_move], axis=1)
    mean_stats = pd.concat([mean_stats, stat_df_mean], axis=1)
    var_stats = pd.concat([var_stats, stat_df_var], axis=1)
    n2_stats = pd.concat([n2_stats, stat_df_n2], axis=1)
    all_data = pd.concat([all_data, extendedData])
    charts[nDay] = con_merge


concurrent_stats = concurrent_stats.sort_index()
move_stats = move_stats.sort_index(axis=1)
mean_stats = mean_stats.sort_index(axis=1)
var_stats = var_stats.sort_index(axis=1)
n2_stats = n2_stats.sort_index(axis=1)

c = ((charts['01-Day'] |charts['03-Day']|charts['07-Day'] ) & (charts['15-Day']|charts['30-Day']))

save(c, r'output\bivariate_mulitple_nday.svg', method = 'selenium')

print('here')

extend_chart_var = alt.Chart(all_data.loc[all_data.Record_Type.str.contains('variance')]).mark_circle().encode(
    x = alt.X('WY:T', axis = alt.Axis(format = '%Y')),
    y = alt.Y('FLOW'),
    color = alt.Color('Record_Type'),
    facet = alt.Facet('n-day', columns = 3)
    # tooltip = [alt.Tooltip('WY:T', format='%Y') ,'FLOW','Record_Type']
)

aa = all_data.loc[all_data.Record_Type.str.contains('n2')]
aa = aa.drop('Record_Type', axis=1)
aa = aa.set_index(['WY','n-day']).unstack('n-day')

