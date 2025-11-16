import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import json
import os
import math
import sys

# Configurações da Janela
LARGURA_TELA = 800
ALTURA_TELA = 600

# Cores / constantes
COR_BRANCA = (255, 255, 255)
COR_ROXA = (170, 0, 255)

# Coletor
coletor_x = 0.0
coletor2_x = 2.0
coletor_y = -3.0
coletor2_y = -3.0 
COLETOR_MEIA_LARGURA = 0.8
COLETOR_MEIA_ALTURA = 0.8

# Cenário
LIMITE_ESQUERDA = -10.0
LIMITE_DIREITA = 10.0
LIMITE_TOPO = 8.0
LIMITE_FUNDO = -7.0

# Limites Y para o movimento do coletor
COLETOR_LIMITE_TOPO = 0.0
COLETOR_LIMITE_FUNDO = -6.0

# Ajuste de HITBOX (ESTRELA)---
ITEM_MEIA_LARGURA = 0.3
ITEM_MEIA_ALTURA = 0.3

# Luz
light_position = [5.0, 5.0, 5.0, 1.0]

# Objetivos
OBJETIVO_TEMPO_LIMITE = 60
OBJETIVO_ENCHER_PONTOS = 300
PONTOS_PERDIDOS_ZERAR = 15
VIDAS_INICIAIS = 3 

# Estados
ESTADO_MENU = "MENU"
ESTADO_SELECIONAR_DIFICULDADE = "SELECIONAR_DIFICULDADE" 
ESTADO_JOGANDO = "JOGANDO"
ESTADO_PAUSA = "PAUSA"
ESTADO_FIM = "FIM_DE_JOGO"

ARQUIVO_SCORES = "highscores.json"

# Fontes
fonte_placar = None
fonte_menu = None
fonte_titulo = None
fonte_scores = None

# Variáveis de jogo
nivel_dificuldade = "MÉDIO"

# Arquivos e utilitários
def carregar_pontuacoes():
    if not os.path.exists(ARQUIVO_SCORES):
        return {"TEMPO": [], "ZERAR": [], "ENCHER": [], "DISPUTA": [], "VIDAS": []}
    try:
        with open(ARQUIVO_SCORES, "r") as f:
            scores = json.load(f)
            for k in ["TEMPO", "ZERAR", "ENCHER", "DISPUTA", "VIDAS"]:
                if k not in scores:
                    scores[k] = []
            return scores
    except json.JSONDecodeError:
        return {"TEMPO": [], "ZERAR": [], "ENCHER": [], "DISPUTA": [], "VIDAS": []}

def salvar_pontuacoes(scores):
    try:
        with open(ARQUIVO_SCORES, "w") as f:
            json.dump(scores, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar pontuacoes: {e}")

def adicionar_pontuacao(scores, modo, nova_pontuacao):
    if modo not in scores:
        print(f"Modo de jogo '{modo}' desconhecido para salvar score.")
        return scores
    lista_scores = scores[modo]
    lista_scores.append(nova_pontuacao)
    lista_scores.sort(reverse=True)
    scores[modo] = lista_scores[:3]
    return scores

# Carregar textura
def carregar_textura(filepath):
    try:
        textura_surface = pygame.image.load(filepath).convert_alpha()
        textura_data = pygame.image.tostring(textura_surface, "RGBA", True)
        largura = textura_surface.get_width()
        altura = textura_surface.get_height()
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, largura, altura, 0, GL_RGBA, GL_UNSIGNED_BYTE, textura_data)
        return texid
    except Exception as e:
        print(f"Erro ao carregar textura {filepath}: {e}")
        return None

