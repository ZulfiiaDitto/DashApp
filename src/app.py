import pandas as pd
import numpy as np
from collections import defaultdict
from dash import Dash, dcc, Output, Input, html, State
import dash_bootstrap_components as dbc 
import plotly.express as px
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)



########## data wrangling before analysis 

df = pd.read_csv("https://raw.githubusercontent.com/ZulfiiaDitto/VizualizationFolder/master/Viz_With_Bokeh/Weekly_Provisional_Counts_of_Deaths_by_State_and_Select_Causes__2020-2022.csv")
df = df.sort_values(by = ['Jurisdiction of Occurrence','MMWR Year', 'MMWR Week'])
df['MMWR Year'] = df['MMWR Year'].astype(str)
df['Week Ending Date'] =df['Week Ending Date'].astype('datetime64[ns]')
df['Quarter'] =df['Week Ending Date'].dt.to_period('Q').astype(str)
df['Q']=df['Quarter'].apply(lambda x : x[-2:])
usa = df.loc[df['Jurisdiction of Occurrence'] =='United States']
dfState = df[~df['Jurisdiction of Occurrence'].isin(['United States','District of Columbia','New York City','Puerto Rico'])]




listChronic = ['Diabetes mellitus (E10-E14)', 'Alzheimer disease (G30)',
       'Chronic lower respiratory diseases (J40-J47)',
       'Diseases of heart (I00-I09,I11,I13,I20-I51)',
       'Cerebrovascular diseases (I60-I69)']

# lets create discrete pallete for the listChronic        
colorList = ['red', 'green', 'blue', 'goldenrod',]
colors = { k: v for (k,v) in zip(listChronic, colorList)  }
#print(colors)

listColumns = ['Natural Cause',
       'Septicemia (A40-A41)', 'Malignant neoplasms (C00-C97)',
       'Diabetes mellitus (E10-E14)', 'Alzheimer disease (G30)',
       'Influenza and pneumonia (J09-J18)',
       'Chronic lower respiratory diseases (J40-J47)',
       'Other diseases of respiratory system (J00-J06,J30-J39,J67,J70-J98)',
       'Nephritis, nephrotic syndrome and nephrosis (N00-N07,N17-N19,N25-N27)',
       'Symptoms, signs and abnormal clinical and laboratory findings, not elsewhere classified (R00-R99)',
       'Diseases of heart (I00-I09,I11,I13,I20-I51)',
       'Cerebrovascular diseases (I60-I69)',
       'COVID-19 (U071, Multiple Cause of Death)',
       'COVID-19 (U071, Underlying Cause of Death)']

resp = ['Influenza and pneumonia (J09-J18)',
       'Chronic lower respiratory diseases (J40-J47)',
       'COVID-19 (U071, Multiple Cause of Death)',
       'COVID-19 (U071, Underlying Cause of Death)' ]


#data = dfState[['Week Ending Date', 'Jurisdiction of Occurrence','MMWR Year', 'Q' ]].copy()
#print(data)

app = Dash(__name__, external_stylesheets=[dbc.themes.PULSE])
server = app.server
app.config.suppress_callback_exceptions=True
sidebar =html.Div(
       [
              dbc.Nav
              ([
                     dbc.NavLink('About', href = '/', active = "exact"),
                     dbc.NavLink("All cases, chonic disease cases", href='/all_cases', active ='exact'),
                     dbc.NavLink("Respiratory diseases cases", href = '/respiratory_disease_cases', active = 'exact')

              ], vertical = False, pills = True, fill=True, justified= True)
       ]
)

content = html.Div(id = "content_page", children= [])

