"""
This is the main module. Main function initializes
the GUI and calls the mainloop
"""
import os

import spotipy
import yaml
from dotmap import DotMap
from spotipy.oauth2 import SpotifyOAuth

from gui import Gui


class AlbumArt:
    """Main class of Album Art"""
    config = None
    gui = None

    @staticmethod
    def load_config():
        """Loads the yaml config file"""
        try:
            # read in the config file
            with open(os.getcwd() + '/app_config.yaml') as app_config_file:
                AlbumArt.config = DotMap(yaml.full_load(app_config_file))

            app_config_file.close()
        except OSError:
            print('ERROR trying to read ' + os.getcwd() + '/app_config.yaml')

    @staticmethod
    def create_spotify_obj():
        """Create the Spotify object"""

        spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            username=AlbumArt.config.credentials.username,
            client_id=AlbumArt.config.credentials.id,
            client_secret=AlbumArt.config.credentials.secret,
            scope=AlbumArt.config.credentials.scope,
            redirect_uri=AlbumArt.config.credentials.uri))

        return spotify

    @staticmethod
    def init():
        """Initializations - load config, create Spotify object, create the GUI"""
        AlbumArt.load_config()
        spotify = AlbumArt.create_spotify_obj()
        AlbumArt.gui = Gui(spotify, AlbumArt.config)


if __name__ == '__main__':
    AlbumArt.init()
    AlbumArt.gui.update()
    AlbumArt.gui.mainloop()
