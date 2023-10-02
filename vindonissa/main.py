#!/usr/bin/env python3

import pygame
import pygame_gui

from vindonissa.menu import Menu


class MainLoop(object):
    def __init__(self):
        self.display_width = 1200
        self.display_height = 800
        self.display = (self.display_width, self.display_height)

        self.pygame = pygame

    def update_screen(self):
        self.manager.draw_ui(self.window_surface)
        pygame.display.update()

    def write_left_text(self, text: str):
        assert self.left_text is not None
        self.left_text.append_html_text("<br>" + text)
        self.update_screen()

    def build_interface(self):
        datebox_height = 40
        datebox_width = 140
        self.date_box = pygame_gui.elements.UITextBox(
            "01. Jan. 0001",
            pygame.Rect((10, 10, datebox_width, datebox_height)))
        
        button_width = 50
        self.speed_settings = ["II", "1x", "2x", "4x", "8x"]
        self.speed_values = [0, 1000, 500, 250, 125]
        self.speed_buttons = []
        for i, ss in enumerate(self.speed_settings):
            x_pos = datebox_width + 10 + i * button_width
            self.speed_buttons.append(pygame_gui.elements.UIButton(pygame.Rect((x_pos, 10, button_width, datebox_height)), ss))

        self.left_text = pygame_gui.elements.UITextBox(
            "",
            pygame.Rect((10, 10 + datebox_height, self.display_width/2-20, self.display_height-60-datebox_height)))
        self.left_input = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((10, self.display_height-50, self.display_width/2-20, 40))
        )
        self.right_text = pygame_gui.elements.UITextBox(
            "",
            pygame.Rect((self.display_width/2, 10, self.display_width/2-10, self.display_height-60)))
        self.right_input = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((self.display_width/2, self.display_height-50, self.display_width/2-10, 40))
        )

    def assign_session(self, session):
        self.session = session

    def start_game(self):
        pygame.init()

        pygame.display.set_caption('Quick Start')
        self.window_surface = pygame.display.set_mode(self.display)

        background = pygame.Surface(self.display)
        background.fill(pygame.Color('#000000'))

        self.manager = pygame_gui.UIManager(self.display)

        self.build_interface()

        clock = pygame.time.Clock()
        # start in menu, may switch later
        scene = Menu(self)
        self.session = None
        # TODO: change menu so it shows this whenever scene switches to it
        
        is_running = True
        while is_running:
            time_delta = clock.tick(60)/1000.0

            day_passed = False  # makes sure at maximum one day can pass per frame

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

                if event.type == pygame_gui.UI_BUTTON_PRESSED and self.session is not None:
                    self.session.calendar.start_timer(self.speed_values[self.speed_buttons.index(event.ui_element)])

                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.left_input:
                        text_elem = self.left_text  
                        input_elem = self.left_input 
                    elif event.ui_element == self.right_input:
                        text_elem = self.right_text  
                        input_elem = self.right_input
                    else:
                        continue
                        
                    text_elem.append_html_text("<br>> " + event.text)
                    input_elem.clear()
                    self.update_screen()
                    scene.process_command(event.text)

                if self.session is not None and event.type == self.session.calendar.time_event and not day_passed:
                    self.session.calendar.pass_day()
                    self.date_box.clear()
                    self.date_box.append_html_text(self.session.calendar.datestring)
                    day_passed = True

                self.manager.process_events(event)

            self.manager.update(time_delta)

            self.window_surface.blit(background, (0, 0))
            self.manager.draw_ui(self.window_surface)

            pygame.display.update()

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


if __name__ == "__main__":
    m = MainLoop()
    m.start_game()
    
