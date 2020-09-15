##### libraries #####
import dash
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

import plotly.graph_objects as go
import plotly.express as px


# Load processed file 
df_plot=pd.read_csv('../data/processed/COVID_infected_cases_dynamic_model.csv', sep=';')  


fig = go.Figure()

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)
app.layout = html.Div([

    dcc.Markdown('''
    #  Applied Data Science on COVID-19 data - SIR model

    In the dashboard, the SIR model is used for calculation for dynamic simulated infection spread. 
    The simulated values of curve are obtained after finding optimized values of infection rate and recovery rate as interval fit to data for every 7 days.

    '''),

    dcc.Markdown('''
    ## Select a country for visualization
    '''),


    dcc.Dropdown(
        id='country_drop_down',
        options=[ {'label': each,'value':each} for each in ['United Kingdom', 'Brazil', 'US']],
        value='Brazil',  #  pre-selected
        multi=False
    ),


    dcc.Graph(id='dynamic', figure= fig, )
])

@app.callback(
    Output('dynamic', 'figure'),
    [Input('country_drop_down', 'value')])

def update_figure(country):
    
    # column names
    ydata = '{}_ydata'.format(country)
    fitted = '{}_fitted'.format(country)
    
    # select data
    df_select = df_plot[[ydata, fitted]]
    
    
    
    # Add traces
    traces=[]
    traces.append(go.Scatter(x=df_select.index, y=df_select[ydata],
                        mode='lines+markers', name='{}'.format(country),
                             marker=dict(
                         color='rgb(125, 178, 102)',
                         size=10,
                         line=dict(
                            color='DarkSlateGrey',
                            width=1
                          ),

                             ))),
                 
                 
    traces.append(go.Bar( x = df_select.index, y=df_select[fitted],
                        name='{}_simulated'.format(country), 
                          )
                 ) 
             
    
    return {
            'data': traces,
             
            'layout': dict (
                width = 1280,
                height = 720,
                
                xaxis={'title':'No. of days of infection',
                        'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#171717"),
                      },

                yaxis= {'title':'No. of infected cases (non-log scale)',
                        'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#171717"),
                      },
                xaxis_rangeslider_visible = True
        )
    }


# dashboard
if __name__ == '__main__':

    app.run_server(debug=True, use_reloader=False, port = 8853)