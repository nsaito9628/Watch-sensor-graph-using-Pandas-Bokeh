# coding: utf-8
import datetime
import os
import datetime
import pandas as pd
import pandas_bokeh
import boto3
from boto3.dynamodb.conditions import Key, Attr
  

#環境変数の読み込み
TABLE_NAME = []
TITLES = []
num_tables = int(os.environ["NUM_TABLES"])   
for i in range(num_tables):
    table = 'TABLE_NAME' + str(i+1)
    title = 'TITLE' + str(i+1)
    TABLE_NAME.append(str(os.environ[table]))
    TITLES.append(os.environ[title]) 
#logger.info(TABLE_NAME)
#logger.info(TITLES)
GRAPH_RANGE = int(os.environ['GRAPH_RANGE'])
DATA_SPAN = int(os.environ['DATA_SPAN'])
No_of_Days = int(os.environ['NUM_DAYS'])


# ③DynamoDBオブジェクトを取得
dynamodb = boto3.resource('dynamodb')

#Tableのkeyを取得
def get_keys(table_name):

    table = dynamodb.Table(table_name)

    response = table.scan(Limit=1, ReturnConsumedCapacity='TOTAL')
    ITEM = response['Items']

    keys = []
    for key in list(ITEM[0]):
        if key == "Timestamp":
            keys.append(key)     
    for key in list(ITEM[0]):
        if key == "DeleteTime":
            keys.append(key)
    for key in list(ITEM[0]):
        if "Time" not in key:
            keys.append(key)

    return keys


def get_table(keys, Limit_No, table_name):

    table = dynamodb.Table(table_name)

    items = []
    response = table.scan(Limit=Limit_No, ReturnConsumedCapacity='TOTAL')
    items = response['Items']
    print(Limit_No)
    print(items)

    if items ==[]:
        dummy = {}
        for key in keys:
            if "Time" in key:
                dummy[key] = int((datetime.datetime.now()).timstamp())
            else:
                dummy[key] = 0
        items.append(dummy)

    return items


def conv_df(keys, items):

    COLUMNS = [key for key in keys]
    df = pd.DataFrame(items, columns=COLUMNS)

    for key in keys:
        try:
            if "Time" in key:
                df[key] = df[key].astype(int)
            else:
                df[key] = df[key].astype(float)
        except ValueError:
            continue

    #Timestampをdatetime変換してtz=JSTを付与
    df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
    df = df.sort_values('datetime').reset_index(drop=True)
    df = df.set_index('datetime')
    df.index = df.index.tz_localize('UTC').tz_convert('Asia/Tokyo')
    df.index = df.index.tz_localize(None)
    df = df.reset_index()
    #表示に使わない要素をdrop
    df = df.drop('Timestamp', axis=1)
    df = df.drop('DeleteTime', axis=1)

    return df


def draw_chart(DFS, TITLES, GRAPH_START_TIMESTAMP, GRAPH_END_TIMESTAMP):
    #グラフの出力先
    pandas_bokeh.output_file("/tmp/index.html", "My Room Watcher")
    #dfごとの描画を保存するlist
    plt = [] 
    #dfごとに描画
    plt = [DF.plot_bokeh.line(
            x="datetime",
            stacked=False,
            #colormap=["green", "red", "orange", "yellow"],
            title=TITLE,
            #ylabel="",
            #xlabel="",
            xlim=(GRAPH_START_TIMESTAMP, GRAPH_END_TIMESTAMP),
            figsize=(1000,450),
            show_figure=False)
            for DF, TITLE in zip(DFS, TITLES)]

    N_DFS = len(DFS)
    if N_DFS == 1:
        pandas_bokeh.plot_grid([[plt[0]]], 
                            plot_width=900)
    elif N_DFS == 2:
        pandas_bokeh.plot_grid([[plt[0], plt[1]]], 
                            plot_width=900)
    elif N_DFS == 3:
        pandas_bokeh.plot_grid([[plt[0], plt[1]],
                                [plt[2]]], 
                            plot_width=900)
    elif N_DFS == 4:
        pandas_bokeh.plot_grid([[plt[0], plt[1]],
                                [plt[2], plt[3]]], 
                            plot_width=900)


# ④Lambdaのメイン関数
def lambda_handler(event, context):

    #Bokehで描画するグラフのx軸の視点と終点
    now = datetime.datetime.now()
    g_start_td = now - datetime.timedelta(hours=GRAPH_RANGE)
    GRAPH_START_TIMESTAMP = (g_start_td + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
    GRAPH_END_TIMESTAMP = (now + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')

    Limit_No = int(1440 / 10 * No_of_Days)

    KEYS = [get_keys(table_name) for table_name in TABLE_NAME]
    ITEMS = [get_table(key, Limit_No, table_name) for key, table_name in zip(KEYS, TABLE_NAME)]
    DFS = [conv_df(keys, items) for keys, items in zip(KEYS, ITEMS)] 
    
    draw_chart(DFS, TITLES, GRAPH_START_TIMESTAMP, GRAPH_END_TIMESTAMP)


    with open('/tmp/index.html' , encoding='utf-8') as f:
        html = f.read()
    #api gareway経由でhtmlをbodyにしてresponseを返す
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': html}