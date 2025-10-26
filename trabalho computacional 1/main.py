import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import tkinter as tk
from tkinter import filedialog

# --- Importa as SUAS funções do outro arquivo ---
try:
    import funcoes as pdi
except ImportError:
    print("[ERRO FATAL] O arquivo 'funcoes' não foi encontrado.")
    print("Certifique-se de que ambos os arquivos .py estão na mesma pasta.")
    sys.exit(1)

# --- Variável Global para Imagem ---
current_image = None
current_image_path = ""

# --- Funções Auxiliares ---
def show_image(title, img):
    if img is None:
        print(f"Erro: Imagem '{title}' está vazia.")
        return
    if img.dtype == np.float64 or img.dtype == np.float32:
        img = cv2.convertScaleAbs(img)
        
    print(f"Exibindo: {title}. Pressione qualquer tecla para fechar.")
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyWindow(title)

def get_int_input(prompt, default):
    try:
        val_str = input(f"{prompt} (padrão: {default}): ")
        if val_str == "":
            return default
        return int(val_str)
    except ValueError:
        print("Entrada inválida. Usando valor padrão.")
        return default

def get_float_input(prompt, default):
    try:
        val_str = input(f"{prompt} (padrão: {default}): ")
        if val_str == "":
            return default
        return float(val_str)
    except ValueError:
        print("Entrada inválida. Usando valor padrão.")
        return default

def check_image_loaded():
    if current_image is None:
        print("\n[ERRO] Nenhuma imagem carregada.")
        print("Por favor, carregue uma imagem (opção 1) ou capture da câmera (opção 2) primeiro.")
        return False
    return True

def is_image_binary(img):
    if img is None or len(img.shape) > 2:
        return False 
    unique_vals = np.unique(img)
    if len(unique_vals) <= 2: 
        return True
    return False 


# --- Aquisição de Imagens ---
def req_2a_load_image():
    global current_image, current_image_path
    
    root = tk.Tk()
    root.withdraw()
    
    file_types = [
        ('Imagens', '*.png *.jpg *.jpeg *.bmp *.tif *.tiff'),
        ('Todos os arquivos', '*.*')
    ]
    
    path = filedialog.askopenfilename(
        title="Selecione uma imagem para carregar",
        filetypes=file_types
    )
    
    root.destroy()
    
    if not path:
        print("Seleção de arquivo cancelada.")
        return

    if not os.path.exists(path):
        print(f"Erro: Arquivo '{path}' não encontrado.")
        return
        
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    
    if img is None:
        print(f"Erro: Não foi possível ler a imagem em '{path}'.")
        return
        
    current_image = img
    current_image_path = os.path.basename(path) 
    print(f"Imagem '{current_image_path}' carregada com sucesso.")
    show_image(f"Imagem Carregada: {current_image_path}", current_image)

def req_2b_capture_camera():
    global current_image, current_image_path
    print("Acessando câmera... Pressione 's' para salvar o frame, 'q' para sair.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmera.")
        return
    captured = False
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro: Não foi possível capturar o frame.")
            break
        cv2.imshow("Camera - 's' para salvar, 'q' para sair", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            current_image = frame
            current_image_path = "captura_camera.png"
            print("Frame capturado e definido como imagem atual.")
            captured = True
            break
        elif key == ord('q'):
            print("Captura da câmera cancelada.")
            break
    cap.release()
    cv2.destroyAllWindows()
    if captured:
        show_image("Frame Capturado", current_image)


# --- Conversões ---

def req_3a_grayscale():
    global current_image
    if not check_image_loaded(): return

    if len(current_image.shape) > 2:
        print("Usando cv2.cvtColor")
        gray_img = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
        print("Imagem convertida para níveis de cinza.")
        current_image = gray_img
        show_image("3a - Níveis de Cinza", current_image)
    else:
        print("A imagem atual já está em níveis de cinza.")


def req_3b_negative():
    if not check_image_loaded(): return
    print("Usando sua função 'negativo'")
    negative_img = pdi.meu_negativo(current_image)
    print("Imagem convertida para negativo.")
    show_image("3b - Negativo", negative_img)

def req_3c_otsu():
    global current_image
    if not check_image_loaded(): return

    img_to_process = current_image
    
    if len(img_to_process.shape) > 2:
        print("Aplicando Otsu... (Convertendo para cinza primeiro)")
        img_to_process = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2GRAY)
    
    print("Usando sua função 'otsu'")
    thresh_val, binary_img = pdi.meu_otsu(img_to_process)
    
    print(f"Limiarização de Otsu aplicada. Limiar (threshold) encontrado: {thresh_val}")
    current_image = binary_img
    show_image("3c - Binária (Otsu)", current_image)


