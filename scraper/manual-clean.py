from selenium import webdriver
import pandas as pd
import sys

df = pd.read_csv("../server/data/channels.csv")
num = int(sys.argv[1]) if len(sys.argv) > 1 else 0
driver = webdriver.Firefox()

for index, row in df[num:].iterrows():
    column_value = row["ChannelUrl"]
    driver.execute_script(f"window.open('{column_value}/videos', '_blank');")
    driver.switch_to.window(driver.window_handles[1])
    validation = input(f"{index}, Delete Or Pass: ")

    if validation.strip().lower()[:1] == "d":
        print("Row deleted.")
        df.drop(index, inplace=True)
    elif validation.strip().lower()[:1] == "q":
        df.to_csv("channels.csv", index=False)
        exit(0)
    else:
        print("Row kept.")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

driver.quit()
df.to_csv("../server/data/channels.csv", index=False)
