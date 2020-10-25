import os

import spotipy
import yaml
from spotipy.oauth2 import SpotifyOAuth

from gui import Gui


class AlbumArt:
    config = None
    gui = None

    @staticmethod
    def load_config():
        try:
            # read in the config file
            with open(os.getcwd() + '/app_config.yaml') as app_config_file:
                AlbumArt.config = yaml.full_load(app_config_file)

            app_config_file.close()
        except OSError:
            print('ERROR trying to read ' + os.getcwd() + '/app_config.yaml')

    @staticmethod
    def create_spotify_obj():
        credentials = AlbumArt.config['credentials']

        spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            username=credentials['username'],
            client_id=credentials['id'],
            client_secret=credentials['secret'],
            scope=credentials['scope'],
            redirect_uri=credentials['uri']))

        return spotify

    @staticmethod
    def init():
        AlbumArt.load_config()

        spotify = AlbumArt.create_spotify_obj()

        AlbumArt.gui = Gui(spotify,
                           AlbumArt.config['dimensions'],
                           AlbumArt.config['fonts'],
                           AlbumArt.config['timings'])


if __name__ == '__main__':
    AlbumArt.init()
    AlbumArt.gui.update()
    AlbumArt.gui.mainloop()
