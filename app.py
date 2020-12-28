# Import all the necessary libraries

# All plots are done using plotly here instead of matplotlib

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from plotly import graph_objs as go
from wordcloud import WordCloud, STOPWORDS
import csv
import calendar
import dash_bootstrap_components as dbc
import plotly.io as plt_io

#Creating template for Dark Theme
plt_io.templates["custom_dark"] = plt_io.templates["plotly_dark"]
plt_io.templates["custom_dark"]['layout']['paper_bgcolor'] = '#30404D'
plt_io.templates["custom_dark"]['layout']['plot_bgcolor'] = '#30404D'
plt_io.templates['custom_dark']['layout']['yaxis']['gridcolor'] = '#4f687d'
plt_io.templates['custom_dark']['layout']['xaxis']['gridcolor'] = '#4f687d'

# Read data 
dfMessages = pd.read_csv("./data/messages_modified.csv")
dfInvitations = pd.read_csv("./data/Invitations.csv")
dfConnections = pd.read_csv("./data/Connections.csv")
dfReactions = pd.read_csv("./data/Reactions.csv")
dfLocations = pd.read_csv("./data/Locations.csv")
dfAdsClicked = pd.read_csv("./data/AdsClicked.csv")

# Plot Sent/Recieved Messages as Stacked Bar Plot
dfMessages['DATE'] = pd.DatetimeIndex(dfMessages['DATE']).year
dfMessagesSent = dfMessages[dfMessages['FROM']=='Anish Mukherjee']
dfMessagesReceived= dfMessages[dfMessages['TO']=='Anish Mukherjee']
dfMessagesSentCount= dfMessagesSent.groupby(['DATE']).size().reset_index(name="Count")
dfMessagesReceivedCount= dfMessagesReceived.groupby(['DATE']).size().reset_index(name="Count")

# Plot Invitations Pie Chart
dfInviteCount = dfInvitations.groupby(['Direction']).size().reset_index(name="Count")

# Word Cloud of Company
dfConnections = dfConnections.dropna()

positionString=''
for index,row in dfConnections.iterrows():
    z=row['Position']
    z1=str(z)
    positionString=positionString+z1+' ,'

wordcloud1 = WordCloud(width = 300, height = 200, random_state=1, background_color='salmon', colormap='Pastel1', collocations=False, stopwords = STOPWORDS).generate(positionString)
wordcloud1.to_file('./assets/wordcloud1.png')

# Table to show reactions
dfReactions['Date'] = pd.DatetimeIndex(dfReactions['Date']).year
dfReactionsCount= dfReactions.groupby(['Date','Type']).size().reset_index(name="Count")
dfReactionsUniqueYear = dfReactionsCount['Date'].unique()

# Connections by location

fig3 = px.scatter_geo(dfLocations, locations="iso_alpha", color = "Continent",hover_name="Country", size="Count",
                     projection="natural earth")
                 

# Line Plot to show Ads Clicked
dfAdsClicked['Year']= pd.DatetimeIndex(dfAdsClicked['Date']).year
dfAdsClicked['Month']= pd.DatetimeIndex(dfAdsClicked['Date']).month
dfAdsClicked['Month Name']= pd.DatetimeIndex(dfAdsClicked['Date']).month_name
dfAd2020 = dfAdsClicked[dfAdsClicked['Year']==2020]
dfAd2020Count = dfAd2020.groupby('Month').size().reset_index(name="Count")
dfAd2020Count['Month'] = dfAd2020Count['Month'].apply(lambda x: calendar.month_abbr[x])
dfAd2020Count['Month'] = dfAd2020Count['Month'].apply(lambda x: x+" 2020")
dfAd2019 = dfAdsClicked[dfAdsClicked['Year']==2019]
dfAd2019Count = dfAd2019.groupby('Month').size().reset_index(name="Count")
dfAd2019Count['Month'] = dfAd2019Count['Month'].apply(lambda x: calendar.month_abbr[x])
dfAd2019Count['Month'] = dfAd2019Count['Month'].apply(lambda x: x+" 2019")
dfAdsFinal = dfAd2019Count.append(dfAd2020Count)

fig4 = px.line(dfAdsFinal, x="Month", y="Count", title='Ads Clicked Over Time')
fig4.layout.template = "custom_dark"