# Desenho de texto
def desenhar_texto(texto, fonte, x, y, cor=(255, 255, 255, 255), sombra_offset=(0, 0), align="left"):
    cor_rgb = (cor[0], cor[1], cor[2])
    text_surface = fonte.render(texto, True, cor_rgb)
    if len(cor) > 3:
        text_surface.set_alpha(cor[3])
    else:
        text_surface.set_alpha(255)
    largura = text_surface.get_width()
    altura = text_surface.get_height()

    if align == "center":
        x = x - largura // 2
    elif align == "right":
        x = x - largura

    if sombra_offset != (0, 0):
        shadow_surface = fonte.render(texto, True, (200, 200, 200))
        shadow_surface.set_alpha(200)
        shadow_data = pygame.image.tostring(shadow_surface, "RGBA", True)
        glRasterPos2d(x + sombra_offset[0], y + sombra_offset[1])
        glDrawPixels(shadow_surface.get_width(), shadow_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, shadow_data)

    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2d(x, y)
    glDrawPixels(largura, altura, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

# Retângulo arredondado
def _draw_circle_fan(cx, cy, radius, start_angle, end_angle, segments=12):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        t = start_angle + (end_angle - start_angle) * (i / segments)
        x = cx + math.cos(t) * radius
        y = cy + math.sin(t) * radius
        glVertex2f(x, y)
    glEnd()

def draw_rounded_rect(x, y, w, h, r, color):
    r = max(0.0, min(r, min(w, h) / 2.0))
    glColor4f(color[0], color[1], color[2], color[3])
    glBegin(GL_QUADS)
    glVertex2f(x + r, y)
    glVertex2f(x + w - r, y)
    glVertex2f(x + w - r, y + h)
    glVertex2f(x + r, y + h)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(x, y + r)
    glVertex2f(x + r, y + r)
    glVertex2f(x + r, y + h - r)
    glVertex2f(x, y + h - r)
    glVertex2f(x + w - r, y + r)
    glVertex2f(x + w, y + r)
    glVertex2f(x + w, y + h - r)
    glVertex2f(x + w - r, y + h - r)
    glEnd()
    _draw_circle_fan(x + r, y + r, r, math.pi, 1.5 * math.pi)
    _draw_circle_fan(x + w - r, y + r, r, 1.5 * math.pi, 0.0)
    _draw_circle_fan(x + w - r, y + h - r, r, 0.0, 0.5 * math.pi)
    _draw_circle_fan(x + r, y + h - r, r, 0.5 * math.pi, math.pi)

# Desenho de nave/item
class OBJ:
    def __init__(self, filename):
        self.vertices = []
        self.normals = []
        self.faces = []

        try:
            with open(filename, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    values = line.split()
                    if not values:
                        continue
                        
                    if values[0] == 'v':
                        self.vertices.append([float(v) for v in values[1:4]])
                    elif values[0] == 'vn':
                        self.normals.append([float(v) for v in values[1:4]])
                    elif values[0] == 'f':
                        face = []
                        for v in values[1:]:
                            w = v.split('/')
                            face.append((int(w[0]), int(w[2])))
                        self.faces.append(face)
        except Exception as e:
            print(f"Erro ao ler o arquivo OBJ {filename}: {e}")
            raise

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glFrontFace(GL_CCW) 
        
        for face in self.faces:
            if len(face) == 3:
                glBegin(GL_TRIANGLES)
            elif len(face) == 4:
                glBegin(GL_QUADS)
            else:
                continue

            for vertex_index, normal_index in face:
                glNormal3fv(self.normals[normal_index - 1])
                glVertex3fv(self.vertices[vertex_index - 1])
            
            glEnd()
            
        glEndList()

    def render(self):
        glCallList(self.gl_list)

class Item:
    def __init__(self):
        global nivel_dificuldade
        self.x = random.uniform(LIMITE_ESQUERDA, LIMITE_DIREITA)
        self.y = LIMITE_TOPO
        self.z = 0.0
        
        if nivel_dificuldade == "FÁCIL":
            self.velocidade = random.uniform(0.02, 0.06)
        elif nivel_dificuldade == "DIFÍCIL":
            self.velocidade = random.uniform(0.07, 0.13)
        else: 
            self.velocidade = random.uniform(0.04, 0.09)
        
        self.rotacao = random.uniform(0, 360)
        self.velocidade_rotacao = random.uniform(1, 3)

    def update(self):
        self.y -= self.velocidade
        self.rotacao += self.velocidade_rotacao
        if self.rotacao > 360:
            self.rotacao -= 360

    def draw(self, model):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(0.02, 0.02, 0.02) 
        glRotatef(self.rotacao, 0.5, 1.0, 0.2)
        glColor3f(1.0, 1.0, 0.0)
        if model:
            model.render()
        glPopMatrix()

def check_collision(item, c_x, c_y):
    coletor_min_x = c_x - COLETOR_MEIA_LARGURA
    coletor_max_x = c_x + COLETOR_MEIA_LARGURA
    coletor_min_y = c_y - COLETOR_MEIA_ALTURA
    coletor_max_y = c_y + COLETOR_MEIA_ALTURA
    item_min_x = item.x - ITEM_MEIA_LARGURA
    item_max_x = item.x + ITEM_MEIA_LARGURA
    item_min_y = item.y - ITEM_MEIA_ALTURA
    item_max_y = item.y + ITEM_MEIA_ALTURA
    colisao_x = (coletor_min_x < item_max_x) and (coletor_max_x > item_min_x)
    colisao_y = (coletor_min_y < item_max_y) and (coletor_max_y > item_min_y)
    return colisao_x and colisao_y

def desenhar_nave(model, color=(0.0, 1.0, 0.0)):
    glPushMatrix()
    glScalef(0.05, 0.05, 0.05)
    glColor3f(*color)
    if model:
        model.render()
    glPopMatrix()

# Projeção ortográfica para HUD
def set_ortho_mode(largura, altura):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, largura, 0, altura) 
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def unset_ortho_mode():
    glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()

# desenhar fundo menu 2D 
def desenhar_fundo_menu_2d(texture_id, largura, altura):
    if not texture_id:
        glColor4f(0.03, 0.03, 0.06, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(largura, 0)
        glVertex2f(largura, altura)
        glVertex2f(0, altura)
        glEnd()
        return
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)
    glTexCoord2f(1, 0); glVertex2f(largura, 0)
    glTexCoord2f(1, 1); glVertex2f(largura, altura)
    glTexCoord2f(0, 1); glVertex2f(0, altura)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

# setup lighting
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0) 
    glEnable(GL_LIGHT1) 
    
    # LUZ 0 (Sol/Ambiente)
    ambient_light = [0.2, 0.2, 0.2, 1.0] 
    diffuse_light = [0.6, 0.6, 0.6, 1.0] 
    specular_light = [0.8, 0.8, 0.8, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)

    # LUZ 1 (Lanterna)
    light1_ambient = [0.0, 0.0, 0.0, 1.0]
    light1_diffuse = [1.0, 1.0, 1.0, 1.0] 
    light1_specular = [1.0, 1.0, 1.0, 1.0]
    glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
    glLightfv(GL_LIGHT1, GL_SPECULAR, light1_specular)
    
    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 45.0) 
    glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 10.0) 
    
    # Materiais
    mat_diffuse = [1.0, 1.0, 1.0, 1.0]
    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = 50
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)
    
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    glDisable(GL_LIGHT1)

