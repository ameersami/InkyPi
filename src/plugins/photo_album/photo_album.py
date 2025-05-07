from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image
from utils.app_utils import resolve_path
from pathlib import Path
import logging
import os
from utils.watch_buttons import Worker
from utils.image_utils import resize_image, change_orientation

logger = logging.getLogger(__name__)

class PhotoAlbum(BasePlugin):

    def __init__(self, config):
      super().__init__(config)  # Call the base class constructor
      self.device_config = None
      self.current_Image_Index = 0
      self.buttonWatcher = Worker(self.increment, self.decrement)  # Now created inside __init__
      self.inky_display = None

    def generate_image(self, settings, device_config, inky_display):
        
        # Open the image using Pillow
        try:
          self.device_config = device_config
          if inky_display is not None:
            self.inky_display = inky_display
          all_images = os.listdir(os.path.join(Path(resolve_path("static")), "images", "saved"))
          image_location = os.path.join(Path(resolve_path("static")), "images", "saved", all_images[self.current_Image_Index])
          image = Image.open(image_location)
        except Exception as e:
          print("Error reading file");
          logger.error(f"Failed to read image file: {str(e)}")
          raise RuntimeError("Failed to read image file.")

        self.current_Image_Index += 1

        if self.current_Image_Index < (len(all_images) - 1):
          print("Index is within range")
        else:
          self.current_Image_Index = 0

        return image

    def increment(self):
      if self.inky_display is not None:
        try:
          print("Increment index:")
          print(self.current_Image_Index)
          all_images = os.listdir(os.path.join(Path(resolve_path("static")), "images", "saved"))
          image_location = os.path.join(Path(resolve_path("static")), "images", "saved", all_images[self.current_Image_Index])
          image = Image.open(image_location)

          # Resize and adjust orientation
          image = change_orientation(image, "horizontal")
          image = resize_image(image, self.device_config.get_resolution(), [])

          self.current_Image_Index += 1
          if self.current_Image_Index < (len(all_images) - 1):
            print("Index is within range")
          else:
            self.current_Image_Index = 0

          self.inky_display.set_image(image)
          self.inky_display.show()
        except Exception as e:
          logger.error(f"Failed to read image file: {str(e)}")
          raise RuntimeError("Failed to read image file.")

    def decrement(self):
      if self.inky_display is not None:
        try:
          print("Decrement index:")
          print(self.current_Image_Index)
          self.current_Image_Index -= 2

          all_images = os.listdir(os.path.join(Path(resolve_path("static")), "images", "saved"))
          image_location = os.path.join(Path(resolve_path("static")), "images", "saved", all_images[self.current_Image_Index])
          image = Image.open(image_location)

          # Resize and adjust orientation
          image = change_orientation(image, "horizontal")
          image = resize_image(image, self.device_config.get_resolution(), [])

          self.current_Image_Index += 1
          if self.current_Image_Index < (len(all_images) - 1):
            print("Index is within range")
          else:
            self.current_Image_Index = 0

          self.inky_display.set_image(image)
          self.inky_display.show()
        except Exception as e:
          logger.error(f"Failed to read image file: {str(e)}")
          raise RuntimeError("Failed to read image file.")