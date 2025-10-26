import PySimpleGUI as sg
import cv2
import numpy as np
import os
import sys

try:
    import funcoes as pdi
except ImportError:
    sg.popup_error("[ERRO FATAL] O arquivo 'funcoes.py' não foi encontrado.\n\nCertifique-se de que ambos os arquivos .py estão na mesma pasta.")
    sys.exit(1)

# --- Funções Auxiliares da GUI ---
def convert_to_bytes(img, resize=None):
    if img is None:
        return None
        
    # Se for redimensionar
    if resize and isinstance(resize, tuple) and len(resize) == 2:
        img = cv2.resize(img, resize, interpolation=cv2.INTER_AREA)

    # Converte para PNG em memória
    is_success, buffer = cv2.imencode(".png", img)
    if is_success:
        return buffer.tobytes()
    else:
        return None

def is_image_binary(img):
    if img is None or len(img.shape) > 2:
        return False 
    unique_vals = np.unique(img)
    return len(unique_vals) <= 2

# --- Funções de Análise (Adaptadas para a GUI) ---
def gui_5b_binary_properties(current_image):
    if current_image is None:
        return "[ERRO] Nenhuma imagem carregada."
        
    if not is_image_binary(current_image):
        return "[ERRO] Esta operação requer uma imagem binária.\nPor favor, aplique a 'Limiarização de Otsu' (Req 3c) primeiro."

    img_copy = current_image.copy()
    contours, _ = cv2.findContours(img_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    output_str = f"--- Propriedades dos Objetos (5b) ---\n"
    output_str += f"Total de objetos encontrados: {len(contours)}\n"
    
    if not contours:
        return output_str + "Nenhum objeto detectado."

    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        equivalent_diameter = np.sqrt(4 * area / np.pi)
        
        output_str += f"\nObjeto {i+1}:\n"
        output_str += f"  Área: {area:.2f} pixels\n"
        output_str += f"  Perímetro: {perimeter:.2f} pixels\n"
        output_str += f"  Diâmetro: {equivalent_diameter:.2f} pixels\n"
                        
    return output_str

def gui_5c_object_counting(current_image):
    if current_image is None:
        return "[ERRO] Nenhuma imagem carregada."

    if not is_image_binary(current_image):
        return "[ERRO] Esta operação requer uma imagem binária.\nPor favor, aplique a 'Limiarização de Otsu' (Req 3c) primeiro."
        
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

    return f"--- Contagem de Objetos (5c) ---\nTotal (crescimento de região): {object_count}"

# --- Definição do Layout da GUI ---
def create_layout():
    """ Cria o layout da janela principal """
    
    image_display_size = (400, 400) # Tamanho (width, height) para as janelas de imagem
    
    # --- Coluna 1: Controles ---    
    col_req2 = [
        [sg.Button("1. Carregar Imagem", key='-LOAD-', expand_x=True),
         sg.Button("2. Capturar Câmera", key='-CAM-', expand_x=True)],
        [sg.Text("Arquivo:", size=(8,1)), sg.Text("Nenhum", key='-FILENAME-', expand_x=True)]
    ]
    
    col_req3 = [
        [sg.Button("a. Níveis de Cinza", key='-GRAY-', expand_x=True)],
        [sg.Button("b. Negativo", key='-NEG-', expand_x=True)],
        [sg.Button("c. Binário (Otsu)", key='-OTSU-', expand_x=True)]
    ]

    col_req4a = [
        [sg.Text("Kernel:", size=(8,1)), sg.Input("5", size=(5,1), key='-K_SMOOTH-'),
         sg.Button("Média", key='-MEAN-'), sg.Button("Mediana", key='-MEDIAN-')]
    ]

    col_req4b = [
        [sg.Text("T1:", size=(3,1)), sg.Input("100", size=(5,1), key='-T1-'),
         sg.Text("T2:", size=(3,1)), sg.Input("200", size=(5,1), key='-T2-'),
         sg.Button("Aplicar", key='-CANNY-')]
    ]
    
    col_req4c = [
        [sg.Text("Kernel:", size=(8,1)), sg.Input("5", size=(5,1), key='-K_MORPH-')],
        [sg.Button("Erosão", key='-ERODE-'), sg.Button("Dilatação", key='-DILATE-')],
        [sg.Button("Abertura", key='-OPEN-'), sg.Button("Fechamento", key='-CLOSE-')]
    ]
    
    col_req5 = [
        [sg.Button("a. Histograma", key='-HIST-', expand_x=True)],
        [sg.Button("b. Propriedades", key='-PROPS-', expand_x=True)],
        [sg.Button("c. Contagem de Objetos", key='-COUNT-', expand_x=True)]
    ]
    
    col_extras = [
        [sg.Button("Log", key='-LOG-'), sg.Button("Equalizar", key='-EQ-')],
        [sg.Button("Laplaciano", key='-LAP-'), sg.Button("Sobel", key='-SOBEL-')],
        [sg.Button("Prewitt", key='-PRE-'), sg.Button("Roberts", key='-ROB-')],
        [sg.Frame("Potência:", [[
            sg.Text("C:", size=(2,1)), sg.Input("1.0", size=(4,1), key='-C_POT-'),
            sg.Text("G:", size=(2,1)), sg.Input("1.0", size=(4,1), key='-G_POT-'),
            sg.Button("Aplicar", key='-POT-')
        ]])]
    ]

    # Montagem da Coluna de Controle
    control_column = [
        [sg.Frame("Requisito 2: Aquisição", col_req2, expand_x=True)],
        [sg.Frame("Requisito 3: Conversões", col_req3, expand_x=True)],
        [sg.Frame("Requisito 4a: Suavização", col_req4a, expand_x=True)],
        [sg.Frame("Requisito 4b: Canny", col_req4b, expand_x=True)],
        [sg.Frame("Requisito 4c: Morfologia", col_req4c, expand_x=True)],
        [sg.Frame("Requisito 5: Análise", col_req5, expand_x=True)],
        [sg.Frame("Funções Extras", col_extras, expand_x=True)],
        [sg.Frame("Saída de Texto:", [[
            sg.Multiline(size=(45, 8), key='-OUTPUT-', autoscroll=True, disabled=True)
        ]], expand_x=True)],
        [sg.Button("Sair", key='-EXIT-', button_color=('white', 'red'), expand_x=True)]
    ]

    # --- Coluna 2: Imagens ---
    image_column = [
        [sg.Text("Imagem Original"), sg.Button("Restaurar Original", key='-RESET-')],
        [sg.Image(key='-IMG_ORIG-', size=image_display_size, background_color='gray')],
        [sg.Text("Imagem Processada")],
        [sg.Image(key='-IMG_PROC-', size=image_display_size, background_color='gray')]
    ]

    # --- Layout Final ---
    layout = [
        [sg.Column(control_column, scrollable=True, vertical_scroll_only=True, size=(450, 700)),
         sg.VSeperator(),
         sg.Column(image_column)]
    ]
    
    return layout

# --- Função Principal da GUI ---
def main():
    sg.theme("LightBlue2")
    layout = create_layout()
    window = sg.Window("Trabalho Prático PDI - Interface Gráfica", layout, finalize=True)

    original_image = None  # Armazena a imagem carregada
    current_image = None   # Armazena a imagem processada
    img_size = (400, 400)  # Tamanho para exibir

    # Loop de Eventos
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, '-EXIT-'):
            break

        # --- Aquisição ---
        if event == '-LOAD-':
            file_types = [("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif"), ("Todos", "*.*")]
            path = sg.popup_get_file("Selecione uma imagem", file_types=file_types)
            if path:
                try:
                    original_image = cv2.imread(path, cv2.IMREAD_COLOR)
                    current_image = original_image.copy()
                    window['-FILENAME-'].update(os.path.basename(path))
                    window['-IMG_ORIG-'].update(data=convert_to_bytes(original_image, resize=img_size))
                    window['-IMG_PROC-'].update(data=convert_to_bytes(current_image, resize=img_size))
                except Exception as e:
                    sg.popup_error(f"Erro ao carregar a imagem:\n{e}")

        elif event == '-CAM-':
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                sg.popup_error("Erro: Não foi possível abrir a câmera.")
            else:
                sg.popup_quick_message("Abrindo câmera... 's' para salvar, 'q' para sair.", auto_close_duration=2)
                captured = False
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    cv2.imshow("Camera - 's' salvar, 'q' sair", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('s'):
                        original_image = frame
                        current_image = frame.copy()
                        captured = True
                        break
                    elif key == ord('q'):
                        break
                cap.release()
                cv2.destroyAllWindows()
                if captured:
                    window['-FILENAME-'].update("captura_camera.png")
                    window['-IMG_ORIG-'].update(data=convert_to_bytes(original_image, resize=img_size))
                    window['-IMG_PROC-'].update(data=convert_to_bytes(current_image, resize=img_size))

        elif event == '-RESET-':
            if original_image is not None:
                current_image = original_image.copy()
                window['-IMG_PROC-'].update(data=convert_to_bytes(current_image, resize=img_size))
                window['-OUTPUT-'].update("Imagem restaurada ao original.")
            else:
                sg.popup_error("Nenhuma imagem original carregada.")

        if current_image is None and event not in ('-LOAD-', '-CAM-', sg.WIN_CLOSED, '-EXIT-'):
            sg.popup_error("Nenhuma imagem carregada!", "Por favor, carregue uma imagem ou capture da câmera primeiro.")
            continue

        try:
            # --- Conversões ---
            if event == '-GRAY-':
                if len(current_image.shape) > 2:
                    current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
                else:
                    window['-OUTPUT-'].update("Imagem já está em Níveis de Cinza.")
            
            elif event == '-NEG-':
                current_image = pdi.meu_negativo(current_image)
            
            elif event == '-OTSU-':
                img_gray = current_image
                if len(img_gray.shape) > 2:
                    img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
                thresh_val, current_image = pdi.meu_otsu(img_gray)
                window['-OUTPUT-'].update(f"Limiar de Otsu aplicado: {thresh_val}")

            # --- Operações ---
            elif event == '-MEAN-':
                k = int(values['-K_SMOOTH-'])
                current_image = pdi.media(current_image, k)
            
            elif event == '-MEDIAN-':
                k = int(values['-K_SMOOTH-'])
                current_image = pdi.mediana(current_image, k)
            
            elif event == '-CANNY-':
                t1, t2 = int(values['-T1-']), int(values['-T2-'])
                img_gray = current_image
                if len(img_gray.shape) > 2:
                    img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
                current_image = pdi.meu_canny(img_gray, t1, t2)
            
            elif event in ('-ERODE-', '-DILATE-', '-OPEN-', '-CLOSE-'):
                k = int(values['-K_MORPH-'])
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
                if event == '-ERODE-':
                    current_image = pdi.meu_erode(current_image, kernel)
                elif event == '-DILATE-':
                    current_image = pdi.meu_dilate(current_image, kernel)
                elif event == '-OPEN-':
                    current_image = pdi.meu_abertura(current_image, kernel)
                elif event == '-CLOSE-':
                    current_image = pdi.meu_fechamento(current_image, kernel)
            
            # --- Análise ---
            elif event == '-HIST-':
                pdi.mostrar_histograma(current_image)
                window['-OUTPUT-'].update("Histograma exibido em nova janela.")
            
            elif event == '-PROPS-':
                output_text = gui_5b_binary_properties(current_image)
                window['-OUTPUT-'].update(output_text)
            
            elif event == '-COUNT-':
                output_text = gui_5c_object_counting(current_image)
                window['-OUTPUT-'].update(output_text)
            
            # --- Extras ---
            elif event == '-LOG-':
                current_image = pdi.logaritmico(current_image)
            elif event == '-EQ-':
                current_image = pdi.equalizacao(current_image)
            elif event == '-LAP-':
                current_image = pdi.laplaciano(current_image)
            elif event == '-SOBEL-':
                current_image = pdi.sobel(current_image)
            elif event == '-PRE-':
                current_image = pdi.prewitt(current_image)
            elif event == '-ROB-':
                current_image = pdi.roberts(current_image)
            elif event == '-POT-':
                c = float(values['-C_POT-'])
                g = float(values['-G_POT-'])
                current_image = pdi.potencia(current_image, c, g)

        except ValueError:
            sg.popup_error("Erro de Valor!", "Verifique se os parâmetros (Kernel, T1, T2, C, G) são números válidos.")
        except Exception as e:
            sg.popup_error(f"Ocorreu um erro inesperado:\n{e}")

        if event not in ('-HIST-', '-PROPS-', '-COUNT-'):
             window['-IMG_PROC-'].update(data=convert_to_bytes(current_image, resize=img_size))

    window.close()

if __name__ == "__main__":
    main()