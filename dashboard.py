import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Moléculas ILAR",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Dashboard de Moléculas ILAR")
st.markdown("---")

# Función para cargar datos
@st.cache_data
def load_data():
    # Reemplaza esta ruta con la ruta a tu archivo Excel
    df = pd.read_excel('Version final Extracto base de datos Mar 2023.xlsx', sheet_name='Base en inglés')
    return df

# Cargar datos
try:
    df = load_data()
    
    # Sidebar para filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de molécula con búsqueda
    molecules = sorted(df['Molecule'].unique())
    selected_molecule = st.sidebar.selectbox(
        "Selecciona una molécula:",
        options=["Todas las moléculas"] + molecules,
        help="Busca y selecciona una molécula específica"
    )
    
    # Filtrar datos por molécula si se seleccionó una específica
    if selected_molecule != "Todas las moléculas":
        filtered_df = df[df['Molecule'] == selected_molecule]
    else:
        filtered_df = df
    
    # Filtro de países
    countries = sorted(filtered_df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Selecciona países:",
        options=countries,
        default=[],  # Sin países seleccionados por defecto
        help="Selecciona uno o más países para analizar (vacío = todos los países)"
    )
    
    # Aplicar filtro de países
    if selected_countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]
    
    # Filtro adicional por tipo RX/OTC
    rx_otc_options = filtered_df['RX-OTC - Molecule'].unique()
    selected_rx_otc = st.sidebar.multiselect(
        "Tipo de medicamento:",
        options=rx_otc_options,
        default=rx_otc_options,
        help="Filtra por tipo de medicamento (RX o OTC)"
    )
    
    if selected_rx_otc:
        filtered_df = filtered_df[filtered_df['RX-OTC - Molecule'].isin(selected_rx_otc)]
    
    # Mostrar información general
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de registros", len(filtered_df))
    
    with col2:
        st.metric("Países únicos", filtered_df['Country'].nunique())
    
    with col3:
        st.metric("Moléculas únicas", filtered_df['Molecule'].nunique())
    
    st.markdown("---")
    
    # Crear tabs para diferentes visualizaciones
    tab1, tab2 = st.tabs(["📋 Datos", "📊 Análisis por País"])
    
    with tab1:
        st.header("Datos Filtrados")
        
        # Mostrar el dataframe filtrado
        st.write(f"Mostrando {len(filtered_df)} registros:")
        
        # Selectbox para elegir qué columnas mostrar
        all_columns = filtered_df.columns.tolist()
        selected_columns = st.multiselect(
            "Selecciona columnas a mostrar:",
            options=all_columns,
            default=['Molecule', 'Switch Year', 'Country', 'RX-OTC - Molecule', 'Strength']
        )
        
        if selected_columns:
            display_df = filtered_df[selected_columns]
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Selecciona al menos una columna para mostrar los datos.")
    
    with tab2:
        st.header("Análisis por País")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras - Moléculas por país
            country_molecules = filtered_df.groupby('Country')['Molecule'].nunique().sort_values(ascending=False).head(15)
            fig_bar = px.bar(
                x=country_molecules.index,
                y=country_molecules.values,
                title="Número de moléculas por país",
                labels={'x': 'País', 'y': 'Número de moléculas'},
                color=country_molecules.values,
                color_continuous_scale="viridis"
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Gráfico de pie - Distribución RX vs OTC
            rx_otc_counts = filtered_df['RX-OTC - Molecule'].value_counts()
            fig_pie = px.pie(
                values=rx_otc_counts.values,
                names=rx_otc_counts.index,
                title="Distribución RX vs OTC"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ No se pudo encontrar el archivo Excel. Por favor, asegúrate de que el archivo 'Version final Extracto base de datos Mar 2023.xlsx' esté en el mismo directorio que este script.")
    st.info("Puedes subir el archivo usando el widget de carga de archivos de Streamlit o ajustar la ruta en el código.")
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.info("Verifica que el archivo Excel tenga el formato correcto y que la hoja 'Base en inglés' exista.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Usa los filtros en la barra lateral para explorar diferentes aspectos de los datos.")