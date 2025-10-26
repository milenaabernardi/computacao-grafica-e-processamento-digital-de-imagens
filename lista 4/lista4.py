import cv2
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


img1 = cv2.imread('circuito.tif', cv2.IMREAD_GRAYSCALE)
med1 = cv2.medianBlur(img1, 3)
med2 = cv2.medianBlur(med1, 3)
med3 = cv2.medianBlur(med2, 3)
cv2.imwrite("circuito_original.jpg", img1)
cv2.imwrite("circuito_mediana1.jpg", med1)
cv2.imwrite("circuito_mediana2.jpg", med2)
cv2.imwrite("circuito_mediana3.jpg", med3)


img2 = cv2.imread("pontos.png", cv2.IMREAD_GRAYSCALE)
kernel = np.array([[0,-1,0],[-1,8,-1],[0,-1,0]], dtype=np.float32)
resp = cv2.filter2D(img2, -1, kernel)
_, pontos = cv2.threshold(resp, 200, 255, cv2.THRESH_BINARY)
cv2.imwrite("pontos_original.jpg", img2)
cv2.imwrite("pontos_detectados.jpg", pontos)


img3 = cv2.imread("linhas.png", cv2.IMREAD_GRAYSCALE)
kh = np.array([[-1,-1,-1],[2,2,2],[-1,-1,-1]], np.float32)
kv = kh.T
kd1 = np.array([[2,-1,-1],[-1,2,-1],[-1,-1,2]], np.float32)
kd2 = np.array([[-1,-1,2],[-1,2,-1],[2,-1,-1]], np.float32)
resp_h = cv2.filter2D(img3, -1, kh)
resp_v = cv2.filter2D(img3, -1, kv)
resp_d1 = cv2.filter2D(img3, -1, kd1)
resp_d2 = cv2.filter2D(img3, -1, kd2)
_, bh = cv2.threshold(resp_h, 80, 255, cv2.THRESH_BINARY)
_, bv = cv2.threshold(resp_v, 80, 255, cv2.THRESH_BINARY)
_, bd1 = cv2.threshold(resp_d1, 80, 255, cv2.THRESH_BINARY)
_, bd2 = cv2.threshold(resp_d2, 80, 255, cv2.THRESH_BINARY)
final = cv2.bitwise_or(cv2.bitwise_or(bh, bv), cv2.bitwise_or(bd1, bd2))
cv2.imwrite("linhas_original.jpg", img3)
cv2.imwrite("linhas_detectadas.jpg", final)


img4 = cv2.imread("igreja.png", cv2.IMREAD_GRAYSCALE)
canny = cv2.Canny(img4, 100, 200)
cv2.imwrite("igreja_original.jpg", img4)
cv2.imwrite("igreja_canny.jpg", canny)


def region_growing(img, seed, tol=15):
    h, w = img.shape
    seed_val = int(img[seed[1], seed[0]])
    mask = np.zeros_like(img, np.uint8)
    stack = [seed]
    while stack:
        x, y = stack.pop()
        if mask[y, x] == 0 and abs(int(img[y, x]) - seed_val) <= tol:
            mask[y, x] = 255
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        stack.append((nx, ny))
    return mask

img5_color = cv2.imread("root.jpg")
img5_gray = cv2.cvtColor(img5_color, cv2.COLOR_BGR2GRAY)
seed = (400, 350)  
mask = region_growing(img5_gray, seed, tol=18)
highlight = img5_color.copy()
highlight[mask==255] = [0,0,0]
cv2.imwrite("root_original.jpg", img5_color)
cv2.imwrite("root_segmentada.jpg", highlight)

arquivos = ["harewood.jpg", "nuts.jpg", "snow.jpg", "img_aluno.jpg"]
for arq in arquivos:
    img6 = cv2.imread(arq, cv2.IMREAD_GRAYSCALE)
    if img6 is None: 
        continue
    _, otsu = cv2.threshold(img6, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imwrite(arq.replace(".jpg","")+"_original.jpg", img6)
    cv2.imwrite(arq.replace(".jpg","")+"_otsu.jpg", otsu)


doc = SimpleDocTemplate("Resultados_Lista4.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = []

def add_img(title, path, w=400, h=300):
    story.append(Paragraph(title, styles["Heading3"]))
    story.append(Spacer(1, 10))
    story.append(Image(path, width=w, height=h))
    story.append(Spacer(1, 20))

add_img("Exercício 1 - Circuito Original", "circuito_original.jpg")
add_img("Exercício 1 - Mediana 1", "circuito_mediana1.jpg")
add_img("Exercício 1 - Mediana 2", "circuito_mediana2.jpg")
add_img("Exercício 1 - Mediana 3", "circuito_mediana3.jpg")

add_img("Exercício 2 - Pontos Originais", "pontos_original.jpg")
add_img("Exercício 2 - Pontos Detectados", "pontos_detectados.jpg")

add_img("Exercício 3 - Linhas Original", "linhas_original.jpg")
add_img("Exercício 3 - Linhas Detectadas", "linhas_detectadas.jpg")

add_img("Exercício 4 - Igreja Original", "igreja_original.jpg")
add_img("Exercício 4 - Bordas Canny", "igreja_canny.jpg")

add_img("Exercício 5 - Root Original", "root_original.jpg")
add_img("Exercício 5 - Root Segmentada", "root_segmentada.jpg")

add_img("Exercício 6 - Harewood Original", "harewood_original.jpg")
add_img("Exercício 6 - Harewood Otsu", "harewood_otsu.jpg")
add_img("Exercício 6 - Nuts Original", "nuts_original.jpg")
add_img("Exercício 6 - Nuts Otsu", "nuts_otsu.jpg")
add_img("Exercício 6 - Snow Original", "snow_original.jpg")
add_img("Exercício 6 - Snow Otsu", "snow_otsu.jpg")
add_img("Exercício 6 - Img Aluno Original", "img_aluno_original.jpg")
add_img("Exercício 6 - Img Aluno Otsu", "img_aluno_otsu.jpg")

doc.build(story)
