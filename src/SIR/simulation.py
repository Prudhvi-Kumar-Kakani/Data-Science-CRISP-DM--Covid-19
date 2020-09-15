##### libraries #####
import pandas as pd
import numpy as np
import os
import pickle

from sklearn.metrics import make_scorer
from scipy import optimize
from scipy import integrate

import matplotlib as mpl
import matplotlib.pyplot as plt


# SIR dynamic model
def SIR_model_t(SIR,t,beta,gamma):

    ''' Simple SIR model
        S: susceptible population
        t: time step, mandatory for integral.odeint
        I: infected people
        R: recovered people
        beta: 
        
        overall condition is that the sum of changes (differnces) sum up to 0
        dS+dI+dR=0
        S+I+R= N (constant size of population)
    
    '''
    
    S,I,R=SIR
    dS_dt=-beta*S*I/N0          #S*I is the 
    dI_dt=beta*S*I/N0-gamma*I
    dR_dt=gamma*I
    return dS_dt,dI_dt,dR_dt

def SIR_model(SIR,beta,gamma):
    ''' Simple SIR model
        S: susceptible population
        t: time step, mandatory for integral.odeint
        I: infected people
        R: recovered people
        beta: 
        
        overall condition is that the sum of changes (differnces) sum up to 0
        dS+dI+dR=0
        S+I+R= N (constant size of population)
    
    '''
    
    S,I,R=SIR
    dS_dt=-beta*S*I/N0          
    dI_dt=beta*S*I/N0-gamma*I
    dR_dt=gamma*I
    return dS_dt,dI_dt,dR_dt

def fit_odeint(x, beta, gamma):
    '''
    helper function for the integration
    '''
    return integrate.odeint(SIR_model_t, (S0, I0, R0), x, args=(beta, gamma))[:,1] # we only would like to get dI


def set_parameters(df_analyse, country):
    '''
    initalize parameters for 
    '''
 
    # initlaize population for particular country
    population = {
        'Brazil' : 209000000,
        'US' : 330000000,
        'United Kingdom' : 67000000
    }
    
    # get index for country with more than 1000 cases as start point
    n = df_analyse[df_analyse[country] >= 1000][country] .idxmin()
#     print(n)
    
    # store infected cases 
    ydata = np.array(df_analyse[country][n:])
    
    # get day index
    t=np.arange(0, len(ydata))
    
  
    return ydata, t, population[country]

def SIR_dynamic_model(country, interval = 7):
    
    global S0, I0, R0, N0, t
     # load processed data
    df_analyse=pd.read_csv('../data/processed/COVID_small_table_confirmed.csv',sep=';') 
    
    ## set parameters ##
    ydata, t, population_size = set_parameters(df_analyse, country)
       
    # initalization for SIR_model
    N0= population_size  # population
    I0=ydata[0]    # infected 
    S0=N0-I0       # suspected
    R0=0           # recovered
    
    #initaliye hzperparameters
    beta=0.4
    gamma=0.4
    
    ######## Among three solutions, interval fit is selected ##########
    
    # initalize array
    interval_fitted = np.array([])

    # initalize array of SIR values
    SIR=np.array([S0,I0,R0])
    
    for i in range(len(ydata)):
        
        # select interval data
        interval_data = ydata[i*interval:(i*interval)+interval]
        interval_t = np.arange(len(interval_data))
        
        # check for condition
        if interval_data.size == 0:
            break

        #Re-initialize SIR for each interval
        I0 = interval_data[0]                  
        S0 = N0-I0 
        R0 = SIR[2] 
    
        # optimize curvefit
        popt, pcov = optimize.curve_fit(fit_odeint, interval_t, interval_data, maxfev=1500)
    
        # Recalculate SIR with new_delta
        new_delta = SIR_model(SIR,*popt)
        SIR = SIR + new_delta
        
        # temporary fit for interval
        temp_fit = fit_odeint(interval_t,*popt)
        
        # fit with other interval data
        interval_fitted = np.hstack((interval_fitted, temp_fit))
        
    return ydata, interval_fitted

if __name__ == '__main__':
    

    Brazil_ydata, Brazil_fitted = SIR_dynamic_model('Brazil')
    United_Kingdom_ydata, United_Kingdom_fitted = SIR_dynamic_model('United Kingdom')
    US_ydata, US_fitted = SIR_dynamic_model('US')
    
    cocn_dict = {'Brazil_ydata' : Brazil_ydata, 'Brazil_fitted' : Brazil_fitted }
    df_Brazil= pd.DataFrame(cocn_dict)
    
    cocn_dict = {'United_Kingdom_ydata' : United_Kingdom_ydata, 'United_Kingdom_fitted' : United_Kingdom_fitted }
    df_United_Kingdom = pd.DataFrame(cocn_dict)
    
    cocn_dict = {'US_ydata': US_ydata, 'US_fitted' : US_fitted}
    df_US = pd.DataFrame(cocn_dict)
    
    dynamic_model = pd.concat([df_Brazil, df_US, df_United_Kingdom], axis=1)

    dynamic_model.to_csv('../data/processed/COVID_infected_cases_dynamic_model.csv', sep = ';', index=False)