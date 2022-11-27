from dash import Dash, html, dcc, Output, Input, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd


###### EXTRACTION & TRANSFORM
# import yfinance as yf
# def load_data():
#     url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
#     html = pd.read_html(url, header = 0)
#     df = html[0]
#     return df

# STOCKS = load_data()
# sector = STOCKS.groupby('GICS Sector')

# #FORMATTER = {'Close':'${0:,.2f}', 'Volume': '{:,.0f}'}


# # Stock data (TO BE CALLED ONCE PER PAGE LOADING)
# df = STOCKS.sample(frac=0.6)
# data = yf.download(
#         tickers = list(df.Symbol),
#         period = "1mo",
#         interval = "1d",
#         group_by = 'ticker',
#         auto_adjust = True
#     )
    
# STOCK_DATA=data.melt(ignore_index=False, value_name="price").reset_index()
# STOCK_DATA = STOCK_DATA.stack().reset_index()
# print(STOCK_DATA[:15])

# STOCKS.to_csv('sp500_list.csv', index=False)
# STOCK_DATA.to_csv("mystocks.csv", index=False)

############## LOADING
STOCKS = pd.read_csv("https://raw.githubusercontent.com/ldavidr3/sp500_dashboard/main/sp500_list.csv")

STOCK_DATA = pd.read_csv("https://raw.githubusercontent.com/ldavidr3/sp500_dashboard/main/mystocks.csv")

STOCK_DATA.rename(columns = {'variable_0':'Stock'}, inplace = True)

app = Dash(__name__, 
                external_stylesheets=[dbc.themes.JOURNAL],
                title='S&P 500',
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
            )

# Layout:
# ************************************************************************
alert = dbc.Alert("Por favor, escoja un Sector para ver los resultados", 
                color="danger",
                dismissable=True, 
                style={'fontSize':15})  # use dismissable or duration=5000 for alert to close in x milliseconds
                
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("S&P 500 Dashboard", className='text-center text-primary mb-4'),
                width=12),
        style={"margin-top": "1rem",}
    ),
    dbc.Row([
            dbc.Col([    
                dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H2("Acciones por Sector", className="card-title text-center text-primary"),
                            dbc.CardImg(src="/assets/icon.png", title="Acciones S&P 500", className="h-50 w-50 mx-5 d-inline-block"),
                            html.H6("Escoge un sector para tener una muestra de las acciones: \n", className="card-text my-3"),
                            html.Div(id="the_alert"),
                            dcc.Dropdown(id='my-dpdn', multi=False, value='Consumer Discretionary', style={"color": "#000000"},
                                options=[{'label':x, 'value':x}
                                        for x in sorted(STOCKS['GICS Sector'].unique())],
                                ),
                            html.H6("Acciones disponibles: \n", className="card-text my-3" ),
                            dcc.Dropdown(id='my-dpdn2', multi=True, value=['ABC'],
                                    options=[{'label':x, 'value':x}
                                    for x in sorted(STOCK_DATA['Stock'].unique())],
                                ),                        
                        ]
                    ),
                ],
                color="light", className='my-50',
        ),
        ], xs=5, sm=5, md=5, lg=3, xl=3,
        ),
        dbc.Col([
            dbc.Card(
                [   
                    dbc.CardBody(
                        html.H2("Resumen del Sector", className="card-text text-info")
                    ),
                    dcc.Markdown(children='', id='text-desc', className='text-center lead row align-items-center'),                 
                ],
            )
        ], xs=12, sm=12, md=12, lg=3, xl=3,
        ),
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardBody(
                        html.H2("Companias Acumuladas por Sector", className="card-text text-info")
                    ),
                    dcc.Graph(id='my-hist', figure={}, style={'width': '100%', 'height': '65%'}),                    
                ],   
            )
        ],xs=12, sm=12, md=12, lg=5, xl=5,
        ),
    ],  align="center", justify='around', className="margin-x 2"),  # Horizontal:start,center,end,between,around
    dbc.Row([
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardBody(
                        html.H2("Precio de Cierre de la Accion", className="card-text text-info")
                    ),
                    dcc.Graph(id='line-fig2', figure={}, style={'width': '100%', 'height': '65%'}),
                ],                
            )
        ], xs=12, sm=12, md=12, lg=5, xl=5,
        ),
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardBody(
                        html.H2("Lideres de Sector por Volumen de Transacciones", className="card-text text-info")
                    ),
                    dcc.Graph(id='box-fig', figure={}),                    
                ],                
            )
        ], xs=12, sm=12, md=12, lg=5, xl=5,
        ),
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardBody(
                        html.H4("Eevee esta feliz de verte!", className="card-text text-success")
                    ),
                    dbc.CardImg(src="/assets/eevee_running.gif", bottom=True, class_name='w-75 mx-auto d-inline-block'),
                ],
            )
        ], xs=12, sm=12, md=12, lg=2, xl=2,
        )
    ],style={"margin-top": "1rem", }, align="center", justify='around', className='margin-x 2'),  # Vertical: start, center, end
    dbc.Row(
        dbc.Col([
                html.Footer([
                            "hecho con ♡ infinito, ", 
                            html.A("212ldavidr", href='https://instagram.com/212ldavidr', target="_blank")],
                        className='text-center text-danger'),
                ], width=12),
        style={"margin-top": "2rem"}, className='text-center text-success mb-4',
    ),
], fluid=True)


