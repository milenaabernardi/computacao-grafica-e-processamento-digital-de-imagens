import cv2

def media(img, k=3):
    return cv2.blur(img, (k, k))

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

lena_f = media(lena, 5)
aluno_f = media(aluno, 5)

cv2.imshow('Lena Media', lena_f)
cv2.imshow('Aluno Media', aluno_f)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_media_lena.png', lena_f)
cv2.imwrite('saida_media_aluno.png', aluno_f)