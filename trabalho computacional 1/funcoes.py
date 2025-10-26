import cv2
import numpy as np
import matplotlib.pyplot as plt

def negativo(img):
    return 255 - img

def otsu(img_gray):
    return cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

def media(img, k=3):
    return cv2.blur(img, (k, k))

def mediana(img, k=3):
    if k % 2 == 0: # medianBlur exige kernel ímpar
        k += 1
    return cv2.medianBlur(img, k)

def canny(img, t1, t2):
    return cv2.Canny(img, t1, t2)

def erosao(img, kernel):
    return cv2.erode(img, kernel, iterations=1)

def dilatacao(img, kernel):
    return cv2.dilate(img, kernel, iterations=1)

def abertura(img, kernel):
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

def fechamento(img, kernel):
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

def mostrar_histograma(img):
    print("Calculando e exibindo histograma...")
    plt.figure(figsize=(10, 6))
    if len(img.shape) == 2:
        plt.hist(img.ravel(), 256, [0, 256])
        plt.title('Histograma (Níveis de Cinza)')
    else:
        color = ('b', 'g', 'r')
        for i, col in enumerate(color):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
        plt.title('Histograma (Cores BGR)')
        plt.legend(['Azul (B)', 'Verde (G)', 'Vermelho (R)'])
    plt.grid(True)
    print("Exibindo histograma. Feche a janela do Matplotlib para continuar...")
    plt.show()

def logaritmico(img):
    img_float = img.astype(np.float32)
    c = 255 / np.log(1 + np.max(img_float))
    log_img = c * np.log(1 + img_float)
    return np.uint8(np.clip(log_img, 0, 255))

def potencia(img, c=1, gamma=1):
    img_float = img.astype(np.float32) / 255
    pot_img = c * (img_float ** gamma)
    return np.uint8(np.clip(pot_img * 255, 0, 255))

def equalizacao(img):
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img
    return cv2.equalizeHist(img_gray)

def laplaciano(img):
    return cv2.Laplacian(img, cv2.CV_64F)

def roberts(img):
    kernelx = np.array([[1, 0], [0, -1]], dtype=np.float32)
    kernely = np.array([[0, 1], [-1, 0]], dtype=np.float32)
    x = cv2.filter2D(img, -1, kernelx)
    y = cv2.filter2D(img, -1, kernely)
    return cv2.convertScaleAbs(x + y)

def prewitt(img):
    kernelx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)
    kernely = np.array([[1,1,1],[0,0,0],[-1,-1,-1]], dtype=np.float32)
    x = cv2.filter2D(img, -1, kernelx)
    y = cv2.filter2D(img, -1, kernely)
    return cv2.convertScaleAbs(x + y)

def sobel(img):
    x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    return cv2.convertScaleAbs(x + y)