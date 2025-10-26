import cv2
import numpy as np

def potencia(img, c=1, gamma=1):
    img = img.astype(np.float32) / 255
    pot_img = c * (img ** gamma)
    return np.uint8(np.clip(pot_img * 255, 0, 255))

lena = cv2.imread('lena.png')
aluno = cv2.imread('img_aluno.jpg')

pot_lena = potencia(lena, 2, 2)
pot_aluno = potencia(aluno, 2, 2)

cv2.imshow('Lena Potência', pot_lena)
cv2.imshow('Aluno Potência', pot_aluno)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_pot_lena.png', pot_lena)
cv2.imwrite('saida_pot_aluno.png', pot_aluno)