## CALLBACKS
#*****************************************************************************************
# Treemap chart
@callback(
    Output('box-fig', 'figure'),
    Input('my-dpdn2', 'value')
)
def update_graph(stock_slctd):
    if stock_slctd == None :
        return {}
    aux = STOCK_DATA[STOCK_DATA['Stock'].isin(stock_slctd)]
    vol = aux.groupby(['Stock'])['Volume'].last().sort_values(ascending=False).to_frame()
    vol = vol.reset_index()
    fig_tree = px.treemap(vol, path = [px.Constant('All'), 'Stock', 'Volume'], 
                    values='Volume',
                    color='Volume',
                    color_continuous_scale = px.colors.sequential.Agsunset)
    fig_tree.update_layout(
                    hovermode=False,
                    font=dict(            
                            size=14),   
                    )
    fig_tree.update_traces(texttemplate = "%{value:,.0f}")
    return fig_tree


# Histogram
@callback(
    Output('my-hist', 'figure'),
    Input('my-dpdn', 'value')
)
def update_graph(stock_slctd):
    dff = STOCKS
    fighist = px.histogram(dff["GICS Sector"],  
                    template ="simple_white",
                    text_auto=True, color_discrete_sequence = ['#a398ee']).update_xaxes(categoryorder="total descending")
    fighist.update_layout(
                    title_x=0.5,
                    xaxis_title="",
                    yaxis_title="",
                    showlegend=False,
                    xaxis_tickfont_size=14,
                    xaxis_showgrid=False,
                    yaxis_showgrid=False,
                    xaxis_zeroline=False, 
                    yaxis_zeroline=False,
                    xaxis_tickangle=-45,
                    font=dict(
                            size=14),   
                    )
    fighist.add_annotation(text="Chosen sector!", 
                            x=stock_slctd, 
                            y=STOCKS.groupby('GICS Sector')['Symbol'].nunique().loc[stock_slctd],
                            arrowhead=1, showarrow=True)
    return fighist

# Line chart - multiple
@callback(
    Output('line-fig2', 'figure'),
    Input('my-dpdn2', 'value')
)
def update_graph(stock_slctd):
    dff = STOCK_DATA[STOCK_DATA['Stock'].isin(stock_slctd)]
    figln2 = px.line(dff, x='Date', y='Close', color='Stock', template ="simple_white")
    figln2.update_layout(
                title_x=0.5,
                xaxis_title="",
                yaxis_title="",
                xaxis_tickfont_size=14,
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                xaxis_zeroline=False, 
                yaxis_zeroline=False,
                xaxis_tickangle=-45,
                legend=dict(
                        title='Stocks',
                        ),         
                )
    return figln2


# Getting sample stocks from SECTOR selected
@callback(
    [Output("my-dpdn2", component_property="options"),
    Output("my-dpdn2", component_property="value")],
    Input('my-dpdn', component_property='value')
)
def update_stocks(sec_chosen):
    sym = list(STOCKS[STOCKS['GICS Sector'] == sec_chosen].Symbol)
    aux = STOCK_DATA[STOCK_DATA['Stock'].isin(sym)]
    vol = aux.groupby(['Stock'])['Volume'].last().sort_values(ascending=False).to_frame()
    symb = list(vol.index)[:5]
    return list(vol.index), symb

# Updating Resume
@callback(
    [Output('text-desc','children'),
     Output("the_alert", "children")],
    Input('my-dpdn', component_property='value')
)
def update_markdown(sec_chosen):
    if sec_chosen == None :
        text = ""
        return text, alert
    else:
        ## Total companies in the sector
        df_m = STOCKS
        df_m = df_m.groupby('GICS Sector')['Symbol'].nunique()
        df_m = df_m.loc[sec_chosen]
        text = " There are **{} companies** in the {} sector.  \n".format(df_m, sec_chosen)
        
        #### Average closing price

        sym = list(STOCKS[STOCKS['GICS Sector'] == sec_chosen].Symbol)
        aux = STOCK_DATA[STOCK_DATA['Stock'].isin(sym)]
        text += " In average, the sector' stock prices ** close in  ${0:,.2f}. ** ".format(aux['Close'].mean())
        return text, ""


if __name__=='__main__':
    app.run_server(debug=True, port=8000)