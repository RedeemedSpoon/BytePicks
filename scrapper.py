from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from random import choice
from time import sleep
import os, json

channels_ids = []
addon_path = os.path.expanduser("~/.mozilla/firefox/qz5c3f97.default-release/extensions/uBlock0@raymondhill.net.xpi")
with open("topics.json", "r") as file:
    search_terms = json.load(file)["EN"]

options = FirefoxOptions()
options.add_argument("--headless")
options.set_preference("media.volume_scale", "0.0")
driver = webdriver.Firefox(options=options)
driver.install_addon(addon_path)

for _ in range(50):
    try:
        chosen_topic = choice(search_terms)
        search_terms.remove(chosen_topic)
        driver.get(f"https://www.youtube.com/results?search_query={chosen_topic}"); sleep(2)

        recommended_channels = driver.find_elements(By.ID, "channel-thumbnail")
        channels = [channel.get_attribute("href").split("@")[1] for channel in recommended_channels]

        video_links = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
        choice(video_links[5:]).click()

        for __ in range(7):
            sleep(3); recommended_channel = driver.find_element(By.CSS_SELECTOR, "a.ytd-video-owner-renderer").get_attribute("href")
            recommended_video = driver.find_elements(By.TAG_NAME, "ytd-compact-video-renderer")
            choice(recommended_video[:5]).click()
            channels.append(recommended_channel.split("@")[1])

        driver.get("https://www.streamweasels.com/tools/youtube-channel-id-and-user-id-convertor/")
        form = driver.find_element(By.CLASS_NAME, "cp-youtube-to-id__target")
        result = driver.find_element(By.CLASS_NAME, "cp-youtube-to-id__result")

        for channel in channels:
            form.clear()
            form.send_keys(channel + Keys.RETURN); sleep(1)
            channels_ids.append(result.text)

        with open("channels.csv", "a") as f:
            f.writelines(channel_id + "\n" for channel_id in channels_ids)
    except:
        pass

driver.quit()
