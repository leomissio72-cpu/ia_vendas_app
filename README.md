import requests
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import sys

SHEETDB_URL = 'https://sheetdb.io/api/v1/b8497l310h84g'

def carregar_planilha():
    resp = requests.get(SHEETDB_URL)
    return resp.json() if resp.status_code == 200 else []

def extrair_categorias_lojas(produtos):
    categorias = sorted(set(p.get('categoria', '').strip() for p in produtos if p.get('categoria')))
    lojas = sorted(set(p.get('loja', '').strip() for p in produtos if p.get('loja')))
    return categorias, lojas

def extrair_info_url(url):
    info = {
        'nome': '',
        'preco': '',
        'descricao': '',
        'imagem': '',
        'loja_sugerida': ''
    }
    dominio = urlparse(url).netloc.lower()
    if 'amazon' in dominio:
        info['loja_sugerida'] = 'Amazon'
    elif 'mercadolivre' in dominio or 'mercadolibre' in dominio:
        info['loja_sugerida'] = 'Mercado Livre'
    elif 'shopee' in dominio:
        info['loja_sugerida'] = 'Shopee'
    else:
        info['loja_sugerida'] = 'Outros'

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Título
        title = soup.title.string if soup.title else ''
        for sep in ['|', '-', '–']:
            if sep in title:
                title = title.split(sep)[0].strip()
        info['nome'] = title
        # Preço
        html_text = resp.text
        price_patterns = [r'R\$\s*([\d.,]+)', r'R\$\s*(\d+\.\d{2})', r'R\$\s*(\d+,\d{2})']
        for pattern in price_patterns:
            match = re.search(pattern, html_text)
            if match:
                preco = match.group(1).replace('.', '').replace(',', '.')
                info['preco'] = f"R$ {float(preco):.2f}".replace('.', ',')
                break
        # Descrição
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            info['descricao'] = meta_desc['content'][:250]
        # Imagem
        og_img = soup.find('meta', property='og:image')
        if og_img and og_img.get('content'):
            info['imagem'] = og_img['content']
        else:
            img = soup.find('img', src=True)
            if img:
                src = img['src']
                if not src.startswith('http'):
                    src = urljoin(url, src)
                info['imagem'] = src
    except Exception as e:
        print(f"⚠️ Erro na extração: {e}", file=sys.stderr)
    return info

def main():
    # Lê os inputs do GitHub Actions (variáveis de ambiente)
    url = sys.argv[1] if len(sys.argv) > 1 else ''
    nome_fornecido = sys.argv[2] if len(sys.argv) > 2 else ''
    preco_fornecido = sys.argv[3] if len(sys.argv) > 3 else ''
    desc_fornecido = sys.argv[4] if len(sys.argv) > 4 else ''
    img_fornecido = sys.argv[5] if len(sys.argv) > 5 else ''
    cat_fornecido = sys.argv[6] if len(sys.argv) > 6 else ''
    loja_fornecido = sys.argv[7] if len(sys.argv) > 7 else ''

    if not url:
        print("❌ Nenhuma URL fornecida.")
        sys.exit(1)

    # Carrega planilha
    produtos = carregar_planilha()
    categorias, lojas = extrair_categorias_lojas(produtos)

    # Extrai informações
    info = extrair_info_url(url)

    # Aplica valores fornecidos manualmente (se existirem)
    if nome_fornecido:
        info['nome'] = nome_fornecido
    if preco_fornecido:
        info['preco'] = preco_fornecido
    if desc_fornecido:
        info['descricao'] = desc_fornecido
    if img_fornecido:
        info['imagem'] = img_fornecido

    # Se categoria ou loja não foram fornecidos, sugere e lista opções
    if not cat_fornecido:
        print("📂 Categorias disponíveis:", ', '.join(categorias))
        print(f"   ➜ Sugerido: {info['loja_sugerida']} (para loja)")
        cat_fornecido = input("Digite a categoria (ou Enter para 'Eletronicos'): ").strip()
        if not cat_fornecido:
            cat_fornecido = 'Eletronicos'
    if not loja_fornecido:
        loja_fornecido = input(f"Digite a loja (Enter para '{info['loja_sugerida']}'): ").strip()
        if not loja_fornecido:
            loja_fornecido = info['loja_sugerida']

    # Calcular novo ID
    ids = [int(p.get('id', 0)) for p in produtos if str(p.get('id', '')).isdigit()]
    novo_id = max(ids) + 1 if ids else 1

    # Monta linha CSV
    linha = f"{novo_id},\"{info['nome']}\",\"{info['descricao']}\",{info['preco']},{info['imagem']},,,{url},{cat_fornecido},{loja_fornecido}"
    print("\n" + "="*80)
    print("📋 LINHA PRONTA PARA COLAR NA PLANILHA (copie a linha abaixo):")
    print("="*80)
    print(linha)
    print("="*80)
    print("\n💡 Instruções: Abra sua planilha, vá até a primeira linha vazia e cole (Ctrl+V).")

if __name__ == "__main__":
    main()
