import os
import glob
import sys
import subprocess
import pygame
from PIL import Image
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

import moviepy.editor as mpy


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