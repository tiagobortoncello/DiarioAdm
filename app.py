# Importar bibliotecas necessárias
import streamlit as st
import re
import csv
import io
import fitz

def processar_e_salvar_csv_streamlit(pdf_bytes):
    """
    Processa bytes de um arquivo PDF e retorna dados em formato CSV.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        st.error(f"Erro ao abrir o arquivo PDF: {e}")
        return None

    resultados = []

    # Regex para normas normais
    regex = re.compile(
        r'(DELIBERAÇÃO DA MESA|PORTARIA DGE|ORDEM DE SERVIÇO PRES/PSEC)\s+Nº\s+([\d\.]+)\/(\d{4})'
    )

    # Regex para DCS (sem número/ano)
    regex_dcs = re.compile(r'DECIS[ÃA]O DA 1ª-SECRETARIA')

    for page in doc:
        text = page.get_text("text")
        text = re.sub(r'\s+', ' ', text)

        for match in regex.finditer(text):
            tipo_texto = match.group(1)
            numero = match.group(2).replace('.', '')
            ano = match.group(3)

            if tipo_texto.startswith("DELIBERAÇÃO DA MESA"):
                sigla = "DLB"
            elif tipo_texto.startswith("PORTARIA"):
                sigla = "PRT"
            elif tipo_texto.startswith("ORDEM DE SERVIÇO"):
                sigla = "OSV"
            else:
                continue

            resultados.append([sigla, numero, ano])

        if regex_dcs.search(text):
            resultados.append(["DCS", "", ""])

    doc.close()

    # Cria um buffer de memória para o arquivo CSV
    output_csv = io.StringIO()
    writer = csv.writer(output_csv, delimiter="\t")
    writer.writerows(resultados)
    
    # Retorna o conteúdo do buffer
    return output_csv.getvalue().encode('utf-8')


def run_app():
    # --- Custom CSS para estilizar o título ---
    st.markdown("""
        <style>
        .title-container {
            text-align: center;
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .main-title {
            color: #d11a2a;
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 0;
        }
        .subtitle-gil {
            color: gray;
            font-size: 1.5em;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # --- Título e informações para o usuário ---
    st.markdown("""
        <div class="title-container">
            <h1 class="main-title">Extrator do Diário Administrativo</h1>
            <h4 class="subtitle-gil">GERÊNCIA DE INFORMAÇÃO LEGISLATIVA - GIL/GDI</h4>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    st.markdown("<p style='font-size: 1.1em; color: firebrick;'>Faça o upload de um arquivo PDF para extrair as normas administrativas.</p>", unsafe_allow_html=True)
    
    # --- Upload do PDF ---
    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

    if uploaded_file is not None:
        st.success("PDF lido com sucesso! O processamento começou.")
        
        with st.spinner('Extraindo dados...'):
            pdf_bytes = uploaded_file.read()
            csv_data = processar_e_salvar_csv_streamlit(pdf_bytes)

            if csv_data:
                st.success("Dados extraídos com sucesso! ✅")
                st.divider()
                
                csv_filename = "Normas_Administrativo.csv"
                
                st.download_button(
                    label="Clique aqui para baixar o arquivo CSV",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv"
                )
                st.info("O download do arquivo CSV com todos os dados extraídos está pronto.")

# Executa a função principal
if __name__ == "__main__":
    run_app()