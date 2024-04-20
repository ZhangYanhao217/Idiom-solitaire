import pygame
import sys
import time
import random
import os
from pygame.locals import *

os.environ["SDL_IME_SHOW_UI"] = "1"  # 显示输入候选框

pygame.init()  # 初始化pygame

pygame.mixer.init()  # 初始化音频
pygame.mixer.music.load('data/背景音乐.mp3')  # 加载音乐
pygame.mixer.music.play(-1)  # 循环播放音乐

size = width, height = 480*2, 360*2  # 设置窗口大小
screen = pygame.display.set_mode(size)  # 创建窗口
screen_rect = screen.get_rect()  # 获取窗口矩形
pygame.display.set_caption("成语接龙")  # 设置窗口标题
 
with open('data/idioms.txt', 'r', encoding='utf-8') as file:
    idiom_list = file.read().splitlines()
with open('data/word.txt', 'r', encoding='utf-8') as file:
    chinese_list = file.read().splitlines()
with open('data/pinyin.txt', 'r', encoding='utf-8') as file:
    pinyin_list = file.read().splitlines()

last_idiom = random.choice(idiom_list)
idioms_used = [last_idiom]
 
# 加载背景图片
bg = pygame.image.load('data/背景.png')

# 加载主标题
title = pygame.image.load('data/标题.png')
title_rect = title.get_rect()
title_rect.center = (width/2, height/2-70*2)
 
# 加载开始按钮
start_button = pygame.image.load('data/开始按钮.png')
start_button_rect = start_button.get_rect()
start_button_rect.center = (width/2, height/2+80*2)
 
highlight_start_button = pygame.transform.scale(pygame.image.load('data/开始按钮_高亮.png'), (int(start_button.get_width() * 1.2),int(start_button.get_height() * 1.2)))  # 放大高亮按钮
highlight_start_button_rect = highlight_start_button.get_rect()
highlight_start_button_rect.center = start_button_rect.center  # 高亮按钮位置与开始按钮一致

# 加载返回按钮
back_button = pygame.image.load('data/返回按钮.png')
back_button_rect = back_button.get_rect()
back_button_rect.center = (width/2-190*2, height/2-320)  # 位置设置
 
highlight_back_button = pygame.transform.scale(pygame.image.load('data/返回按钮_高亮.png'), (int(back_button.get_width() * 1.2), int(back_button.get_height() * 1.2)))  # 放大高亮按钮
highlight_back_button_rect = highlight_back_button.get_rect()
highlight_back_button_rect.center = back_button_rect.center  # 高亮按钮位置与返回按钮一致

# 加载重试按钮
retry_button = pygame.image.load('data/重试.png')
retry_button_rect = retry_button.get_rect()
retry_button_rect.center = (width/2-retry_button.get_width()/2+240+80, height/2-retry_button.get_height()/2+180+60)

highlight_retry_button = pygame.transform.scale(pygame.image.load('data/重试_高亮.png'), (int(retry_button.get_width() * 1.2), int(retry_button.get_height() * 1.2)))  # 放大高亮按钮
highlight_retry_button_rect = highlight_retry_button.get_rect()
highlight_retry_button_rect.center = retry_button_rect.center  # 高亮按钮位置与重试按钮一致

# 加载接龙提示
# 1.成语未匹配上一个
not_matched = pygame.image.load('data/成语未匹配上一个.png')
not_matched = pygame.transform.scale(not_matched, (int(not_matched.get_width() * 0.5), int(not_matched.get_height() * 0.5)))  # 缩小提示图片
not_matched_rect = not_matched.get_rect()
not_matched_rect.center = (width/2, height/2-100*2)
# 2.这不是成语
not_idiom = pygame.image.load('data/这不是成语.png')
not_idiom = pygame.transform.scale(not_idiom, (int(not_idiom.get_width() * 0.5), int(not_idiom.get_height() * 0.5)))  # 缩小提示图片
not_idiom_rect = not_idiom.get_rect()
not_idiom_rect.center = (width/2, height/2-100*2)
# 3.接龙成功
success = pygame.image.load('data/接龙成功.png')
success = pygame.transform.scale(success, (int(success.get_width() * 0.5), int(success.get_height() * 0.5)))  # 缩小提示图片
success_rect = success.get_rect()
success_rect.center = (width/2, height/2-100*2)
# 4.成语已使用的文字提示
used = pygame.font.Font('data/汉仪小隶书简.ttf', 36).render('这个成语已经使用过了，换一个吧！', True, '#bfa46f')
used_rect = used.get_rect()

