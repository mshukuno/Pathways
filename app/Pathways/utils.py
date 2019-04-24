from Pathways.server import db, CONFIG
from Pathways.models import Aphis, Disp, City, Country
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
import plotly.graph_objs as go
from sqlalchemy import or_


class Utils:

    def __init__(self):
        self.funcdateym = db.func.to_char(Aphis.REPORT_DT, 'YYYY-MM')
        self.funcdatem = db.func.to_char(Aphis.REPORT_DT, 'MM')

    def get_country_list(self, number=None):
        cl = []
        if number:
            query = db.session.query(Aphis.ORIGIN_NM, db.func.count(Aphis.F280_ID))\
                .group_by(Aphis.ORIGIN_NM)\
                .having(db.func.count(Aphis.F280_ID) >= number)\
                .order_by(db.func.count(Aphis.F280_ID).desc()).all()
        else:
            query = db.session.query(Aphis.ORIGIN_NM, db.func.count(Aphis.F280_ID))\
                .group_by(Aphis.ORIGIN_NM)\
                .order_by(db.func.count(Aphis.F280_ID).desc()).all()

        df = pd.DataFrame(query, columns=['Country', 'Count'])

        for c in df.to_dict('rows'):
            strnum = '{:,}'.format(c['Count'])
            ops = {'label': f'{c["Country"]} ({strnum})', 'value': c["Country"]}
            cl.append(ops)
        
        cl.insert(0, {'label': 'All', 'value': 'All'})

        return cl


    def consolidate_values(self, df, group_by_col, column, grater_than=None):
        if grater_than is None:
            vals = [{group_by_col: row[group_by_col], column: row[column]} for row in df.to_dict('rows')]

        else:
            vals = [{group_by_col: row[group_by_col], column: row[column]} 
                        for idx, row in df.loc[df[column] >= grater_than].iterrows()]
            vals.append({group_by_col: f'Less than ({grater_than}%)', 
                column: 100 - df.loc[df[column] >= 1][column].sum()})
        return vals


    def list_generator(self, key, dict_list):
        result = [row[key] for row in dict_list]
        return result


    def convert_month_label(self, label_key, value_key, dict_list, name):
        ld_vals = []
        for row in dict_list:
            new_vals = {label_key: '', value_key: ''}
            month = CONFIG['MONTH'][str(row[label_key])[:-2]]
            new_vals[label_key] = month
            new_vals[value_key] = row[value_key]
            ld_vals.append(new_vals)
        result = {
            'values': self.list_generator(value_key, ld_vals),
            'labels': self.list_generator(label_key, ld_vals),
            'name': name
        }
        
        return result


    def pie_value_generator(self, label_key, value_key, dict_list, name):

        if label_key == 'MON':
            result = self.convert_month_label(label_key, value_key, dict_list, name)
        else:
            result = {
                'values': self.list_generator(value_key, dict_list),
                'labels': self.list_generator(label_key, dict_list),
                'name': name
            }
        return result


    # Layout - returns html.Div
    def chart_count_quantity_subplots(self, count_pie_vals, quantity_pie_vals, df, title):
        l_pie = []
        l_box = []
        l_domain = [{'x': [0, .5], 'y': [0, 1]}, {'x': [.5, 1], 'y': [0, 1]}]
        l_vals = [count_pie_vals, quantity_pie_vals]
        l_anno_x = [.2, .82]
        l_anno = []
        layout_box = dict(
            # title='',
            # margin=dict(),
            height=300
        )

        for i, v in enumerate(l_vals):
            l_pie.append(
                go.Pie(
                    values=v['values'],
                    labels=v['labels'],
                    domain=l_domain[i],
                    name=v['name'],
                    hoverinfo='label+percent+name',
                    hole=.4
                )
            )

            l_anno.append({
                'font': {'size': 20},
                'showarrow': False,
                'text': v['name'],
                'x': l_anno_x[i],
                'y': .5
            })

            l_box.append(
                go.Box(
                    y=df[v['name']],
                    name=v['name']
                )
            )

        layout_pie = dict(
            title=title,
            margin=dict(l=0, r=0),
            annotations=l_anno
        )

        # Data Table
        dt_htmldiv = self.table_count_quantity(df)
        
        htmldiv = [
            # Left
            html.Div([
                # Pie subplots
                html.Div([
                    dcc.Graph(
                        id='count-quantity-pie',
                        figure=dict(
                        data=l_pie,
                        layout=layout_pie)
                    )
                ], className='row'),
                # Boxplot subplots
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='count-quantity-box-one',
                            figure=dict(
                                data=[l_box[0]],
                                layout=layout_box)
                        )   
                    ], className='six columns'), 
                            
                    html.Div([
                        dcc.Graph(
                            id='count-quantity-box-two',
                            figure=dict(
                                data=[l_box[1]],
                                layout=layout_box)
                        )   
                    ], className='six columns')
                ], className='row')
            ], className='six columns'),

            # Right
            dt_htmldiv
        ]

        return htmldiv


    def table_count_quantity(self, df):
        # 'COUNT': '{:,}'.format(row['COUNT'])
        dl_data = []
        dl_cols = []
        columns = df.columns.values
       
        for row in df.to_dict('rows'):
            d_row = {}
            for col in columns:
                if col == 'Count':
                    d_row[col] = '{:,}'.format(row[col])
                elif col == 'Quantity':
                    d_row[col] = '{:,}'.format(row[col])[:-2]
                else:
                    d_row[col] = row[col]
            dl_data.append(d_row)

        for c in df.columns.values:
            d_col = {}
            d_col['id'] = c
            if c == 'CountPer':
                d_col['name'] = 'Count (%)'
            elif c == 'QuantityPer':
                d_col['name'] = 'Quantity (%)'
            else:
                d_col['name'] = c
            dl_cols.append(d_col)

        htmldiv = html.Div([
            dt.DataTable(
                id='datatable',
                data=dl_data,
                columns=[{'id': c['id'], 'name': c['name']} for c in dl_cols],
                filtering=True,
                sorting=True,
                sorting_type='multi',
                style_table={'maxHeight': 700, 'overflowY': 'scroll'},
                style_cell={'textAlign': 'left'}
            )
        ], className='six columns')

        return htmldiv

    def query_group_by_one(self, group_col, count_quantity, percentage='no'):
        # count_quantity: 'count' or 'quantity' or 'both'
        # percentage: 'yes' or 'no'
        col = getattr(Aphis, group_col)
        
        if count_quantity == 'count':
            query = db.session.query(col, db.func.count(Aphis.F280_ID))\
                .group_by(col)\
                .order_by(db.func.count(Aphis.F280_ID).desc()).all()
            columns = [group_col, 'Count']

        elif count_quantity == 'quantity':
            query = db.session.query(col, db.func.sum(Aphis.QUANTITY))\
                .group_by(col)\
                .order_by(db.func.sum(Aphis.QUANTITY).desc()).all()
            columns = [group_col, 'Quantity']

        elif count_quantity == 'both':
            query = db.session.query(col, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .group_by(col)\
                .order_by(db.func.count(Aphis.F280_ID).desc()).all()
            columns = [group_col, 'Count', 'Quantity']

        df = pd.DataFrame(query, columns=columns)

        if percentage == 'yes': 
            df['CountPer'] = df['Count']/df['Count'].sum() * 100
            df['QuantityPer'] = df['Quantity']/df['Quantity'].sum() * 100
            df['CountPer'] = df['CountPer'].round(1)
            df['QuantityPer'] = df['QuantityPer'].round(1)
    
        return df

    def data_pest_found_temporal(self, date_group, country):
        
        if country == 'All':
            if date_group == 'all':
                query = db.session.query(self.funcdateym, Disp.pest_found, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .join(Disp)\
                .filter(or_(Disp.pest_found == 'Yes', Disp.pest_found == 'No'))\
                .group_by(self.funcdateym, Disp.pest_found).all()
                

            elif date_group == 'month':
                query = db.session.query(self.funcdatem, Disp.pest_found, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .join(Disp)\
                .filter(or_(Disp.pest_found == 'Yes', Disp.pest_found == 'No'))\
                .group_by(self.funcdatem, Disp.pest_found).all()
        else:
            if date_group == 'all':
                query = db.session.query(self.funcdateym, Disp.pest_found, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .join(Disp)\
                .filter(Aphis.ORIGIN_NM == country, or_(Disp.pest_found == 'Yes', Disp.pest_found == 'No'))\
                .group_by(self.funcdateym, Disp.pest_found).all()

            elif date_group == 'month':
                query = db.session.query(self.funcdatem, Disp.pest_found, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .join(Disp)\
                .filter(Aphis.ORIGIN_NM == country, or_(Disp.pest_found == 'Yes', Disp.pest_found == 'No'))\
                .group_by(self.funcdatem, Disp.pest_found).all()

        df = pd.DataFrame(query, columns=['Date', 'PestFound', 'Count', 'Quantity'])

        return df


    def data_pest_found_by_country(self, country):
        query = db.session.query(Aphis.ORIGIN_NM, City.city, Disp.pest_found, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
            .join(City, Disp)\
            .filter(Aphis.ORIGIN_NM == country, or_(Disp.pest_found == 'Yes', Disp.pest_found == 'No'))\
            .group_by(Aphis.ORIGIN_NM, City.city, Disp.pest_found).all()

        df = pd.DataFrame(query, columns=['Country', 'Port', 'PestFound', 'Count', 'Quantity'])
        df_yes = df[df.PestFound == 'Yes']
        df_no = df[df.PestFound == 'No']
        # Left Join - only merges df_no where df_yes is not null
        df_merge = pd.merge(df_yes, df_no, on='Port', how='left')

        return df_merge


    def chart_pest_found_temporal(self, date_group, country, count_quantity, layout):
        layout['title'] = 'Pest Found (%)'
        # Get data
        df = self.data_pest_found_temporal(date_group, country)
        df_yes = df[df.PestFound == 'Yes']
        df_no = df[df.PestFound == 'No']

        df_merge = pd.merge(df_yes, df_no, on='Date', how='left')

        # Add count Yes/(Yes+No)
        df_merge['CountPer'] = (df_merge['Count_x']/(df_merge['Count_x']+df_merge['Count_y']) * 100).round(1)
        # Add quantity Yes/(Yes+No)
        df_merge['QuantityPer'] = (df_merge['Quantity_x']/(df_merge['Quantity_x']+df_merge['Quantity_y']) * 100).round(1) 

        x = [d for d in df_merge['Date']] 
        if count_quantity == 'count':
            y = [c for c in df_merge['CountPer']]
        elif count_quantity == 'quantity':
            y = [q for q in df_merge['QuantityPer']]
        
        plot = go.Scatter(
            x=x,
            y=y,
            name='Pest Found',
            line=dict(color='rgb(214, 39, 40)')
        )
        
        htmldiv = html.Div([
            dcc.Graph(
                id='temporal-line',
                figure=dict(data=[plot], layout=layout)
            )  
        ])

        return htmldiv

    def chart_pest_found_by_country(self, country, count_quantity):
        trace = []
        layout = dict(
            margin=go.layout.Margin(t=50), 
            title = 'Pest Found Ports',
            yaxis = dict(automargin=True)
        )
        plot = go.Bar(
            name='Pest Found',
            orientation='h',
            marker=dict(
                color=CONFIG['DISP_GROUP_DESC']['AP']['color']
            )
        )
        # Get data
        df = self.data_pest_found_by_country(country)
        # // Count is selected //
        if count_quantity == 'count':
            df['CountPer'] = (df['Count_x']/(df['Count_x']+df['Count_y']) * 100).round(1)
            plot['y'] = [p for p in df['Port']]
            plot['x'] = [c for c in df['CountPer']]

        # // Quantity is selected //    
        elif count_quantity == 'quantity':
            df['QuantityPer'] = (df['Quantity_x']/(df['Quantity_x']+df['Quantity_y']) * 100).round(1)
            plot['y'] = [p for p in df['Port']]
            plot['x'] = [q for q in df['QuantityPer']]

        trace.append(plot)

        # Return: Pest found ports bar chart
        htmldiv = [
            dcc.Graph(
                id='ports-stack-bar',
                figure=dict(data=trace, layout=layout)
            )                
        ]

        return htmldiv

    
    def data_disp_temporal(self, date_group, country, disp_group):
        if country == 'All':
            if date_group == 'all':
                if disp_group == 'All':
                    query = db.session.query(self.funcdateym, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                    .join(Disp)\
                    .group_by(self.funcdateym, Disp.disp_group).all()
                else:
                    query = db.session.query(self.funcdateym, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                    .join(Disp)\
                    .filter(Disp.disp_group == disp_group)\
                    .group_by(self.funcdateym, Disp.disp_group).all()                

            elif date_group == 'month':
                if disp_group == 'All':
                    query = db.session.query(self.funcdatem, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                    .join(Disp)\
                    .group_by(self.funcdatem, Disp.disp_group).all()
                else:
                    query = db.session.query(self.funcdatem, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                    .join(Disp)\
                    .filter(Disp.disp_group == disp_group)\
                    .group_by(self.funcdatem, Disp.disp_group).all() 

        else:
            if date_group == 'all':
                if disp_group == 'All':
                    query = db.session.query(self.funcdateym, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                        .join(Disp)\
                        .filter(Aphis.ORIGIN_NM == country)\
                        .group_by(self.funcdateym, Disp.disp_group).all()
                else:
                    query = db.session.query(self.funcdateym, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                        .join(Disp)\
                        .filter(Aphis.ORIGIN_NM == country, Disp.disp_group == disp_group)\
                        .group_by(self.funcdateym, Disp.disp_group).all()


            elif date_group == 'month':
                if disp_group == 'All':
                    query = db.session.query(self.funcdatem, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                        .join(Disp)\
                        .filter(Aphis.ORIGIN_NM == country)\
                        .group_by(self.funcdatem, Disp.disp_group).all()
                else:
                    query = db.session.query(self.funcdatem, Disp.disp_group, 
                        db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                        .join(Disp)\
                        .filter(Aphis.ORIGIN_NM == country, Disp.disp_group == disp_group)\
                        .group_by(self.funcdatem, Disp.disp_group).all()


        df = pd.DataFrame(query, columns=['Date', 'DISPGroup', 'Count', 'Quantity'])

        return df

    def data_busiest_port_by_country(self, country):
        query = db.session.query(Aphis.ORIGIN_NM, City.city,    db.func.count(Aphis.F280_ID))\
            .join(City).filter(Aphis.ORIGIN_NM == country)\
            .group_by(Aphis.ORIGIN_NM, City.city)\
            .order_by(db.func.count(Aphis.F280_ID).desc()).all()
        busiest = query[0][1]

        return busiest

    def data_ports_by_country(self, country, disp_group):
        if country != 'All':
            if disp_group == 'All':
                query = db.session.query(Aphis.ORIGIN_NM, City.city, Disp.disp_group, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .join(City, Disp)\
                .filter(Aphis.ORIGIN_NM == country)\
                .group_by(Aphis.ORIGIN_NM, City.city, Disp.disp_group).all()
            
            else:
                query = db.session.query(Aphis.ORIGIN_NM, City.city, Disp.disp_group, db.func.count(Aphis.F280_ID),db.func.sum(Aphis.QUANTITY))\
                .join(City, Disp)\
                .filter(Aphis.ORIGIN_NM == country, Disp.disp_group == disp_group)\
                .group_by(Aphis.ORIGIN_NM, City.city, Disp.disp_group).all()
               
            df = pd.DataFrame(query, columns=['Country', 'PortCity', 'DISPGroup', 'Count', 'Quantity'])

            return df

    def data_high_risk_flowers_by_country(self, country, port, disp_group, high_risk_flowers):
        
        if country != 'All':
            if disp_group == 'All':
                query = db.session.query(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY,
                        Disp.disp_group, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                    .join(City, Disp)\
                    .filter(Aphis.ORIGIN_NM == country, City.city == port, Aphis.COMMODITY.in_(high_risk_flowers))\
                    .group_by(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY, Disp.disp_group)\
                    .order_by(City.city, Aphis.COMMODITY, Disp.disp_group).all()
            else:
                query = db.session.query(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY,
                        Disp.disp_group, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                    .join(City, Disp)\
                    .filter(Aphis.ORIGIN_NM == country, City.city == port, Disp.disp_group == disp_group, Aphis.COMMODITY.in_(high_risk_flowers))\
                    .group_by(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY, Disp.disp_group)\
                    .order_by(City.city, Aphis.COMMODITY, Disp.disp_group).all()

            df = pd.DataFrame(query, columns=['Country', 'City', 'Flower', 'DISPGroup', 'Count', 'Quantity']) 

            return df


    def data_low_risk_flowers_by_country(self, country, port, disp_group, low_risk_flowers):
        
        if country != 'All':
            if disp_group == 'All':
                query = db.session.query(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY,
                    Disp.disp_group, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .join(City, Disp)\
                .filter(Aphis.ORIGIN_NM == country, City.city == port, Aphis.COMMODITY.in_(low_risk_flowers))\
                .group_by(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY, Disp.disp_group)\
                .order_by(City.city, Aphis.COMMODITY, Disp.disp_group).all()
            else:
                query = db.session.query(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY,
                    Disp.disp_group, db.func.count(Aphis.F280_ID), db.func.sum(Aphis.QUANTITY))\
                .join(City, Disp)\
                .filter(Aphis.ORIGIN_NM == country, City.city == port, Aphis.COMMODITY.in_(low_risk_flowers))\
                .group_by(Aphis.ORIGIN_NM, City.city, Aphis.COMMODITY, Disp.disp_group)\
                .order_by(City.city, Aphis.COMMODITY, Disp.disp_group).all()  

            df = pd.DataFrame(query, columns=['Country', 'City', 'Flower', 'DISPGroup', 'Count', 'Quantity'])

            return df


    def data_pest_risk_level(self, data, country):
        result = {'high': '', 'low': ''}
        for prl in data:
            if prl['CountryName'] == country:
                result['high'] = prl['PestRiskLevel']['High']
                result['low'] = prl['PestRiskLevel']['Low']
        
        return result

    # By Country Right charts
    # All show all displacement code
    def data_high_low_pest_risk_flowers(self, count_quantity, df_risk, risk_levels):
        trace = []

        dispg = df_risk['DISPGroup'].unique()
        for dg in dispg:
            subset = df_risk[df_risk['DISPGroup']==dg]
            fval = dict.fromkeys(risk_levels, 0)
            if count_quantity == 'count':
                for s in subset.to_dict('rows'):
                    fval[s['Flower']] = s['Count']
            elif count_quantity == 'quantity':
                for s in subset.to_dict('rows'):
                    fval[s['Flower']] = s['Quantity'] 
            plot_high = go.Bar(
                y=[key for key, val in fval.items()],
                x=[val for key, val in fval.items()],
                name=CONFIG['DISP_GROUP_DESC'][dg]['name'],
                orientation='h',
                marker=dict(
                    color=CONFIG['DISP_GROUP_DESC'][dg]['color']
                )
            )
            trace.append(plot_high) 
        return trace
    # By Country Right charts
    # Displacement code is selected  
    def data_high_low_pest_risk_flowers_disp(self, count_quantity, df_risk, disp_group):
        trace = []
        plot = go.Bar(
            y=[f for f in df_risk['Flower']],
            x=[c for c in df_risk[count_quantity]],
            name=CONFIG['DISP_GROUP_DESC'][disp_group]['name'],
            orientation='h',
            marker=dict(
                color=CONFIG['DISP_GROUP_DESC'][disp_group]['color']
            )
        )
        trace.append(plot)
        return trace


    
    
    
    
    
    def initDB(self):
        db.create_all()
        db.session.commit()
