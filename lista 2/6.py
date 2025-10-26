import cv2
import numpy as np

def prewitt(img):
    kernelx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)
    kernely = np.array([[1,1,1],[0,0,0],[-1,-1,-1]], dtype=np.float32)
    x = cv2.filter2D(img, -1, kernelx)
    y = cv2.filter2D(img, -1, kernely)
    return cv2.convertScaleAbs(x + y)

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

lena_f = prewitt(lena)
aluno_f = prewitt(aluno)

cv2.imshow('Lena Prewitt', lena_f)
cv2.imshow('Aluno Prewitt', aluno_f)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_prewitt_lena.png', lena_f)
cv2.imwrite('saida_prewitt_aluno.jpg', aluno_f)
