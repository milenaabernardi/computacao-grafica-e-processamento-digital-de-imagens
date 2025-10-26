import cv2

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

cv2.imshow('Lena Cinza', lena)
cv2.imshow('Aluno Cinza', aluno)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_cinza_lena.png', lena)
cv2.imwrite('saida_cinza_aluno.png', aluno)