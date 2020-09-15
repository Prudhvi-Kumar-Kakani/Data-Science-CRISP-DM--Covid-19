##### libraries #####

import pandas as pd
import numpy as np

from datetime import datetime


def store_relational_JH_data():
    """
    Transformes the COVID data in a relational data set

    """
    
    # Load raw data
    data_path='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    raw_df = pd.read_csv(data_path)

    # rename columns
    pd_data_base = raw_df.rename(columns={'Country/Region':'country', 'Province/State':'state'})

    # fill countries without states with 'no'
    pd_data_base['state']=pd_data_base['state'].fillna('no')

    # drop lat and lon position columns
    pd_data_base = pd_data_base.drop(['Lat','Long'],axis=1)

    # change date to rows and countries to column
    pd_relational_model = pd_data_base.set_index(['state','country']) \
                                .T                              \
                                .stack(level=[0,1])             \
                                .reset_index()                  \
                                .rename(columns={'level_0':'date',
                                                   0:'confirmed'},
                                                  )
    
    # change format
    pd_relational_model['date']=pd_relational_model.date.astype('datetime64[ns]')

    # save to drive
    pd_relational_model.to_csv('data/processed/COVID_relational_confirmed.csv',sep=';',index=False)
    print(' Number of rows stored: '+str(pd_relational_model.shape[0]))
    print(' Latest date is: '+str(max(pd_relational_model.date)))

if __name__ == '__main__':

    store_relational_JH_data()