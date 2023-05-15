import dash
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc, html
import dash_bootstrap_components as dbc
import datetime as dt
import pickle
import pandas as pd
import plotly.express as px
import json

# https://www.google.com/search?q=position+on+the+page+dash+app&oq=position+on+the+page+dash+app&aqs=edge..69i57.5640j0j1&sourceid=chrome&ie=UTF-8#fpstate=ive&vld=cid:d062947d,vid:MtSgh6FOL7I
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
data_curves = load_table_pickle(root, name_file_df_data)
df_curves = data_curves[['vol_FV', 'flow_FV']]


app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([

    html.Div([
        html.Div([
            html.Pre(children='Curve index:'),
        ], style={'display': 'inline-block'}),

        html.Div([
            html.Pre(id='curveIndex'),
        ], style={'display': 'inline-block'}),

        html.Div([
            html.Button('Previous curve', id='previous_curve', n_clicks=0),
            html.Button('Next curve', id='next_curve', n_clicks=0),
        ]),

        dcc.Graph(
            id='flow_vol_curve',
            # figure=fig
        ),
    ], style={'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(['Artefact', 'Cough', 'Irregularity', 'Not defined'], 'Not defined', id='demo-dropdown'),

        html.Pre(id='selected-data'),

        html.Button('add Selected Data', id='adding-data-button', n_clicks=0),

        dash_table.DataTable(id='abnormalities-idx-tab'),



        html.Button('Export to Excel', id='save_to_csv', n_clicks=0),
        # Create notification when saving to excel
        html.Div(id='placeholder', children=[]),
    ], style={'display': 'inline-block'}),

    dcc.Store(id="store", data=0),
    dcc.Interval(id='interval', interval=1000),

])


# ------------------------------------------------------------------------------------------------


@app.callback(
    Output(component_id='curveIndex', component_property='children'),
    Input(component_id='previous_curve', component_property='n_clicks'),
    Input(component_id='next_curve', component_property='n_clicks'),
    State(component_id='curveIndex', component_property='children'),
)
def updateIndex(prev_clicks, next_clicks, index):
    """
    When the next or previous buttons are clicked, update the image index
    ensuring it stays within 0 <= index < len(contents)
    """
    if index is None:
        index = 0
    # get which button click triggered callback
    trig = dash.callback_context.triggered[0]['prop_id']

    # update data if necessary and return it
    if trig == "previous_curve.n_clicks" and index > 0:
        index = index - 1
    elif trig == "next_curve.n_clicks" and index < len(df_curves) - 1:
        index = index + 1

    return index


@app.callback(
    Output(component_id='flow_vol_curve', component_property='figure'),
    Input(component_id='curveIndex', component_property='children'),
)
def display_curve(n_clicks):
    df_curve = pd.DataFrame({
        "x": df_curves.at[n_clicks, 'vol_FV'],
        "y": df_curves.at[n_clicks, 'flow_FV']
    })
    fig = px.scatter(df_curve, x="x", y="y", width=800, height=800)
    fig.update_layout(clickmode='event+select')
    return fig


@app.callback(
    Output(component_id='abnormalities-idx-tab', component_property='data'),
    Input(component_id='adding-data-button', component_property='n_clicks'),
    State(component_id='flow_vol_curve', component_property='selectedData'),
    State(component_id='demo-dropdown', component_property='value'),
    State(component_id='curveIndex', component_property='children'),
    State(component_id='abnormalities-idx-tab', component_property='data'),
)
def add_rows_select(n_clicks, selectedData, abno_type, curve_idx, existing_rows):

    if n_clicks > 0:
        if not (selectedData is None or len(selectedData["points"]) == 0):
            value_start = selectedData["points"][0]['pointIndex']
            value_end = selectedData["points"][-1]['pointIndex']

            if existing_rows is None:
                existing_rows = ({
                    'Curve index': curve_idx,
                    'Abnormality Type': abno_type,
                    'Start Index': value_start,
                    'Stop Index': value_end}),

            else:
                existing_rows.append({
                    'Curve index': curve_idx,
                    'Abnormality Type': abno_type,
                    'Start Index': value_start,
                    'Stop Index': value_end}),

            return existing_rows

        else:
            print('select data')



# @app.callback(
#     Output(component_id='flow_vol_curve', component_property='selectedData'),
#     Input(component_id='previous_curve', component_property='n_clicks'),
#     Input(component_id='next_curve', component_property='n_clicks'),
# )
# def clear_selected_data_change_fig(prev_n_clicks, next_n_clicks):
#     return None


@app.callback(
    Output(component_id='selected-data', component_property='children'),
    Input(component_id='flow_vol_curve', component_property='selectedData'))
def display_selected_data(selectedData):  # selectedData is a property of Graph

    if selectedData is None or len(selectedData["points"]) == 0:
        res = 'No data selected yet'
    else:
        first_index = selectedData["points"][0]
        last_index = selectedData["points"][-1]
        res = {'FirstPoint': first_index, 'LastPoint': last_index}

    return json.dumps(res, indent=12)


@app.callback(
    [Output(component_id='placeholder', component_property='children'),
     Output(component_id="store", component_property="data")],
    [Input(component_id='save_to_csv', component_property='n_clicks'),
     Input(component_id="interval", component_property="n_intervals")],
    [State(component_id='abnormalities-idx-tab', component_property='data'),
     State(component_id='store', component_property='data')]
)
def df_to_csv(n_clicks, n_intervals, dataset, s):
    output = html.Plaintext("The data has been saved to your folder.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_triggered == "save_to_csv":
        s = 6
        df = pd.DataFrame(dataset)
        df.to_csv(r"\\filer300\USERS3007\I0337516\Desktop\DataTest.csv", index=False, mode='a', header=False)
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s - 1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s


if __name__ == '__main__':
    app.run_server(port=8053, debug=True)
