import dash                                # pip install dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries # pip install alpha-vantage


# -------------------------------------------------------------------------------
# Set up initial key and financial category

key = '0Q466LJ33OMBCN3O' # Use your own API Key or support my channel if you're using mine :)
# # https://github.com/RomelTorres/alpha_vantage
# # Chose your output format or default to JSON (python dict)
ts = TimeSeries(key, output_format='pandas') # 'pandas' or 'json' or 'csv' 从api中提取pandas格式的时间序列
ttm_data, ttm_meta_data = ts.get_intraday(symbol='TTM',interval='1min', outputsize='compact') # 这是我们从api中提取的地方，intraday就是当天的数据，TTM是我们拉取的公司股票，设置每一分钟拉动一次，当然我们只会拉取400行的数据，
df = ttm_data.copy()
df=df.transpose() # 然后是转置，重命名，合并
df.rename(index={"1. open":"open", "2. high":"high", "3. low":"low",
                 "4. close":"close","5. volume":"volume"},inplace=True)
df=df.reset_index().rename(columns={'index': 'indicator'})
df = pd.melt(df,id_vars=['indicator'],var_name='date',value_name='rate')
df = df[df['indicator']!='volume'] # 这里给主列重命名，这些都是为了更容易去进行绘图和方便后面dash的操作
print(df.head()) # 这上面就是我们调用api获取数据，顺带做了下清洗的步骤，回头我会把代码放出来，清洗的步骤不是必要的，大家参考下

df.to_csv("data.csv", index=False) # 最后建议大家还是把上面打印的数据保存到本地，因为如果你构建dash之后，每次点击刷新网页，都会对你的api和应用程序产生负担。
#每人只能申请五个免费api，每分钟只能请求一次，所以我们调用一次api之后，存到本地，然后用dash从csv中拉取数据就能避免api使用过多。
exit()


# Read the data we already downloaded from the API
dff = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Analytic_Web_Apps/Financial/data.csv")
dff = dff[dff.indicator.isin(['high'])]


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardImg(
                        src="/assets/tata.png",
                        top=True,
                        style={"width": "6rem"},
                    ),

                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P("CHANGE (1D)")
                            ]),

                            dbc.Col([
                                dcc.Graph(id='indicator-graph', figure={},
                                          config={'displayModeBar':False})
                            ])
                        ]),

                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='daily-line', figure={},
                                          config={'displayModeBar':False})
                            ])
                        ]),

                        dbc.Row([
                            dbc.Col([
                                dbc.Button("SELL"),
                            ]),

                            dbc.Col([
                                dbc.Button("BUY")
                            ])
                        ]),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label(id='low-price', children="12.237"),
                            ]),
                            dbc.Col([
                                dbc.Label(id='high-price', children="13.418"),
                            ])
                        ])
                    ]),
                ],
                style={"width": "24rem"},
                className="mt-3"
            )
        ], width=6)
    ], justify='center'),

    dcc.Interval(id='update', n_intervals=0, interval=1000*5)
])

# Indicator Graph
@app.callback(
    Output('indicator-graph', 'figure'),
    Input('update', 'n_intervals')
)
def update_graph(timer):
    dff_rv = dff.iloc[::-1]
    day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
    day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]

    fig = go.Figure(go.Indicator(
        mode="delta",
        value=day_end,
        delta={'reference': day_start, 'relative': True, 'valueformat':'.2%'}))
    fig.update_traces(delta_font={'size':12})
    fig.update_layout(height=30, width=70)

    if day_end >= day_start:
        fig.update_traces(delta_increasing_color='green')
    elif day_end < day_start:
        fig.update_traces(delta_decreasing_color='red')

    return fig


if __name__=='__main__':
    app.run_server(debug=True, port=3000)

 # https://youtu.be/iOkMaeU8dqE
