import cv2

def laplaciano(img):
    return cv2.Laplacian(img, cv2.CV_64F)

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

lena_f = laplaciano(lena)
aluno_f = laplaciano(aluno)

cv2.imshow('Lena Laplaciano', lena_f)
cv2.imshow('Aluno Laplaciano', aluno_f)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_laplaciano_lena.png', lena_f)
cv2.imwrite('saida_laplaciano_aluno.jpg', aluno_f)
