import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go
import json


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

config_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), 'config.json'))
with open(config_path, 'r') as f:
    CONFIG = json.load(f)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.server.config['SQLALCHEMY_DATABASE_URI'] = CONFIG[0]['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.supress_callback_exceptions = True
app.title = 'Pathways'
db = SQLAlchemy(app.server)

class Aphis(db.Model):
    __tablename__ = 'F280'
    F280_ID = db.Column(db.Integer, primary_key=True)
    REPORT_DT = db.Column(db.DateTime)
    PATHWAY= db.Column(db.String(20))
    FY = db.Column(db.Integer)
    MON = db.Column(db.Integer)
    LOCATION = db.Column(db.String(126))
    COMMODITY = db.Column(db.String(150))
    CTYPE_CD = db.Column(db.String(2))
    CTYPE_NM = db.Column(db.String(25))
    CFORM_NM = db.Column(db.String(20))
    DISP_CD = db.Column(db.String(4))
    DISP_NM = db.Column(db.String(255))    
    ORIGIN_NM = db.Column(db.String(50))
    DEST_NM = db.Column(db.String(20))
    QUANTITY = db.Column(db.Integer)
    NUM_SHIP = db.Column(db.Integer)    
    ENTRY_NUM = db.Column(db.String(50))
    CONTAINER_NUM = db.Column(db.String(50))
    BILL_NUM = db.Column(db.String(50))
    HOUSE_BILL_NUM = db.Column(db.String(50))
    EAN_ID = db.Column(db.String(50))
    city_fid = db.Column(db.Integer, db.ForeignKey('city.city_fid'))
    country_fid = db.Column(db.Integer)
    disp_fid = db.Column(db.Integer, db.ForeignKey('disp_code.disp_fid'))

    

    def __init__(self, F280_ID, REPORT_DT, PATHWAY, FY, MON, LOCATION, COMMODITY, 
        CTYPE_CD, CTYPE_NM, CFORM_NM, DISP_CD, DISP_NM, ORIGIN_NM, DEST_NM, QUANTITY, NUM_SHIP,
        ENTRY_NUM, CONTAINER_NUM, BILL_NUM, HOUSE_BILL_NUM, EAN_ID, city_fid, country_fid, disp_fid):
        self.F280_ID = F280_ID
        self.REPORT_DT = REPORT_DT
        self.PATHWAY = PATHWAY
        self.FY = FY
        self.MON = MON
        self.LOCATION = LOCATION
        self.COMMODITY = COMMODITY
        self.CTYPE_CD = CTYPE_CD
        self.CTYPE_NM = CTYPE_NM
        self.CFORM_NM = CFORM_NM
        self.DISP_CD = DISP_CD
        self.DISP_NM = DISP_NM 
        self.ORIGIN_NM = ORIGIN_NM
        self.DEST_NM = DEST_NM  
        self.QUANTITY = QUANTITY
        self.NUM_SHIP = NUM_SHIP     
        self.ENTRY_NUM = ENTRY_NUM
        self.CONTAINER_NUM = CONTAINER_NUM
        self.BILL_NUM = BILL_NUM
        self.HOUSE_BILL_NUM = HOUSE_BILL_NUM
        self.EAN_ID = EAN_ID
        self.city_fid = city_fid
        self.country_fid = country_fid
        self.disp_fid = disp_fid



    # def __repr__(self):
    #     return 'Aphis<{0}, {1}, {2}, {3}, {4}, {5}>'.format(
    #         self.F280_ID, self.REPORT_DT, self.FY, self.MON, self.PATHWAY, 
    #         self.ORIGIN_NM, self.LOCATION, self.COMMODITY, self.CFORM_NM, self.DISP_CD, 
    #         self.DISP_NM, self.QUANTITY, self.NUM_SHIP)


class Disp(db.Model):
    __tablename__ = 'disp_code'
    disp_code = db.Column(db.String(4))   
    disp_desc = db.Column(db.String(255))
    disp_group = db.Column(db.String(5))    
    disp_fid = db.Column(db.Integer, primary_key=True) 

    disprel = db.relationship('Aphis')

    def init(self, disp_code, disp_desc, disp_group, disp_fid):
        self.disp_code = disp_code
        self.disp_desc = disp_desc
        self.disp_group = disp_group
        self.disp_fid = disp_fid


class City(db.Model):
    __tablename__ = 'city'
    city_fid = db.Column(db.Integer, primary_key=True)
    state_abbrv = db.Column(db.String(2))
    city = db.Column(db.String(180))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def init(self, city_fid, state_abbrv, city, latitude, longitude):
        self.city_fid = city_fid
        self.state_abbrv = state_abbrv
        self.city = city
        self.latitude = latitude
        self.longitude = longitude



def initDB():
    db.create_all()
    db.session.commit()

def getColumnsF280():
    columns = Aphis.__table__.columns.keys()
    return columns


def getCountryList(number):
    cl = []
    query = db.session.query(Aphis.ORIGIN_NM, db.func.count(Aphis.F280_ID))\
        .group_by(Aphis.ORIGIN_NM)\
        .having(db.func.count(Aphis.F280_ID) >= number)\
        .order_by(db.func.count(Aphis.F280_ID).desc()).all()
    df = pd.DataFrame(query, columns=['Country', 'COUNT'])

    for c in df.to_dict('rows'):
        strnum = '{:,}'.format(c['COUNT'])
        ops = {'label': f'{c["Country"]} ({strnum})', 'value': c["Country"]}
        cl.append(ops)
    
    cl.insert(0, {'label': 'All', 'value': 'All'})

    return cl


# MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
risklevel_json = os.path.abspath(os.path.join(os.path.dirname('__file__'), 'RiskLevel.json'))
PEST_RISK_LEVEL = None
with open(risklevel_json, 'r') as f:
    PEST_RISK_LEVEL = json.load(f)

dispgroup = ['AP', 'IR', 'NR', 'PA', 'PD', 'PP', 'R']
dispgroupdesc = {
    'AP': 'Actionable pest',
    'IR': 'Inspected and released',
    'NR': 'Not released',
    'PA': 'Precautionary action',
    'PD': 'Phyto discrepancy',
    'PP': 'Pest permit',
    'R': 'Released without inspection'
}
dbcolumns = getColumnsF280()
countries = getCountryList(50)


app.layout =  html.Div([
    # Header
    html.Div([
            html.Div([
                html.H2('APHIS')
            ], 
            className='one column', 
            style={'width': '100%', 'margin-bottom': '20px', 'padding': '0 50px 0 50px','background-color': 'black', 'color': 'white'})
        ], className='row', style={'margin-bottom': '30px'}),

    # Container
    html.Div(
        className='container',
        style={'max-width': '100%', 'width': '90%'},
        children=[
            html.H2('Group By'),
            # Dropdown
            html.Div([
                dcc.Dropdown(
                    id='db-column-dropdown',
                    options=[{'label': c, 'value': c} for c in dbcolumns],
                    value='LOCATION'
                )
            ], style={'width': '30%'}),

            # Pie/Box/Table
            html.Div(id='group-by-outputs', className='row'),

            html.Hr(),

            html.H2('Temporal'),

            # Radio buttons
            html.Div(
                className='row',
                children=[
                    html.Div([
                        dcc.RadioItems(
                            id='temporal-radio',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': 'By Month', 'value': 'month'}
                            ],
                            value='all',
                            labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}                
                        ),  
                    ], className='four columns', style={'text-align': 'right'}),

                    html.Div([
                        dcc.Dropdown(
                            id='country-dropdown',
                            options=[c for c in countries],
                            value='All'
                        )
                    ], className='three columns')
            ]),

            html.Div(id='temporal-outputs-all'),

            html.Div(id='section-title-country-output'),

            html.Div(id='temporal-outputs-two', className='row'),

        ] #.container.children
    )
]) # layout END


