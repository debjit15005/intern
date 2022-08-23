from asyncio.constants import SSL_HANDSHAKE_TIMEOUT
from cgi import test
#import os
#from socket import AddressFamily
#from flask import Flask,jsonify,request,abort,render_template,session,redirect


import gspread
from oauth2client.service_account import ServiceAccountCredentials


import pandas as pd
import numpy as np

import dash
import dash_auth
from dash import Dash, dash_table,dcc,html,ctx
#from dash.dependencies import State
#import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import MultiplexerTransform, Output, Input, State, DashProxy

credential = ServiceAccountCredentials.from_json_keyfile_name("credentials.json",
                                                              ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credential)
#gsheet = client.open("sample market").get_worksheet(0)




app = DashProxy(prevent_initial_callbacks=True,transforms=[MultiplexerTransform()])
server = app.server
auth = dash_auth.BasicAuth(app,{'test':'test'})



columns = ['Industry','Company','Name','Position','PhoneNo','Email']

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)



#print(df.head(5))
#df['Phone No.'].astype(int)
#df1=df.set_index(['Industry','Company'])
#print(df1.head(10))

#server = Flask(__name__)

#@server.route('/')
#def hello_world():
#    return 'Hello World!'



gsheet = client.open("sample market").get_worksheet(1)
df=pd.DataFrame(gsheet.get_all_records())

app.layout = html.Div([
    html.Div([
        html.H1("Client DB", style={'text-align':'center','font-family':'Roboto'}),
        dash_table.DataTable(
            id='dtb',
            columns=[
                {'name':i,'id':i} for i in df.columns
            ],
            data=df.to_dict('records'),
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            row_selectable='single',
            selected_rows=[],
            page_action='native',
            page_current=0,
            page_size=10,
            style_cell={'minWidth':95,'maxWidth':95, 'width':95},
            style_cell_conditional=[{'textAlign':'center'}],
            style_data={'whiteSpace':'normal','height':'auto'},
            editable=True                          
        ),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
    ]
    + [
        html.H3("Add Client",style={'font-family':'Roboto'}),
        html.H4("Industry",style={'font-family':'Roboto','display':'inline-block','width': '16.6%'}),
        html.H4("Company",style={'font-family':'Roboto','display':'inline-block','width': '16.6%'}),
        html.H4("Name",style={'font-family':'Roboto','display':'inline-block','width': '16.6%'}),
        html.H4("Position",style={'font-family':'Roboto','display':'inline-block','width': '16.6%'}),
        html.H4("Phone No.",style={'font-family':'Roboto','display':'inline-block','width': '16.6%'}),
        html.H4("Email",style={'font-family':'Roboto','display':'inline-block','width':'16.6%'}),
        dcc.Input(id="Industry", placeholder="enter industry", type="text", style={'font-family':'Roboto','display':'inline-block','width':'16.1%'}, debounce=True),
        dcc.Input(id="Company", placeholder="enter company", type="text", style={'font-family':'Roboto','display':'inline-block','width':'16.1%'}, debounce=True),
        dcc.Input(id="Name", placeholder="enter name", type="text", style={'font-family':'Roboto','display':'inline-block','width':'16.1%'}, debounce=True),
        dcc.Input(id="Position", placeholder="enter position", type="text", style={'font-family':'Roboto','display':'inline-block','width':'16.1%'}, debounce=True),
        dcc.Input(id="PhoneNo", placeholder="enter phone number", type="number", style={'font-family':'Roboto','display':'inline-block','width':'16.1%'}, debounce=True),
        dcc.Input(id="Email", placeholder="enter email", type="email", style={'font-family':'Roboto','display':'inline-block','width':'16.1%'}, debounce=True)
    ]
    + [html.Button("Add", id='add-button', n_clicks=0),html.Div(id="output1")]
    + [html.Br()]
    + [html.Div(id="output2"), html.Button("Delete Client", id='del-button', n_clicks=0),html.Div(id="output3")]
    + [html.Br()]
)
    


@app.callback(
    Output('output1', "children"),

    Output('dtb','data'),
    [Output("{}".format(_),"value") for _ in columns],
    Input('add-button', 'n_clicks'),
    [State("{}".format(_), "value") for _ in columns]
)
def add(*vals):
    
    if "add-button"== ctx.triggered_id:
        gsheet = client.open("sample market").get_worksheet(1)
        row = next_available_row(gsheet)
        cells = gsheet.range(row,1,row,6)
        for n, cell in enumerate(cells):
            cell.value = vals[n+1]
        gsheet.update_cells(cells)
        return "Added "+ vals[3], pd.DataFrame(gsheet.get_all_records()).to_dict('records'), "","","","",None,""
    else:
        raise PreventUpdate

@app.callback(
    Output('output2', "children"),
    Output('output3', "children"),
    Output('dtb','data'),
    Input('del-button', 'n_clicks'),
    Input('dtb','selected_rows')
)
def delete(n,row):
    if not row:
       raise PreventUpdate
    else:
        #newrow = next_available_row(gsheet)
        if "del-button"==ctx.triggered_id:
            gsheet = client.open("sample market").get_worksheet(1)
            name = gsheet.cell(row[-1]+2,3).value
            gsheet.delete_rows(row[-1]+2)
            #gsheet.update_cells(cells)
            return "", "Deleted "+name+" ", pd.DataFrame(gsheet.get_all_records()).to_dict('records')
        else:
            gsheet = client.open("sample market").get_worksheet(1)
            return "Delete Client?", "", pd.DataFrame(gsheet.get_all_records()).to_dict('records')

 
 

        



    





if __name__ == '__main__':
    app.run_server(debug=True)