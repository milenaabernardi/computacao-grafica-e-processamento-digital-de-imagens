import cv2
import numpy as np

def planos_de_bits(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    planos = []
    for i in range(8):
        plano = (img >> i) & 1
        planos.append(np.uint8(plano * 255))
    return planos

lena = cv2.imread('lena.png')
aluno = cv2.imread('img_aluno.jpg')

planos_lena = planos_de_bits(lena)
planos_aluno = planos_de_bits(aluno)

for i, p in enumerate(planos_lena):
    cv2.imwrite(f'plano_lena_{i}.png', p)
for i, p in enumerate(planos_aluno):
    cv2.imwrite(f'plano_aluno_{i}.png', p)

cv2.imshow('Plano Lena 7', planos_lena[7]) 
cv2.imshow('Plano Aluno 7', planos_aluno[7])
cv2.waitKey(0)
cv2.destroyAllWindows()