@app.callback(Output('group-by-outputs', 'children'),
                [Input('db-column-dropdown', 'value')])
def groupBy(column):
    # Get data by query
    col = getattr(Aphis, column)
    # print(col)
    query = db.session.query(col, db.func.count(col))\
        .group_by(col).order_by(db.func.count(col).desc()).all()
    df = pd.DataFrame(query, columns=[column, 'COUNT'])

    boxplot = go.Box(
        y=[c for c in df['COUNT']],
        name = 'COUNT'
    )

    return html.Div([
        # Pie chart
        html.Div([
            dcc.Graph(
                id='group-by-donut',
                figure={
                    'data': [
                        {
                            'values': [row for row in df['COUNT'][:10]],
                            'labels': [row for row in df[column][:10]],
                            'hole': .4,
                            'type': 'pie'
                        }
                    ],
                    'layout': {
                        'title': f'Group by {column}'
                    }
                }
            )
        ], className='four columns'),

        # Box chart
        html.Div([
            dcc.Graph(
                id='group-by-box',
                figure={
                    'data': [boxplot],
                    'layout': {
                        'title': f'Group by {column}'
                    }
                }

            )
        ], className='four columns'),

        # Table
        html.Div([
            dt.DataTable(
                id='datatable',
                data=[{column: row[column], 'COUNT': '{:,}'.format(row['COUNT'])} for row in df.to_dict('rows')],
                columns=[{'id': c, 'name': c} for c in df.columns],
                style_table={'maxHeight': '500px', 'overflowY': 'scroll'},
                style_cell={'textAlign': 'left'}
            )
        ], className='four columns')
    ])


@app.callback(Output('country-dropdown-output', 'children'),
                    [Input('country-record-count', 'value')])