def check_chain(idiom1, idiom2):
    try:
        if pinyin_list[chinese_list.index(idiom1[0])] == pinyin_list[chinese_list.index(idiom2[-1])]:
            return True
        else:
            return False
    except:
        return False
 
next_idiom = ''
class ChineseTextInput:  # 定义一个中文输入框类
    def __init__(self, x, y, width, height, text=''):  # 初始化方法
        self.rect = pygame.Rect(x, y, width, height)  # 创建矩形区域
        self.color_inactive = pygame.Color('#7c4b00')  # 非激活状态颜色
        self.color_active = pygame.Color('#f0d890')  # 激活状态颜色
        self.color = self.color_inactive  # 当前颜色为非激活状态颜色
        self.text = text  # 文本内容
        self.font = pygame.font.Font('data/汉仪小隶书简.ttf', 36)  # 使用中文字体
        self.active = False  # 输入框非激活状态
        self.cooldown_time = 0.2  # 冷却时间
        self.last_input_time = 0  # 上次输入时间
        self.in_chinese_input = False  # 是否在中文输入状态
 
    def handle_event(self, event):  # 处理事件方法
        global next_idiom
        current_time = pygame.time.get_ticks() / 1000  # 获取当前时间
        if event.type == pygame.MOUSEBUTTONDOWN:  # 鼠标点击事件
            if self.rect.collidepoint(event.pos):  # 判断鼠标位置是否在输入框内
                if current_time - self.last_input_time > self.cooldown_time:  # 判断冷却时间
                    self.active = True  # 输入框激活
                    self.color = self.color_active  # 切换为激活状态颜色
                    self.last_input_time = current_time  # 更新输入时间
                    time.sleep(0.1)  # 延时0.1秒，防止输入框闪烁
                else:
                    self.active = False  # 输入框非激活
                    self.color = self.color_inactive  # 切换为非激活状态颜色
        if event.type == pygame.KEYDOWN:  
            if self.active and current_time - self.last_input_time > self.cooldown_time:  
                if event.key == pygame.K_RETURN:  
                    globals()['next_idiom'] = self.text  # 更新 next_idiom 变量
                    self.active = False  # 输入框非激活
                    self.color = self.color_inactive  # 切换为非激活状态颜色
                    self.text = ''  # 清空文本内容
                    print(next_idiom)
                elif event.key == pygame.K_BACKSPACE:  # 按下退格键
                    self.text = self.text[:-1]  # 删除最后一个字符
                else:
                    self.text += event.unicode  # 输入字符追加到文本内容
                self.last_input_time = current_time  # 更新输入时间
        if event.type == pygame.TEXTINPUT and self.active and current_time - self.last_input_time > self.cooldown_time:  # 文本输入事件
            if len(self.text)<4: # 限制输入长度为4
                self.text += event.text  # 输入文本追加到文本内容
            self.last_input_time = current_time  # 更新输入时间
        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE and self.active and current_time - self.last_input_time > self.cooldown_time:  # 退格键按下事件
            self.text = self.text[:-1]  # 删除最后一个字符
            self.last_input_time = current_time  # 更新输入时间

    def update(self):  # 更新方法
        width = max(200, self.font.render(self.text, True, self.color).get_width()+10)  # 计算文本渲染后的宽度
        self.rect.w = width  # 更新矩形区域宽度

    def draw(self, screen):  # 绘制方法
        pygame.draw.rect(screen, self.color, self.rect, 2)  # 绘制矩形边框
        text_surface = self.font.render(self.text, True, self.color)  # 渲染文本
        screen.blit(text_surface, (self.rect.x+5, self.rect.y+5))  # 在屏幕上绘制文本

clock = pygame.time.Clock()  # 设置时钟

alpha_data = False

# 设置字体
font = pygame.font.Font('data/汉仪小隶书简.ttf', 40)

input_box = ChineseTextInput(width/2-50+20, height/2+50, 160, 40)  # 创建输入框
input_box.color_inactive = pygame.Color('#7c4b00')  # 将非激活状态的颜色改为#7c4b00
input_box.color_active = pygame.Color('red')  # 将激活状态的颜色改为red