######################## about page ######################
about = [dbc.Row
              (
                     [
                     dbc.Col(dbc.Button(
                                   "About dataset",
                                   id="collapse-button-dataset",
                                   className="mb-3",
                                   color="info", 
                                   n_clicks=0, 
                                   ), style = {
                                          "margin": "auto",
                                          "padding": "10px",
                                          "padding-left" : "250px", 
                                           "padding-top" : "150px",
                                          }, className='six columns'),
                     
                     dbc.Col(dbc.Button(
                                          "About the creator",
                                          id = "collapse-button-creator",
                                          className='mb-3',
                                          color='info', 
                                          n_clicks= 0
                                          ),style = {
                                          "margin": "auto",
                                          "padding": "10px",
                                          "padding-left" : "150px", 
                                          "padding-top" : "150px",
                                          'margin': "auto"
                                          },className='six columns')
                     ]
              ),
       dbc.Row([dbc.Col(dbc.Collapse(dbc.Card(dbc.CardBody(
              [html.P("The analysis utilized a public dataset of the number of deaths in the USA from different causes. The dataset includes three years from 2019 intill 2021, with granularity by state. The link bellow navigates you to the dataset website.",className="card-text"),
              dbc.CardLink("External link to dataset", href="https://catalog.data.gov/dataset/weekly-counts-of-deaths-by-state-and-select-causes-2019-2020")]
              )),
                                   id="collapse",
                                   is_open=False,style={"width": "18rem"}),style ={
                                          "padding": "10px",
                                          "padding-left" : "180px",}),
              dbc.Col(dbc.Collapse(dbc.Card(dbc.CardBody(
              [html.P("This dashboard had been created by Zulfiia Ditto. You can find my personal info in link bellow",className="card-text"),
              dbc.CardLink("External link to personal info", href="https://www.linkedin.com/in/zulfiia-ditto-ph-d-088681a9/")]
              )),
                                   id="collapse-creator",
                                   is_open=False,style={"width": "18rem"}),style ={
                                          "padding": "10px",
                                          "padding-left" : "180px",})
              ])
       ]

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button-dataset", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-creator", "is_open"),
    [Input("collapse-button-creator", "n_clicks")],
    [State("collapse-creator", "is_open")],
)
def toggle_collapse2(n, is_open):
    if n:
        return not is_open
    return is_open
############################### all cases page + chronic disease page
all_cases_content = [html.H2(children='Yearly Overview of Death Causes in USA', 
              style={'textAlign': 'center',
                     'color': 'black',
                     'padding-top': '70px',
                     'padding-bottom': '30px'}),
              dbc.Row(dbc.Col([ html.H6(children = "Please select year", style={'font-style': 'italic', 'color' : 'grey'}),
                            dcc.Dropdown(id = "YearDropDown",
                                                        value = '2020', 
                                                        multi = False, 
                                                        options = list(df['MMWR Year'].unique()),
                                                        clearable=False)],  width={"size": 6, "offset": 3})) , 
         
              dbc.Row([dbc.Col(dcc.Graph(id = "bar_chart", figure= {}, className='six columns' )),
                       dbc.Col(dcc.Graph(id = 'lines_disease', figure={}, 
                     config={
                      'staticPlot': False,     # True, False
                      'scrollZoom': True,      # True, False
                      'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                      'showTips': False,       # True, False
                      'displayModeBar': True,  # True, False, 'hover'
                      'watermark': True,
                        },
                  className='six columns'))]),
              dbc.Row([dbc.Col(className = 'six columns'), 
                     dbc.Col(html.Span(html.P(children= "By hovering over data points you can update the left graph 'Number of Deaths Caused by Chronic Diseases at particular week'",
                     style = {'border': 'solid', 'padding': "5px", })), className = 'six columns'),
                     ]),

                  html.H2(children='Yearly Overview of Death Causes by States', 
                     style={'textAlign': 'center',
                     'color': 'black', 
                     'padding-top': '70px',
                     'padding-bottom': '30px'}),
              
              dbc.Row([dbc.Col([html.H6(children = "Please select state", style={'font-style': 'italic', 'color' : 'grey'}),
                            dcc.Dropdown(id = 'StateDropDown', placeholder='Choose state',value = 'Alabama', 
                                                        multi = False, 
                                                        options = list(dfState['Jurisdiction of Occurrence'].unique()),
                                                        clearable=False)], 
                                          width={"size": 6, "offset": 3})]),  

              dbc.Row([dbc.Col(dcc.Graph(id = 'pie_chart_state', figure={}, className='six columns')),
                      dbc.Col(dcc.Graph(id = 'TS_state', figure = {}, className='six columns'))])  ]
