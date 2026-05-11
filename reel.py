import os
import glob
import sys
import subprocess
import pygame
from PIL import Image
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

import moviepy.editor as mpy

class TextField():


    def __init__(self, pos, size, label):
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.label = label
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            mods = pygame.key.get_mods()
            cmd_or_ctrl = mods & (pygame.KMOD_META | pygame.KMOD_CTRL)
            if cmd_or_ctrl and event.key == pygame.K_v:
                pasted = get_clipboard_text()
                pasted = pasted.replace("\n", "").replace("\r", "")
                self.text += pasted
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.text += event.unicode

    def draw(self, surface, font, label_font):
        label_surf = label_font.render(self.label, True,
                                       pygame.Color(160, 160, 180))
        surface.blit(label_surf, (self.rect.x, self.rect.y - 22))
        bg = pygame.Color(40, 40, 50)
        border_color = (pygame.Color(100, 200, 255)
                        if self.active else pygame.Color(80, 80, 100))
        pygame.draw.rect(surface, bg, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        text_surf = font.render(self.text, True, pygame.Color(220, 220, 230))
        surface.blit(text_surf, (self.rect.x + 8, self.rect.y + 8))


class Button():

    def __init__(self, pos, size, label, color):
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.label = label
        self.color = pygame.Color(color)
        self.hover = False

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font):
        color = self.color
        if self.hover:
            color = pygame.Color(min(color.r + 30, 255),
                                  min(color.g + 30, 255),
                                  min(color.b + 30, 255))
        pygame.draw.rect(surface, color, self.rect)
        text = font.render(self.label, True, pygame.Color(255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


def watermark_images(src_paths, logo_path):
    logo_img = Image.open(logo_path)
    out_paths = []
    for src_path in src_paths:
        name, ext = os.path.splitext(src_path)
        with Image.open(src_path) as img:
            print(f"watermarking {src_path}... ")
            padding = 50
            x = padding
            y = img.height - logo_img.height - padding
            img.paste(logo_img, (x, y), mask=logo_img.getchannel('A'))
            out_path = f"{name}_wm{ext}"
            img.save(out_path)
            out_paths.append(out_path)
    logo_img.close()
    return out_paths


def build_video(img_paths, output_file):
    img_paths.sort()
    print(img_paths)
    clip = mpy.ImageSequenceClip(img_paths, fps=FPS)
    clip.write_videofile(output_file)
    clip.close()


def build_reel(media_folder, logo_path, output_file):
    img_seq = glob.glob(os.path.join(media_folder, '*.png'))
    img_seq.sort()
    if not img_seq:
        raise ValueError(f"No PNG files found in: {media_folder}")

    if logo_path:
        img_seq = watermark_images(img_seq, logo_path)

    build_video(img_seq, output_file)


def main():
    pygame.init()
    pygame.display.set_caption("Demo Reel Builder")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    label_font = pygame.font.SysFont(None, 20)
    title_font = pygame.font.SysFont(None, 36)

    media_field = TextField((40, 80), (WIDTH - 80, 36),
                            "Media folder (PNG frames)")
    logo_field = TextField((40, 160), (WIDTH - 80, 36),
                           "Logo path (optional)")
    output_field = TextField((40, 240), (WIDTH - 80, 36),
                             "Output file (e.g. reel.mp4)")
    fields = [media_field, logo_field, output_field]

    generate_btn = Button((40, 320), (WIDTH - 80, 50),
                          "Generate Reel", (50, 130, 220))

    status = "Fill in the fields and click Generate Reel."
    status_color = pygame.Color(160, 160, 180)

    running = True
    dt = 0
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            for field in fields:
                field.handle_event(event)
            if (event.type == pygame.MOUSEBUTTONDOWN
                    and generate_btn.clicked(event.pos)):
                try:
                    build_reel(media_field.text.strip(),
                               logo_field.text.strip(),
                               output_field.text.strip() or "reel.mp4")
                    status = "Done! Reel saved."
                    status_color = pygame.Color(80, 220, 120)
                except Exception as e:
                    status = f"Error: {e}"
                    status_color = pygame.Color(255, 90, 90)

        generate_btn.update(mouse_pos)

        # Draw frame
        black = pygame.Color(20, 20, 30)
        screen.fill(black)
        title = title_font.render("Demo Reel Builder", True,
                                  pygame.Color(100, 200, 255))
        screen.blit(title, (40, 20))

        for field in fields:
            field.draw(screen, font, label_font)
        generate_btn.draw(screen, font)

        status_surf = label_font.render(status, True, status_color)
        screen.blit(status_surf, (40, HEIGHT - 40))

        pygame.display.flip()
        dt = clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()