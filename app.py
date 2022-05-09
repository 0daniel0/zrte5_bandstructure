#!/usr/bin/env python
#coding: utf-8

import numpy as np
from dash import Dash, dcc, html, Input, Output

from fig_maker import create_pahse_bands, create_bands, xax, yax
from fig_maker import get_strain_fig, get_shear_fig, get_phase_fig

# global variables
# cheating values, usually works
param = np.random.randint(0, 100000)  # just a large random number
on_click = {param: [0.0, 0.0]}  # arbitrary init values
flip = {param: False}  # whether to lock hover update
top_names = ["Strong TI", "Metallic", "Weak TI"]

# a 3 'fő' ábra
fig_strain = get_strain_fig()
fig_shear = get_shear_fig()
fig_phase = get_phase_fig()

# app = Dash(requests_pathname_prefix='/ZrTe5_project/')  # ezt fogjuk futtatni a végén
app = Dash()  # ezt fogjuk futtatni a végén

# Itt hozzuk létre a statikus elemeket. Most csak az ábrákat,
# lehetne még szöveget, meg minden egyebet is
app.layout = html.Div([
    #     Egy szöveges rész
    html.H1("ZrTe5 band structures", style={'textAlign': 'center', 'color': 'red'}),
    html.H2("For more see: [linktopaper]"),
    #     phase figures
    #     id: a callback részben ezzel hivatkozunk az adott elemre
    html.Div([dcc.Graph(id='phase', figure=fig_phase)],
             #              inline-block: próbálja sorba tenni
             #              block: egymás alá teszi
             style={'width': '50%', 'display': 'inline-block'}),
    html.Div([dcc.Graph(id='phase_band')],
             style={'display': 'inline-block', 'width': '40%'}),

    #     strain figures
    html.Div([dcc.Graph(id='strain', figure=fig_strain)],
             style={'width': '50%', 'display': 'inline-block'}),
    html.Div([dcc.Graph(id='strain_band')],
             style={'display': 'inline-block', 'width': '40%'}),

    #     strain figures
    html.Div([dcc.Graph(id='shear', figure=fig_shear)],
             style={'display': 'inline-block', 'width': '50%'}),
    html.Div([dcc.Graph(id='shear_band', figure=fig_shear)],
             style={'display': 'inline-block', 'width': '40%'}),
])


# Ez csinálja az interakciót, ha Input módosul, akkor módosítja az Outputot
# Inputnak '[' ']' között kell lennie. Vagy csak szarol telepítettem a dash-t
# Itt a bemenet a phase ábra hoverdatája (amit az egér miatt látunk)
# a kimenet meg a hozzá kapcsolódó ábra, amit alább gyártunk le.
# phase callback
@app.callback(Output('phase_band', 'figure'), [Input("phase", "hoverData"),
                                               Input("phase", "clickData")])
def update_bands(hover_data, click_data):
    # az argumentum mindig az Input
    # argumentumnak felel meg, de a neve önkényes
    #     Mivel nem adtam meg default ábrát, először None a hover_data
    if click_data is None:
        return create_pahse_bands(10, 10, "Title")

    # the actual mouse positions
    tempx = click_data['points'][0]['x']
    tempy = click_data['points'][0]['y']

    # if we click on a different position, update mode changes
    if not ((on_click[param][0] == tempx) and (on_click[param][1] == tempy)):
        flip[param] = not flip[param]
        on_click[param] = [tempx, tempy]

    # this changes the update mode
    if flip[param]:
        mode = click_data
    else:
        mode = hover_data

    idx = mode['points'][0]['z']  # a gap értéke
    idx = int(np.sign(idx)) + 1  # az ábra nevéhez kell
    #     Itt kimókolom, hogy melyik pont melyik sávszerkezetnek felel meg
    xpos, ypos = mode['points'][0]['x'], mode['points'][0]['y']
    j, i = np.where(xax == xpos)[0][0], np.where(yax == ypos)[0][0]
    title = top_names[idx]
    return create_pahse_bands(i, j, title)


# A következő 2 callback hasonló, csak egyszerűbb.
# Ők a shear és strain ábráit teszik interaktívvá
# strain callback
@app.callback(Output('strain_band', 'figure'), [Input('strain', 'hoverData')])
def update_strain_bands(hover_data):
    if hover_data:
        if hover_data['points'][0]['curveNumber'] == 0:
            title = "Bandstructure of \u03B5<sub>xx</sub>"
            i = hover_data['points'][0]['pointIndex']
            return create_bands(i, "x", title)
        if hover_data['points'][0]['curveNumber'] == 1:
            i = hover_data['points'][0]['pointIndex']
            title = "Bandstructure of \u03B5<sub>zz</sub>"
            return create_bands(i, "z", title)
    return create_bands(10, "x", "Bandstructure")


# shear callback
@app.callback(Output('shear_band', 'figure'), [Input('shear', 'hoverData')])
def update_shear_bands(hover_data):
    if hover_data:
        if hover_data['points'][0]['curveNumber'] == 0:
            title = "Bandstructure of \u03B5<sub>xy</sub>"
            i = hover_data['points'][0]['pointIndex']
            return create_bands(i, "xy", title)
        if hover_data['points'][0]['curveNumber'] == 1:
            i = hover_data['points'][0]['pointIndex']
            title = "Bandstructure of \u03B5<sub>yz</sub>"
            return create_bands(i, "yz", title)
    return create_bands(10, "xy", "Bandstructure")


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)  # futtatjuk az interaktív ábrát