@app.callback(
       [Output(component_id='lines_disease', component_property='figure'), 
       Output(component_id='TS_state', component_property='figure'), 
       Output(component_id= 'pie_chart_state', component_property='figure')],
       [Input(component_id='YearDropDown', component_property='value'),
       Input(component_id='StateDropDown', component_property='value')])

def update_graph(year, state):
       # Updating the line graph for USA 
       data = df.loc[(df['Jurisdiction of Occurrence'] =='United States') & (df['MMWR Year'].isin([year]))]
       fig = px.line(data_frame=data, x = 'Week Ending Date', 
                     y = 'All Cause', color = 'MMWR Year',
                     title=f'Number of All Deaths in USA in {year}',)
       fig.update_traces(mode='lines+markers')
       fig.update_layout(title_x=0.5, xaxis_title= None)

       if state is None: 
              dfState = df.loc[(df['Jurisdiction of Occurrence'].isin(['Alabama'])) 
                            & (df['MMWR Year']=='2020')]
       else: 
              dfState = df.loc[(df['Jurisdiction of Occurrence'].isin([state])) 
                            & (df['MMWR Year']==year)]

       stateFig = px.line(data_frame=dfState, x='Week Ending Date',
                     y = listChronic,
                     #color = listColumns, 
                     title = f'Number of Deaths Caused by Chronic Diseases <br> in State {state}, Year {year}', color_discrete_map=colors)
       stateFig.update_layout(title_x=0.5, xaxis_title= None)

       statePie = pd.melt(dfState.groupby(['MMWR Year'], as_index = False)[listChronic].sum(), var_name = 'disease', value_name='death count')
       statePie = statePie.loc[statePie.disease != 'MMWR Year']
       statePiefig = px.pie(data_frame= statePie, values='death count', 
                            names='disease', color = 'disease', title= f'Distribution(%) of Deaths Caused by Chronic Diseases in <br> State {state} during {year}',
                            color_discrete_map=colors, hole=0.3)
       statePiefig.update_layout(title_x=0.5, xaxis_title= None)      
       return (fig, stateFig, statePiefig)

@app.callback(
       Output(component_id='bar_chart', component_property='figure'),
      [Input(component_id='lines_disease', component_property='hoverData')])

def update_side_graph(hov_data):
    
    if hov_data is None:

        dff2 = df.loc[(df['Jurisdiction of Occurrence'] =='United States') & 
                     (df['Week Ending Date']=='2020-04-11'), listChronic]
        summT = pd.melt(dff2, value_vars=listChronic, var_name='disease') 

        fig2 = px.bar(data_frame=summT,  x='disease', y = 'value',  
                      title='Number of Deaths Caused by Chronic Diseases <br> at Week 2020-04-11', 
                      color='disease', color_discrete_map=colors)
        fig2.update_layout(title_x=0.5, xaxis_title= None)
        return fig2

    else:
        hover_week = hov_data['points'][0]['x']
        dff2 = df.loc[(df['Jurisdiction of Occurrence'] =='United States') & 
                     (df['Week Ending Date']==hover_week), listChronic]
        summT = pd.melt(dff2, value_vars=listChronic, var_name='disease')        
        fig2 = px.bar(data_frame=summT, x='disease', y = 'value', color = 'disease', color_discrete_map=colors,
                      title=f'Number of Deaths Caused by Chronic Diseases <br> at Week {hover_week}')
        fig2.update_layout(title_x=0.5, xaxis_title= None)
        return fig2


