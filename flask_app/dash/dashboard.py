#Dash dashboard app structure
#Dec. 8, 2020. Gilson Frías

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(path, '../../web_scrap'))

from caterpillar import CatDataHandler

def init_dashboard(server):
    #TODO: Implement the web scrapping logic here
        #1.Allocate a small amount of memory for the graph arguments inside the CatDataHandler
        #2.Implement callbacks to update the graphs as soon as the argument values change
        #3.Implement some indication on the UI to highlight when a new scrapping session is taking place
        #4.Store scrapped values into a database (Redis?)

   
    dash_app = dash.Dash(
            server=server,
            routes_pathname_prefix='/dashapp/',
            external_stylesheets=[
                '/static/styles.css',
            ]
    )

    #Instance caterpillar data handling object and start scrapping for sale listings
    cat_data = CatDataHandler()
    cat_data.prepare_data()
    cat_data.draw_map()

    #Import Map HTML file
    #map_html = open('flask_app/dash/map.html', 'r').read()
    map_html = open('map.html', 'r').read()

    #Dashboard Markdown description text
    desc_text = '''
    Desglose de indicadores estadísticos acerca de la oferta de venta de equipos de la marca Caterpillar en mercados virtuales de la República Dominicana. La data es adquirida mediante el proceso de web-scrapping de listings en sitios de venta como [corotos.com.do](https://www.corotos.com.do/k/caterpillar) y [mercadolibre.com.do](https://vehiculos.mercadolibre.com.do/caterpillar). 
    '''

    font_settings = dict(
                family="Courier New, monospace",
                size=14,
                #color="Orange",
            )
    #fig_width = 350
    #fig_height = 350

    #Figure 1 
    fig1 = go.Figure(data=go.Histogram(x=cat_data.prices, 
                     histnorm='probability',
                     xbins=dict(
                         start=0,
                         end=5000000,
                         size=750000
                     )))
    fig1.update_layout(
                title={
                    'text':'Distribución de precios',
                    'y':0.85,
                    'x':0.5,
                    'xanchor':'center',
                    'yanchor':'top'
                },
                xaxis_title_text='Precio de venta (DOP)',
                yaxis_title_text='Probabilidad',
                bargap=0.1,
                font=font_settings,
                #width=fig_width,
                height=350
            )

    #Figure 2
    fig2 = go.Figure(data=[go.Pie(labels=cat_data.unique_currencies, 
                        values=cat_data.currencies_counts)])
    fig2.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=20,
                        marker=dict(colors=['mediumturquoise', 'gold'], line=dict(color='#000000', width=2)))
    fig2.update_layout(
                title={
                    'text':'Distribución de monedas',
                    'y':0.85,
                    'x':0.5,
                    'xanchor':'center',
                    'yanchor':'top'
                },
                font=font_settings,
                #width=fig_width,
                height=350
            )

    #Figure 3
    fig3 = go.Figure(data=go.Bar(x=cat_data.unique_models, 
                    y=cat_data.avg_model_prices, marker_color='green'))
    fig3.update_layout(
            title={
                'text':'Precio de venta promedio por modelo',
                'y':0.85,
                'x':0.5,
                'xanchor':'center',
                'yanchor':'top'
            },
            xaxis_title_text='Modelo Caterpillar',
            yaxis_title_text='Precio de venta (DOP)',
            font=font_settings,
            #width=fig_width,
            height=400
    )

    #Figure 4
    fig4 = go.Figure(data=go.Bar(
            x=cat_data.unique_provs, y=cat_data.unique_provs_counts, 
            marker_color='lightsalmon', text=cat_data.unique_provs_counts,
            textposition='auto'
    ))
    fig4.update_layout(
            title={
                'text':'Número de ofertas por provincia',
                'y':0.85,
                'x':0.5,
                'xanchor':'center',
                'yanchor':'top'
            },
            #title_text='Número de ofertas por provincia',
            xaxis_title_text='Provincia',
            yaxis_title_text='Vehículos ofertados',
            xaxis_tickangle=45,
            font=font_settings
    )

    #Dash HTML layout
    dash_app.layout = html.Div(className='dash-container',
                children=[
                    html.Meta(name='viewport', content='width=device-width, initial-scale'),
                    #html.Link(rel='stylesheet', href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"),
                    html.Div(className='title-div', children=[
                        html.H1(children=[
                            'Análisis de la oferta de productos ', 
                            html.Span(className='cat-span', children='Caterpillar'),
                            ' en el mercado de ventas por internet.'
                        ])
                    ]),
                    html.Div(className='cred-div', children=[
                        html.Div(className='author-div', children=[
                            html.Span(className='author-text',children=[
                                'Creado por: Gilson A. Frías P.'
                            ])
                        ]),
                        html.Div(className='social-media-div', children=[
                            html.Div(className='github-div', children=[
                                html.Img(className='github-img', src=dash_app.get_asset_url('github.png')),
                                html.A(className='social-media-url', href='https://github.com/GilsonFrias', children=['https://github.com/GilsonFrias'])
                            ]),
                            html.Div(className='linkedin-div', children=[
                                html.Img(className='linkedin-img', src=dash_app.get_asset_url('linkedin.png')),
                                html.A(className='social-media-url', href='www.linkedin.com/in/gilsonfrias', children=['www.linkedin.com/in/gilsonfrias'])
                            ])
                        ]),
                        html.Div(className='date-div', children=[
                            html.Span(className='date-text', children=[
                                'Última actualización: ',
                                html.Span(className='date-span', children=[cat_data.today_date])
                            ])
                        ])
                    ]),
                    html.Div(className='desc-div', children=[
                        dcc.Markdown(children=desc_text)
                    ]),
                    html.Div(className='fig1-container', children=[
                        html.Div(className='fig1-div', children=[
                            dcc.Graph(
                                id='prices-dist-hist',
                                figure=(fig1))
                        ]),
                        html.Div(className='fig1-div', children=[
                            html.Ul(className='fig1-metrics-ul', children=[
                                html.Li(className='header-li', children=['Volumen total ofertado (DOP):']),
                                html.Li(id='total-sales-li', className='field-li', children=[format(cat_data.total_sale_price, ',d')]),
                                html.Li(className='header-li', children=['Total vehículos ofertados:']),
                                html.Li(id='total-listings-li', className='field-li', children=[format(cat_data.total_listings, ',d')]),
                                html.Li(className='header-li', children=['Precio de venta promedio (DOP):']),
                                html.Li(id='avg-price-li', className='field-li', children=[format(cat_data.avg_price, ',d')])
                            ])
                        ]),
                        html.Div(className='fig1-div', children=[
                            dcc.Graph(
                                id='currencies-pie',
                                className='fig2-fig',
                                figure=(fig2))
                        ])
                    ]),
                    html.Div(className='prov-div', children=[
                            html.Iframe(className='map-div', srcDoc=map_html),
                            html.Div(className='map-div', children=[
                                dcc.Graph(
                                    id='provinces-bar',
                                    className='fig4-fig',
                                    figure=(fig4))
                            ])
                        ]),
                    #html.H2(children='Análisis de ofertas de venta de acuerdo a modelo'),
                    html.Div(className='fig3-container', children=[
                        html.Div(className='fig3-div', children=[
                            dcc.Graph(
                                id='prices-per-model',
                                className='fig3-fig',
                                figure=(fig3))
                        ])
                    ]),
                    html.Div(className='models-title', children=[
                        html.H2(children='Top 3 modelos más ofertados')]
                    ),
                    html.Div(className='models-container', children=[
                        html.Div(className='models-div', children=[
                            html.Div(className='models-fig-div', children=[
                                html.Img(className='models-fig', src=cat_data.images_urls[cat_data.top_models[n][0]])
                            ]),
                            html.Div(className='models-text-div', children=[ 
                                html.Ul(className='models-ul', children=[
                                    html.Li(className='models-li-header', children=[
                                        cat_data.top_models[n][0]
                                    ]),
                                    html.Li(className='models-li', children=[
                                        'Precio promedio (DOP): {}'.format(format(int(cat_data.top_models[n][1]), ',d'))
                                    ]),
                                    html.Li(className='models-li', children=[
                                        'Cantidad en oferta: {} ({}%)'.format(cat_data.unique_models_counts[cat_data.unique_models==cat_data.top_models[n][0]][0], 
                                            '{0:.2f}'.format(cat_data.unique_models_counts[cat_data.unique_models==cat_data.top_models[n][0]][0]/cat_data.unique_models_counts.sum()*100))
                                    ])
                                ])
                            ])
                        ])
                    for n in range(3)]),
                ]
            )

    return dash_app.server

