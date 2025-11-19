import pygame 
import string
import os
import random
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import ttk
from PIL import ImageDraw, ImageFont
# Initialize pygame mixer
pygame.mixer.init()

# Define sound effects
correct_guess_sound = pygame.mixer.Sound('correct_guess.wav')
wrong_guess_sound = pygame.mixer.Sound('wrong_guess.wav')
win_sound = pygame.mixer.Sound('win_sound.mp3')
game_over_sound = pygame.mixer.Sound('game_over.wav')

word_lists = {
    'Beginner': {
        'animals': ['tiger', 'zebra', 'koala', 'snake', 'goose', 'otter', 'raven', 'gazelle', 'skunk', 'whale', 'horse', 'sloth', 'crane', 'lemur', 'shark', 'frogs', 'sheep', 'zebra'],
        'fruits': ['mango', 'melon', 'grape', 'lemon', 'peach', 'grape', 'melon', 'grape', 'lemon'],
        'flowers': ['tulip', 'daisy', 'lupin', 'aster', 'lotus', 'violet', 'tulip', 'clove', 'daisy', 'rose', 'clove', 'daisy', 'tulip']
    },
    'Intermediate': {
        'animals': ['zebra', 'whale', 'panda', 'shark', 'tiger', 'horse', 'lemur', 'koala', 'otter', 'raven', 'skunk', 'frogs'],
        'fruits': ['peach', 'melon', 'mango', 'grape', 'lemon', 'apple', 'berry', 'grape', 'melon'],
        'flowers': ['tulip', 'rose', 'daisy', 'poppy', 'violet', 'tulip', 'daisy', 'poppy', 'violet']
    },
    'Advanced': {
        'animals': ['hippo', 'rhino', 'crocs', 'chimp', 'lemur', 'hyena', 'dingo', 'whale', 'shark'],
        'fruits': ['pomeg', 'persi', 'grape', 'mango', 'quinc', 'guava', 'dates', 'plant', 'lemon', 'lyche', 'apric', 'papay', 'mulbe', 'berry', 'prune', 'mango', 'grape'],
        'flowers': ['chrys', 'hydrn', 'anemo', 'camel', 'clemi', 'tulip', 'daisy', 'poppy', 'daffo', 'vibur', 'mimic', 'dahli']
    }
}

class GameApplication:
    def __init__(self):
        self.selected_difficulty = None
        self.difficulty_frame = None
        self.game_frame = None
        self.create_difficulty_frame()

    def create_difficulty_frame(self):
        self.difficulty_frame = tk.Tk()
        self.difficulty_frame.title("Word Guessing Game")
        self.difficulty_frame.geometry("950x630")

        try:
            bg_image = PhotoImage(file="background_image.png")
        except Exception as e:
            print(f"Error loading background image: {e}")
            bg_image = None

        if bg_image:
            bg_label = tk.Label(self.difficulty_frame, image=bg_image)
            bg_label.place(relwidth=1, relheight=1)


        x_position = 530  # Set the horizontal position
        y_position_beginner = 250
        y_position_intermediate = 320
        y_position_advanced = 390

        
        beginner_image = PhotoImage(file="beginner_image.png")
        intermediate_image = PhotoImage(file="intermediate_image.png")
        advanced_image = PhotoImage(file="advanced_image.png")
        play_image = PhotoImage(file="play_image.png")
        beginner_button = ttk.Button(self.difficulty_frame, command=lambda: self.set_selected_difficulty("Beginner"), image=beginner_image, compound=tk.LEFT)
        intermediate_button = ttk.Button(self.difficulty_frame, command=lambda: self.set_selected_difficulty("Intermediate"), image=intermediate_image, compound=tk.LEFT)
        advanced_button = ttk.Button(self.difficulty_frame, command=lambda: self.set_selected_difficulty("Advanced"), image=advanced_image, compound=tk.LEFT)

        # Center the buttons both horizontally and vertically
        beginner_button.place(x=x_position, y=y_position_beginner)
        intermediate_button.place(x=x_position, y=y_position_intermediate)
        advanced_button.place(x=x_position, y=y_position_advanced)

       
        # Add a play button
        play_button = ttk.Button(self.difficulty_frame, command=self.start_game,  image=play_image, compound=tk.LEFT)
        play_button.place(x=525, y=y_position_advanced + 70)  # Adjust the vertical position

        self.difficulty_frame.mainloop()
    def set_selected_difficulty(self, difficulty):
        self.selected_difficulty = difficulty

    def start_game(self):
        if self.selected_difficulty:
            self.difficulty_frame.destroy()

            self.game_frame = tk.Tk()
            self.game_frame.title("Word Guessing Game")
            self.game_frame.geometry("950x630")
            self.game_frame.resizable(1, 1)

            self.alphaList = list(string.ascii_lowercase)

            self.game = WordGuessingGame(self.selected_difficulty, self.game_frame, self.alphaList)

    def quit_game(self):
        self.game_frame.destroy()


