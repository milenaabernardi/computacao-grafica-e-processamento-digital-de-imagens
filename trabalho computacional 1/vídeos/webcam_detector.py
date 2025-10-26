import cv2
import numpy as np
import os

# --- 1. Definir Caminhos e Constantes ---
MODEL_DIR = "yolo_model"
WEIGHTS_PATH = os.path.join(MODEL_DIR, "yolov3-tiny.weights")
CONFIG_PATH = os.path.join(MODEL_DIR, "yolov3-tiny.cfg")
NAMES_PATH = os.path.join(MODEL_DIR, "coco.names")

CLASSE_ALVO = "cell phone"

CONF_THRESHOLD = 0.3 
NMS_THRESHOLD = 0.4  

# --- 2. Carregar o Modelo e as Classes ---
if not all(os.path.exists(p) for p in [WEIGHTS_PATH, CONFIG_PATH, NAMES_PATH]):
    print("Erro: Arquivos do modelo YOLO não encontrados na pasta 'yolo_model'.")
    print("Por favor, baixe 'yolov3-tiny.weights', 'yolov3-tiny.cfg' e 'coco.names'.")
    exit()

try:
    with open(NAMES_PATH, "r") as f:
        classes = [line.strip() for line in f.readlines()]
except Exception as e:
    print(f"Erro ao ler o arquivo de classes: {e}")
    exit()

try:
    net = cv2.dnn.readNet(WEIGHTS_PATH, CONFIG_PATH)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
except cv2.error as e:
    print(f"Erro ao carregar o modelo YOLO: {e}")
    print("Verifique se os arquivos .weights e .cfg estão corretos.")
    exit()

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

print(f"Modelo YOLO carregado. Procurando por: '{CLASSE_ALVO}'")

# --- 3. Inicializar a Webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível acessar a câmera.")
    exit()

# --- 4. Loop Principal ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao ler frame da webcam.")
        break
        
    (H, W) = frame.shape[:2] 

    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)

    net.setInput(blob)
    layerOutputs = net.forward(output_layers)

    boxes = []     
    confidences = [] 
    class_ids = []   

    # --- 5. Processar as Saídas da Rede ---
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]      
            class_id = np.argmax(scores)  
            confidence = scores[class_id] 
            
            if confidence > CONF_THRESHOLD and classes[class_id] == CLASSE_ALVO:
                
                box_coords = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box_coords.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # --- 6. Aplicar Supressão Não-Máxima (NMS) ---
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)

    # --- 7. Desenhar os Resultados no Frame ---
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            text = f"{classes[class_ids[i]]}: {confidences[i]:.2%}"
            cv2.putText(frame, text, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # --- 8. Exibir o Frame ---
    cv2.imshow("Detector de Celular (YOLO) - Pressione 'q' para sair", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 9. Limpeza ---
print("Encerrando...")
cap.release()
cv2.destroyAllWindows()