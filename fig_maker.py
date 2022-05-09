#!/usr/bin/env python
# coding: utf-8

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from data_loader import get_phase_data, get_strain_datas, get_bands_data, get_data, ROOT_PATH

# for phase figure some data

topgap, gap, feat, x, y, z = get_phase_data()  # phase figure datas
n = 20
xax = np.linspace(x.min(), x.max(), n)
yax = np.linspace(y.min(), y.max(), n)
# end of phase figure data

# strain and shear figure data
COLOR = {"x": '#F9461F', "z": '#1F6CF9'}
(d_strain, x_strain, z_strain, datax_strain,
 dataz_strain, pathx_strain, pathz_strain) = get_strain_datas()
root = ROOT_PATH + "line_graphs/shear"
gapxy, dataxy, path_list_xy = get_data(root + "xy", n=21)
gapyz, datayz, path_list_yz = get_data(root + "yz", n=21)
shear_x = 100 * np.linspace(-0.1, 0.1, 21, endpoint=True)

# Figure settings
FIG_HEIGHT: int = 450
FIG_RIGHT_DECREASE: int = 50
FIG_MARGIN: dict = {'l': 0, 'b': 0, 'r': 0, 't': 50}


# ## Ábrák készítése, fontos rész

def get_strain_fig():
    # go: plotly alacsony szintu ~(matplotlib) ábra készítő almodulja
    # a görög betűk nekem csak a unikód karakterkódokkal működtek :/
    #     scatter plot adatgenerálás
    datax = go.Scatter(x=d_strain, y=x_strain, mode='markers+lines', name=u"\u03B5<sub>xx</sub>")
    dataz = go.Scatter(x=d_strain, y=z_strain, mode='markers+lines', name=u"\u03B5<sub>zz</sub>")
    data = [datax, dataz]

    #     itt adom meg az ábra címét, tengelyfeliratokat, ...
    layout = go.Layout(height=FIG_HEIGHT,
                       margin=FIG_MARGIN,
                       title='Uniaxial strain',
                       xaxis=go.layout.XAxis(title='Strain (%)'),
                       yaxis=go.layout.YAxis(title='Gap (meV)'),
                       )
    #     itt kombinálódik az adat meg a layout, és készül el az ábra
    fig = go.Figure(data=data, layout=layout)

    #     ha az egeret egy ponthoz visszük, ez a szöveg fog megjelenni. (van rá plotly-s template)
    #     html stílusban kell írni a dolgokat.
    #     x, y: a tengelyek értékei, customdata: oda azt teszel, amit akarsz (én a mappák utvonalát)
    hovertemplate = ('<b>Gap: %{y:.2f} meV</b><br>' +
                     'strain: %{x:.2f} (%)<br>'
                     #             'more data:<br>'+
                     #             '<i>path-to-folder/%{customdata}</i><extra></extra>'
                     )
    #     fölösleges 2 sor, csak átnevetem őket
    customdatax = np.array(pathx_strain)
    customdataz = np.array(pathz_strain)

    #     az ábra elkészülte után is szabadon lehet módosítani minden részt
    # Hozzáadjuk a hover szöveget, és magadjuk a vonalak színeit
    # becsületes módosítás
    fig.update_traces(go.Scatter(hovertemplate=hovertemplate, customdata=customdatax))

    #     Így lehet a nyers adatokat módosítani - kevésbé becsületes módosítás
    fig.data[1]["customdata"] = customdataz
    fig['data'][0]['line']['color'] = COLOR["x"]  # egyik görbe
    fig['data'][1]['line']['color'] = COLOR["z"]  # másik görbe
    return fig


# Ez lényegében ugyanaz, mint a get_strain_fig, csak más a tengelyfelirat, meg a cím
def get_shear_fig():
    dataz = go.Scatter(x=shear_x, y=gapyz, mode='markers+lines', name=u"\u03B5<sub>yz</sub>")
    datax = go.Scatter(x=shear_x, y=gapxy, mode='markers+lines', name=u"\u03B5<sub>xy</sub>")
    data = [datax, dataz]

    layout = go.Layout(height=FIG_HEIGHT,
                       margin=FIG_MARGIN,
                       title='Shear',
                       xaxis=go.layout.XAxis(title='Shear (%)'),
                       yaxis=go.layout.YAxis(title='Gap (meV)'),
                       )
    fig = go.Figure(data=data, layout=layout)

    hovertemplate = ('<b>Gap: %{y:.2f} meV</b><br>' +
                     'shear: %{x:.2f} (%)<br>'
                     #             'more data:<br>'+
                     #             '<i>path-to-folder/%{customdata}</i><extra></extra>'
                     )
    customdatax = np.array(path_list_xy)
    customdataz = np.array(path_list_yz)
    fig.update_traces(go.Scatter(hovertemplate=hovertemplate, customdata=customdatax))
    fig.data[1]["customdata"] = customdataz
    fig['data'][1]['line']['color'] = COLOR["z"]
    fig['data'][0]['line']['color'] = COLOR["x"]
    return fig