fig1 = go.Figure(data=[
    go.Bar(name='Sent', x=dfMessagesSentCount['DATE'], y=dfMessagesSentCount['Count']),
    go.Bar(name='Received', x=dfMessagesReceivedCount['DATE'], y=dfMessagesReceivedCount['Count'])
])

# Change the bar mode
fig1.update_layout(barmode='stack')
fig1.layout.template = "custom_dark"

# Pie Chart Object Created
fig2 = px.pie(dfInviteCount, values=dfInviteCount['Count'], names=dfInviteCount['Direction'])
fig2.layout.template = "custom_dark"

# Creating an instance of the dash object
app = dash.Dash(__name__,title="LinkedInVisualization",external_stylesheets=[dbc.themes.GRID])

# This is the top level Div which covers the entire screen
app.layout = html.Div(children=[

    html.Div([
        # Top Level Div
        dbc.Row([
            # First Row
            dbc.Col(
               # Firsr Column
               html.Div([

               ],id = "Div1"),width = 2 
            ),

            dbc.Col(
                # Second Column
                html.Div([
                    # First Graph Row
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                html.H1("My LinkedIn Data Visualization",id="H1")
                            ]),id ="Div10"
                        )
                    ]),
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                dcc.Graph(id="MessagesGraph",figure=fig1)
                            ]),id="Div2",width = 6
                        ),
                        dbc.Col(
                            html.Div([
                                dcc.Graph(id="InvitationGraph",figure=fig2)
                            ]),id="Div3",width = 6
                        )
                    ]),
                    # New Row
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                dcc.Graph(id="LocationPlot",figure=fig3)
                            ]),id="Div4",width = 6
                        ),
                        dbc.Col(
                            html.Div([
                                #html.Img(id='wordCloudImage',src='./assets/wordcloud1.png')
                            ]),id="Div5",width = 6 
                        )
                    ]),
                    # New Row
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                dcc.Graph(id="AdsGraph",figure=fig4)
                            ]),id="Div6",width = 6
                        ),
                        dbc.Col(
                            html.Div([
                                    dcc.Dropdown(
                                        id='yearDropDown',
                                        options=[{'label':x, 'value':x} for x in dfReactionsUniqueYear],
                                        value=2020),
                                    html.Br(),

                                    html.Table([
                                        html.Tr([
                                            html.Th("Like"), 
                                            html.Th("Empathy"),
                                            html.Th("Interest"),
                                            html.Th("Maybe"),
                                            html.Th("Praise")
                                        ]),
                                        html.Tr([
                                            html.Td([
                                                html.Div(id='likeval')
                                            ]),
                                            html.Td([
                                                html.Div(id='empathyval')
                                            ]),
                                            html.Td([
                                                html.Div(id='interestval')
                                            ]),
                                            html.Td([
                                                html.Div(id='maybeval')
                                            ]),
                                            html.Td([
                                                html.Div(id='praiseval')
                                            ])
                                        ])
                                    ]),
                                    
                            ]),id="Div7",width = 6
                        )
                    ])
                ])
            )
        ])
    ]),
   
    
])

@app.callback(
    [Output('likeval','children'), 
    Output('empathyval','children'),
    Output('interestval','children'),
    Output('maybeval','children'),
    Output('praiseval','children')],
    Input('yearDropDown','value')
    )

def updateTable(yearDropDown):
    year = yearDropDown
    x = dfReactionsCount[dfReactionsCount['Date']==year]

    z1 = x.loc[x['Type']=='LIKE','Count'].reset_index()

    if (z1.empty == True):
        like = 0
    else:
        like = z1['Count'][0]

    z2 = x.loc[x['Type']=='EMPATHY','Count'].reset_index()
    
    if (z2.empty == True):
        empathy = 0
    else:
        empathy = z2['Count'][0]

    z3 = x.loc[x['Type']=='INTEREST','Count'].reset_index()
    
    if (z3.empty == True):
        interest = 0
    else:
        interest = z3['Count'][0]

    z4 = x.loc[x['Type']=='MAYBE','Count'].reset_index()
    
    if (z4.empty == True):
        maybe = 0
    else:
        maybe = z4['Count'][0]

    z5 = x.loc[x['Type']=='PRAISE','Count'].reset_index()
    
    if (z5.empty == True):
        praise = 0
    else:
        praise = z5['Count'][0]

    return like,empathy,interest,maybe,praise

if __name__ == '__main__':
    app.run_server(debug=False)