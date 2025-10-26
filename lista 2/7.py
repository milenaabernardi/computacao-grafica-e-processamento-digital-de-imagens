import cv2

def sobel(img):
    x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    return cv2.convertScaleAbs(x + y)

lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
aluno = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)

lena_f = sobel(lena)
aluno_f = sobel(aluno)

cv2.imshow('Lena Sobel', lena_f)
cv2.imshow('Aluno Sobel', aluno_f)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_sobel_lena.png', lena_f)
cv2.imwrite('saida_sobel_aluno.jpg', aluno_f)