class WordGuessingGame:
    def __init__(self, difficulty, master, alphaList):
        self.played_word = ""
        self.gameboard = []
        self.gameboard_finished = []
        self.guess_archive = ['Guesses:']
        self.lives = ['Lives(5):']
        self.end_state = False
        self.image_index = 0
        self.images = [
            'img0.png', 'img1.png', 'img2.png', 'img3.png', 'img4.png', 'img5.png', 'img6.png', 'img7.png', 'img8.png',
            'img9.png', 'img10.png', 'img11.png', 'img12.png', 'img13.png', 'img14.png', 'img15.png', 'img16.png',
            'img17.png', 'img18.png', 'img19.png', 'img20.png', 'img21.png', 'img22.png', 'img23.png', 'img24.png',
            'img25.png', 'img26.png', 'img27.png', 'img28.png', 'img29.png', 'img30.png', 'img31.png', 'img32.png',
            'img33.png', 'img34.png', 'img35.png', 'img36.png', 'img37.png', 'img38.png', 'img39.png', 'img40.png',
            'img41.png', 'img42.png', 'img43.png', 'img44.png', 'img45.png', 'img46.png', 'img47.png', 'img48.png',
            'img49.png', 'img50.png', 'img51'
        ]

        self.master = master
        self.alphaList = alphaList
        self.button_states = {letter: False for letter in self.alphaList}  # New attribute to store button states

        self.category = random.choice(list(word_lists[difficulty].keys()))
        self.word_list = word_lists[difficulty][self.category]

        self.played_word = random.choice(self.word_list)
        self.set_create_board(self.played_word)
        self.set_finished_board(self.played_word)

        self.create_gui()

    def set_finished_board(self, word):
        self.gameboard_finished = list(word)

    def set_create_board(self, word):
        self.gameboard = ['_'] * len(word)

    def set_move(self, guess, location):
        self.gameboard[location] = guess

    def set_guess(self, player_guess):
        if player_guess in self.guess_archive:
            print("You have already tried to play " + player_guess)
        elif player_guess in self.gameboard_finished:
            for position, char in enumerate(self.gameboard_finished):
                if char == player_guess:
                    self.set_move(player_guess, position)
                    self.animate_correct_guess()
        else:
            self.lives.append('x')
            self.guess_archive.append(player_guess)
            wrong_guess_sound.play()

    def animate_correct_guess(self):
        if self.image_index < len(self.images) - 1:
            self.image_index += 1
            img_path = self.images[self.image_index]
            img = Image.open(img_path)
            img = img.resize((600, 250))
            img = ImageTk.PhotoImage(img)
            self.img_label.config(image=img)
            self.img_label.image = img
            correct_guess_sound.play()

    def get_eg_status(self):
        if len(self.lives) == 6:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.end_state = True
            game_over_sound.play()
            result = messagebox.askquestion("GAME OVER!", f"GAME OVER: Thanks for playing! \n Answer:\t{''.join(self.gameboard_finished)}\nDo you want to play again?")
            if result == 'yes':
                self.restart_game()
            else:
                self.master.quit()
        elif self.gameboard == self.gameboard_finished:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.end_state = True
            win_sound.play()
            result = messagebox.askquestion("Congrats!", "You won! Thanks for playing!\nDo you want to play again?")
            if result == 'yes':
                self.restart_game()
            else:
                self.master.quit()

    def restart_game(self):
        self.master.destroy()
        app = GameApplication()
        app.difficulty_frame.mainloop()
    def quit_game(self):
        if self.game_frame:
            self.game_frame.destroy()
    # Quit the application
        self.difficulty_frame.destroy()

    def get_user_guess(self, letter):
        char = str(letter)
        if len(char) == 1 and char.isalpha():
            self.set_guess(char.lower())
        else:
            print("Guess must be a single letter!")

    def create_gui(self):
        try:
            game_bg_image = PhotoImage(file="background_image.png")
        except Exception as e:
            print(f"Error loading background image: {e}")
            game_bg_image = None

        if game_bg_image:
            game_bg_label = tk.Label(self.master, image=game_bg_image)
            game_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.gui_hint = tk.Label(self.master, text=f"Hint- Category: {self.category.capitalize()}\nFirst letter: {self.played_word[0].capitalize()}", font="Verdana 12 bold")
        self.gui_hint.pack(side="top")
        word_len = len(self.played_word)
        if word_len == 3:
            self.image_index = 3
        elif word_len == 4:
            self.image_index = 7
        elif word_len == 5:
            self.image_index = 12
        elif word_len == 6:
            self.image_index = 18
        elif word_len == 7:
            self.image_index = 25
        elif word_len == 8:
            self.image_index = 33
        elif word_len == 9:
            self.image_index = 43
        img_path = self.images[self.image_index]
        img = Image.open(img_path)
        img = img.resize((600, 250))
        img = ImageTk.PhotoImage(img)
        self.img_label = tk.Label(self.master, image=img)
        self.img_label.image = img
        self.img_label.pack()

        self.gui_gameboard = tk.Label(self.master, text=self.gameboard, font="Verdana 30 bold")
        self.gui_gameboard.pack(side="top")

        self.gui_guess_archive = tk.Label(self.master, text=self.guess_archive, font="Verdana 10 bold")
        self.gui_guess_archive.pack()
        self.gui_guess_archive.place(bordermode=OUTSIDE, x=100, y=300)

        self.gui_lives = tk.Label(self.master, text=self.lives, font="Verdana 10 bold")
        self.gui_lives.pack()
        self.gui_lives.place(bordermode=OUTSIDE, x=100, y=330)

        def btn_Click(letter):
            if not self.button_states[letter]:
                self.button_states[letter] = True
                self.get_user_guess(letter.lower())
                self.gui_gameboard['text'] = self.gameboard
                self.gui_guess_archive['text'] = self.guess_archive
                self.gui_lives['text'] = self.lives
                self.get_eg_status()
                print(letter)

        def create_button(letter, xpos, ypos):
            button = tk.Button(self.master, text=letter.upper(), command=lambda l=letter: btn_Click(l), font=("Pacifico", 16))
            button.pack()
            button.place(bordermode=OUTSIDE, height=50, width=100, x=xpos, y=ypos)
            self.buttons.append(button)
            return button

        def populate_board():
            c = 0
            xpos = 150
            ypos = 370
            while c < 26:
                if c == 6:
                    ypos = 420
                    xpos = 150
                elif c == 12:
                    ypos = 470
                    xpos = 150
                elif c == 18:
                    ypos = 520
                    xpos = 150
                elif c == 24:
                    ypos = 570
                    xpos = 150

                button = create_button(self.alphaList[c], xpos, ypos)
                self.buttons.append(button)
                xpos = xpos + 100
                c = c + 1

        self.buttons = []
        populate_board()


if __name__ == "__main__":
    app = GameApplication()
    app.difficulty_frame.mainloop()
