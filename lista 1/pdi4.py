import cv2
import numpy as np

def logaritmico(img):
    img = img.astype(np.float32)
    c = 255 / np.log(1 + np.max(img))
    log_img = c * np.log(1 + img)
    return np.uint8(np.clip(log_img, 0, 255))

lena = cv2.imread('lena.png')
aluno = cv2.imread('img_aluno.jpg')

log_lena = logaritmico(lena)
log_aluno = logaritmico(aluno)

cv2.imshow('Lena Log', log_lena)
cv2.imshow('Aluno Log', log_aluno)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_log_lena.png', log_lena)
cv2.imwrite('saida_log_aluno.png', log_aluno)