# Skybox
def desenhar_skybox(textures):
    glDepthMask(GL_FALSE)
    glDisable(GL_LIGHTING) 
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_CULL_FACE)
    size = 30.0
    faces = {
        "sky_front":  ([[-size, -size, -size], [ size, -size, -size], [ size,  size, -size], [-size,  size, -size]]),
        "sky_back":   ([[-size, -size,  size], [ size, -size,  size], [ size,  size,  size], [-size,  size,  size]]),
        "sky_left":   ([[-size, -size, -size], [-size, -size,  size], [-size,  size,  size], [-size,  size, -size]]),
        "sky_right":  ([[ size, -size, -size], [ size, -size,  size], [ size,  size,  size], [ size,  size, -size]]),
        "sky_top":    ([[-size,  size, -size], [ size,  size, -size], [ size,  size,  size], [-size,  size,  size]]),
        "sky_bottom": ([[-size, -size, -size], [ size, -size, -size], [ size, -size,  size], [-size, -size,  size]]),
    }
    glColor3f(1.0, 1.0, 1.0)
    for name, verts in faces.items():
        tex = textures.get(name) if textures else None
        if not tex:
            continue
        glBindTexture(GL_TEXTURE_2D, tex)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(*verts[0])
        glTexCoord2f(1, 0); glVertex3f(*verts[1])
        glTexCoord2f(1, 1); glVertex3f(*verts[2])
        glTexCoord2f(0, 1); glVertex3f(*verts[3])
        glEnd()
    glEnable(GL_CULL_FACE)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING) 
    glDepthMask(GL_TRUE)

# Menu utilities
def draw_botao(buffer, rect, texto, hovered, fonte):
    cor_fill = (255, 255, 255, 120) if hovered else (255, 255, 255, 60)
    cor_border = (255, 255, 255, 255)
    pygame.draw.rect(buffer, cor_fill, rect, border_radius=16)
    pygame.draw.rect(buffer, cor_border, rect, width=3, border_radius=16)
    texto_img = fonte.render(texto, True, (255, 255, 255))
    buffer.blit(
        texto_img,
        (rect.x + rect.w / 2 - texto_img.get_width() / 2,
         rect.y + rect.h / 2 - texto_img.get_height() / 2)
    )

# Reset jogo
def resetar_jogo():
    global coletor_x, coletor2_x, coletor_y, coletor2_y 
    coletor_x = -2.0
    coletor2_x = 2.0
    coletor_y = -3.0  
    coletor2_y = -3.0 
    pontos = 0
    pontos_p2 = 0
    lista_itens = []
    tempo_inicio = pygame.time.get_ticks()
    vidas = VIDAS_INICIAIS
    print("Jogo resetado.")
    return (pontos, lista_itens, tempo_inicio, coletor_x, coletor2_x, pontos_p2, coletor_y, coletor2_y, vidas)