# --- Operações ---
def req_4a_smoothing():
    if not check_image_loaded(): return
    
    k = get_int_input("Digite o tamanho do kernel (ímpar)", 5)
    
    print("Usando sua função 'media'")
    mean_img = pdi.media(current_image, k)

    print("Usando sua função 'mediana'")
    median_img = pdi.mediana(current_image, k)
    
    show_image(f"4a - Suavização pela Média ({k}x{k})", mean_img)
    show_image(f"4a - Suavização pela Mediana ({k}x{k})", median_img)

def req_4b_canny():
    if not check_image_loaded(): return

    print("O detector de Canny funciona melhor em imagens em tons de cinza.")
    t1 = get_int_input("Digite o Limiar (threshold) 1", 100)
    t2 = get_int_input("Digite o Limiar (threshold) 2", 200)

    img_to_process = current_image
    if len(current_image.shape) > 2:
        img_to_process = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)

    print("Usando sua função 'canny'")
    canny_edges = pdi.meu_canny(img_to_process, t1, t2)
    
    print("Detector de bordas de Canny aplicado.")
    show_image(f"4b - Canny (T1={t1}, T2={t2})", canny_edges)

def req_4c_morphology():
    if not check_image_loaded(): return
    
    k = get_int_input("Digite o tamanho do kernel (ímpar)", 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))

    erode_img = pdi.meu_erode(current_image, kernel)
    dilate_img = pdi.meu_dilate(current_image, kernel)
    open_img = pdi.meu_abertura(current_image, kernel)
    close_img = pdi.meu_fechamento(current_image, kernel)

    show_image(f"4c - Erosão ({k}x{k})", erode_img)
    show_image(f"4c - Dilatação ({k}x{k})", dilate_img)
    show_image(f"4c - Abertura ({k}x{k})", open_img)
    show_image(f"4c - Fechamento ({k}x{k})", close_img)


# --- Requisito 5: Operações em Imagens ---
def req_5a_histogram():
    if not check_image_loaded(): return
    print("Usando sua função 'mostrar_histograma'")
    pdi.mostrar_histograma(current_image)

