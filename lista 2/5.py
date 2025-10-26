import cv2
import numpy as np

def roberts(img):
    kernelx = np.array([[1, 0], [0, -1]], dtype=np.float32)
    kernely = np.array([[0, 1], [-1, 0]], dtype=np.float32)
    x = cv2.filter2D(img, -1, kernelx)
    y = cv2.filter2D(img, -1, kernely)
    return cv2.convertScaleAbs(x + y)

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

lena_f = roberts(lena)
aluno_f = roberts(aluno)

cv2.imshow('Lena Roberts', lena_f)
cv2.imshow('Aluno Roberts', aluno_f)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_roberts_lena.png', lena_f)
cv2.imwrite('saida_roberts_aluno.jpg', aluno_f)
