from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

import kivy

import sqlite3 as sl
import bussiness
import random

kivy.require('1.9.1')

Window.keyboard_anim_args = {'d': 0.2, 't': 'in_out_quart'}
Window.softinput_mode = 'below_target'


class MyRoot(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.con = sl.connect("resources/pokedata.db")

        self.scroll_speed = 0.1
        self.event = Clock.schedule_interval(self.scroll_text, self.scroll_speed)

        self.pkmn_count = 898

        self.all_pokemon_entries = []
        self.entry_idx = 0
        self.pokemon_number = 1
        self.pokemon_name = ""

        self.image_info = []
        self.sprite_idx = 0
        self.character_idx = 0

        self.ui_sound = SoundLoader.load("resources/ui_assets/text_sound_pkmn.wav")

        self.cry_index = 0
        self.play_once = True
        self.pkmn_cry_list = []
        self.pkmn_cry = None
        self.cry_volume = 0.2

        self.get_pkmn_info(self.pokemon_number)
        self.update_view()

    def get_pkmn_info(self, number_or_name):
        cur = self.con.cursor()
        cur.execute("SELECT ID, NAME, DESCRIPTION, IMAGE_INFO, CRY FROM POKEMON_DATA WHERE ID=? OR NAME=?",
                    (number_or_name, number_or_name))
        rec = cur.fetchall()[0]
        self.pokemon_number, self.pokemon_name = str(rec[0]).zfill(3), rec[1]
        formatted_text = bussiness.format_input_text(rec[2])
        self.all_pokemon_entries = list(filter(None, formatted_text.split("\n")))
        self.all_pokemon_entries.append(formatted_text)
        self.entry_idx = 0

        self.image_info = list(filter(None, rec[3].split("\n")))
        self.sprite_idx = 0

        self.pkmn_cry_list = list(filter(None, rec[4].split("\n")))
        self.cry_index = random.randrange(len(self.pkmn_cry_list))
        self.play_pkmn_cry()

    def update_view(self):
        self.ids.pokedex_number.text = "#" + str(self.pokemon_number).zfill(3)
        self.ids.pokedex_name.text = self.pokemon_name
        self.ids.pokedex_entry.text = self.all_pokemon_entries[0][0]
        self.character_idx = 0
        self.event = Clock.schedule_interval(self.scroll_text, self.scroll_speed)
        self.ids.pokedex_sprite.source = self.image_info[self.sprite_idx]

    def get_next_pkmn(self):
        current_pokemon_num = int(self.pokemon_number)

        if current_pokemon_num < self.pkmn_count:
            self.pokemon_number = current_pokemon_num + 1
        else:
            self.pokemon_number = 1

        self.get_pkmn_info(self.pokemon_number)
        self.update_view()
        self.ui_sound.play()

    def get_previous_pkmn(self):
        current_pokemon_num = int(self.pokemon_number)

        if current_pokemon_num > 1:
            self.pokemon_number = current_pokemon_num - 1
        else:
            self.pokemon_number = self.pkmn_count

        self.get_pkmn_info(self.pokemon_number)
        self.update_view()
        self.character_idx = 0
        self.ui_sound.play()

    def change_sprite(self, touch):
        relative_pos_x = touch.x/Window.width
        if relative_pos_x <= 0.5:
            self.get_previous_sprite()
        else:
            self.get_next_sprite()

    def get_next_sprite(self):
        self.sprite_idx += 1
        if self.sprite_idx >= len(self.image_info) - 1:
            self.sprite_idx = 0
        self.ui_sound.play()
        self.ids.pokedex_sprite.source = self.image_info[self.sprite_idx]

    def get_previous_sprite(self):
        self.sprite_idx -= 1
        if self.sprite_idx < 0:
            self.sprite_idx = len(self.image_info) - 1
        self.ui_sound.play()
        self.ids.pokedex_sprite.source = self.image_info[self.sprite_idx]

    def play_pkmn_cry(self, dt=0):
        self.pkmn_cry = SoundLoader.load(self.pkmn_cry_list[self.cry_index])
        self.pkmn_cry.volume = self.cry_volume
        self.pkmn_cry.play()

    def get_next_pkmn_sound(self):
        self.cry_index += 1
        if self.cry_index >= len(self.pkmn_cry_list):
            self.cry_index = 0
        self.play_pkmn_cry()

    def get_next_entry(self):
        if self.character_idx < len(self.all_pokemon_entries[self.entry_idx]):
            self.ids.pokedex_entry.text = self.all_pokemon_entries[self.entry_idx]
            Clock.unschedule(self.event)
            self.character_idx = len(self.all_pokemon_entries[self.entry_idx])
            self.ui_sound.play()
        else:
            self.entry_idx += 1
            self.character_idx = 0
            if self.entry_idx >= len(self.all_pokemon_entries):
                self.entry_idx = 0
            self.event = Clock.schedule_interval(self.scroll_text, self.scroll_speed)
            self.ui_sound.play()

    def scroll_text(self, dt=0):
        self.character_idx += 1
        self.ids.pokedex_entry.text = self.all_pokemon_entries[self.entry_idx][0:self.character_idx]
        if self.character_idx >= len(self.all_pokemon_entries[self.entry_idx]):
            Clock.unschedule(self.event)

    def search_pokemon(self):
        searched_pkmn = self.ids.search_pkmn_box.text
        try:
            self.get_pkmn_info(searched_pkmn.capitalize())
            self.update_view()
            self.ids.search_pkmn_box.text = ""
        except IndexError:
            popup = Popup(title="", separator_height=0,
                          content=TextInput(text='Name or entry not in the Pokédex.\n Check for spelling errors',
                                            font_size="15dp",
                                            multiline=False,
                                            background_color=(1, 1, 1, 0),
                                            disabled_foreground_color=(1, 1, 1, 1),
                                            halign='center',
                                            readonly=True,
                                            disabled=True),

                          size_hint=(0.9, 0.2))
            popup.open()
            self.ids.search_pkmn_box.text = ""


class ImageButton(ButtonBehavior, Image):
    pass


class SpriteButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(SpriteButton, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            relative_x = touch.x/Window.width
            if relative_x >= 0.5:
                self.app.root.get_next_sprite()
            else:
                self.app.root.get_previous_sprite()
        return super(SpriteButton, self).on_touch_down(touch)


class EntryText(ButtonBehavior, TextInput):
    pass


class Pokedex(App):
    def build(self):
        return MyRoot()


pokedex = Pokedex()
pokedex.run()