def req_5b_binary_properties():
    if not check_image_loaded(): return

    if not is_image_binary(current_image):
        print("\n[ERRO] Esta operação requer uma imagem binária.")
        print("Por favor, aplique a 'Limiarização de Otsu' (opção 3c) primeiro.")
        return

    print("[AVISO] Usando cv2.findContours, cv2.contourArea, cv2.arcLength.")

    img_copy = current_image.copy()
    contours, hierarchy = cv2.findContours(
        img_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    print(f"\n--- Propriedades dos Objetos (Requisito 5b) ---")
    print(f"Total de objetos encontrados (contornos): {len(contours)}")
    if not contours:
        print("Nenhum objeto detectado.")
        return

    output_img = cv2.cvtColor(current_image, cv2.COLOR_GRAY2BGR)
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        equivalent_diameter = np.sqrt(4 * area / np.pi)
        
        print(f"\nObjeto {i+1}:")
        print(f"  Área: {area:.2f} pixels")
        print(f"  Perímetro: {perimeter:.2f} pixels")
        print(f"  Diâmetro Equivalente: {equivalent_diameter:.2f} pixels")
        
        cv2.drawContours(output_img, [c], -1, (0, 255, 0), 2)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            cv2.putText(output_img, str(i+1), (cX, cY), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
    show_image("5b - Propriedades dos Objetos", output_img)

def req_5c_object_counting():
    if not check_image_loaded(): return

    if not is_image_binary(current_image):
        print("\n[ERRO] Esta operação requer uma imagem binária.")
        print("Por favor, aplique a 'Limiarização de Otsu' (opção 3c) primeiro.")
        return
        
    print("Iniciando contagem de objetos com crescimento de região (conforme 5c)...")
    
    img_bin = current_image.copy()
    visited = np.zeros(img_bin.shape, dtype=np.uint8)
    rows, cols = img_bin.shape
    object_count = 0
    
    for y in range(rows):
        for x in range(cols):
            if img_bin[y, x] == 255 and visited[y, x] == 0:
                object_count += 1
                stack = [(y, x)]
                visited[y, x] = 1
                while len(stack) > 0:
                    cy, cx = stack.pop()
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0: continue
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < rows and 0 <= nx < cols:
                                if img_bin[ny, nx] == 255 and visited[ny, nx] == 0:
                                    visited[ny, nx] = 1
                                    stack.append((ny, nx))

    print(f"\n--- Contagem de Objetos (Requisito 5c) ---")
    print(f"Total de objetos encontrados (crescimento de região): {object_count}")

# --- Funções Extras ---
def run_extra(func, name, *args):
    if not check_image_loaded(): return
    img_to_process = current_image
    
    if func in [pdi.laplaciano, pdi.roberts, pdi.prewitt, pdi.sobel]:
        if len(current_image.shape) > 2:
            img_to_process = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
            
    print(f"Aplicando sua função '{name}'...")
    result_img = func(img_to_process, *args)
    show_image(f"Extra - {name}", result_img)

# --- Loop Principal (Interface Interativa) ---
def print_menu():
    print("\n" + "="*50)
    print("Trabalho Computacional 1")
    print("="*50)
    
    img_status = f"'{current_image_path}'" if current_image is not None else "Nenhuma"
    print(f"Imagem Atual: {img_status}")
    print("\n--- Menu Principal ---")
    print("\n(Requisito 2: Aquisição)")
    print("  1. Carregar imagem (Janela de Seleção)")
    print("  2. Capturar imagem da câmera")
    print("\n(Requisito 3: Conversões)")
    print("  3a. Converter para Níveis de Cinza")
    print("  3b. Converter para Negativo")
    print("  3c. Converter para Binário (Otsu)")
    print("\n(Requisito 4: Operações)")
    print("  4a. Suavização (Média e Mediana)")
    print("  4b. Detector de Bordas (Canny)")
    print("  4c. Morfologia")
    print("\n(Requisito 5: Operações em Imagens)")
    print("  5a. Exibir Histograma")
    print("  5b. Propriedades (Área, Perímetro, Diâmetro)")
    print("  5c. Contagem de Objetos (Crescimento de Região)")
    print("\n(Itens Extras)")
    print("  e1. Transformação Logarítmica")
    print("  e2. Transformação de Potência")
    print("  e3. Equalização de Histograma")
    print("  e4. Detector Laplaciano")
    print("  e5. Detector de Roberts")
    print("  e6. Detector de Prewitt")
    print("  e7. Detector de Sobel")
    print("\n  0. Sair")
    print("-"*50)

def main():
    while True:
        print_menu()
        choice = input("Escolha uma opção: ").strip().lower()

        if choice == '1': req_2a_load_image()
        elif choice == '2': req_2b_capture_camera()
        
        elif choice == '3a': req_3a_grayscale()
        elif choice == '3b': req_3b_negative()
        elif choice == '3c': req_3c_otsu()
        
        elif choice == '4a': req_4a_smoothing()
        elif choice == '4b': req_4b_canny()
        elif choice == '4c': req_4c_morphology()
        
        elif choice == '5a': req_5a_histogram()
        elif choice == '5b': req_5b_binary_properties()
        elif choice == '5c': req_5c_object_counting()
            
        # Extras
        elif choice == 'e1': run_extra(pdi.logaritmico, "Logarítmico")
        elif choice == 'e2':
            if check_image_loaded():
                c = get_float_input("Digite o valor de C", 1.0)
                g = get_float_input("Digite o valor de Gamma", 1.0)
                run_extra(pdi.potencia, f"Potência (C={c}, G={g})", c, g)
        elif choice == 'e3': run_extra(pdi.equalizacao, "Equalização")
        elif choice == 'e4': run_extra(pdi.laplaciano, "Laplaciano")
        elif choice == 'e5': run_extra(pdi.roberts, "Roberts")
        elif choice == 'e6': run_extra(pdi.prewitt, "Prewitt")
        elif choice == 'e7': run_extra(pdi.sobel, "Sobel")
            
        elif choice == '0':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    try:
        import tkinter
    except ImportError:
        print("[AVISO] A biblioteca 'tkinter' não foi encontrada.")
        print("A seleção de arquivos por janela (Opção 1) não funcionará.")
    
    main()