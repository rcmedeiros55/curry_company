
### Bibliotecas ###
from datetime import datetime
from haversine import haversine
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image #import PIL.Image as imgpil
import folium
from streamlit_folium import folium_static

######## FUNÇÕES #############

def clean_code(df1):
    '''
    Esta função tem a responsabilidade de limpar o dataframe

    Tipos de limpeza: 
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

    Input: Dataframe
    Output: Dataframe
    
    '''
    
    #Excluindo as linhas nulas
    linhasSelecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhasSelecionadas, :].copy()
    ###### Convertendo os tipos das colunas ##########
    
    #convertendo 'Delivery_person_Age' para int
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    #convertendo 'Delivery_person_Ratings' para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    #convertendo 'Order_Date' para Datetime
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')
    
    #convertendo 'multiple_deliveries' para int
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
        
    #### Resetando os índices ####
    df1 = df1.reset_index(drop = True) ##Drop = True; para não criar coluna adicional
    
    #### Removendo os espaços das strings ####
    #for i in range( len(df1) ):
    #    df1.loc[i,'ID'] = df1.loc[i, 'ID'].strip()
    #    df1.loc[i, 'Delivery_person_ID'] = df1.loc[i, 'Delivery_person_ID'].strip()
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    #### Limpando a coluna time taken ####
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1


def order_metric(df1):
    
    #order metric
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    #df_aux
    #desenhar o gráfico de linhas
    #matplotlib
    #Seaborn
    #Bokeh
    #Plotly
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID' )
    return fig

def traffic_order_share(df1):
    
    #3. Distribuição dos pedidos por tipo de tráfego.
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()
    df_aux['entregas_perc'] = round(df_aux['entregas_perc']*100, 2)
    #df_aux.head()
    fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
    return fig

def traffic_order_city(df1):
    df_aux = df1.loc[: , ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig


def order_by_week(df1):
    #criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig

def order_share_by_week(df1):
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    
    df_aux = pd.merge(df_aux01, df_aux02, how = 'inner')
    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    fig = px.line (df_aux, x='week_of_year', y = 'order_by_deliver')
    return fig

def country_maps(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                     popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
    
        
    folium_static( map, width = 1024 , height = 600 )
    return None

#-------------INÍCIO DA ESTUTURA DO CÓDIGO----------------


### Import dataset ###
df = pd.read_csv('train.csv')

### Limpando os dados ###
df1 = clean_code(df)


#Barra Lateral


st.header('Marketplace - Visão Entregadores')

image_path = 'logoCDS.png'
image = Image.open( image_path )
st.sidebar.image( image, width = 150 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )
date_slider = st.sidebar.slider(
    'Até qual valor',
    value = datetime(2022, 4, 13 ),
    min_value = datetime(2022, 2 , 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY' )

#st.header(date_slider)
st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
        'Quais as condições de trânsito?',
        ['Low', 'Medium', 'High', 'Jam'],
        default = ['Low', 'Medium', 'High', 'Jam']
        )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )


#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


#filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#Layout no Streamlit


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'] ) 

with tab1:
    with st.container():
        
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        
        with col1:
            #A menor e maior idade dos entregadores.
            
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)

        with col2:
            
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)

        with col3:
            #2. A pior e a melhor condição de veículos.
            
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_condicao)
            

        with col4:
            
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação Média Por Entregador')
            #3. A avaliação média por entregador.
            avg_ratings_per_deliver = round( df1[['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index() , 2)
            st.dataframe(avg_ratings_per_deliver)

        with col2:
            st.markdown('##### Avaliação Média Por Trânsito')
            #4. A avaliação média e o desvio padrão por tipo de tráfego.
            
            avg_std_rating_by_traffic = df1[['Delivery_person_Ratings', 'Road_traffic_density']].groupby(['Road_traffic_density']).agg(['mean', 'std']).reset_index()
            avg_std_rating_by_traffic.columns = ['Condição', 'Média', 'StD']
            st.dataframe(avg_std_rating_by_traffic)
            
            
            st.markdown('##### Avaliação Média Por Clima')
            #5. A avaliação média e o desvio padrão por condições climáticas.
            mean_std = round(df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(['Weatherconditions']).agg(['mean', 'std']).reset_index(), 2)
            mean_std.columns = ['Condições Climáticas', 'Média', 'Desv. Padrão']
            st.dataframe(mean_std)
    
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top Entregadores Mais Rápidos' )
            #6. Os 10 entregadores mais rápidos por cidade.
            df2 = (df1.loc[df1['City'] != 'NaN', ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID'])
                   .min()
                   .sort_values(['City', 'Time_taken(min)'])
                   .reset_index() )
            
            aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
            aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            
            df3 = pd.concat([aux1, aux2, aux3])
            df3.reset_index()
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top Entregadores Mais Lentos' )
            #7. Os 10 entregadores mais lentos por cidade.

            df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).max()
                      .sort_values(['City', 'Time_taken(min)'], ascending = False)
                      .reset_index() )
            
            aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
            aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            
            df3 = pd.concat([aux1, aux2, aux3])
            df3.reset_index()

            st.dataframe(df3)

