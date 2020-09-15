##### libraries #####
import numpy as np
from sklearn import linear_model

import pandas as pd

from scipy import signal

# regression model
reg = linear_model.LinearRegression(fit_intercept=True)

def get_doubling_time_via_regression(input_array):
    """
        Use a linear regression to approximate the doubling rate

            Parameters:
            ----------
            input_array : pandas.series

            Returns:
            ----------
            Doubling rate: double
    """

    y = np.array(input_array)
    X = np.arange(-1, 2).reshape(-1, 1)

    assert len(input_array)==3

    reg.fit(X, y)
    intercept=reg.intercept_
    slope=reg.coef_

    return intercept/slope


def savgol_filter(df_input, column='confirmed', window=3, degree=1):
    """
       Savgol Filter which can be used in groupby apply function (data structure kept)

        parameters:
        ----------
        df_input : pandas.series
        column : str
        window : int
            used for data points to calculate the filter result
        degree : int
            polynomial degree

        Returns:
        ----------
        df_result: pd.DataFrame
            the index of the df_input has to be preserved in result
    
    """

    
    df_result=df_input

    filter_in=df_input[column].fillna(0) # attention with the neutral element here

    result=signal.savgol_filter(np.array(filter_in),
                           window, # window size used for filtering
                           degree  # degree of ploynomial
                               )

    df_result[str(column+'_filtered')]=result

    return df_result


def rolling_reg(df_input,col='confirmed', days_back=3):
    """
        Rolling Regression to approximate the doubling time'

            Parameters:
            ----------
            df_input: pd.DataFrame
            col: str
                defines the used column
            days_back : int
                time period days for rolling 

            Returns:
            ----------
            result: pd.DataFrame
    
    """
    
    result=df_input[col].rolling(
                window=days_back,
                min_periods=days_back).apply(get_doubling_time_via_regression, raw=False)

    return result


def calc_filtered_data(df_input,filter_on='confirmed'):
    '''  
    Calculate savgol filter and return merged data frame

        Parameters:
        ----------
        df_input: pd.DataFrame
        filter_on: str
            defines the used column

        Returns:
        ----------
        df_output: pd.DataFrame
            the result will be joined as a new column on the input data frame
    '''

    must_contain=set(['state','country',filter_on])

    assert must_contain.issubset(set(df_input.columns)), ' Error in -calc_filtered_data-func, not all required columns in data frame'

    df_output=df_input.copy() # we need a copy here otherwise the filter_on column will be overwritten

    pd_filtered_result=df_output[['state','country',filter_on]].groupby(['state','country']).apply(savgol_filter)#.reset_index()

    df_output=pd.merge(df_output,pd_filtered_result[[str(filter_on+'_filtered')]],left_index=True, right_index=True, how='left')
    #print(df_output[df_output['country']=='Germany'].tail())

    return df_output.copy()


def calc_doubling_rate(df_input, filter_on='confirmed'):
    ''' 
    Calculate approximated doubling rate and return merged data frame

        Parameters:
        ----------
        df_input: pd.DataFrame
        filter_on: str
            defines the used column

        Returns:
        ----------
        df_output: pd.DataFrame
            the result will be joined as a new column on the input data frame
    '''

    must_contain=set(['state','country',filter_on])
    assert must_contain.issubset(set(df_input.columns)), ' Error in -calc_filtered_data-func, not all required columns in data frame'


    pd_DR_result= df_input.groupby(['state','country']).apply(rolling_reg,filter_on).reset_index()

    pd_DR_result=pd_DR_result.rename(columns={filter_on:filter_on+'_DR',
                             'level_2':'index'})

    #we do the merge on the index of our big table and on the index column after groupby
    df_output=pd.merge(df_input,pd_DR_result[['index',str(filter_on+'_DR')]],left_index=True,right_on=['index'],how='left')
    df_output=df_output.drop(columns=['index'])


    return df_output


if __name__ == '__main__':

    # test structure
    test_data_reg=np.array([2,4,6])
    result=get_doubling_time_via_regression(test_data_reg)
    print('the test slope is: '+str(result))


    pd_JH_data=pd.read_csv('data/processed/COVID_relational_confirmed.csv',sep=';',parse_dates=[0])
    pd_JH_data=pd_JH_data.sort_values('date',ascending=True).copy()

    pd_result_larg=calc_filtered_data(pd_JH_data)
    pd_result_larg=calc_doubling_rate(pd_result_larg)
    pd_result_larg=calc_doubling_rate(pd_result_larg,'confirmed_filtered')


    mask=pd_result_larg['confirmed']>100
    pd_result_larg['confirmed_filtered_DR']=pd_result_larg['confirmed_filtered_DR'].where(mask, other=np.NaN)
    pd_result_larg.to_csv('data/processed/COVID_final_set.csv',sep=';',index=False)
    print(pd_result_larg[pd_result_larg['country']=='Germany'].tail())