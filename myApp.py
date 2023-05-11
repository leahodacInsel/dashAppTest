import dash
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc, html
import datetime as dt
import pickle
import pandas as pd
import plotly.express as px
import json
import numpy as np


# incorporate data into app
def load_table_pickle(path, name_file):
    file = path + "\\" + name_file + '_rawCurves.pkl'

    print("\nStarted loading dictionary from .pkl file", name_file)
    with open(file, 'rb') as fp:
        df_ = pickle.load(fp)
    print("... done loading dictionary from file", file)
    return df_


root = r'\\filer300\USERS3007\I0337516\Desktop\spiroQC_project\XBJC_set'
name_file_df_data = 'format_df_data_from_XML'
data = load_table_pickle(root, name_file_df_data)
df = data[['vol_FV', 'flow_FV']]
flow = df.at[0, 'flow_FV']
vol = df.at[0, 'vol_FV']
df = pd.DataFrame({
    "x": vol,
    "y": flow
})

fig = px.scatter(df, x="x", y="y", width=800, height=800)
fig.update_layout(clickmode='event+select')

currentdatetime = dt.datetime.now()

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([

    dcc.Graph(
        id='flow_vol_curve',
        figure=fig
    ),

    html.Pre(id='selected-data'),

    # html.Div([
    #     dcc.Input(
    #         id='value_start',
    #         placeholder='Start zone of interest',
    #         type='number',
    #         value='',
    #         style={'padding': 10}
    #     ),
    #     dcc.Input(
    #         id='value_end',
    #         placeholder='End zone of interest',
    #         type='number',
    #         value='',
    #         style={'padding': 10}
    #     ),
    #     html.Button('add Data', id='adding-data-button', n_clicks=0)
    # ], style={'height': 50}),

    dash_table.DataTable(id='abnormalities-idx-tab'),

    html.Button('Export to Excel', id='save_to_csv', n_clicks=0),

    # Create notification when saving to excel
    html.Div(id='placeholder', children=[]),
    dcc.Store(id="store", data=0),
    dcc.Interval(id='interval', interval=1000),

])


# ------------------------------------------------------------------------------------------------


# @app.callback(
#     Output(component_id='abnormalities-idx-tab', component_property='data'),
#     [Input(component_id='adding-data-button', component_property='n_clicks')],
#     [State(component_id='value_start', component_property='value'),
#      State(component_id='value_end', component_property='value'),
#      State(component_id='abnormalities-idx-tab', component_property='data')],
# )
# def add_rows(n_clicks, value_start, value_end, existing_rows):
#     if n_clicks > 0:
#         if existing_rows is None:
#             existing_rows = ({
#                 'Abnormality Type': 'test',
#                 'Start Index': value_start,
#                 'Stop Index': value_end}),
#
#         else:
#             existing_rows.append({
#                 'Abnormality Type': 'test',
#                 'Start Index': value_start,
#                 'Stop Index': value_end}),
#
#     return existing_rows


@app.callback(
    Output(component_id='abnormalities-idx-tab', component_property='data'),
    Input(component_id='flow_vol_curve', component_property='selectedData'),
    State(component_id='abnormalities-idx-tab', component_property='data'),
)
def add_rows_select(selectedData, existing_rows):

    if not selectedData is None:
        value_start = selectedData["points"][0]['pointIndex']
        value_end = selectedData["points"][-1]['pointIndex']
        print(value_start)

        if existing_rows is None:
            existing_rows = ({
                'Abnormality Type': 'test',
                'Start Index': value_start,
                'Stop Index': value_end}),

        else:
            existing_rows.append({
                'Abnormality Type': 'test',
                'Start Index': value_start,
                'Stop Index': value_end}),

        return existing_rows


@app.callback(
    Output(component_id='selected-data', component_property='children'),
    Input(component_id='flow_vol_curve', component_property='selectedData'))
def display_selected_data(selectedData):  # selectedData is a property of Graph
    if selectedData is None:
        res = dict()
    else:
        first_index = selectedData["points"][0]
        last_index = selectedData["points"][-1]
        res = {'FirstPoint': first_index, 'LastPoint': last_index}

    return json.dumps(res, indent=12)


# @app.callback(
#     [Output('placeholder', 'children'),
#      Output("store", "data")],
#     [Input('save_to_csv', 'n_clicks'),
#      Input("interval", "n_intervals")],
#     [State('our-table', 'data'),
#      State('store', 'data')]
# )
# def df_to_csv(n_clicks, n_intervals, dataset, s):
#     output = html.Plaintext("The data has been saved to your folder.",
#                             style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
#     no_output = html.Plaintext("", style={'margin': "0px"})
#
#     input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
#
#     if input_triggered == "save_to_csv":
#         print(dataset)
#         s = 6
#         df = pd.DataFrame(dataset)
#         df.to_csv("Data2.csv", index=False, mode='a', header=False)
#         return output, s
#     elif input_triggered == 'interval' and s > 0:
#         s = s - 1
#         if s > 0:
#             return output, s
#         else:
#             return no_output, s
#     elif s == 0:
#         return no_output, s


if __name__ == '__main__':
    app.run_server(port=8053, debug=True)