# for strian and shear sávszerkezetek
def create_bands(i, which, title):
    #     i: hanyadik adatpont, which: eldönti, hogy strian/shear, és aznon belül, melyik
    #     megfelelő adatok betöltése
    if which == "x":
        eigh, lk, kt, kl = datax_strain[i]
    elif which == "z":
        eigh, lk, kt, kl = dataz_strain[i]
    elif which == "xy":
        eigh, lk, kt, kl = dataxy[i]
    elif which == "yz":
        eigh, lk, kt, kl = datayz[i]
    else:
        title = "Bandstructure"
        eigh, lk, kt, kl = dataz_strain[i]
    x = lk
    y = [*eigh.T]
    #     Ábra készítés
    fig = px.line(x=x, y=y)
    # Hozzáadom a tengely feliratokat, meg egyebeket, ehhez dict-eket kell használni
    fig.update_traces(mode='lines')

    fig.update_layout(height=FIG_HEIGHT - FIG_RIGHT_DECREASE,
                      margin=FIG_MARGIN,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=kt,
                          ticktext=kl,
                          title='<b>k</b>'
                      ),
                      yaxis=dict(title='Energy (eV)'),
                      title={
                          'text': title,
                          'y': 1.0,
                      },
                      )
    fig.update_yaxes(range=[-0.3, 0.3])

    #     Itt is a nyers adatokat módosítjuk
    for i in range(len(y)):
        fig['data'][i]['line']['color'] = '#000000'
        fig['data'][i]['showlegend'] = False
        hover_name = 'Band: ' + str(66 + i) + '<br>energy=%{y} (eV)<extra></extra>'
        fig['data'][i]['hovertemplate'] = hover_name
    return fig


def get_phase_fig():
    #     ugyanazok a lépések, mint get_strain_fig-nél, csak 2d-s ábrára
    # divergens színt választottam, hogy a pozitív-negatív értékek elkülönüljenek
    # a szín megadása tényleg ilyen bonyi, a color="picnic" nem működik
    fig = px.imshow(topgap.reshape(n, n).T,
                    origin="lower",
                    aspect='auto',
                    x=xax,
                    y=yax,
                    color_continuous_scale="RdBu",
                    color_continuous_midpoint=0,
                    )

    hovertemplate = (u'<b>Gap: %{z:.2f} meV</b><br>' +
                     '\u0394x and \u0394z: %{x:.2f} (%)<br>' +
                     '\u0394y: %{y:.2f} (%)<br>'
                     #                     'full bandstructure:<br>'+
                     #                     '<i>path-to-folder%{customdata}</i><extra></extra>'
                     )
    #     Itt a végén kell a reshape(n, n), mert az ábrázolt adatok is egy nxn-es mátrix. És a
    #     kettő shape-jének egyeznie kell (ez 1d-ben trivi).
    customdata = np.array([str(i) + '-' + str(j) for j in range(n) for i in range(n)]).reshape(n, n)
    fig.update_traces(go.Heatmap(hovertemplate=hovertemplate, customdata=customdata))

    fig.update_layout(height=FIG_HEIGHT,
                      margin=FIG_MARGIN,
                      hovermode='closest',
                      title={
                          'text': "Phase diagram",
                      },
                      xaxis=dict(title='\u0394x and \u0394z (%)'),
                      yaxis=dict(title='\u0394y (%)'),
                      coloraxis_colorbar=dict(title="Gap (meV)", ),
                      )
    return fig


# phase ábrához mellékelt sávszerkezet, olyan, mint a create_bands, csak nem vonal,
def create_pahse_bands(i, j, title):

    eigh, lk, kt, kl = get_bands_data(i, j)
    x = lk
    y = [*eigh.T]
    fig = px.line(x=x, y=y)

    #     fig.update_traces(mode='lines+markers')
    fig.update_traces(mode='lines')

    fig.update_layout(height=FIG_HEIGHT - FIG_RIGHT_DECREASE,
                    margin=FIG_MARGIN,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=kt,
                          ticktext=kl,
                          title='<b>k</b>'  # bold font html-ben
                      ),
                      yaxis=dict(title='Energy (eV)'),
                      title={
                          'text': title,
                      },
                      )
    fig.update_yaxes(range=[-0.3, 0.3])


    for i in range(len(y)):
        fig['data'][i]['line']['color'] = '#000000'
        fig['data'][i]['showlegend'] = False
        hover_name = 'Band: ' + str(66 + i) + '<br>energy=%{y} (eV)<extra></extra>'
        fig['data'][i]['hovertemplate'] = hover_name
# hanem 2d ábrához készült
    return fig
