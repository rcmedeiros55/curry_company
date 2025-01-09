import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = 'Home',
    page_icon = '\o/'
)

image = Image.open('logoCDS.png')


st.sidebar.image( image, width = 150)

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write('# Curry Company Growth Dashboard')
st.markdown (
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
    
            -Visão Gerencial: Métrcas gerais de comportamento.
        
            -Visão Tática: Indicadores Semanais de Crescimento.
        
            -Visão Geográfica: Insights de Geolocalização.
        
    - Visão Entregador:
    
        -Acompanhamento dos Indicadores Semanais de Crescimento.
        
    - Visão Restaurante:
    
        -Indicadores semanais de crescimento dos restaurantes.
      
     
          
    """
)

