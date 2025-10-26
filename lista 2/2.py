import cv2

def media_k_vizinhos(img, h=10):
    return cv2.fastNlMeansDenoising(img, None, h, 7, 21)

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

lena_f = media_k_vizinhos(lena, 15)
aluno_f = media_k_vizinhos(aluno, 15)

cv2.imshow('Lena K-vizinhos', lena_f)
cv2.imshow('Aluno K-vizinhos', aluno_f)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_kviz_lena.png', lena_f)
cv2.imwrite('saida_kviz_aluno.png', aluno_f)
