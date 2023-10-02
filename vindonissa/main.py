#!/usr/bin/env python3

import pygame
import pygame_gui

from vindonissa.util.calendar import Calendar

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

    datebox_height = 40
    datebox_width = 140
    DATE_BOX = pygame_gui.elements.UITextBox(
        "01. Jan. 0001",
        pygame.Rect((10, 10, datebox_width, datebox_height)))
    
    button_width = 50
    speed_settings = ["II", "1x", "2x", "4x", "8x"]
    speed_values = [0, 1000, 500, 250, 125]
    speed_buttons = []
    for i, ss in enumerate(speed_settings):
        x_pos = datebox_width + 10 + i * button_width
        speed_buttons.append(pygame_gui.elements.UIButton(pygame.Rect((x_pos, 10, button_width, datebox_height)), ss))

    LEFT_TEXT = pygame_gui.elements.UITextBox(
        "",
        pygame.Rect((10, 10 + datebox_height, DISPLAY_WIDTH/2-20, DISPLAY_HEIGHT-60-datebox_height)))
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

    calendar = Calendar(pygame)

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

        day_passed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                calendar.start_timer(speed_values[speed_buttons.index(event.ui_element)])

            """
            TODO: Reimplement keyboard shortcuts for time control later
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                if timespeed == 0:
                    print("UNPAUSE")
                    timespeed = 1000
                    calendar.start_timer(1000)
                else:
                    print("PAUSE")
                    timespeed = 0
                    calendar.start_timer(0)
            """

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == left_input:
                    text_elem = LEFT_TEXT  
                    input_elem = left_input 
                elif event.ui_element == right_input:
                    text_elem = RIGHT_TEXT  
                    input_elem = right_input
                else:
                    continue
                    
                text_elem.append_html_text("<br>> " + event.text)
                update_screen(manager, window_surface)
                to_process.append(event)
                input_elem.clear()

            if event.type == calendar.time_event and not day_passed:
                calendar.pass_day()
                DATE_BOX.clear()
                DATE_BOX.append_html_text(calendar.datestring)
                day_passed = True
                
            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

if __name__ == "__main__":
    main()
    
