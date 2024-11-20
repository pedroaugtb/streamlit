import streamlit as st
import json
import os
import plotly.graph_objects as go
import pandas as pd
import glob
import plotly.express as px
import numpy as np

# Configuração da página
st.set_page_config(page_title="Trabalho de Algoritmos II - Compressão e Descompressão LZW", layout="wide")

# Título da Aplicação
st.title("Trabalho de Algoritmos II - Compressão e Descompressão LZW")

# Introdução
st.markdown("""
Este relatório apresenta os resultados dos testes de funcionamento e desempenho do método de compressão LZW para tamanho fixo e variado. Foram utilizados diferentes tipos de dados, incluindo arquivos de texto, imagens em bitmap e outros formatos de entrada não comprimidos, para avaliar a eficácia do algoritmo. A seguir, são detalhadas as análises e os gráficos gerados a partir dos testes realizados.
""")

# Função para carregar estatísticas de múltiplos arquivos na pasta 'stats'
def load_all_stats(directory):
    stats_list = []
    if not os.path.exists(directory):
        st.warning(f"O diretório {directory} não foi encontrado.")
        return stats_list
    files = glob.glob(os.path.join(directory, '*.json'))
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                stats = json.load(f)
                stats['file_name'] = os.path.basename(file_path)
                stats_list.append(stats)
        except json.JSONDecodeError:
            st.error(f"Erro ao decodificar o arquivo {file_path}.")
    return stats_list   

# Mapeamento de nomes de arquivos para tipos de texto com classificação de tamanho
file_type_mapping = {
    'input.txt': {'description': 'Enunciado TP', 'size_type': 'fixed'},
    'input2.txt': {'description': 'História Aleatória', 'size_type': 'fixed'},
    'input3.txt': {'description': 'Bits Aleatórios', 'size_type': 'fixed'},
    'input.pdf' : {'description': 'PDF', 'size_type': 'variable'},
    'input_image.bmp': {'description': 'Imagem Bitmap', 'size_type': 'variable'}  # Exemplo adicional para imagens
}

# Mapeamento de arquivos de estatísticas para inputs
stats_file_mapping = {
    'compression_stats.json': 'input.txt',
    'compression_stats2.json': 'input2.txt',
    'compression_stats3.json': 'input3.txt',
    'compression_stats4.json' : 'input.pdf',
    'compression_stats5.json' : 'input_image.bmp',  # Adicionado para imagem
    'decompression_stats.json': 'input.txt',
    'decompression_stats2.json': 'input2.txt',
    'decompression_stats3.json': 'input3.txt',
    'decompression_stats4.json' : 'input.pdf',
    'decompression_stats5.json' : 'input_image.bmp'   # Adicionado para imagem
}

# Carregar todas as estatísticas de compressão e descompressão da pasta 'stats'
all_stats = load_all_stats('stats')

# Atualizar os nomes dos arquivos com base nos mapeamentos e classificar por tamanho
for stats in all_stats:
    stats_file_name = stats.get('file_name', '')
    associated_input = stats_file_mapping.get(stats_file_name)
    if associated_input:
        stats['input_file'] = associated_input
        type_info = file_type_mapping.get(associated_input, {})
        stats['file_type'] = type_info.get('description')
        stats['size_type'] = type_info.get('size_type')
    else:
        stats['input_file'] = None
        stats['file_type'] = None
        stats['size_type'] = None

# Filtrar para incluir apenas os tipos desejados
desired_types = ['Enunciado TP', 'História Aleatória', 'Bits Aleatórios', 'PDF', 'Imagem Bitmap']
all_stats = [stats for stats in all_stats if stats.get('file_type') in desired_types]

# Separar os dados em tamanho fixo e variável
fixed_stats = [stats for stats in all_stats if stats.get('size_type') == 'fixed']
variable_stats = [stats for stats in all_stats if stats.get('size_type') == 'variable']

