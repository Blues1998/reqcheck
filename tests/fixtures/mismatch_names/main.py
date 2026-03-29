from PIL import Image  # package is Pillow
import yaml  # package is PyYAML

img = Image.open("photo.jpg")
data = yaml.safe_load("{}")
