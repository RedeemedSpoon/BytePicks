from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from random import choice
from time import sleep
import os, json

channelsIDs = []
addonPath = os.path.expanduser("~/.mozilla/firefox/qz5c3f97.default-release/extensions/uBlock0@raymondhill.net.xpi")
with open("topics.json", "r") as file:
    searchTerms = json.load(file)["EN"]

options = FirefoxOptions()
options.add_argument("--headless")
options.set_preference("media.volume_scale", "0.0")
driver = webdriver.Firefox(options=options)
driver.install_addon(addonPath)

for _ in range(50):
    try:
        chosenTopic = choice(searchTerms)
        searchTerms.remove(chosenTopic)
        driver.get(f"https://www.youtube.com/results?search_query={chosenTopic}&lr=lang_en")
        sleep(2)

        allRecommendedChannels = driver.find_elements(By.ID, "channel-thumbnail")
        channels = [channel.get_attribute("href").split("@")[1] for channel in allRecommendedChannels]

        videoLinks = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
        choice(videoLinks[5:]).click()

        for i in range(7):
            sleep(3)
            recommendedChannel = driver.find_element(By.CSS_SELECTOR, "a.ytd-video-owner-renderer").get_attribute("href")
            recommendedVideo = driver.find_elements(By.TAG_NAME, "ytd-compact-video-renderer")
            choice(recommendedVideo[:5]).click()
            channels.append(recommendedChannel.split("@")[1])

        driver.get("https://www.streamweasels.com/tools/youtube-channel-id-and-user-id-convertor/")
        form = driver.find_element(By.CLASS_NAME, "cp-youtube-to-id__target")
        result = driver.find_element(By.CLASS_NAME, "cp-youtube-to-id__result")

        for channel in channels:
            form.clear()
            form.send_keys(channel + Keys.RETURN)
            sleep(1)
            channelsIDs.append(result.text)

        with open("new.csv", "a") as f:
            f.writelines(channelId + "\n" for channelId in channelsIDs)
    except:
        pass

driver.quit()
