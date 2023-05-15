import dash
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc



app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2('Grading application first version')
            ])
        ], style={'background-color': '#ADD8E6'}),
        # dbc.Row([
        #     dbc.Col([
        #     ], width=3, style={'background-color': 'red'}),
        #     dbc.Col([
        #     ], width=6, style={'background-color': 'black'}),
        # ])
    ]),
])


if __name__ == '__main__':
    app.run_server(port=8053, debug=True)