# Funções de plotagem
def plot_compression_ratio(stats_subset):
    data = []
    for stats in stats_subset:
        if ('compression_ratio' in stats and 'original_size_bytes' in stats and 'compressed_size_bytes' in stats):
            data.append({
                'Tipo do Texto': stats.get('file_type'),
                'Original (bytes)': stats['original_size_bytes'],
                'Comprimido (bytes)': stats['compressed_size_bytes'],
                'Razão de Compressão': stats['compression_ratio']
            })
    if data:
        df = pd.DataFrame(data)
        fig = go.Figure(data=[
            go.Bar(name='Original', x=df['Tipo do Texto'], y=df['Original (bytes)']),
            go.Bar(name='Comprimido', x=df['Tipo do Texto'], y=df['Comprimido (bytes)'])
        ])
        fig.update_layout(
            barmode='group',
            title='Razão de Compressão para Diferentes Arquivos',
            yaxis_title='Tamanho (bytes)',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para gerar o gráfico.")

def plot_compression_dictionary_growth(stats_subset):
    fig = go.Figure()
    for stats in stats_subset:
        if 'dictionary_size_over_time' in stats and stats['dictionary_size_over_time']:
            df = pd.DataFrame({
                'Número de Códigos': range(1, len(stats['dictionary_size_over_time']) + 1),
                'Tamanho do Dicionário': stats['dictionary_size_over_time']
            })
            fig.add_trace(go.Scatter(
                x=df['Número de Códigos'],
                y=df['Tamanho do Dicionário'],
                mode='lines+markers',
                name=f"{stats.get('file_type')}"
            ))

    fig.update_layout(
        title='Crescimento do Dicionário ao Longo do Tempo (Compressão)',
        xaxis_title='Número de Códigos',
        yaxis_title='Tamanho do Dicionário',
        template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_execution_time(stats_subset, operation='compression'):
    data = []
    for stats in stats_subset:
        key = 'execution_time_seconds'
        if operation == 'decompression':
            key = 'decompression_time_seconds'
        if key in stats:
            data.append({
                'Tipo do Texto': stats.get('file_type'),
                'Tempo de Execução (s)': stats[key]
            })
    if data:
        df = pd.DataFrame(data)
        fig = go.Figure(data=[
            go.Bar(x=df['Tipo do Texto'], y=df['Tempo de Execução (s)'])
        ])
        fig.update_layout(
            title=f'Tempo de Execução para {operation.capitalize()} Diferentes Arquivos',
            yaxis_title='Tempo (segundos)',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para gerar o gráfico.")

def plot_dictionary_size_over_time(stats_subset):
    fig = go.Figure()
    for stats in stats_subset:
        if 'dictionary_size_over_time' in stats and stats['dictionary_size_over_time']:
            df = pd.DataFrame({
                'Número de Códigos': range(1, len(stats['dictionary_size_over_time']) + 1),
                'Tamanho do Dicionário': stats['dictionary_size_over_time']
            })
            fig.add_trace(go.Scatter(
                x=df['Número de Códigos'],
                y=df['Tamanho do Dicionário'],
                mode='lines+markers',
                name=f"{stats.get('file_type')}"
            ))

    fig.update_layout(
        title='Tamanho do Dicionário ao Longo do Tempo',
        xaxis_title='Número de Códigos',
        yaxis_title='Tamanho do Dicionário',
        template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_compression_heatmap(stats_subset):
    data = []
    for stats in stats_subset:
        if 'compression_ratio' in stats and 'compressed_size_bytes' in stats:
            data.append({
                'Tipo do Texto': stats.get('file_type'),
                'Tamanho Comprimido (bytes)': stats['compressed_size_bytes'],
                'Razão de Compressão': stats['compression_ratio']
            })
    if data:
        df = pd.DataFrame(data)
        pivot_table = df.pivot_table(
            index='Tipo do Texto',
            values='Tamanho Comprimido (bytes)',
            aggfunc='mean'
        ).reset_index()

        fig = px.imshow(
            [pivot_table['Tamanho Comprimido (bytes)']],
            labels=dict(x="Tipo do Texto", y="", color="Tamanho Comprimido (bytes)"),
            x=pivot_table['Tipo do Texto'],
            y=[''],
            color_continuous_scale='Viridis',
            aspect="auto",
            text_auto=True
        )
        fig.update_layout(
            title='Heatmap do Tamanho Comprimido dos Arquivos',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para gerar o heatmap.")

# Seções para Tamanho Fixo
st.header("Dados de Tamanho Fixo")

# Seção 1: Razão de Compressão (Tamanho Fixo)
st.subheader("Razão de Compressão")
st.markdown("""
A razão de compressão indica a eficiência do algoritmo LZW em reduzir o tamanho dos arquivos de tamanho fixo. Abaixo, podemos observar a comparação entre o tamanho original e o tamanho comprimido para diferentes tipos de arquivos.
""")
plot_compression_ratio(fixed_stats)

# Seção 2: Crescimento do Dicionário durante a Compressão (Tamanho Fixo)
st.subheader("Crescimento do Dicionário durante a Compressão")
st.markdown("""
Durante o processo de compressão, o tamanho do dicionário cresce à medida que novos padrões são adicionados. O gráfico a seguir mostra como o dicionário se desenvolve ao longo do tempo para diferentes tipos de arquivos de tamanho fixo.
""")
plot_compression_dictionary_growth(fixed_stats)

# # Seção 3: Tempo de Execução da Compressão (Tamanho Fixo)
# st.subheader("Tempo de Execução da Compressão")
# st.markdown("""
# O tempo de execução é um fator crucial na avaliação de algoritmos de compressão. A seguir, apresentamos o tempo necessário para comprimir diferentes tipos de arquivos de tamanho fixo.
# """)
# plot_execution_time(fixed_stats, operation='compression')

# Seção 4: Tamanho do Dicionário ao Longo do Tempo (Tamanho Fixo)
st.subheader("Tamanho do Dicionário ao Longo do Tempo")
st.markdown("""
Este gráfico detalha o crescimento do dicionário ao longo do processo de compressão, fornecendo uma visão mais detalhada de como o algoritmo LZW gerencia os padrões encontrados em arquivos de tamanho fixo.
""")
plot_dictionary_size_over_time(fixed_stats)

# Seção 5: Heatmap do Tamanho Comprimido (Tamanho Fixo)
st.subheader("Heatmap do Tamanho Comprimido")
st.markdown("""
O heatmap abaixo ilustra visualmente o tamanho comprimido dos arquivos de tamanho fixo, permitindo uma comparação rápida e intuitiva entre os diferentes tipos de dados.
""")
plot_compression_heatmap(fixed_stats)  

# Seção 6: Tempo de Execução da Descompressão (Tamanho Fixo)
st.subheader("Tempo de Execução da Descompressão")
st.markdown("""
Além da compressão, o tempo necessário para descomprimir os arquivos de tamanho fixo também é analisado. Isso é essencial para entender a eficiência total do algoritmo.
""")
plot_execution_time(fixed_stats, operation='decompression')    

# Seções para Tamanho Variável
st.header("Dados de Tamanho Variável")

# Seção 1: Razão de Compressão (Tamanho Variável)
st.subheader("Razão de Compressão")
st.markdown("""
A razão de compressão indica a eficiência do algoritmo LZW em reduzir o tamanho dos arquivos de tamanho variável. Abaixo, podemos observar a comparação entre o tamanho original e o tamanho comprimido para diferentes tipos de arquivos.
""")
plot_compression_ratio(variable_stats)

# Seção 2: Crescimento do Dicionário durante a Compressão (Tamanho Variável)
st.subheader("Crescimento do Dicionário durante a Compressão")
st.markdown("""
Durante o processo de compressão, o tamanho do dicionário cresce à medida que novos padrões são adicionados. O gráfico a seguir mostra como o dicionário se desenvolve ao longo do tempo para diferentes tipos de arquivos de tamanho variável.
""")
plot_compression_dictionary_growth(variable_stats)

# Seção 3: Tempo de Execução da Compressão (Tamanho Variável)
st.subheader("Tempo de Execução da Compressão")
st.markdown("""
O tempo de execução é um fator crucial na avaliação de algoritmos de compressão. A seguir, apresentamos o tempo necessário para comprimir diferentes tipos de arquivos de tamanho variável.
""")
plot_execution_time(variable_stats, operation='compression')

# Seção 4: Tamanho do Dicionário ao Longo do Tempo (Tamanho Variável)
st.subheader("Tamanho do Dicionário ao Longo do Tempo")
st.markdown("""
Este gráfico detalha o crescimento do dicionário ao longo do processo de compressão, fornecendo uma visão mais detalhada de como o algoritmo LZW gerencia os padrões encontrados em arquivos de tamanho variável.
""")
plot_dictionary_size_over_time(variable_stats)

# Seção 5: Heatmap do Tamanho Comprimido (Tamanho Variável)
st.subheader("Heatmap do Tamanho Comprimido")
st.markdown("""
O heatmap abaixo ilustra visualmente o tamanho comprimido dos arquivos de tamanho variável, permitindo uma comparação rápida e intuitiva entre os diferentes tipos de dados.
""")
plot_compression_heatmap(variable_stats)

# Seção 6: Tempo de Execução da Descompressão (Tamanho Variável)
st.subheader("Tempo de Execução da Descompressão")
st.markdown("""
Além da compressão, o tempo necessário para descomprimir os arquivos de tamanho variável também é analisado. Isso é essencial para entender a eficiência total do algoritmo.
""")
plot_execution_time(variable_stats, operation='decompression')

# Seção 7: Exemplos de Compressão e Descompressão de Texto
st.header("Exemplos de Compressão e Descompressão de Texto")
st.markdown("""
A seguir, apresentamos exemplos práticos de como o algoritmo LZW realiza a compressão e descompressão de arquivos de texto.

**Exemplo 1: Compressão**
- **Texto Original**: "ABABABA"
- **Texto Comprimido**: [65, 66, 256, 258, 260]

**Exemplo 2: Descompressão**
- **Texto Comprimido**: [65, 66, 256, 258, 260]
- **Texto Descomprimido**: "ABABABA"

Estes exemplos demonstram a capacidade do LZW em identificar e reutilizar padrões repetitivos para reduzir o tamanho do arquivo.
""")

# Seção 8: Análise dos Resultados
st.header("Análise dos Resultados")
st.markdown("""
Os resultados obtidos mostram que o algoritmo LZW é eficaz na compressão de diferentes tipos de dados, especialmente aqueles que contêm padrões repetitivos, como arquivos de texto. As imagens bitmap, embora não tão eficientes quanto os textos, ainda apresentam uma redução significativa no tamanho.

O tempo de execução da compressão e descompressão varia conforme o tipo de arquivo, sendo mais rápido para arquivos menores e com menos complexidade. O crescimento do dicionário durante a compressão é linear para textos simples, mas pode variar para formatos mais complexos.

Em geral, o LZW demonstra um bom equilíbrio entre eficiência de compressão e tempo de execução, tornando-o uma escolha adequada para diversas aplicações.
""")

# Seção 9: Dados Brutos (opcional)
st.header("Dados Brutos")
st.markdown("""
Abaixo, são apresentados os dados brutos utilizados para gerar os gráficos. Estes dados contêm informações detalhadas sobre cada teste realizado.
""")
if st.checkbox("Mostrar Dados Brutos"):
    st.subheader("Dados de Tamanho Fixo")
    for stats in fixed_stats:
        st.subheader(f"Dados Brutos para {stats.get('file_type')}")
        st.json(stats)
    
    st.subheader("Dados de Tamanho Variável")
    for stats in variable_stats:
        st.subheader(f"Dados Brutos para {stats.get('file_type')}")
        st.json(stats)
