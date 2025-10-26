import cv2
import numpy as np
import sys
import os

# Tenta importar a biblioteca reportlab, necessária para gerar o PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
except ImportError:
    print("Erro: A biblioteca 'reportlab' não foi encontrada.")
    print("Por favor, instale-a usando o comando: pip install reportlab")
    sys.exit(1)

# --- 1. CONFIGURAÇÃO INICIAL ---

# Criação de caminhos absolutos para evitar erros de localização
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RESULTS_FOLDER = os.path.join(SCRIPT_DIR, 'resultados_pdf')
IMAGE_FOLDER = os.path.join(SCRIPT_DIR, 'PDI_Lista_de_Exercicios_5_Imagens')
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Preparação do Documento PDF
pdf_path = os.path.join(SCRIPT_DIR, "Resultados_Lista_5_Final.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=A4)
story = []
styles = getSampleStyleSheet()

story.append(Paragraph("Resultados - Lista de Exercícios 5: Morfologia Matemática", styles['Title']))
story.append(Spacer(1, 0.3 * inch))

def add_to_pdf(title, path):
    """Adiciona um título e uma imagem ao PDF."""
    story.append(Paragraph(title, styles["h2"]))
    story.append(Spacer(1, 10))
    if os.path.exists(path):
        story.append(Image(path, width=4.5*inch))
    else:
        story.append(Paragraph(f"Imagem não encontrada: {path}", styles["Normal"]))
    story.append(Spacer(1, 20))

# --- 2. EXECUÇÃO DOS EXERCÍCIOS ---

# --- Exercício 1: Erosão e Dilatação ---
print("Processando Exercício 1...")
image_fig1 = np.array([
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,0,0], [0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,0,0],
    [0,0,1,1,0,0,1,1,1,1,1,1,1,0,0,1,1,0,0], [0,0,0,1,1,0,0,0,1,1,1,0,0,0,1,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
], dtype=np.uint8) * 255
se_a = np.ones((3, 3), dtype=np.uint8)
se_b = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
erosion_a = cv2.erode(image_fig1, se_a)
erosion_b = cv2.erode(image_fig1, se_b)
dilation_a = cv2.dilate(image_fig1, se_a)
dilation_b = cv2.dilate(image_fig1, se_b)

path_orig1 = os.path.join(RESULTS_FOLDER, "ex1_original.png")
path_ea = os.path.join(RESULTS_FOLDER, "ex1_erosao_a.png")
path_eb = os.path.join(RESULTS_FOLDER, "ex1_erosao_b.png")
path_da = os.path.join(RESULTS_FOLDER, "ex1_dilatacao_a.png")
path_db = os.path.join(RESULTS_FOLDER, "ex1_dilatacao_b.png")
cv2.imwrite(path_orig1, image_fig1)
cv2.imwrite(path_ea, erosion_a)
cv2.imwrite(path_eb, erosion_b)
cv2.imwrite(path_da, dilation_a)
cv2.imwrite(path_db, dilation_b)

add_to_pdf("Exercício 1: Imagem Original", path_orig1)
add_to_pdf("Exercício 1.i: Erosão com SE (a)", path_ea)
add_to_pdf("Exercício 1.ii: Erosão com SE (b)", path_eb)
add_to_pdf("Exercício 1.iii: Dilatação com SE (a)", path_da)
add_to_pdf("Exercício 1.iv: Dilatação com SE (b)", path_db)

# --- Exercício 2: Filtro por Tamanho (Abertura) ---
print("Processando Exercício 2...")
path_quadrados = os.path.join(IMAGE_FOLDER, 'quadrados.png')
quadrados_img = cv2.imread(path_quadrados, cv2.IMREAD_GRAYSCALE)
if quadrados_img is not None:
    _, bin_img = cv2.threshold(quadrados_img, 127, 255, cv2.THRESH_BINARY)
    se = np.ones((41, 41), dtype=np.uint8)
    eroded_img = cv2.erode(bin_img, se)
    restored_img = cv2.dilate(eroded_img, se)

    path_orig2 = os.path.join(RESULTS_FOLDER, "ex2_original.png")
    path_eroded2 = os.path.join(RESULTS_FOLDER, "ex2_erosao.png")
    path_restored2 = os.path.join(RESULTS_FOLDER, "ex2_resultado.png")
    cv2.imwrite(path_orig2, bin_img)
    cv2.imwrite(path_eroded2, eroded_img)
    cv2.imwrite(path_restored2, restored_img)
    
    add_to_pdf('Exercício 2: Imagem Original', path_orig2)
    add_to_pdf('Exercício 2: Após Erosão', path_eroded2)
    add_to_pdf('Exercício 2: Resultado Final (Abertura)', path_restored2)

# --- Exercício 3: Abertura e Fechamento ---
print("Processando Exercício 3...")
path_ruidos = os.path.join(IMAGE_FOLDER, 'ruidos.png')
ruidos_img = cv2.imread(path_ruidos, cv2.IMREAD_GRAYSCALE)
if ruidos_img is not None:
    _, bin_img = cv2.threshold(ruidos_img, 127, 255, cv2.THRESH_BINARY)
    se = np.ones((5, 5), dtype=np.uint8)
    abertura = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, se)
    fechamento = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, se)
    
    path_orig3 = os.path.join(RESULTS_FOLDER, "ex3_original.png")
    path_abertura3 = os.path.join(RESULTS_FOLDER, "ex3_abertura.png")
    path_fechamento3 = os.path.join(RESULTS_FOLDER, "ex3_fechamento.png")
    cv2.imwrite(path_orig3, bin_img)
    cv2.imwrite(path_abertura3, abertura)
    cv2.imwrite(path_fechamento3, fechamento)

    add_to_pdf('Exercício 3: Imagem Original', path_orig3)
    add_to_pdf('Exercício 3.i: Abertura (remove ruído de fundo)', path_abertura3)
    add_to_pdf('Exercício 3.ii: Fechamento (remove ruído do objeto)', path_fechamento3)

