# https://dash.plotly.com/interactive-graphing
from dash import Dash, dcc, Output, Input, html, ctx  # pip install dash
import plotly.express as px
import pickle
import pandas as pd
import json


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

# app
app = Dash(__name__)

fig = px.scatter(df, x="x", y="y")
fig.update_layout(clickmode='event+select')

app.layout = html.Div([
    dcc.Graph(
        id='flow_vol_curve',
        figure=fig
    ),

    html.Pre(id='selected-data'),

    html.Button('Fini', id='btn_fini', n_clicks=0)
])


@app.callback(
    Output('selected-data', 'children'),
    Input('flow_vol_curve', 'selectedData'))
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=12)


@app.callback(
    Input('btn_fini', 'n_clicks'))
def save_JSON():
    if "btn_fini" == ctx.triggered_id:
        json_data = json.dumps('selectedData')
        jsonFile = open("dataTEST.json", "w")
        jsonFile.write(json_data)
        jsonFile.close()



if __name__ == '__main__':
    app.run_server(port=8053, debug=True)