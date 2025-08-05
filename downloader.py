# https://github.com/rainier39/Minecraft-Modpack-Downloader
import json
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
import time
import sys
from zipfile import ZipFile

def gracefulExit():
  # If we're on Windows, wait for user input so the window doesn't just close with no output from their perspective.
  if (sys.platform == "win32"):
    input("Press enter to exit: ")
  exit()

# Prompt the user for a modpack file if one wasn't supplied on the command line.
if (len(sys.argv) < 2):
  modpack = input("Please enter the name of the modpack file: ")
else:
  modpack = sys.argv[1]

# Make sure the file exists and is a file (not a directory).
if os.path.isfile(modpack) and not os.path.isdir(modpack):
  with ZipFile(os.path.join(os.getcwd(), modpack), "r") as z:
    print("Extracting zipfile...")
    z.extractall(os.path.join(os.getcwd(), modpack[:modpack.rfind(".")]))
# Print an error and exit if there isn't a file.
else:
  print("Error: specified file doesn't exist.")
  gracefulExit()

print("Finished extracing zipfile.")

# Open and read the files that contain the links to the mods and the ids of the specific mod files.
with open(os.path.join(os.getcwd(), modpack[:modpack.rfind(".")] + "/manifest.json"), "r") as f:
  parsed = json.load(f)
with open(os.path.join(os.getcwd(), modpack[:modpack.rfind(".")] + "/modlist.html"), "r") as f:
  S = BeautifulSoup(f.read(), 'lxml')

URLS = []
links = []

# Get the links to the mods, change to the legacy site URL so that direct links to the files can be made.
for tag in S.find_all('a'):
  URLS.append(tag["href"].replace("www.curseforge", "legacy.curseforge"))
# Construct the links to each individual mod file itself.
for URL, p in zip(URLS, parsed["files"]):
  temp = URL + "/download/" + str(p["fileID"]) + "/file"
  links.append(temp)

# Store the path to the mods folder in a variable, we will be using it multiple times.
modsdir = os.path.join(os.getcwd(), modpack[:modpack.rfind(".")] + "/overrides/mods")

# Create a mods folder inside the modpack's override folder if it doesn't exist yet.
if not os.path.isdir(modsdir):
  os.mkdir(modsdir)

# Initialize a Chrome browser.
options = webdriver.ChromeOptions()
# We need these options for the downloads to work.
prefs = {"download.default_directory" : modsdir, "download.prompt_for_download": False, "download.directory_upgrade": True, "safebrowsing.enabled": True}#, "safebrowsing_for_trusted_sources_enabled": False}
options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(options=options)
params = {"behavior" : "allow", "downloadPath": modsdir}
driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

print("Downloading mods from modpack...")

# Download the mods.
for link in links:
  driver.get(link)

# Wait for all of the files to finish downloading.
while True:
  files = os.listdir(modsdir)
  if any(f.endswith(".crdownload") for f in files):
    time.sleep(1)
  else:
    break

# Exit.
print("Finished downloading mods from modpack.")
driver.quit()
gracefulExit()
