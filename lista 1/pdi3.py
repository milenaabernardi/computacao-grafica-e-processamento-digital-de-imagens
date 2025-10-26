import cv2

def normalizacao(img, new_min, new_max):
    return cv2.normalize(img, None, alpha=new_min, beta=new_max, norm_type=cv2.NORM_MINMAX)

lena = cv2.imread('lena.png')
aluno = cv2.imread('img_aluno.jpg')

norm_lena = normalizacao(lena, 0, 100)
norm_aluno = normalizacao(aluno, 0, 100)

cv2.imshow('Lena Normalizada', norm_lena)
cv2.imshow('Aluno Normalizado', norm_aluno)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_norm_lena.png', norm_lena)
cv2.imwrite('saida_norm_aluno.png', norm_aluno)
