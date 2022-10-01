import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

#タイトル
st.title('日本の賃金データダッシュボード')

#読み込み
df_jp_ind = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv',encoding = 'shift_jis')
df_jp_category = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv',encoding = 'shift_jis')
df_pref_ind = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv',encoding = 'shift_jis')

#ヘッダー
st.header('■2019年:一人あたり平均賃金のヒートマップ')

#読み込み
jp_lat_lon = pd.read_csv('./pref_lat_lon.csv')
#列名の変更
jp_lat_lon = jp_lat_lon.rename(columns = {'pref_name':'都道府県名'})

#'年齢計'と2019に集約
df_pref_map = df_pref_ind[(df_pref_ind['年齢'] == '年齢計') & (df_pref_ind['集計年'] == 2019)]
#'都道府県名'の列を基準に結合
df_pref_map = pd.merge(df_pref_map,jp_lat_lon,on = '都道府県名')

#'一人当たり賃金'の列を正規化した列を追加、最小値0、最大値1
df_pref_map['一人当たり賃金（相対値）'] = ((df_pref_map['一人当たり賃金（万円）'] - df_pref_map['一人当たり賃金（万円）'].min()) / (df_pref_map['一人当たり賃金（万円）'].max() - df_pref_map['一人当たり賃金（万円）'].min()))

#都庁所在地でViewの設定
view = pdk.ViewState(
    longitude = 139.691648,
    latitude = 35.689185,
    zoom = 4,
    pitch = 40.5,
)

#ヒートマップにする
layer = pdk.Layer(
    'HeatmapLayer',
    data = df_pref_map,
    opacity = 0.4,#不透明度
    get_position = ['lon','lat'],#経度、緯度
    threshold = 0.3,#閾値を決める
    get_weight = '一人当たり賃金（相対値）'#どの列を可視化するか
)

#レンダリング
layer_map = pdk.Deck(
    layers = layer,
    initial_view_state = view,
)

#表示
st.pydeck_chart(layer_map)

#チェックボックスで表示、非表示の切り替え
show_df = st.checkbox('Show DataFrame')
if show_df == True:
    st.write(df_pref_map)

#ヘッダー
st.header('■集計年別の一人あたり賃金（万円））の推移')

#列の要素が'年齢計'に該当するものだけに集約
df_ts_mean = df_jp_ind[(df_jp_ind['年齢'] == '年齢計')]
#列名の置き換え
df_ts_mean = df_ts_mean.rename(columns = {'一人当たり賃金（万円）':'全国_一人当たり賃金（万円）'})

#列の要素が'年齢計'に該当するものだけに集約
df_pref_mean = df_pref_ind[(df_pref_ind['年齢'] == '年齢計')]
#'都道府県名'の列のユニークデータを抽出
pref_list = df_pref_mean['都道府県名'].unique()
#都道府県名のセレクトボックス
option_pref = st.selectbox(
        '都道府県',
        (pref_list))
#セレクトボックスで選択された都道府県のデータを代入
df_pref_mean = df_pref_mean[(df_pref_mean['都道府県名'] == option_pref)]

#'集計年'の列を基準に結合
df_mean_line = pd.merge(df_ts_mean,df_pref_mean,on = '集計年')
#列を3つに絞る
df_mean_line = df_mean_line[['集計年','全国_一人当たり賃金（万円）','一人当たり賃金（万円）']]
#'集計年'の列をindexに変更
df_mean_line = df_mean_line.set_index('集計年')
#表示
st.line_chart(df_mean_line)

#ヘッダー
st.header('■年齢階級別の全国一人当たりの賃金（万円）')

#列の要素が'年齢計'に以外に該当するものだけに集約
df_mean_bubble = df_jp_ind[df_jp_ind['年齢'] != '年齢計']

#バブルチャートをアニメーション表示
fig = px.scatter(df_mean_bubble,
                 x = "一人当たり賃金（万円）",
                 y = "年間賞与その他特別給与額（万円）",
                 range_x = [150,700],
                 range_y = [0,150],
                 size = "所定内給与額（万円）",#バブルサイズ
                 size_max = 38,
                 color = "年齢",#色分けをする列
                 animation_frame = "集計年",#
                 animation_group = "年齢")

#streamlitで呼び出し
st.plotly_chart(fig)


#ヘッダー
st.header('■産業別の賃金推移')

#集計年でセレクトボックス化
year_list = df_jp_category['集計年'].unique()
option_year = st.selectbox(
    '集計年',
    (year_list))

#賃金の種類でセレクトボックス化
wage_list = ['一人当たり賃金（万円）','所定内給与額（万円）','年間賞与その他特別給与額（万円）']
option_wage = st.selectbox(
    '賃金の種類',
    (wage_list))

#条件抽出
df_mean_categ = df_jp_category[(df_jp_category['集計年'] == option_year)]

#賃金の種類によって最大値を取得
max_x = df_mean_categ[option_wage].max() + 50

#棒グラフを表示
fig = px.bar(df_mean_categ,
                 x = option_wage,
                 y = '産業大分類名',
                 range_x = [0,max_x],
                 color = '産業大分類名',
                 animation_frame = '年齢',
                 orientation = 'h',#横棒グラフで表示
                 width = 800,
                 height = 500)


#streamlitで呼び出し
st.plotly_chart(fig)

#データの出典元を記載
st.text('出典:RESAS（地域経済分析システム）')
st.text('本結果はRESAS（地域経済分析システム）を加工して作成')

