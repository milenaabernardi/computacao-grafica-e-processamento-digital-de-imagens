import cv2
import pygame
import os

# --- 1. CONFIGURAÇÕES ---
VIDEO_PATH = "The Last of Us Complete - Trailer de Lançamento.mp4"
SOUND_PATH = "the-last-of-us-clicker-sound-dlive.mp3"
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
WINDOW_NAME = "THE LAST OF US (WEAPON DETECTOR)" # Nome da janela simplificado

# --- 2. GABARITO COM COORDENADAS ---
WEAPON_DATA = [
    (12.312, 14.200, [(378, 189, 60, 72)]),
    (14.448, 15.400, [(664, 218, 177, 502)]),
    (15.415, 16.600, [(421, 375, 266, 345)]),
    (19.586, 21.520, [(588, 441, 87, 241)]),
    (23.500, 24.150, [(475, 220, 72, 78), (629, 0, 131, 450), (926, 0, 328, 714)]),
    (24.324, 26.350, [(182, 491, 314, 229)]),
    (28.595, 30.000, [(427, 404, 88, 90)]),
    (30.060, 30.992, [(429, 367, 110, 106)]),
    (36.092, 41.480, [(829, 431, 289, 289)]),
    (44.444, 45.540, [(1097, 224, 171, 496)]),
    (53.854, 54.245, [(302, 357, 102, 363)]),
    (54.254, 54.655, [(271, 304, 187, 385)]),
    (54.405, 54.700, [(274, 308, 154, 412)]),
    (54.855, 55.832, [(390, 167, 98, 215)]),
    (57.891, 58.345, [(296, 353, 278, 235)]),
    (61.150, 61.815, [(889, 270, 391, 450)]),
    (62.696, 63.100, [(134, 0, 356, 175)]),
    (67.267, 68.840, [(638, 476, 213, 200)]),
    (72.967, 73.550, [(416, 1, 348, 479)]), 
]

# --- 3. FUNÇÕES DE AJUDA ---
def get_boxes_for_time(current_seconds):
    """Verifica se o tempo atual está na lista e retorna as caixas."""
    for start, end, boxes in WEAPON_DATA:
        if start <= current_seconds < end:
            return boxes
    return []

# --- 4. CARREGAR SOM E VÍDEO ---
if not os.path.exists(VIDEO_PATH) or not os.path.exists(SOUND_PATH):
    print("Erro: Arquivo de vídeo ou som não encontrado.")
    exit()

try:
    pygame.mixer.init()
    alert_sound = pygame.mixer.Sound(SOUND_PATH)
except Exception as e:
    print(f"Erro ao carregar o som: {e}")
    exit()
music_playing = False

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Erro: Não foi possível abrir o arquivo de vídeo: {VIDEO_PATH}")
    exit()

cv2.namedWindow(WINDOW_NAME)

print(f"\nIniciando player... Pressione 'ESC' para sair.")
print(f"Aperte 'ESPAÇO' para pausar e despausar.")

is_paused = False

while cap.isOpened():
    # Se não estiver pausado, leia o próximo frame
    if not is_paused:
        ret, frame = cap.read()
        if not ret:
            print(">> O vídeo terminou.")
            break
            
        display_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        
    # --- 5. PROCESSAMENTO DE TEMPO E CAIXAS ---
    
    # Pega o tempo atual do vídeo em segundos
    current_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    
    # Verifica se o tempo atual está na nossa lista
    boxes_to_draw = get_boxes_for_time(current_sec)
    
    # Limpa o frame (copia) para redesenhar as caixas
    frame_com_caixas = display_frame.copy()
    
    if len(boxes_to_draw) > 0:
        if not is_paused:
            if not music_playing:
                print(f">> ARMA DETECTADA! (Tempo: {current_sec:.2f}s) Tocando som!")
                alert_sound.play(loops=-1)
                music_playing = True
            
        # Desenha todas as caixas para este momento
        for (x, y, w, h) in boxes_to_draw:
            cv2.rectangle(frame_com_caixas, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame_com_caixas, "Weapon", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
    else:
        # Para o som
        if music_playing:
            print(f">> Cena limpa. (Tempo: {current_sec:.2f}s) Parando som.")
            alert_sound.stop()
            music_playing = False
            
    # --- 6. EXIBIR O VÍDEO ---
    cv2.imshow(WINDOW_NAME, frame_com_caixas)

    # --- 7. CONTROLE DE PAUSA E TECLAS ---
    # Se pausado, espera indefinidamente. Se não, espera 25ms.
    wait_time = 0 if is_paused else 25
    key = cv2.waitKey(wait_time) 
    
    if key == 27:  # 'ESC' para sair
        break
    if key == 32:  # 'ESPAÇO' para pausar
        is_paused = not is_paused
        if is_paused:
            print(">> Vídeo pausado.") 
            alert_sound.stop()
        else:
            print(">> Vídeo retomado.")

# --- 8. LIMPEZA ---
alert_sound.stop()
cap.release()
cv2.destroyAllWindows()
print("Processamento finalizado.")