import cv2

lena = cv2.imread('lena.png')
aluno = cv2.imread('img_aluno.jpg')

neg_lena = 255 - lena
neg_aluno = 255 - aluno

cv2.imshow('Negativo Lena', neg_lena)
cv2.imshow('Negativo Aluno', neg_aluno)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_negativo_lena.png', neg_lena)
cv2.imwrite('saida_negativo_aluno.png', neg_aluno)
