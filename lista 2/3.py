import cv2

def mediana(img, k=3):
    return cv2.medianBlur(img, k)

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

lena_f = mediana(lena, 5)
aluno_f = mediana(aluno, 5)

cv2.imshow('Lena Mediana', lena_f)
cv2.imshow('Aluno Mediana', aluno_f)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_mediana_lena.png', lena_f)
cv2.imwrite('saida_mediana_aluno.jpg', aluno_f)