# MAIN
def main():
    global fonte_placar, fonte_menu, fonte_titulo, fonte_scores
    global coletor_x, coletor2_x, coletor_y, coletor2_y  
    global nivel_dificuldade

    pygame.init()
    pygame.font.init()

    # fontes
    try:
        nome_da_fonte = "Nasalization Rg.otf"
        fonte_placar = pygame.font.Font(nome_da_fonte, 28)
        fonte_menu = pygame.font.Font(nome_da_fonte, 22)
        fonte_titulo = pygame.font.Font(nome_da_fonte, 64)
        fonte_scores = pygame.font.Font(nome_da_fonte, 20)
    except Exception:
        fonte_placar = pygame.font.Font(pygame.font.get_default_font(), 28)
        fonte_menu = pygame.font.Font(pygame.font.get_default_font(), 22)
        fonte_titulo = pygame.font.Font(pygame.font.get_default_font(), 64)
        fonte_scores = pygame.font.Font(pygame.font.get_default_font(), 20)

    display = (LARGURA_TELA, ALTURA_TELA)
    pygame.display.set_caption("STARDROP")
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    setup_lighting()

    # imagens / texturas
    skybox_textures = {
        "sky_front": carregar_textura("./images/sky_front.png"),
        "sky_back": carregar_textura("./images/sky_back.png"),
        "sky_left": carregar_textura("./images/sky_left.png"),
        "sky_right": carregar_textura("./images/sky_right.png"),
        "sky_top": carregar_textura("./images/sky_top.png"),
        "sky_bottom": carregar_textura("./images/sky_bottom.png"),
    }

    # Carregar Modelos OBJ
    modelo_estrela = None
    modelo_coletor = None
    modelo_coletor_p2 = None
    try:
        modelo_estrela = OBJ("./images/estrela.obj")
        modelo_coletor = OBJ("./images/textura_coletor.obj") 
        modelo_coletor_p2 = OBJ("./images/textura_coletor.obj") 
    except Exception as e:
        print("---------------------------------------------------------")
        print(f"ERRO AO CARREGAR MODELOS .OBJ: {e}")
        print("Certifique-se que 'estrela.obj' e 'textura_coletor.obj' estao na mesma pasta que o main.py")
        print("O jogo continuara sem os modelos 3D.")
        print("---------------------------------------------------------")

    texture_menu_fundo = carregar_textura("./images/sky_back.png")

    # câmera
    camera_distance = 15.0
    camera_rot_x = 20.0
    camera_rot_y = 0.0

    # jogo
    pontos = 0
    pontos_p2 = 0
    vidas = 0
    lista_itens = []
    tempo_inicio = pygame.time.get_ticks()

    game_state = ESTADO_MENU
    modo_de_jogo = None

    high_scores = carregar_pontuacoes()

    clock = pygame.time.Clock()
    running = True

    botao_labels = [
        f"Tempo ({OBJETIVO_TEMPO_LIMITE}s)",
        f"Encher ({OBJETIVO_ENCHER_PONTOS} pts)",
        "Sobrevivência (Vidas)",
        "Zerar (Não negative!)",
        "Disputa (2P)"
    ]
    botao_modes = ["TEMPO", "ENCHER", "VIDAS", "ZERAR", "DISPUTA"]

    # Variáveis de pausa
    tempo_pausa_inicio = 0
    
    btn_w_pausa = int(LARGURA_TELA * 0.40)
    btn_h_pausa = int(ALTURA_TELA * 0.085)
    espaco_pausa = int(ALTURA_TELA * 0.03)
    
    botao_pausa_voltar_rect = pygame.Rect(
        (LARGURA_TELA / 2) - (btn_w_pausa / 2),
        (ALTURA_TELA / 2) - (btn_h_pausa + espaco_pausa / 2),
        btn_w_pausa, btn_h_pausa
    )
    botao_pausa_menu_rect = pygame.Rect(
        (LARGURA_TELA / 2) - (btn_w_pausa / 2),
        (ALTURA_TELA / 2) + (espaco_pausa / 2),
        btn_w_pausa, btn_h_pausa
    )

    # Variáveis menu (DIFICULDADE)
    btn_w_dif = int(LARGURA_TELA * 0.40)
    btn_h_dif = int(ALTURA_TELA * 0.085)
    espaco_dif = int(ALTURA_TELA * 0.03)
    base_y_dif = ALTURA_TELA * 0.4
    
    botao_dif_facil_rect = pygame.Rect(
        (LARGURA_TELA / 2) - (btn_w_dif / 2),
        base_y_dif,
        btn_w_dif, btn_h_dif
    )
    botao_dif_medio_rect = pygame.Rect(
        (LARGURA_TELA / 2) - (btn_w_dif / 2),
        base_y_dif + (btn_h_dif + espaco_dif),
        btn_w_dif, btn_h_dif
    )
    botao_dif_dificil_rect = pygame.Rect(
        (LARGURA_TELA / 2) - (btn_w_dif / 2),
        base_y_dif + 2 * (btn_h_dif + espaco_dif),
        btn_w_dif, btn_h_dif
    )

    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos() 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == ESTADO_JOGANDO:
                        game_state = ESTADO_PAUSA
                        tempo_pausa_inicio = pygame.time.get_ticks()
                    elif game_state == ESTADO_PAUSA:
                        game_state = ESTADO_JOGANDO
                        tempo_que_ficou_pausado = pygame.time.get_ticks() - tempo_pausa_inicio
                        tempo_inicio += tempo_que_ficou_pausado
            
            if game_state == ESTADO_PAUSA:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if botao_pausa_voltar_rect.collidepoint(mouse_pos):
                        game_state = ESTADO_JOGANDO
                        tempo_que_ficou_pausado = pygame.time.get_ticks() - tempo_pausa_inicio
                        tempo_inicio += tempo_que_ficou_pausado
                    elif botao_pausa_menu_rect.collidepoint(mouse_pos):
                        game_state = ESTADO_MENU
            
            elif game_state == ESTADO_SELECIONAR_DIFICULDADE:
                 if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if botao_dif_facil_rect.collidepoint(mouse_pos):
                        nivel_dificuldade = "FACIL"
                        game_state = ESTADO_JOGANDO
                        pontos, lista_itens, tempo_inicio, coletor_x, coletor2_x, pontos_p2, coletor_y, coletor2_y, vidas = resetar_jogo()
                    elif botao_dif_medio_rect.collidepoint(mouse_pos):
                        nivel_dificuldade = "MEDIO"
                        game_state = ESTADO_JOGANDO
                        pontos, lista_itens, tempo_inicio, coletor_x, coletor2_x, pontos_p2, coletor_y, coletor2_y, vidas = resetar_jogo()
                    elif botao_dif_dificil_rect.collidepoint(mouse_pos):
                        nivel_dificuldade = "DIFICIL"
                        game_state = ESTADO_JOGANDO
                        pontos, lista_itens, tempo_inicio, coletor_x, coletor2_x, pontos_p2, coletor_y, coletor2_y, vidas = resetar_jogo()

            elif game_state == ESTADO_JOGANDO:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        camera_distance -= 0.5
                    elif event.button == 5:
                        camera_distance += 0.5
                if event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:
                        camera_rot_y += event.rel[0] * 0.5
                        camera_rot_x += event.rel[1] * 0.5

            elif game_state == ESTADO_FIM:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    game_state = ESTADO_MENU

        # MENU
        if game_state == ESTADO_MENU:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            set_ortho_mode(LARGURA_TELA, ALTURA_TELA)

            desenhar_fundo_menu_2d(texture_menu_fundo, LARGURA_TELA, ALTURA_TELA)

            buffer = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            buffer.fill((0, 0, 0, 0))

            titulo_img = fonte_titulo.render("STARDROP", True, (255, 255, 255))
            titulo_y = int(ALTURA_TELA * 0.05) 
            buffer.blit(titulo_img, (int(LARGURA_TELA * 0.05), titulo_y))

            btn_w = int(LARGURA_TELA * 0.40)
            btn_h = int(ALTURA_TELA * 0.075) 
            espaco = int(ALTURA_TELA * 0.02) 
            base_x = int(LARGURA_TELA * 0.05)
            base_y = int(ALTURA_TELA * 0.30)

            botoes_rects = []
            for i in range(len(botao_labels)):
                r = pygame.Rect(base_x, base_y + i * (btn_h + espaco), btn_w, btn_h)
                botoes_rects.append(r)

            for i, r in enumerate(botoes_rects):
                hovered = r.collidepoint(mouse_pos)
                draw_botao(buffer, r, botao_labels[i], hovered, fonte_menu)

            score_tempo = high_scores["TEMPO"][0] if high_scores["TEMPO"] else 0
            score_zerar = high_scores["ZERAR"][0] if high_scores["ZERAR"] else 0
            score_encher = high_scores["ENCHER"][0] if high_scores["ENCHER"] else 0
            score_disputa = high_scores["DISPUTA"][0] if high_scores["DISPUTA"] else 0
            score_vidas = high_scores["VIDAS"][0] if high_scores["VIDAS"] else 0

            sx = int(LARGURA_TELA * 0.62)
            sy = int(ALTURA_TELA * 0.35) 
            lines = [
                ("Melhores Pontuações:", fonte_menu),
                (f"Tempo: {score_tempo}", fonte_scores),
                (f"Encher: {score_encher}", fonte_scores),
                (f"Vidas: {score_vidas}", fonte_scores),
                (f"Zerar: {score_zerar}", fonte_scores),
                (f"Disputa: {score_disputa}", fonte_scores)
            ]
            offset = 0
            for texto, fnt in lines:
                img = fnt.render(texto, True, (255, 255, 255))
                buffer.blit(img, (sx, sy + offset))
                offset += 30 

            final = pygame.image.tostring(buffer, "RGBA", True)
            glWindowPos2d(0, 0)
            glDrawPixels(LARGURA_TELA, ALTURA_TELA, GL_RGBA, GL_UNSIGNED_BYTE, final)

            if pygame.mouse.get_pressed()[0]:
                for idx, r in enumerate(botoes_rects):
                    if r.collidepoint(mouse_pos):
                        modo_de_jogo = botao_modes[idx]
                        if modo_de_jogo == "DISPUTA":
                            nivel_dificuldade = "MEDIO" 
                            game_state = ESTADO_JOGANDO
                            pontos, lista_itens, tempo_inicio, coletor_x, coletor2_x, pontos_p2, coletor_y, coletor2_y, vidas = resetar_jogo()
                        else:
                            game_state = ESTADO_SELECIONAR_DIFICULDADE
                        break
            
            unset_ortho_mode()

        # Menu de dificuldade
        elif game_state == ESTADO_SELECIONAR_DIFICULDADE:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            set_ortho_mode(LARGURA_TELA, ALTURA_TELA)

            desenhar_fundo_menu_2d(texture_menu_fundo, LARGURA_TELA, ALTURA_TELA)
            
            buffer = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            buffer.fill((0, 0, 0, 150)) 

            titulo_img = fonte_titulo.render("DIFICULDADE", True, (255, 255, 255))
            buffer.blit(titulo_img, (
                (LARGURA_TELA / 2) - (titulo_img.get_width() / 2),
                botao_dif_facil_rect.y - titulo_img.get_height() - espaco_dif * 2
            ))

            hover_facil = botao_dif_facil_rect.collidepoint(mouse_pos)
            draw_botao(buffer, botao_dif_facil_rect, "Facil", hover_facil, fonte_menu)
            
            hover_medio = botao_dif_medio_rect.collidepoint(mouse_pos)
            draw_botao(buffer, botao_dif_medio_rect, "Medio", hover_medio, fonte_menu)

            hover_dificil = botao_dif_dificil_rect.collidepoint(mouse_pos)
            draw_botao(buffer, botao_dif_dificil_rect, "Dificil", hover_dificil, fonte_menu)
            
            final = pygame.image.tostring(buffer, "RGBA", True)
            glWindowPos2d(0, 0)
            glDrawPixels(LARGURA_TELA, ALTURA_TELA, GL_RGBA, GL_UNSIGNED_BYTE, final)
            
            unset_ortho_mode()

        # Fim de jogo
        elif game_state == ESTADO_FIM:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            set_ortho_mode(LARGURA_TELA, ALTURA_TELA)
            desenhar_fundo_menu_2d(texture_menu_fundo, LARGURA_TELA, ALTURA_TELA)

            desenhar_texto("FIM DE JOGO", fonte_titulo, LARGURA_TELA // 2, int(ALTURA_TELA * 0.68),
                           (255, 255, 255, 255), sombra_offset=(0, 0), align="center")

            if modo_de_jogo == "DISPUTA":
                desenhar_texto(f"P1 Pontos: {pontos}", fonte_placar, LARGURA_TELA // 2, int(ALTURA_TELA * 0.5),
                               align="center")
                desenhar_texto(f"P2 Pontos: {pontos_p2}", fonte_placar, LARGURA_TELA // 2, int(ALTURA_TELA * 0.42),
                               align="center")
            else:
                desenhar_texto(f"PONTUAÇÃO FINAL: {pontos}", fonte_placar, LARGURA_TELA // 2,
                               int(ALTURA_TELA * 0.5), align="center")

            desenhar_texto("Clique para voltar ao menu", fonte_menu, LARGURA_TELA // 2, int(ALTURA_TELA * 0.22),
                           align="center")
            unset_ortho_mode()

        # JOGANDO / PAUSADO
        elif game_state == ESTADO_JOGANDO or game_state == ESTADO_PAUSA:
            
            if game_state == ESTADO_JOGANDO:
                keys = pygame.key.get_pressed()
                
                if keys[pygame.K_a]:
                    coletor_x -= 0.1
                if keys[pygame.K_d]:
                    coletor_x += 0.1
                if keys[pygame.K_w]:
                    coletor_y += 0.1
                if keys[pygame.K_s]:
                    coletor_y -= 0.1
                    
                if coletor_x < LIMITE_ESQUERDA:
                    coletor_x = LIMITE_ESQUERDA
                if coletor_x > LIMITE_DIREITA:
                    coletor_x = LIMITE_DIREITA
                if coletor_y > COLETOR_LIMITE_TOPO:
                    coletor_y = COLETOR_LIMITE_TOPO
                if coletor_y < COLETOR_LIMITE_FUNDO:
                    coletor_y = COLETOR_LIMITE_FUNDO

                if modo_de_jogo == "DISPUTA":
                    if keys[pygame.K_LEFT]:
                        coletor2_x -= 0.1
                    if keys[pygame.K_RIGHT]:
                        coletor2_x += 0.1
                    if keys[pygame.K_UP]:
                        coletor2_y += 0.1
                    if keys[pygame.K_DOWN]:
                        coletor2_y -= 0.1
                        
                    if coletor2_x < LIMITE_ESQUERDA:
                        coletor2_x = LIMITE_ESQUERDA
                    if coletor2_x > LIMITE_DIREITA:
                        coletor2_x = LIMITE_DIREITA
                    if coletor2_y > COLETOR_LIMITE_TOPO:
                        coletor2_y = COLETOR_LIMITE_TOPO
                    if coletor2_y < COLETOR_LIMITE_FUNDO:
                        coletor2_y = COLETOR_LIMITE_FUNDO

                taxa_spawn = 0.03 # Medio
                if nivel_dificuldade == "FACIL":
                    taxa_spawn = 0.02
                elif nivel_dificuldade == "DIFICIL":
                    taxa_spawn = 0.05
                
                if random.random() < taxa_spawn:
                    lista_itens.append(Item())

                tempo_atual_seg = (pygame.time.get_ticks() - tempo_inicio) / 1000

                itens_para_remover = []
                for item in lista_itens:
                    item.update()
                    colidiu_p1 = check_collision(item, coletor_x, coletor_y) 
                    colidiu_p2 = False
                    if modo_de_jogo == "DISPUTA":
                        colidiu_p2 = check_collision(item, coletor2_x, coletor2_y)
                    if colidiu_p1:
                        pontos += 10
                        itens_para_remover.append(item)
                    elif colidiu_p2:
                        pontos_p2 += 10
                        itens_para_remover.append(item)
                    elif item.y < LIMITE_FUNDO:
                        itens_para_remover.append(item)
                        if modo_de_jogo == "ZERAR":
                            pontos -= PONTOS_PERDIDOS_ZERAR
                        
                        elif modo_de_jogo == "VIDAS":
                            vidas -= 1
                            print(f"Vida perdida! Vidas restantes: {vidas}")
                
                for item in itens_para_remover:
                    if item in lista_itens:
                        lista_itens.remove(item)

                # fim condições
                jogo_terminou = False
                if (modo_de_jogo == "TEMPO" or modo_de_jogo == "DISPUTA") and tempo_atual_seg >= OBJETIVO_TEMPO_LIMITE:
                    jogo_terminou = True
                elif modo_de_jogo == "ZERAR" and pontos < 0:
                    jogo_terminou = True
                elif modo_de_jogo == "ENCHER" and pontos >= OBJETIVO_ENCHER_PONTOS:
                    jogo_terminou = True
                elif modo_de_jogo == "VIDAS" and vidas <= 0:
                    jogo_terminou = True

                if jogo_terminou:
                    game_state = ESTADO_FIM
                    if modo_de_jogo == "DISPUTA":
                        high_scores = adicionar_pontuacao(high_scores, "DISPUTA", pontos)
                        high_scores = adicionar_pontuacao(high_scores, "DISPUTA", pontos_p2)
                    else:
                        high_scores = adicionar_pontuacao(high_scores, modo_de_jogo, pontos)
                    salvar_pontuacoes(high_scores)

            # RENDERIZACAO (JOGO E PAUSA)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # skybox
            glPushMatrix()
            glRotatef(camera_rot_x, 1.0, 0.0, 0.0)
            glRotatef(camera_rot_y, 0.0, 1.0, 0.0)
            desenhar_skybox(skybox_textures)
            glPopMatrix()

            glClear(GL_DEPTH_BUFFER_BIT)

            glLoadIdentity()
            
            glLightfv(GL_LIGHT0, GL_POSITION, light_position)
            
            glTranslatef(0.0, 0.0, -camera_distance)
            glRotatef(camera_rot_x, 1.0, 0.0, 0.0)
            glRotatef(camera_rot_y, 0.0, 1.0, 0.0)
            
            for item in lista_itens:
                item.draw(modelo_estrela)

            # COLETOR P1 E LANTERNA
            glPushMatrix()
            glTranslatef(coletor_x, coletor_y, 0.0) 
            
            light1_pos = [0.0, 0.0, 1.0, 1.0] 
            light1_dir = [0.0, -1.0, -0.5] 
            glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
            glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, light1_dir)
            glEnable(GL_LIGHT1)

            desenhar_nave(modelo_coletor, color=(0.0, 1.0, 0.0))
            glPopMatrix()
            
            glDisable(GL_LIGHT1) 

            if modo_de_jogo == "DISPUTA":
                glPushMatrix()
                glTranslatef(coletor2_x, coletor2_y, 0.0) 
                desenhar_nave(modelo_coletor_p2, color=(1.0, 0.5, 0.0))
                glPopMatrix()
            
            # HUD (2D)
            set_ortho_mode(LARGURA_TELA, ALTURA_TELA)
            desenhar_texto(f"P1 Pontos: {pontos}", fonte_placar, 16, ALTURA_TELA - 40, (255, 255, 255, 255))
            
            if game_state == ESTADO_PAUSA:
                tempo_pausado_seg = (tempo_pausa_inicio - tempo_inicio) / 1000
                tempo_a_mostrar = tempo_pausado_seg
            else:
                tempo_a_mostrar = (pygame.time.get_ticks() - tempo_inicio) / 1000

            if modo_de_jogo == "DISPUTA":
                desenhar_texto(f"P2 Pontos: {pontos_p2}", fonte_placar, LARGURA_TELA - 220, ALTURA_TELA - 40,
                               (255, 255, 255, 255))
                tempo_restante = max(0, int(OBJETIVO_TEMPO_LIMITE - tempo_a_mostrar))
                desenhar_texto(f"Tempo: {tempo_restante}s", fonte_placar, (LARGURA_TELA // 2) - 60, ALTURA_TELA - 40,
                               (255, 255, 255, 255))
            elif modo_de_jogo == "TEMPO":
                tempo_restante = max(0, int(OBJETIVO_TEMPO_LIMITE - tempo_a_mostrar))
                desenhar_texto(f"Tempo: {tempo_restante}s", fonte_placar, LARGURA_TELA - 160, ALTURA_TELA - 40,
                               (255, 255, 255, 255))
            elif modo_de_jogo == "ZERAR":
                desenhar_texto("Modo: Zerar", fonte_placar, LARGURA_TELA - 160, ALTURA_TELA - 40,
                               (255, 255, 255, 255))
            elif modo_de_jogo == "ENCHER":
                desenhar_texto(f"Meta: {OBJETIVO_ENCHER_PONTOS}", fonte_placar, LARGURA_TELA - 160, ALTURA_TELA - 40,
                               (255, 255, 255, 255))
            elif modo_de_jogo == "VIDAS":
                desenhar_texto(f"Vidas: {vidas}", fonte_placar, LARGURA_TELA - 160, ALTURA_TELA - 40,
                               (255, 255, 255, 255))
            
            # DESENHA O MENU DE PAUSA POR CIMA
            if game_state == ESTADO_PAUSA:
                overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150)) 
                
                hover_voltar = botao_pausa_voltar_rect.collidepoint(mouse_pos)
                draw_botao(overlay, botao_pausa_voltar_rect, "Voltar ao Jogo", hover_voltar, fonte_menu)
                
                hover_menu = botao_pausa_menu_rect.collidepoint(mouse_pos)
                draw_botao(overlay, botao_pausa_menu_rect, "Voltar ao Menu", hover_menu, fonte_menu)

                titulo_img = fonte_titulo.render("PAUSA", True, (255, 255, 255))
                overlay.blit(titulo_img, (
                    (LARGURA_TELA / 2) - (titulo_img.get_width() / 2),
                    botao_pausa_voltar_rect.y - titulo_img.get_height() - espaco_pausa * 2
                ))

                final = pygame.image.tostring(overlay, "RGBA", True)
                glWindowPos2d(0, 0)
                glDrawPixels(LARGURA_TELA, ALTURA_TELA, GL_RGBA, GL_UNSIGNED_BYTE, final)
            
            unset_ortho_mode()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()