# --- Exercício 4: Extração de Bordas ---
print("Processando Exercício 4...")
path_cachorro = os.path.join(IMAGE_FOLDER, 'cachorro.png')
cachorro_img = cv2.imread(path_cachorro, cv2.IMREAD_GRAYSCALE)
if cachorro_img is not None:
    _, bin_img = cv2.threshold(cachorro_img, 127, 255, cv2.THRESH_BINARY)
    se = np.ones((3, 3), dtype=np.uint8)
    eroded = cv2.erode(bin_img, se)
    dilated = cv2.dilate(bin_img, se)
    borda_interna = bin_img - eroded
    borda_externa = dilated - bin_img
    
    path_orig4 = os.path.join(RESULTS_FOLDER, "ex4_original.png")
    path_int4 = os.path.join(RESULTS_FOLDER, "ex4_borda_interna.png")
    path_ext4 = os.path.join(RESULTS_FOLDER, "ex4_borda_externa.png")
    cv2.imwrite(path_orig4, bin_img)
    cv2.imwrite(path_int4, borda_interna)
    cv2.imwrite(path_ext4, borda_externa)

    add_to_pdf('Exercício 4: Imagem Original', path_orig4)
    add_to_pdf('Exercício 4: Borda Interna', path_int4)
    add_to_pdf('Exercício 4: Borda Externa', path_ext4)