############################### respiratory disease page 
resp_disease_content = [html.H3(children='Yearly Overview of Deaths Caused by Respiratory Diseases', 
                             style={'textAlign': 'center',
                                   'color': 'black',
                                   'padding-top': '70px',
                                   'padding-bottom': '30px'}),
                     dbc.Row([dbc.Col(html.H6(children = "Please select year"),md=4, width={'offset': 1}, 
                                                 style={'font-style': 'italic', 'color' : 'grey'}),
                             dbc.Col(html.H6(children="Please select state"), md = 4, 
                                                 style={'font-style': 'italic', 'color' : 'grey'})]),

                     dbc.Row([dbc.Col(dcc.Dropdown(id = "YearRespDown",
                                                        value = '2020', 
                                                        multi = False, 
                                                        options = list(df['MMWR Year'].unique()),
                                                        clearable=False),
                                                        style={'padding-bottom' :'30px'}, md = 4, width={'offset': 1}) ,
                     
                            (dbc.Col(dcc.Dropdown(id = "StateRespDown", placeholder = 'Select State',
                                                        value = 'Alabama', 
                                                        multi = False, 
                                                        options = list(dfState['Jurisdiction of Occurrence'].unique()),
                                                        clearable=False),  md = 4)) ]) ,
 

                     dbc.Row([dbc.Col(html.Div(dcc.Graph(id = 'line-chart-resp', figure={}, className='six columns')))]),
                            
                     dbc.Row([dbc.Col(html.Div(dcc.Graph(id = 'box-plot-resp', figure = {}) ), md = 8),
                            dbc.Col([html.H6(children='Please select the quarter', style= {"color": 'grey', 'font-style': 'italic' , 'padding-top': '50px'}),
                                     html.Div(dcc.Dropdown(id = 'QuarterSelector',  
                                                          value = 'Q1', 
                                                          multi = False, 
                                                          clearable = False,
                                                        options = list(dfState['Q'].unique())
                                                        ))
                                   ], md = 4)])]   


@app.callback(
       [Output(component_id='line-chart-resp', component_property='figure'),
       Output(component_id='box-plot-resp', component_property='figure')],   
       [Input(component_id='YearRespDown', component_property='value'),
       Input(component_id='StateRespDown', component_property='value'),
       Input(component_id='QuarterSelector', component_property='value')  
       ])


def update_graph_tab2(year, state, quar):
       data = dfState[resp + ['Week Ending Date', 'Jurisdiction of Occurrence','MMWR Year', 'Q' ]].copy()
       data = data.fillna(value = 0)

       if state is None and year is None: 

              respdf = data.loc[(data['Jurisdiction of Occurrence']== 'Alabama') 
              & (data['MMWR Year']== '2020')]
       else:
              respdf = data.loc[(data['Jurisdiction of Occurrence']== state) & (data['MMWR Year']== year) ]


       if quar is None:
                     respdfQ = respdf.loc[respdf['Q'] == 'Q1']
       else:

                     respdfQ = respdf.loc[respdf['Q'] == quar]
              
       figBox = px.box(respdfQ, x = resp , title=f'Distribution of the Respiratory Deaths <br> in State {state}, Year {year}, Quarter {quar}')                       
       figBox.update_layout(title_x=0.6, xaxis_title= None)

       respline = px.line(data_frame=respdf, x='Week Ending Date',
                     y = resp, 
                     title = f'Number of Deaths in State {state}, Year {year} from Respiratory Diseases' )
       respline.update_layout(title_x=0.5, xaxis_title= None)

       
       
       return (respline, figBox)


############################ render page logic 

@app.callback(Output('content_page', 'children'), [Input('url', 'pathname')])
def render_page(pathname):
       if pathname == '/all_cases':
              return all_cases_content
       elif pathname == '/respiratory_disease_cases':
              return resp_disease_content
       elif pathname=='/':
              return about



app.layout = html.Div([dcc.Location(id = 'url'), 
                     sidebar, content]) 

if __name__ == "__main__":
    app.run_server(debug = True)

