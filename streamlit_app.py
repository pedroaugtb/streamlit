import streamlit as st
import json
import os
import plotly.graph_objects as go
import pandas as pd
import glob
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Trabalho de Algoritmos II - Compressão e Descompressão LZW", layout="wide")

# Título da Aplicação
st.title("Trabalho de Algoritmos II - Compressão e Descompressão LZW")

# Introdução
st.markdown("""
Este relatório apresenta os resultados dos testes de funcionamento e desempenho do método de compressão LZW para diferentes tipos de arquivos. Foram utilizados arquivos de texto (.txt), arquivos CSV (.csv), imagens bitmap (.bmp) e arquivos de log (.log) para avaliar a eficácia do algoritmo. A seguir, são detalhadas as análises e os gráficos gerados a partir dos testes realizados.
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

# Mapeamento de nomes de arquivos para tipos de dados
file_type_mapping = {
    'input.txt': 'Arquivo TXT',
    'input.csv': 'Arquivo CSV',
    'input.bmp': 'Imagem BMP',
    'input.log': 'Arquivo LOG'
}

# Mapeamento de arquivos de estatísticas para inputs
stats_file_mapping = {
    'compression_stats.json': 'input.txt',
    'compression_stats2.json': 'input.csv',
    'compression_stats3.json': 'input.bmp',
    'compression_stats4.json': 'input.log',
    'decompression_stats.json': 'input.txt',
    'decompression_stats2.json': 'input.csv',
    'decompression_stats3.json': 'input.bmp',
    'decompression_stats4.json': 'input.log'
}

# Carregar todas as estatísticas de compressão e descompressão da pasta 'stats'
all_stats = load_all_stats('stats')

# Atualizar os nomes dos arquivos com base nos mapeamentos e identificar a operação
for stats in all_stats:
    stats_file_name = stats.get('file_name', '')
    associated_input = stats_file_mapping.get(stats_file_name)
    if associated_input:
        stats['input_file'] = associated_input
        stats['file_type'] = file_type_mapping.get(associated_input, 'Desconhecido')
        # Identificar a operação com base no nome do arquivo de estatísticas
        if 'compression' in stats_file_name:
            stats['operation'] = 'Compressão'
        elif 'decompression' in stats_file_name:
            stats['operation'] = 'Descompressão'
        else:
            stats['operation'] = 'Desconhecida'
    else:
        stats['input_file'] = None
        stats['file_type'] = 'Desconhecido'
        stats['operation'] = 'Desconhecida'

# Filtrar para incluir apenas os tipos desejados e operações conhecidas
desired_types = ['Arquivo TXT', 'Arquivo CSV', 'Imagem BMP', 'Arquivo LOG']
desired_operations = ['Compressão', 'Descompressão']
all_stats = [stats for stats in all_stats if stats.get('file_type') in desired_types and stats.get('operation') in desired_operations]

# Funções de plotagem
def plot_compression_ratio(stats_subset):
    data = []
    for stats in stats_subset:
        if ('compression_ratio' in stats and 
            'original_size_bytes' in stats and 
            'compressed_size_bytes' in stats and 
            stats['operation'] == 'Compressão'):
            data.append({
                'Tipo de Arquivo': stats.get('file_type'),
                'Original (bytes)': stats['original_size_bytes'],
                'Comprimido (bytes)': stats['compressed_size_bytes'],
                'Razão de Compressão': stats['compression_ratio']
            })
    if data:
        df = pd.DataFrame(data)
        fig = go.Figure(data=[
            go.Bar(name='Original', x=df['Tipo de Arquivo'], y=df['Original (bytes)']),
            go.Bar(name='Comprimido', x=df['Tipo de Arquivo'], y=df['Comprimido (bytes)'])
        ])
        fig.update_layout(
            barmode='group',
            title='Razão de Compressão para Diferentes Arquivos',
            yaxis_title='Tamanho (bytes)',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para gerar o gráfico de Razão de Compressão.")

def plot_execution_time_compression(stats_subset):
    data = []
    for stats in stats_subset:
        if 'execution_time_seconds' in stats and stats['operation'] == 'Compressão':
            data.append({
                'Tipo de Arquivo': stats.get('file_type'),
                'Tempo de Compressão (s)': stats['execution_time_seconds']
            })
    if data:
        df = pd.DataFrame(data)
        fig = go.Figure(data=[
            go.Bar(x=df['Tipo de Arquivo'], y=df['Tempo de Compressão (s)'], name='Compressão')
        ])
        fig.update_layout(
            title='Tempo de Execução da Compressão',
            yaxis_title='Tempo (segundos)',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para gerar o gráfico de Tempo de Execução da Compressão.")

def plot_compression_heatmap(stats_subset):
    data = []
    for stats in stats_subset:
        if ('compression_ratio' in stats and 
            'compressed_size_bytes' in stats and 
            stats['operation'] == 'Compressão'):
            data.append({
                'Tipo de Arquivo': stats.get('file_type'),
                'Tamanho Comprimido (bytes)': stats['compressed_size_bytes'],
                'Razão de Compressão': stats['compression_ratio']
            })
    if data:
        df = pd.DataFrame(data)
        pivot_table = df.pivot_table(
            index='Tipo de Arquivo',
            values='Tamanho Comprimido (bytes)',
            aggfunc='mean'
        ).reset_index()

        fig = px.imshow(
            [pivot_table['Tamanho Comprimido (bytes)']],
            labels=dict(x="Tipo de Arquivo", y="", color="Tamanho Comprimido (bytes)"),
            x=pivot_table['Tipo de Arquivo'],
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

def plot_dictionary_statistics(stats_subset):
    data = []
    for stats in stats_subset:
        if 'dictionary_size_over_time' in stats and stats['dictionary_size_over_time']:
            data.append({
                'Tipo de Arquivo': stats.get('file_type'),
                'Operação': stats['operation'],
                'Espaço em Memória (bytes)': stats.get('peak_memory_usage_bytes', 0)
            })
    if data:
        df = pd.DataFrame(data)
        fig = go.Figure()

        # Gráfico para Espaço em Memória
        fig.add_trace(go.Bar(
            x=df['Tipo de Arquivo'] + " - " + df['Operação'],
            y=df['Espaço em Memória (bytes)'],
            name='Espaço em Memória (bytes)'
        ))

        fig.update_layout(
            barmode='group',
            title='Estatísticas do Dicionário',
            yaxis_title='Espaço em Memória (bytes)',
            xaxis_title='Tipo de Arquivo e Operação',
            template='plotly_dark',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para gerar o gráfico de Estatísticas do Dicionário.")

# Seção de Resultados
st.header("Resultados")

# Seção: Razão de Compressão
st.subheader("Razão de Compressão")
st.markdown("""
A razão de compressão indica a eficiência do algoritmo LZW em reduzir o tamanho dos diferentes tipos de arquivos. Abaixo, podemos observar a comparação entre o tamanho original e o tamanho comprimido para cada tipo de arquivo.
""")
plot_compression_ratio(all_stats)

# Seção: Tempo de Execução da Compressão
st.subheader("Tempo de Execução da Compressão")
st.markdown("""
O tempo de execução é um fator crucial na avaliação de algoritmos de compressão. A seguir, apresentamos o tempo necessário para comprimir diferentes tipos de arquivos.
""")
plot_execution_time_compression(all_stats)

# Seção: Heatmap do Tamanho Comprimido
st.subheader("Heatmap do Tamanho Comprimido")
st.markdown("""
O heatmap abaixo ilustra visualmente o tamanho comprimido dos arquivos, permitindo uma comparação rápida e intuitiva entre os diferentes tipos de dados.
""")
plot_compression_heatmap(all_stats)

# Seção: Estatísticas do Dicionário
st.subheader("Estatísticas do Dicionário")
st.markdown("""
Esta seção apresenta informações detalhadas sobre o tamanho do dicionário utilizado durante o processo de compressão e descompressão. Inclui o espaço em memória ocupado.
""")
plot_dictionary_statistics(all_stats)

# Seção: Análise dos Resultados
st.header("Análise dos Resultados")
st.markdown("""
Os resultados obtidos mostram que o algoritmo LZW é eficaz na compressão de diferentes tipos de dados, especialmente aqueles que contêm padrões repetitivos, como arquivos de texto e CSV. As imagens bitmap e arquivos de log apresentaram comportamentos variados: enquanto alguns arquivos apresentaram uma compressão eficaz, outros indicaram um aumento de tamanho.

O tempo de execução da compressão varia conforme o tipo de arquivo, sendo mais rápido para arquivos menores e com menos complexidade. As estatísticas do dicionário indicam a eficiência do algoritmo em gerenciar padrões repetitivos, com um crescimento controlado do dicionário durante o processo.

Em geral, o LZW demonstra um bom equilíbrio entre eficiência de compressão, gerenciamento de memória e tempo de execução, tornando-o uma escolha adequada para diversas aplicações.
""")

# Seção: Explicação dos Métodos e Implementações
st.header("Explicação dos Métodos e Implementações")
st.markdown("""
### Classe `TrieNode`

- **Descrição:** Representa um único nó na estrutura de dados Trie (árvore de prefixo).
- **Atributos:**
  - `children` (dicionário): Mapeia caracteres para objetos `TrieNode`, representando os filhos do nó atual.
  - `value` (int ou `None`): Código associado à string que termina neste nó.
  - `is_end_of_word` (bool): Indica se o nó marca o final de uma palavra válida.
- **Método `__init__`:**
  - Inicializa os atributos com valores padrão: nenhum filho, valor `None` e `is_end_of_word` como `False`.

### Classe `Trie`

- **Descrição:** Implementa uma estrutura Trie para armazenamento e recuperação eficiente de strings.
- **Atributos:**
  - `root` (`TrieNode`): Nó raiz da Trie.
  - `next_code` (int): Próximo código disponível para codificação de strings.
- **Método `__init__`:**
  - Inicializa a Trie com um nó raiz vazio e define `next_code` como 256 (códigos 0-255 reservados para caracteres ASCII).
- **Método `insert(string)`:**
  - Insere uma string na Trie.
  - Percorre cada caractere da string, criando nós filhos se necessário.
  - Ao final da string, marca o nó como `is_end_of_word` e atribui um código único.
- **Método `search(string)`:**
  - Busca uma string na Trie.
  - Retorna o código associado se a string for encontrada como uma palavra completa; caso contrário, retorna `None`.
- **Método `delete(string)`:**
  - Remove uma string da Trie.
  - Utiliza recursão para deletar nós que não são mais necessários após a remoção.
- **Método `initialize_with_ascii()`:**
  - Inicializa a Trie com todos os caracteres ASCII (0-255).
  - Cada caractere é inserido como uma entrada individual com seu valor ASCII correspondente.

### Funções de Compressão e Descompressão (`lzw_compress` e `lzw_decompress`)

- **Descrição Geral:**
  - Implementam os algoritmos de compressão e descompressão LZW, suportando modos estático e dinâmico de codificação.
  - Utilizam a estrutura Trie para armazenar e buscar padrões de strings.
  
- **Função `lzw_compress(...)`:**
  - **Parâmetros:**
    - Caminhos para os arquivos de entrada e saída.
    - Configurações como número máximo de bits, coleta de estatísticas e uso de código variável.
  - **Processo:**
    - Inicializa a Trie com caracteres ASCII.
    - Lê o arquivo de entrada e percorre os símbolos para construir sequências.
    - Dependendo do modo (variável ou estático), ajusta o tamanho dos códigos dinamicamente ou mantém um tamanho fixo.
    - Armazena os códigos comprimidos no arquivo de saída.
    - Coleta estatísticas de compressão, se solicitado.
    
- **Função `lzw_decompress(...)`:**
  - **Parâmetros:**
    - Caminhos para os arquivos de entrada comprimida e saída descomprimida.
    - Configurações semelhantes às da função de compressão.
  - **Processo:**
    - Lê os dados comprimidos do arquivo de entrada.
    - Inicializa o dicionário com caracteres ASCII.
    - Decodifica os códigos para reconstruir a string original.
    - Ajusta dinamicamente o tamanho dos códigos se o modo variável estiver ativo.
    - Escreve a string descomprimida no arquivo de saída.
    - Coleta estatísticas de descompressão, se solicitado.

### Função `main()`

- **Descrição:** Ponto de entrada principal para a execução do compressor e descompressor via linha de comando.
- **Processo:**
  - Utiliza `argparse` para parsear os argumentos fornecidos pelo usuário.
  - Determina o modo de operação (compressão ou descompressão) e chama a função correspondente.
  - Exibe estatísticas de operação se o modo de teste estiver habilitado.
  - Trata exceções durante a descompressão, como códigos inválidos.

---

Esta implementação proporciona uma maneira eficiente de comprimir e descomprimir arquivos utilizando o algoritmo LZW, com a flexibilidade de ajustar o tamanho dos códigos e coletar estatísticas detalhadas sobre o processo.
""")

# Seção: Dados Brutos (opcional)
st.header("Dados Brutos")
st.markdown("""
Abaixo, são apresentados os dados brutos utilizados para gerar os gráficos. Estes dados contêm informações detalhadas sobre cada teste realizado.
""")
if st.checkbox("Mostrar Dados Brutos"):
    for stats in all_stats:
        st.subheader(f"Dados Brutos para {stats.get('file_type')} - {stats.get('operation')}")
        st.json(stats)