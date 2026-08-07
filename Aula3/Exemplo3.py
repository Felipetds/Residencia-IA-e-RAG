from pathlib import Path

caminho = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula2\arquivos_md\bioetica_e_ia.md")

def consultar_linha(caminho, numero_linha):
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    
    # Valida se a linha existe no arquivo para evitar erros (IndexError)
    if 0 <= numero_linha < len(linhas):
        return linhas[numero_linha]
    return "Linha não encontrada."

# Exemplo: Acessando a primeira linha (índice 0)
print(consultar_linha(caminho, 12))

#linha 5 até 214