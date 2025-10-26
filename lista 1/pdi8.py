import cv2

def equalizacao(img):
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img
    return cv2.equalizeHist(img_gray)

lena = cv2.imread('lena.png')
unequalized = cv2.imread('unequalized.jpg')
aluno = cv2.imread('img_aluno.jpg')

eq_lena = equalizacao(lena)
eq_uneq = equalizacao(unequalized)
eq_aluno = equalizacao(aluno)

cv2.imshow('Lena Equalizada', eq_lena)
cv2.imshow('Unequalized Equalizada', eq_uneq)
cv2.imshow('Aluno Equalizada', eq_aluno)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('saida_eq_lena.png', eq_lena)
cv2.imwrite('saida_eq_unequalized.png', eq_uneq)
cv2.imwrite('saida_eq_aluno.png', eq_aluno)
