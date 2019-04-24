from Pathways.server import app, CONFIG
from Pathways.utils import Utils
import Pathways.callbacks
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

U = Utils()
countries = U.get_country_list(50)

app.layout =  html.Div([
    # Header
    html.Div(
        className='row',
        style={'margin-bottom': '30px'},
        children=[
            html.Div(
                className='one column', 
                style={'width': '100%', 'margin-bottom': '20px', 'padding': '0 50px 0 50px','background-color': 'black', 'color': 'white'}, 
                children=[html.H2('APHIS')])
        ]),

    # Container
    html.Div(
        className='container',
        style={'max-width': '100%', 'width': '90%'},
        children=[
            # ---------- Section: Group By ----------
            # Child 1
            html.H2('Group By'),
            # Child 2 - F280 DB columns dropdown
            html.Div(
                style={'width': '30%'},               
                children=[
                dcc.Dropdown(
                    id='db-column-dropdown',
                    options=[{'label': v['name'], 'value': k} for k, v in CONFIG['DB_COLUMNS'].items()],
                    value='DISP_CD',
                    clearable=False)
            ]),
            # Child 3 - Pie/Box/Table
            html.Div(id='group-by-outputs', className='row', style={'maxHeight': 700}),

            html.Br(), # Child 4
            html.Hr(), # Child 5
            
            # ---------- Section: Temporal ----------
            html.H2('Temporal'), # Child 1 - Title

            # Child 2 - Temporal line chart selections
            html.Div(
                className='row',
                children=[
                    # // Radio items //
                    # Child 2:1 - {DISP Code or Pest Found}
                    html.Div(
                        className='two columns',
                        style={'align': 'right'},
                        children=[
                            dcc.RadioItems(
                                id='disp-or-pest-found',
                                options=[
                                    {'label': 'DISP', 'value': False},
                                    {'label': 'Pest Found', 'value': True}
                                ],
                                value=False,
                                labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'})
                    ]),
                    # Child 2:2 - {By Year/Month or By Month}
                    html.Div(
                        className='two columns',
                        children=[
                            dcc.RadioItems(
                            id='yearmonth-or-month',
                            options=[
                                {'label': 'Year/Month', 'value': 'all'},
                                {'label': 'Month', 'value': 'month'}
                            ],
                            value='all',
                            labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}) 
                    ]),
                    # Child 2:3 - {Count or Quantity}
                    html.Div(
                        className='two columns', 
                        # style={'background-color': 'rgb(211,211,211)', 'border': '1px solid gray', 'padding': '5px 5px 5px 5px', 'border-radius': 3},
                        children=[
                            dcc.RadioItems(
                                id='count-or-quantity',
                                options=[
                                    {'label': 'Count', 'value': 'count'},
                                    {'label': 'Quantity', 'value': 'quantity'}
                                ],
                                value='count',
                                labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'})  
                    ]),
                    # // Dropdowns //
                    # Child 4 - Country name dropdown
                    html.Div(
                        id='country-dropdown-output',
                        className='three columns',
                        children=[
                            dcc.Dropdown(
                                id='country-dropdown',
                                options=[{'label': c['label'], 'value': c['value']} for c in countries],
                                value='All',
                                clearable=False)
                    ]),
                    # Child 5 - DISP code dropdown
                    html.Div(
                        id='disp-group-dropdown-output',
                        className='three columns', 
                        children=[
                            dcc.Dropdown(
                                id='disp-group-dropdown',
                                options=[{'label': val['name'], 'value': key} for key, val in CONFIG['DISP_GROUP_DESC'].items()],
                                value='All',
                                clearable=False)
                    ])
            ]), # END Child 2 - Temporal Line Chart Selections 

            # Child 3 - Temporal Line Chart 
            html.Div(id='temporal-outputs'),

            # ---------- Section 3: By Country ----------
            # Child 1 - Country name
            html.Div(
                id='section-title-country-output',
                style={'text-align': 'center'}),
            # Child 2 - Stacked bar charts (3)
            html.Div(
                id='by-country-outputs', 
                className='row'
            )


  ]) # END container
]) # END layout