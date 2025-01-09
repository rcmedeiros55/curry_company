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
### Importando o dataset ###
df = pd.read_csv('train.csv')

df1 = df.copy()


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
####### Convertendo os tipos das colunas ###########

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

#Barra Lateral

st.header('Marketplace - Visão Restaurantes')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown('##### Coluna 1')
            #1. A quantidade de entregadores únicos.
            delivery_unique = df1['Delivery_person_ID'].nunique()
            col1.metric('Entr. Únicos', delivery_unique)

        with col2:
            st.markdown('##### Coluna 2')
            #2. A distância média dos resturantes e dos locais de entrega.
            
            col = ['Restaurant_latitude', 'Restaurant_longitude',    'Delivery_location_latitude','Delivery_location_longitude' ]
            
            df1['distance'] = df1.loc[:, col].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1 )
            avg_dist = round( df1['distance'].mean() , 2)
            st.metric('Distância Média', avg_dist)


        with col3:
            st.markdown('##### Coluna 3')
            #6. O tempo médio de entrega durantes os Festivais.
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} ).reset_index()
            
            
            df_aux.columns = ['Festival','avg_time', 'std_time']
            col3.metric('T_Médio (F)',round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'],2) )


        with col4:
            st.markdown('##### Coluna 4')
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} ).reset_index()
            
            
            df_aux.columns = ['Festival','avg_time', 'std_time']
            col4.metric('STD Médio (F)',round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'],2) )
            


        with col5:
            st.markdown('##### Coluna 5')
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} ).reset_index()
            
            
            df_aux.columns = ['Festival','avg_time', 'std_time']
            col5.metric('T_Médio (NF)',round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'],2) )



        with col6:
            st.markdown('##### Coluna 6')
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} ).reset_index()
            
            
            df_aux.columns = ['Festival','avg_time', 'std_time']
            col6.metric('STD Médio (NF)',round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'],2) )



        
    with st.container():
        st.markdown("""---""")
        st.title('Tempo Médio de Entrega Por Cidade')
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                                                 haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Restaurant_longitude']) ), axis =1 )

        avg_distance =  df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data = [ go.Pie( labels = avg_distance['City'], values = avg_distance['distance'], pull=[0, 0, 0.05])])
        st.plotly_chart(fig)
        
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')

        col1, col2 = st.columns(2)
        with col1:
            #3. O tempo médio e o desvio padrão de entrega por cidade.
            cols = ['City', 'Time_taken(min)']
            df_aux = df1.loc[:, cols].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']} ).reset_index()
            
            df_aux.columns = ['City', 'avg_time', 'std_time']
            fig = go.Figure()
            fig.add_trace( go.Bar ( name = 'Control', x = df_aux['City'], y = df_aux['avg_time'], error_y = dict( type = 'data', array = df_aux['std_time'])))
            fig.update_layout(barmode = 'group')
            st.plotly_chart(fig)


        
        with col2:
            st.markdown('##### Coluna 2')
            #4. O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.

            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']} ).reset_index()
            
            df_aux.columns = ['City', 'Road_traffic_density','avg_time', 'std_time']
            fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'avg_time',
                              color = 'std_time', color_continuous_scale = 'RdBu',
                              color_continuous_midpoint = np.average(df_aux['std_time'] ))
            st.plotly_chart(fig)

        
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição da Distância')

        cols = ['City', 'Time_taken(min)', 'Type_of_order']
        df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)': ['mean', 'std']} ).reset_index()
        
        df_aux.columns = ['Cidade', 'Tipo de Pedido','avg_time', 'std_time']
        st.dataframe(df_aux)
