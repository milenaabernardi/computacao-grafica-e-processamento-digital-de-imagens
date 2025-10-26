import cv2
import matplotlib.pyplot as plt

def mostrar_histograma(img, titulo):
    h = cv2.calcHist([img], [0], None, [256], [0, 256])
    plt.plot(h)
    plt.title(titulo)
    plt.show()

unequalized = cv2.imread('unequalized.jpg')
aluno = cv2.imread('img_aluno.jpg')

gray_uneq = cv2.cvtColor(unequalized, cv2.COLOR_BGR2GRAY)
mostrar_histograma(gray_uneq, "Histograma Unequalized (Gray)")

for i, cor in enumerate(['B','G','R']):
    h = cv2.calcHist([aluno], [i], None, [256], [0, 256])
    plt.plot(h, label=cor)
plt.title("Histograma RGB - img_aluno")
plt.legend()
plt.show()

gray_aluno = cv2.cvtColor(aluno, cv2.COLOR_BGR2GRAY)
mostrar_histograma(gray_aluno, "Histograma Gray - img_aluno")