def countryList(number):
    # print('Number', number)
    query = db.session.query(Aphis.ORIGIN_NM, db.func.count(Aphis.F280_ID))\
        .group_by(Aphis.ORIGIN_NM)\
        .having(db.func.count(Aphis.F280_ID) >= number)\
        .order_by(db.func.count(Aphis.F280_ID).desc()).all()
    df = pd.DataFrame(query, columns=['Country', 'COUNT'])
    # countries = [c for c in df['Country']]
    # countries.insert(0, 'All')
    cl = [{'label': f'{c["Country"]} ({c["COUNT"]})', 'value': c["Country"]} for c in df.to_dict('rows')]
    cl.insert(0, {'label': 'All', 'value': 'All'})

    return dcc.Dropdown(
            id='country-dropdown',
            options=cl,
            value='All'
        )


@app.callback(Output('temporal-outputs-all', 'children'),
                [Input('temporal-radio', 'value'), 
                Input('country-dropdown', 'value')])
def temporalAll(check, country):
    # print('check', check, 'country', country)
    trace = []
    layout = {
        'title': 'Grouped DISP',
        'xaxis': dict(
            showgrid=True,
            zeroline=False
        ),
        'yaxis': dict(showgrid=True)
        }
    funcdateym = db.func.to_char(Aphis.REPORT_DT, 'YYYY-MM')
    funcdatem = db.func.to_char(Aphis.REPORT_DT, 'MM')
       

    if country == 'All':
        if check == 'all':
            query = db.session.query(funcdateym, Disp.disp_group, db.func.count(Aphis.F280_ID))\
            .join(Disp)\
            .filter(Aphis.disp_fid == Disp.disp_fid)\
            .group_by(funcdateym, Disp.disp_group).all()

        elif check == 'month':
            query = db.session.query(funcdatem, Disp.disp_group, db.func.count(Aphis.F280_ID))\
            .join(Disp)\
            .filter(Aphis.disp_fid == Disp.disp_fid)\
            .group_by(funcdatem, Disp.disp_group).all()

    else:
        if check == 'all':
            query = db.session.query(funcdateym, Disp.disp_group, db.func.count(Aphis.F280_ID))\
                .join(Disp)\
                .filter(Aphis.disp_fid == Disp.disp_fid, Aphis.ORIGIN_NM == country)\
                .group_by(funcdateym, Disp.disp_group).all()

        elif check == 'month':
            query = db.session.query(funcdatem, Disp.disp_group, db.func.count(Aphis.F280_ID))\
                .join(Disp)\
                .filter(Aphis.disp_fid == Disp.disp_fid, Aphis.ORIGIN_NM == country)\
                .group_by(funcdatem, Disp.disp_group).all()

    df = pd.DataFrame(query, columns=['Date', 'DISPGroup', 'COUNT'])

    # Layout for line chart
    if check == 'month':
        layout['xaxis']['tickmode'] = 'linear'
    else:
        layout['xaxis']['rangeslider']=dict(visible=True)
        layout['xaxis']['type']='date'

    for g in dispgroup:
        subset = df[df.DISPGroup == g]
        
        plot = go.Scatter(
            x=[d for d in subset['Date']],
            y=[c for c in subset['COUNT']],
            name = g,
            mode='lines'
        )
        trace.append(plot)
    
    return html.Div([
        dcc.Graph(
            id='temporal-line',
            figure={
                'data': trace,
                'layout': layout
            }
        )   
    ])

@app.callback(Output('section-title-country-output', 'children'),
                [Input('country-dropdown', 'value')])
def sectionCountryTitle(country):
    return html.H2(country)


@app.callback(Output('temporal-outputs-two', 'children'), 
                    [Input('country-dropdown', 'value')])
