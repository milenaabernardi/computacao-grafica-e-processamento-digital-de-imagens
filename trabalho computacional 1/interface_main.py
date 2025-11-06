import PySimpleGUI as sg
import cv2
import numpy as np
import os
import sys
import subprocess 

try:
    import funcoes as pdi
except ImportError:
    sg.popup_error("[ERRO FATAL] O arquivo 'funcoes.py' não foi encontrado.\n\nCertifique-se de que ambos os arquivos .py estão na mesma pasta.")
    sys.exit(1)

# --- Funções Auxiliares da GUI ---
def convert_to_bytes(img, resize=None):
    if img is None:
        return None
    if resize and isinstance(resize, tuple) and len(resize) == 2:
        img = cv2.resize(img, resize, interpolation=cv2.INTER_AREA)
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

# --- Funções de Análise ---
def gui_5b_binary_properties(current_image):
    if current_image is None:
        return "[ERRO] Nenhuma imagem carregada."
    if not is_image_binary(current_image):
        return "[ERRO] Esta operação requer uma imagem binária.\nPor favor, aplique a 'Limiarização de Otsu' primeiro."

    img_bin = current_image.copy()
    
    num_white_pixels = np.sum(img_bin == 255)
    total_pixels = img_bin.shape[0] * img_bin.shape[1]
    
    if num_white_pixels > (total_pixels / 2):
        img_to_contour = cv2.bitwise_not(img_bin)
    else:
        img_to_contour = img_bin
    
    contours, _ = cv2.findContours(img_to_contour, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output_str = f"--- Propriedades dos Objetos ---\n"
    
    filtered_contours = []
    for c in contours:
        if cv2.contourArea(c) > 10:
            filtered_contours.append(c)
            
    output_str += f"Total de objetos encontrados (> 10 pixels): {len(filtered_contours)}\n"

    if not filtered_contours:
        return output_str + "Nenhum objeto detectado (acima de 10 pixels)."

    for i, c in enumerate(filtered_contours):
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
        return "[ERRO] Esta operação requer uma imagem binária.\nPor favor, aplique a 'Limiarização de Otsu' primeiro."
        
    img_bin = current_image.copy()

    num_white_pixels = np.sum(img_bin == 255)
    total_pixels = img_bin.shape[0] * img_bin.shape[1]
    
    if num_white_pixels > (total_pixels / 2):
        img_to_contour = cv2.bitwise_not(img_bin)
    else:
        img_to_contour = img_bin
    
    contours, _ = cv2.findContours(img_to_contour, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    object_count = 0
    for c in contours:
        if cv2.contourArea(c) > 10:
            object_count += 1
            
    return f"--- Contagem de Objetos (5c) ---\nTotal (objetos > 10 pixels): {object_count}"

# --- Função: Pipeline de Processamento ---
def run_pipeline_on_image(image, pipeline, values):
    if image is None:
        return None, "Nenhuma imagem de entrada."
        
    processed_img = image.copy()
    log_message = "Pipeline:\n"
    
    grayscale_required = ['-OTSU-', '-CANNY-', '-EQ-', '-LAP-', '-SOBEL-', '-PRE-', '-ROB-']

    for filter_event in pipeline:
        try:
            if filter_event in grayscale_required and len(processed_img.shape) > 2:
                processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
                log_message += "- (Auto) Níveis de Cinza\n"

            if filter_event == '-GRAY-':
                if len(processed_img.shape) > 2:
                    processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
                log_message += "- Níveis de Cinza\n"
            
            elif filter_event == '-NEG-':
                processed_img = pdi.negativo(processed_img)
                log_message += "- Negativo\n"
            
            elif filter_event == '-OTSU-':
                thresh_val, processed_img = pdi.otsu(processed_img)
                log_message += f"- Otsu (Limiar={thresh_val})\n"

            elif filter_event == '-MEAN-':
                k = int(values['-K_SMOOTH-'])
                processed_img = pdi.media(processed_img, k)
                log_message += f"- Média (k={k})\n"
            
            elif filter_event == '-MEDIAN-':
                k = int(values['-K_SMOOTH-'])
                processed_img = pdi.mediana(processed_img, k)
                log_message += f"- Mediana (k={k})\n"
            
            elif filter_event == '-CANNY-':
                t1, t2 = int(values['-T1-']), int(values['-T2-'])
                processed_img = pdi.canny(processed_img, t1, t2)
                log_message += f"- Canny (T1={t1}, T2={t2})\n"
            
            elif filter_event in ('-ERODE-', '-DILATE-', '-OPEN-', '-CLOSE-'):
                k = int(values['-K_MORPH-'])
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
                if filter_event == '-ERODE-':
                    processed_img = pdi.erosao(processed_img, kernel)
                    log_message += f"- Erosão (k={k})\n"
                elif filter_event == '-DILATE-':
                    processed_img = pdi.dilatacao(processed_img, kernel)
                    log_message += f"- Dilatação (k={k})\n"
                elif filter_event == '-OPEN-':
                    processed_img = pdi.abertura(processed_img, kernel)
                    log_message += f"- Abertura (k={k})\n"
                elif filter_event == '-CLOSE-':
                    processed_img = pdi.fechamento(processed_img, kernel)
                    log_message += f"- Fechamento (k={k})\n"
            
            elif filter_event == '-LOG-':
                processed_img = pdi.logaritmico(processed_img)
                log_message += "- Logarítmico\n"
            elif filter_event == '-EQ-':
                processed_img = pdi.equalizacao(processed_img)
                log_message += "- Equalização\n"
            elif filter_event == '-LAP-':
                processed_img = pdi.laplaciano(processed_img)
                log_message += "- Laplaciano\n"
            elif filter_event == '-SOBEL-':
                processed_img = pdi.sobel(processed_img)
                log_message += "- Sobel\n"
            elif filter_event == '-PRE-':
                processed_img = pdi.prewitt(processed_img)
                log_message += "- Prewitt\n"
            elif filter_event == '-ROB-':
                processed_img = pdi.roberts(processed_img)
                log_message += "- Roberts\n"
            elif filter_event == '-POT-':
                c = float(values['-C_POT-'])
                g = float(values['-G_POT-'])
                processed_img = pdi.potencia(processed_img, c, g)
                log_message += f"- Potência (C={c}, G={g})\n"

        except ValueError:
            return image, f"[ERRO] Valor inválido para {filter_event}.\nPipeline interrompido."
        except Exception as e:
            return image, f"[ERRO] Falha ao aplicar {filter_event}:\n{e}\nPipeline interrompido."
                
    return processed_img, log_message

# --- Definição do Layout da GUI ---
def create_layout():
    """ Cria o layout da janela principal (Versão Estilizada DarkGrey15) """
    
    image_display_size = (400, 400) 

    BG_COLOR = '#23272A'
    TXT_COLOR = '#FFFFFF'
    FRAME_BG = '#2C2F33'
    INPUT_BG = '#40444B'
    BTN_COLOR = ('#FFFFFF', '#7289DA')
    BTN_RED = ('#FFFFFF', '#D83C3E')
    FRAME_TITLE_COLOR = '#99AAB5'

    FONT_TITULO = ("Helvetica", 12, "bold")
    FONT_CORPO = ("Helvetica", 10)
    FONT_BOTAO = ("Helvetica", 10)
    
    # --- Coluna 1: Controles --- 
    col_req2 = [
        [sg.Button("1. Carregar Imagem", key='-LOAD-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("2. Câmera", key='-CAM_LIVE-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("3. Carregar Vídeo", key='-LOAD_VIDEO-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Text("Arquivo:", size=(8,1), font=FONT_CORPO, background_color=FRAME_BG), 
         sg.Text("Nenhum", key='-FILENAME-', expand_x=True, font=FONT_CORPO, background_color=FRAME_BG)]
    ]
    
    col_detect = [
        [sg.Button("Detector (Celular)", key='-RUN_YOLO-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("Detector TLOU", key='-RUN_WEAPON-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)]
    ]

    col_req3 = [
        [sg.Button("a. Níveis de Cinza", key='-GRAY-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("b. Negativo", key='-NEG-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("c. Binário (Otsu)", key='-OTSU-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)]
    ]

    col_req4a = [
        [sg.Text("Kernel:", size=(8,1), font=FONT_CORPO, background_color=FRAME_BG), 
         sg.Input("5", size=(5,1), key='-K_SMOOTH-', font=FONT_CORPO, background_color=INPUT_BG, text_color=TXT_COLOR)],
        [sg.Button("Média", key='-MEAN-', font=FONT_BOTAO, button_color=BTN_COLOR), 
         sg.Button("Mediana", key='-MEDIAN-', font=FONT_BOTAO, button_color=BTN_COLOR)]
    ]

    col_req4b = [
        [sg.Text("T1:", size=(3,1), font=FONT_CORPO, background_color=FRAME_BG), 
         sg.Input("100", size=(5,1), key='-T1-', font=FONT_CORPO, background_color=INPUT_BG, text_color=TXT_COLOR)],
        [sg.Text("T2:", size=(3,1), font=FONT_CORPO, background_color=FRAME_BG), 
         sg.Input("200", size=(5,1), key='-T2-', font=FONT_CORPO, background_color=INPUT_BG, text_color=TXT_COLOR)],
        [sg.Button("Aplicar", key='-CANNY-', font=FONT_BOTAO, button_color=BTN_COLOR)]
    ]
    
    col_req4c = [
        [sg.Text("Kernel:", size=(8,1), font=FONT_CORPO, background_color=FRAME_BG), 
         sg.Input("5", size=(5,1), key='-K_MORPH-', font=FONT_CORPO, background_color=INPUT_BG, text_color=TXT_COLOR)],
        [sg.Button("Erosão", key='-ERODE-', font=FONT_BOTAO, button_color=BTN_COLOR), 
         sg.Button("Dilatação", key='-DILATE-', font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("Abertura", key='-OPEN-', font=FONT_BOTAO, button_color=BTN_COLOR), 
         sg.Button("Fechamento", key='-CLOSE-', font=FONT_BOTAO, button_color=BTN_COLOR)]
    ]
    
    col_req5 = [
        [sg.Button("a. Histograma", key='-HIST-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("b. Propriedades", key='-PROPS-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("c. Contagem de Objetos", key='-COUNT-', expand_x=True, font=FONT_BOTAO, button_color=BTN_COLOR)]
    ]
    
    col_extras = [
        [sg.Button("Log", key='-LOG-', font=FONT_BOTAO, button_color=BTN_COLOR), 
         sg.Button("Equalizar", key='-EQ-', font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("Laplaciano", key='-LAP-', font=FONT_BOTAO, button_color=BTN_COLOR), 
         sg.Button("Sobel", key='-SOBEL-', font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Button("Prewitt", key='-PRE-', font=FONT_BOTAO, button_color=BTN_COLOR), 
         sg.Button("Roberts", key='-ROB-', font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Frame("Potência:", [[
            sg.Text("C:", size=(2,1), font=FONT_CORPO, background_color=FRAME_BG), 
            sg.Input("1.0", size=(4,1), key='-C_POT-', font=FONT_CORPO, background_color=INPUT_BG, text_color=TXT_COLOR),
            sg.Text("G:", size=(2,1), font=FONT_CORPO, background_color=FRAME_BG), 
            sg.Input("1.0", size=(4,1), key='-G_POT-', font=FONT_CORPO, background_color=INPUT_BG, text_color=TXT_COLOR),
            sg.Button("Aplicar", key='-POT-', font=FONT_BOTAO, button_color=BTN_COLOR)
        ]], font=FONT_CORPO, background_color=FRAME_BG, title_color=FRAME_TITLE_COLOR, border_width=0)]
    ]

    # --- Estilo dos Frames ---
    frame_opts = {
        'font': FONT_TITULO, 
        'title_color': FRAME_TITLE_COLOR, 
        'background_color': FRAME_BG, 
        'expand_x': True,
        'border_width': 1,
        'relief': sg.RELIEF_SOLID
    }

    # Montagem da Coluna de Controle
    control_column = [
        [sg.Frame("Aquisição", col_req2, **frame_opts)],
        [sg.Frame("Detecção", col_detect, **frame_opts)],
        [sg.Frame("Conversões", col_req3, **frame_opts)],
        [sg.Frame("Suavização", col_req4a, **frame_opts)],
        [sg.Frame("Canny", col_req4b, **frame_opts)],
        [sg.Frame("Morfologia", col_req4c, **frame_opts)],
        [sg.Frame("Análise", col_req5, **frame_opts)],
        [sg.Frame("Funções Extras", col_extras, **frame_opts)],
        [sg.Frame("Saída de Texto:", [[
            sg.Multiline(size=(45, 8), key='-OUTPUT-', autoscroll=True, disabled=True, 
                         font=FONT_CORPO, background_color=INPUT_BG, text_color=TXT_COLOR)
        ]], **frame_opts)],
        [sg.Button("Sair", key='-EXIT-', button_color=BTN_RED, expand_x=True, font=FONT_BOTAO, size=(0, 2), pad=((5,5), (10,5)))]
    ]

    # --- Coluna 2: Imagens ---
    image_column = [
        [sg.Text("Imagem Original / Câmera", font=FONT_TITULO, background_color=BG_COLOR), 
         sg.Button("Restaurar Original (Limpar Filtros)", key='-RESET-', font=FONT_BOTAO, button_color=BTN_COLOR)],
        [sg.Image(key='-IMG_ORIG-', size=image_display_size, background_color=FRAME_BG)],
        [sg.Text("Imagem Processada", font=FONT_TITULO, background_color=BG_COLOR)],
        [sg.Image(key='-IMG_PROC-', size=image_display_size, background_color=FRAME_BG)]
    ]

    # --- Layout Final ---
    layout = [
        [sg.Column(control_column, scrollable=True, vertical_scroll_only=True, size=(450, 700), background_color=BG_COLOR),
         sg.VSeperator(color=FRAME_BG),
         sg.Column(image_column, background_color=BG_COLOR)]
    ]
    
    return layout

# --- Função Principal da GUI ---
def main():
    sg.theme("DarkGrey15")
    
    layout = create_layout()
    window = sg.Window("Trabalho Computacional 1", layout, 
                       finalize=True, 
                       background_color='#23272A')

    original_image = None
    current_image = None
    img_size = (400, 400)

    cam_mode = False
    cap = None
    active_pipeline = []
    last_processed_frame = None

    filter_events = [
        '-GRAY-', '-NEG-', '-OTSU-', '-MEAN-', '-MEDIAN-', '-CANNY-',
        '-ERODE-', '-DILATE-', '-OPEN-', '-CLOSE-',
        '-LOG-', '-EQ-', '-LAP-', '-SOBEL-', '-PRE-', '-ROB-', '-POT-'
    ]
    
    action_events = ['-HIST-', '-PROPS-', '-COUNT-']

    def stop_media():
        nonlocal cam_mode, cap, active_pipeline
        cam_mode = False
        if cap:
            cap.release()
            cap = None
        
        active_pipeline = []
        window['-FILENAME-'].update("Nenhum")
        window['-OUTPUT-'].update("Mídia parada.")
        window['-IMG_ORIG-'].update(data=None, size=img_size)
        window['-IMG_PROC-'].update(data=None, size=img_size)
        window['-LOAD-'].disabled = False
        window['-CAM_LIVE-'].disabled = False
        window['-LOAD_VIDEO-'].disabled = False

    # Loop de Eventos
    while True:
        event, values = window.read(timeout=20 if cam_mode else None)

        if event in (sg.WIN_CLOSED, '-EXIT-'):
            break
            
        # --- Evento de Timeout (Loop da Câmera OU Vídeo) ---
        if event == sg.TIMEOUT_EVENT and cam_mode:
            if cap is None: continue
            
            ret, frame = cap.read()
            if not ret:
                # Se 'ret' for falso, ou a câmera falhou ou o vídeo terminou
                is_live_cam = (window['-FILENAME-'].get() == "Câmera ao Vivo")
                
                if is_live_cam:
                    sg.popup_error("Erro ao ler frame da webcam. Parando a câmera.")
                else:
                    window['-OUTPUT-'].update("Vídeo terminado.")
                stop_media() 
                continue

            window['-IMG_ORIG-'].update(data=convert_to_bytes(frame, resize=img_size))
            
            processed_frame, log_msg = run_pipeline_on_image(frame, active_pipeline, values)
            
            last_processed_frame = processed_frame.copy() if processed_frame is not None else frame.copy()
            window['-IMG_PROC-'].update(data=convert_to_bytes(processed_frame, resize=img_size))
            
            continue 

        # --- Eventos de Botões ---  
        # --- Aquisição ---
        if event == '-LOAD-':
            # Limpa stream de vídeo se estiver rodando
            if cam_mode:
                stop_media() # Chama a função de parada
            
            file_types = [("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif"), ("Todos", "*.*")]
            path = sg.popup_get_file("Selecione uma imagem", file_types=file_types)
            if path:
                try:
                    original_image = cv2.imread(path, cv2.IMREAD_COLOR)
                    current_image = original_image.copy()
                    active_pipeline = [] 
                    window['-FILENAME-'].update(os.path.basename(path))
                    window['-IMG_ORIG-'].update(data=convert_to_bytes(original_image, resize=img_size))
                    window['-IMG_PROC-'].update(data=convert_to_bytes(current_image, resize=img_size))
                    window['-OUTPUT-'].update("Imagem carregada. Pipeline de filtros reiniciado.")
                    window['-CAM_LIVE-'].disabled = False
                    window['-LOAD_VIDEO-'].disabled = False
                except Exception as e:
                    sg.popup_error(f"Erro ao carregar a imagem:\n{e}")

        elif event == '-CAM_LIVE-':
            if cam_mode: 
                stop_media()
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                sg.popup_error("Erro: Não foi possível abrir a câmera.")
                cap = None
            else:
                cam_mode = True
                active_pipeline = []
                window['-FILENAME-'].update("Câmera ao Vivo")
                window['-OUTPUT-'].update("Câmera iniciada. Adicione filtros.")
                window['-LOAD-'].disabled = True
                window['-LOAD_VIDEO-'].disabled = True

        elif event == '-LOAD_VIDEO-':
            if cam_mode:
                stop_media()
            
            video_path = sg.popup_get_file("Selecione um arquivo de vídeo", file_types=[("Arquivos de Vídeo", "*.mp4 *.avi *.mkv *.mov"), ("Todos", "*.*")])
            
            if video_path:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    sg.popup_error(f"Erro: Não foi possível abrir o vídeo:\n{video_path}")
                    cap = None
                else:
                    cam_mode = True
                    active_pipeline = []
                    window['-FILENAME-'].update(os.path.basename(video_path))
                    window['-OUTPUT-'].update("Vídeo carregado. Adicione filtros.")
                    window['-LOAD-'].disabled = True
                    window['-CAM_LIVE-'].disabled = True
            
        elif event == '-RESET-':
            active_pipeline = []
            if cam_mode:
                window['-OUTPUT-'].update("Pipeline de filtros reiniciado.")
            elif original_image is not None:
                current_image = original_image.copy()
                window['-IMG_PROC-'].update(data=convert_to_bytes(current_image, resize=img_size))
                window['-OUTPUT-'].update("Pipeline reiniciado. Imagem restaurada ao original.")
            else:
                window['-OUTPUT-'].update("Pipeline reiniciado.")

        # --- Eventos de Detectores ---
        elif event == '-RUN_YOLO-':
            try:
                window['-OUTPUT-'].update("Iniciando detector (Celular/Pessoa) em janela separada...")
                subprocess.Popen([sys.executable, 'webcam_detector.py'])
            except Exception as e:
                sg.popup_error(f"Falha ao iniciar 'webcam_detector.py':\n{e}")
        
        elif event == '-RUN_WEAPON-': 
            try:
                window['-OUTPUT-'].update("Iniciando detector de Armas em janela separada...")
                subprocess.Popen([sys.executable, 'weapon_detector-tlof.py'])
            except Exception as e:
                sg.popup_error(f"Falha ao iniciar 'weapon_detector-tlof.py':\n{e}\n\nCertifique-se de ter baixado o modelo de armas para a pasta 'weapon_model'.")

        # --- Eventos de Filtros ---
        elif event in filter_events:
            if not cam_mode and original_image is None:
                sg.popup_error("Nenhuma imagem ou vídeo carregado!", "Carregue uma imagem, vídeo ou inicie a câmera.")
                continue
            
            active_pipeline.append(event)
            log_msg = f"Filtro '{event}' adicionado ao pipeline."
            
            if not cam_mode:
                processed_image, log_msg = run_pipeline_on_image(original_image, active_pipeline, values)
                if processed_image is not None:
                    current_image = processed_image
                    window['-IMG_PROC-'].update(data=convert_to_bytes(current_image, resize=img_size))
                
            window['-OUTPUT-'].update(log_msg)

        # --- Eventos de Análise ---
        elif event in action_events:
            target_image = None
            if cam_mode:
                target_image = last_processed_frame
            else:
                target_image = current_image 
                
            if target_image is None:
                sg.popup_error("Nenhuma imagem processada para analisar.", "Carregue uma imagem ou inicie a câmera e aplique filtros.")
                continue
            
            try:
                if event == '-HIST-':
                    pdi.mostrar_histograma(target_image)
                    window['-OUTPUT-'].update("Histograma exibido em nova janela.")
                
                elif event == '-PROPS-':
                    output_text = gui_5b_binary_properties(target_image)
                    window['-OUTPUT-'].update(output_text)
                
                elif event == '-COUNT-':
                    output_text = gui_5c_object_counting(target_image)
                    window['-OUTPUT-'].update(output_text)
                    
            except Exception as e:
                sg.popup_error(f"Erro durante a análise '{event}':\n{e}")

    # --- Limpeza ---
    if cap:
        cap.release()
    window.close()

if __name__ == "__main__":
    main()