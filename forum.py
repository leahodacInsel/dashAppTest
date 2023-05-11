import dash
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc, html
import datetime as dt

import pandas as pd
import plotly.express as px

currentdatetime = dt.datetime.now()

app = dash.Dash(__name__,suppress_callback_exceptions=True)


app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='input1',
            placeholder='Input 1',
            type='number',
            value='',
            style={'padding': 10}
        ),
        dcc.Input(
            id='input2',
            placeholder='Input 2',
            type='number',
            value='',
            style={'padding': 10}
        ),
        html.Button('add Data', id='adding-data', n_clicks=0)
    ], style={'height': 50}),

    dash_table.DataTable(
        id='our-table',
    ),

    html.Button('Export to Excel', id='save_to_csv', n_clicks=0),

    # Create notification when saving to excel
    html.Div(id='placeholder', children=[]),
    dcc.Store(id="store", data=0),
    dcc.Interval(id='interval', interval=1000),

])
# ------------------------------------------------------------------------------------------------


@app.callback(
    Output('our-table', 'data'),
    [Input('adding-data', 'n_clicks')],
    [State('input1', 'value'),
     State('input2', 'value'),
     State('our-table', 'data')],
)
def add_rows(n_clicks, value, value2, existing_rows):
    if n_clicks > 0:
        if existing_rows is None:
            existing_rows = ({
                'name': value, 'id': value2}),

        else:
            existing_rows.append({
                'name': value, 'id': value2}),

    return existing_rows





@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_csv', 'n_clicks'),
     Input("interval", "n_intervals")],
    [State('our-table', 'data'),
     State('store', 'data')]
)
def df_to_csv(n_clicks, n_intervals, dataset, s):
    output = html.Plaintext("The data has been saved to your folder.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_triggered == "save_to_csv":
        print(dataset)
        s = 6
        df = pd.DataFrame(dataset)
        df.to_csv("Data.csv", index=False, mode='a', header=False)
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s-1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s


if __name__ == '__main__':
    app.run_server(port=8053, debug=True)