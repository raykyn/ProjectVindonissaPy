#!/usr/bin/env python3

import pygame
import pygame_gui

import menu

DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 800
DISPLAY = (DISPLAY_WIDTH, DISPLAY_HEIGHT)

def update_screen(manager, surface):
    manager.draw_ui(surface)
    pygame.display.update()

def main():
    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode(DISPLAY)

    background = pygame.Surface(DISPLAY)
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager(DISPLAY)

    LEFT_TEXT = pygame_gui.elements.UITextBox(
        "",
        pygame.Rect((10, 10, DISPLAY_WIDTH/2-20, DISPLAY_HEIGHT-60)))
    left_input = pygame_gui.elements.UITextEntryLine(
        pygame.Rect((10, DISPLAY_HEIGHT-50, DISPLAY_WIDTH/2-20, 40))
    )
    RIGHT_TEXT = pygame_gui.elements.UITextBox(
        "",
        pygame.Rect((DISPLAY_WIDTH/2, 10, DISPLAY_WIDTH/2-10, DISPLAY_HEIGHT-60)))
    right_input = pygame_gui.elements.UITextEntryLine(
        pygame.Rect((DISPLAY_WIDTH/2, DISPLAY_HEIGHT-50, DISPLAY_WIDTH/2-10, 40))
    )

    # give scenes references to the objects in main
    menu.LEFT_TEXT = LEFT_TEXT
    menu.RIGHT_TEXT = RIGHT_TEXT

    clock = pygame.time.Clock()
    is_running = True

    # start in menu, may switch later
    scene = menu
    LEFT_TEXT.append_html_text(menu.welcome_message)

    to_process = []
    while is_running:
        time_delta = clock.tick(60)/1000.0

        if to_process:
            for t in to_process:
                scene.process_command(t.text)
            to_process = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                text_elem: pygame_gui.elements.UITextBox = None
                input_elem: pygame_gui.elements.UITextEntryLine = None
                if event.ui_element == left_input:
                    text_elem = LEFT_TEXT  
                    input_elem = left_input 
                elif event.ui_element == right_input:
                    text_elem = RIGHT_TEXT  
                    input_elem = right_input
                    
                text_elem.append_html_text("<br>> " + event.text)
                update_screen(manager, window_surface)
                to_process.append(event)
                input_elem.clear()

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

if __name__ == "__main__":
    main()
    