t = True
# 显示窗口
while True:
    clock.tick(-1)  # 设置帧率
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:  # 监听鼠标点击事件
            if start_button_rect.collidepoint(event.pos):  # 判断鼠标是否点击了按钮
                alpha_data = True
        if event.type == pygame.MOUSEBUTTONDOWN:  # 监听鼠标点击事件
            if back_button_rect.collidepoint(event.pos):  # 判断鼠标是否点击了按钮
                title.set_alpha(255)  # 显示主标题
                start_button.set_alpha(255)  # 显示开始按钮
                highlight_start_button.set_alpha(255)  # 显示高亮按钮
        if event.type == pygame.MOUSEBUTTONDOWN:  # 监听鼠标点击事件
            if retry_button_rect.collidepoint(event.pos):  # 判断鼠标是否点击了按钮
                input_box.text = ''  # 清空输入框内容
                last_idiom = random.choice(idiom_list)
                idioms_used.append(last_idiom)

    if alpha_data:
        if title.get_alpha() == 0 and start_button.get_alpha() == 0 and highlight_start_button.get_alpha() == 0:
            alpha_data = False
        # 让主标题和按钮逐渐变透明直到消失
        title.set_alpha(max(0, title.get_alpha() - 10))
        start_button.set_alpha(max(0, start_button.get_alpha() - 10))
        highlight_start_button.set_alpha(max(0, highlight_start_button.get_alpha() - 10))

    # 绘制背景
    screen.blit(bg, (0, 0))
    # 绘制标题
    screen.blit(title, title_rect)
    # 绘制开始按钮
    if start_button_rect.collidepoint(pygame.mouse.get_pos()):  # 判断鼠标是否在按钮上
        screen.blit(highlight_start_button, (start_button_rect.centerx - highlight_start_button.get_width() / 2, start_button_rect.centery - highlight_start_button.get_height() / 2))  # 只显示高亮按钮
    else:
        screen.blit(start_button, start_button_rect)
 
    # 计算并显示FPS
    #fps = clock.get_fps()
    #fps_text = font.render("FPS: {:.2f}".format(fps), True, (255, 255, 255))
    #screen.blit(fps_text, (730, 10))

    if title.get_alpha() == 0 and start_button.get_alpha() == 0 and highlight_start_button.get_alpha() == 0:
        screen.blit(back_button, back_button_rect)
        if back_button_rect.collidepoint(pygame.mouse.get_pos()):  # 判断鼠标是否在返回按钮上
            screen.blit(highlight_back_button, (back_button_rect.centerx - highlight_back_button.get_width() / 2, back_button_rect.centery - highlight_back_button.get_height() / 2))  # 只显示高亮按钮
        else:
            screen.blit(back_button, back_button_rect)  # 显示返回按钮

        #打印上一个成语
        last_idiom_text = font.render("当前成语：" + last_idiom, True, "#7c4b00")
        screen.blit(last_idiom_text, (width/2-180, height/2))
        #打印接龙提示
        solitaire_text = font.render("请接龙：", True, '#7c4b00')
        screen.blit(solitaire_text, (width/2-180, height/2+50))
        # 绘制重试按钮
        if retry_button_rect.collidepoint(pygame.mouse.get_pos()):  # 判断鼠标是否在重试按钮上
            screen.blit(highlight_retry_button, (retry_button_rect.centerx - highlight_retry_button.get_width() / 2, retry_button_rect.centery - highlight_retry_button.get_height() / 2))  # 只显示高亮按钮        
        else:
            screen.blit(retry_button, retry_button_rect)  # 显示重试按钮
 
        input_box.handle_event(event)
        input_box.update()
        input_box.draw(screen)
        
         # 接龙逻辑
        if next_idiom != '':
            if next_idiom in idiom_list and next_idiom not in idioms_used and check_chain(next_idiom, last_idiom) :
                screen.blit(success, (width/2-success.get_width()/2, height/2-success.get_height()/2-80))
                idioms_used.append(next_idiom)
                last_idiom = next_idiom
                t = True
            elif next_idiom in idiom_list and next_idiom in idioms_used and t == False:
                screen.blit(used, (width/2-used.get_width()/2, height/2-used.get_height()/2-80))
                t = False
            elif next_idiom not in idiom_list and t==False:
                screen.blit(not_idiom, (width/2-not_idiom.get_width()/2, height/2-not_idiom.get_height()/2-80))
                t = False
            elif next_idiom in idiom_list and next_idiom not in idioms_used and (not check_chain(next_idiom, last_idiom)) and t==False:
                screen.blit(not_matched, (width/2-not_matched.get_width()/2, height/2-not_matched.get_height()/2-80))
                t = False   
        if not next_idiom in idiom_list and next_idiom not in idioms_used and t==True:
            t = False
        if t:  # 如果t为True，则继续显示success直到下一步操作
            screen.blit(success, (width/2-success.get_width()/2, height/2-success.get_height()/2-80))

    # 显示窗口
    pygame.display.flip()