# --- Exercício 5: Preenchimento de Região ---
print("Processando Exercício 5...")
path_gato = os.path.join(IMAGE_FOLDER, 'gato.png')
gato_img = cv2.imread(path_gato, cv2.IMREAD_GRAYSCALE)
if gato_img is not None:
    _, boundary = cv2.threshold(gato_img, 127, 255, cv2.THRESH_BINARY)
    boundary_inv = cv2.bitwise_not(boundary)
    seed_point = (200, 200) # Atenção: este ponto pode precisar de ajuste
    
    mask = np.zeros((gato_img.shape[0] + 2, gato_img.shape[1] + 2), np.uint8)
    filled_img = boundary_inv.copy()
    cv2.floodFill(filled_img, mask, seed_point, 255)
    
    # Inverte de volta e combina com a borda
    filled_img = cv2.bitwise_not(filled_img)
    final_img = cv2.bitwise_or(boundary, filled_img)

    path_orig5 = os.path.join(RESULTS_FOLDER, "ex5_original.png")
    path_fill5 = os.path.join(RESULTS_FOLDER, "ex5_preenchido.png")
    cv2.imwrite(path_orig5, boundary)
    cv2.imwrite(path_fill5, final_img)
    
    add_to_pdf('Exercício 5: Bordas Originais', path_orig5)
    add_to_pdf('Exercício 5: Região Preenchida', path_fill5)

# --- Exercício 6: Componentes Conectados ---
print("Processando Exercício 6...")
if quadrados_img is not None:
    _, bin_img = cv2.threshold(quadrados_img, 127, 255, cv2.THRESH_BINARY)
    
    # Pega o label do componente no ponto especificado
    seed_point = (130, 130) # Atenção: este ponto pode precisar de ajuste
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bin_img, 4, cv2.CV_32S)
    
    # Cria uma imagem amarela apenas com o componente selecionado
    component_mask = np.zeros_like(bin_img)
    if labels[seed_point] > 0: # Garante que não é o fundo
        component_label = labels[seed_point]
        component_mask[labels == component_label] = 255

    output_yellow = cv2.cvtColor(bin_img, cv2.COLOR_GRAY2BGR)
    output_yellow[component_mask == 255] = (0, 255, 255)

    path_orig6 = os.path.join(RESULTS_FOLDER, "ex6_original.png")
    path_comp6 = os.path.join(RESULTS_FOLDER, "ex6_componente.png")
    cv2.imwrite(path_orig6, bin_img)
    cv2.imwrite(path_comp6, output_yellow)
    
    add_to_pdf('Exercício 6: Imagem Original', path_orig6)
    add_to_pdf('Exercício 6: Componente Selecionado em Amarelo', path_comp6)

# --- Exercício 7: Morfologia em Níveis de Cinza ---
print("Processando Exercício 7...")
# CORREÇÃO: Carregando .jpg em vez de .png
path_aluno = os.path.join(IMAGE_FOLDER, 'img_aluno.jpg')
img_aluno = cv2.imread(path_aluno, cv2.IMREAD_GRAYSCALE)
if img_aluno is not None:
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(img_aluno, se)
    eroded = cv2.erode(img_aluno, se)
    gradient = cv2.morphologyEx(img_aluno, cv2.MORPH_GRADIENT, se)
    
    path_orig7 = os.path.join(RESULTS_FOLDER, "ex7_original.png")
    path_dil7 = os.path.join(RESULTS_FOLDER, "ex7_dilatacao.png")
    path_ero7 = os.path.join(RESULTS_FOLDER, "ex7_erosao.png")
    path_grad7 = os.path.join(RESULTS_FOLDER, "ex7_gradiente.png")
    cv2.imwrite(path_orig7, img_aluno)
    cv2.imwrite(path_dil7, dilated)
    cv2.imwrite(path_ero7, eroded)
    cv2.imwrite(path_grad7, gradient)

    add_to_pdf('Exercício 7: Imagem Aluno Original', path_orig7)
    add_to_pdf('Exercício 7: Dilatação', path_dil7)
    add_to_pdf('Exercício 7: Erosão', path_ero7)
    add_to_pdf('Exercício 7: Gradiente Morfológico', path_grad7)

# --- 3. CONSTRUÇÃO FINAL DO PDF ---
try:
    print("\nGerando PDF com todos os resultados...")
    doc.build(story)
    print(f"PDF '{os.path.basename(pdf_path)}' gerado com sucesso!")
except Exception as e:
    print(f"Ocorreu um erro ao gerar o PDF: {e}")