def temporalCountryPortDisp(country):
    trace = []
    # print(country)
    if country != 'All':
        query = db.session.query(Aphis.ORIGIN_NM, City.city, Disp.disp_group, db.func.count(Aphis.F280_ID))\
            .join(City, Disp).filter(Aphis.city_fid == City.city_fid, Aphis.disp_fid == Disp.disp_fid, Aphis.ORIGIN_NM == country)\
            .group_by(Aphis.ORIGIN_NM, City.city, Disp.disp_group)\
            .order_by(City.city, Disp.disp_group).all()
        query2 = db.session.query(Aphis.ORIGIN_NM, City.city, db.func.count(Aphis.F280_ID))\
            .join(City).filter(Aphis.city_fid == City.city_fid, Aphis.ORIGIN_NM == country)\
            .group_by(Aphis.ORIGIN_NM, City.city)\
            .order_by(db.func.count(Aphis.F280_ID).desc()).all()
        
        df = pd.DataFrame(query, columns=['Country', 'PortCity', 'DISPGroup', 'COUNT'])
        ports = df['PortCity'].unique()
        dispg = df['DISPGroup'].unique()
        busyp = query2[0][1]
        # print(f'Busy port is: {busyp}')

        for dg in dispg:
            subset = df[df['DISPGroup'] == dg]
            pval = dict.fromkeys(ports, 0)
          
            for s in subset.to_dict('rows'):
                pval[s['PortCity']] = s['COUNT']

            plot = go.Bar(
                y=[key for key, val in pval.items()],
                x=[val for key, val in pval.items()], 
                name=dg,
                orientation='h'
            )
            trace.append(plot)
        layout = {
            'barmode': 'stack',
            'height': 700,
            'margin': go.layout.Margin(t=20)
            }

        return [
            html.Div([
                dcc.Graph(
                    id='temporal-stack-bar',
                    figure={
                        'data': trace,
                        'layout': layout
                    }
                )                
            ], className='six columns'),

            html.Div([
                dcc.Dropdown(
                    id='ports-dropdown',
                    options=[{'label': p, 'value': p} for p in ports],
                    value=busyp
                ),
                html.Div(id='temporal-output-three')
            ], className='six columns')
        ]
    

@app.callback(Output('temporal-output-three', 'children'),
                [Input('country-dropdown', 'value'), Input('ports-dropdown', 'value')])
def temporalCountryFlower(country, port):
    # print(port)
    high = None
    low = None
    trace_high = []
    trace_low = []
    # funcdateym = db.func.to_char(Aphis.REPORT_DT, 'YYYY-MM')
    if country != 'All':
        # print(country)
        for prl in PEST_RISK_LEVEL:
            if prl['CountryName'] == country:
                # print(prl['PestRiskLevel'])
                high = prl['PestRiskLevel']['High']
                # print('High', high)
                low = prl['PestRiskLevel']['Low']
                # print('Low', low)

        query_high = db.session.query(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY,
                    Disp.disp_group, db.func.count(Aphis.F280_ID))\
                .join(City, Disp).filter(Aphis.city_fid == City.city_fid, 
                    Aphis.disp_fid == Disp.disp_fid, Aphis.ORIGIN_NM == country, 
                    City.city == port, Aphis.COMMODITY.in_(high))\
                .group_by(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY, Disp.disp_group)\
                .order_by(City.city, Aphis.COMMODITY, Disp.disp_group).all()
        df_high = pd.DataFrame(query_high, columns=['Country', 'City', 'Flower', 'DISPGroup', 'COUNT'])
        # print(df_high)
        dispg_high = df_high['DISPGroup'].unique()
        for dg in dispg_high:
            subset = df_high[df_high['DISPGroup']==dg]
            fval = dict.fromkeys(high, 0)
            
            for s in subset.to_dict('rows'):
                fval[s['Flower']] = s['COUNT']
            
            plot = go.Bar(
                y=[key for key, val in fval.items()],
                x=[val for key, val in fval.items()],
                name=dg,
                orientation='h'
            )
            trace_high.append(plot)
        
        layout = {
            'barmode': 'stack'
            }

        query_low = db.session.query(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY,
            Disp.disp_group, db.func.count(Aphis.F280_ID))\
        .join(City, Disp).filter(Aphis.city_fid == City.city_fid, 
            Aphis.disp_fid == Disp.disp_fid, Aphis.ORIGIN_NM == country, 
            City.city == port, Aphis.COMMODITY.in_(low))\
        .group_by(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY, Disp.disp_group)\
        .order_by(City.city, Aphis.COMMODITY, Disp.disp_group).all()

        df_low = pd.DataFrame(query_low, columns=['Country', 'City', 'Flower', 'DISPGroup', 'COUNT'])
        # print(df_low)
        dispg_low = df_low['DISPGroup'].unique()
        for dg2 in dispg_low:
            subset2 = df_low[df_low['DISPGroup']==dg2]
            fval2 = dict.fromkeys(low, 0)
            
            for s in subset2.to_dict('rows'):
                fval2[s['Flower']] = s['COUNT']
            
            plot = go.Bar(
                y=[key for key, val in fval2.items()],
                x=[val for key, val in fval2.items()],
                name=dg2,
                orientation='h'
            )
            trace_low.append(plot)

        # flowers = df['Flower'].unique()
        # print(f'Number of flowers: {len(flowers)}')

        return html.Div([
            # html.P(f'Number of Cut Flowers: {len(flowers)}'),

            dcc.Graph(
                id='risk-high-flowers',
                figure={
                    'data': trace_high,
                    'layout': layout
                }
            ),

            dcc.Graph(
                id='risk-low-flowers',
                figure={
                    'data': trace_low,
                    'layout': layout
                }
            )
        ])
        
        





if __name__ == '__main__':
    INITIATE = True
    app.run_server(debug=True)

    if INITIATE:
        initDB()
