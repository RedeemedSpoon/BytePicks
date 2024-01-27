from googleapiclient.discovery import build
import os, datetime, isodate, json, sys
from math import sqrt, log
import pandas as pd

MIN_DUR = isodate.parse_duration("PT30S")
MAX_DUR = isodate.parse_duration("PT10H")
LANGUAGE = ["EN", "FR", "ES", "DE", "PT", "RU", "HI"]
FIELDS = "items(snippet(title,publishedAt,channelTitle,channelId,thumbnails/medium/url), contentDetails(upload/videoId))"

CAPTION_MAPPING = {None: 0.975}
RATING_MAPPING = {None: 1}
DEFINITION_MAPPING = {"sd": 0.90, "fhd": 1.025, "uhd": 1.05}
SUBSCRIBER_MAPPING = {10_000: 1.05, 100_000: 1.025, 500_000: 1, 1_000_000: 0.975, 5_000_000: 0.95}
DURATIONS_MAPPING = [
    (isodate.parse_duration("PT2M"), 0.500),
    (isodate.parse_duration("PT7M"), 0.950),
    (isodate.parse_duration("PT15M"), 0.975),
    (isodate.parse_duration("PT30M"), 1),
    (isodate.parse_duration("PT45M"), 1.025),
    (isodate.parse_duration("PT1H"), 1.050),
]


def search():
    global curPageToken
    request = service.search().list(
        q="programming | coding | computer science | tech | ai | cloud computing | computer",
        type="channel",
        part="id",
        maxResults=50,
        order="relevance",
        relevanceLanguage="en",
        pageToken=curPageToken,
    )

    response = request.execute()
    for item in response.get("items", []):
        tempId = item["id"]["channelId"]
        searchedChannels.append(tempId)

    curPageToken = response.get("nextPageToken")
    if curPageToken is not None:
        search()


def updateInfoChannels():
    for channel in searchedChannels:
        print("Updating channel: " + channel)
        request = service.channels().list(part=["snippet", "statistics", "brandingSettings"], id=channel)
        response = request.execute()

        channelInfo = {
            "ChannelID": response["items"][0]["id"],
            "ChannelName": response["items"][0]["snippet"]["title"],
            "ChannelIcon": response["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
            "ChannelUrl": f'https://www.youtube.com/{response["items"][0]["snippet"].get("customUrl", "None")}',
            "ExistedSince": response["items"][0]["snippet"]["publishedAt"].split("T")[0],
            "SubscriberCount": int(response["items"][0]["statistics"]["subscriberCount"]),
            "VideoCount": int(response["items"][0]["statistics"]["videoCount"]),
            "ViewCount": int(response["items"][0]["statistics"]["viewCount"]),
            "Country": response["items"][0]["snippet"].get("country", "Unknown"),
            "Language": response["items"][0]["snippet"].get("defaultLanguage", "Unknown"),
        }
        if channelInfo["SubscriberCount"] > 10000:
            channels.append(channelInfo)

    df = pd.DataFrame(channels)
    df = pd.concat([channelDF, df], ignore_index=True)
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    to_drop = df["SubscriberCount"] < 10000
    df.drop(df[to_drop].index, inplace=True)
    df.to_csv("data/channels.csv", index=False)


def allMightyAlgorithm(video: json, vidDuration: isodate, SubscriberCount: str) -> int:
    NRLLikeCount = log(video["LikeCount"] + 1)
    NRLCommentCount = log(video["CommentCount"] + 1)
    NRLViewCount = log(video["ViewCount"] + 1)

    viewRate = NRLViewCount / 3.50
    likeRate = NRLLikeCount / NRLViewCount
    commentRate = NRLCommentCount / NRLViewCount * 1.25

    defQuality = DEFINITION_MAPPING.get(video["Definition"], 1)
    capQuality = CAPTION_MAPPING.get(video["Caption"], 1)
    ratQuality = RATING_MAPPING.get(video["ContentRating"], 0.925)
    durQuality = next((quality for duration, quality in DURATIONS_MAPPING if vidDuration < duration), 0.90)
    subBalance = next((balance for channel, balance in SUBSCRIBER_MAPPING.items() if SubscriberCount < channel), 0.925)

    qualityMultiplier = float(subBalance * defQuality * capQuality * ratQuality * durQuality)
    rating = round((viewRate + likeRate + commentRate) * qualityMultiplier * 100, 3)
    return rating


def fetchNewVideos():
    for channel in channelDF["ChannelID"]:
        subcriberCount = channelDF[channelDF["ChannelID"] == channel]["SubscriberCount"].values[0]
        request = service.activities().list(
            part=["snippet", "id", "contentDetails"],
            channelId=channel,
            publishedAfter=yesterday.isoformat() + "T00:00:00Z",
            maxResults=5,
            fields=FIELDS,
        )

        response = request.execute()
        for item in response["items"]:
            try:
                channelName = item["snippet"]["channelTitle"]
                channelId = item["snippet"]["channelId"]
                videoTitle = item["snippet"]["title"]
                videoId = item["contentDetails"]["upload"]["videoId"]
                publishedAt = item["snippet"]["publishedAt"][:16].replace("T", " ")
                thumbnailUrl = item["snippet"]["thumbnails"]["medium"]["url"]

                request = service.videos().list(id=videoId, part=["statistics", "snippet", "contentDetails"])
                response = request.execute()

                viewCount = int(response["items"][0]["statistics"]["viewCount"])
                likeCount = int(response["items"][0]["statistics"]["likeCount"])
                commentCount = int(response["items"][0]["statistics"].get("commentCount", 0))
                categoryId = int(response["items"][0]["snippet"]["categoryId"])
                contentRating = response["items"][0]["contentDetails"]["contentRating"]
                definition = response["items"][0]["contentDetails"]["definition"]
                duration = isodate.parse_duration(response["items"][0]["contentDetails"]["duration"])
                caption = response["items"][0]["contentDetails"]["caption"]
                language = str(
                    response["items"][0]["snippet"].get(
                        "defaultLanguage", response["items"][0]["snippet"].get("defaultAudioLanguage")
                    )
                ).upper()

                if categoryId in [27, 28] and viewCount > 1000 and MIN_DUR < duration < MAX_DUR and language[:2] in LANGUAGE:
                    fullVideoDetails = {
                        "ChannelName": channelName,
                        "ChannelId": channelId,
                        "ChannelIcon": channelDF[channelDF["ChannelID"] == channelId]["ChannelIcon"].values[0],
                        "ChannelUrl": channelDF[channelDF["ChannelID"] == channelId]["ChannelUrl"].values[0],
                        "VideoUrl": f"https://www.youtube.com/watch?v={videoId}",
                        "VideoTitle": videoTitle,
                        "VideoId": videoId,
                        "PublishedDate": publishedAt,
                        "Thumbnail": thumbnailUrl,
                        "Duration": str(duration).split(", ")[1] if ", " in str(duration) else str(duration),
                        "Definition": str(definition).upper(),
                        "language": language,
                        "Caption": False if caption == "false" else True,
                        "ContentRating": False if not contentRating else True,
                        "ViewCount": int(viewCount),
                        "LikeCount": int(likeCount),
                        "CommentCount": int(commentCount),
                        "CategoryId": int(categoryId),
                    }

                    videoRating = allMightyAlgorithm(fullVideoDetails, duration, subcriberCount)
                    Videos[videoRating] = fullVideoDetails
            except:
                pass


def deleteOldVideos():
    if today.weekday() == 0:
        with open("videos/weekly.json", "w") as f:
            json.dump({}, f)

    if today.day == 1:
        with open("videos/monthly.json", "w") as f:
            json.dump({}, f)

    if today.day == 1 and today.month == 1:
        with open("videos/yearly.json", "w") as f:
            json.dump({}, f)


def storeVideos():
    bestVideo = dict(sorted(Videos.items(), key=lambda item: float(item[0]), reverse=True)[:25])
    with open("videos/daily.json", "w") as f:
        json.dump(bestVideo, f, indent=3)

    dayTop = dict(list(bestVideo.items())[:5])
    with open("videos/weekly.json", "r") as f:
        existingWeekly = json.load(f)

    existingWeekly.update(dayTop)
    existingWeekly = dict(sorted(existingWeekly.items(), key=lambda item: float(item[0]), reverse=True))
    with open("videos/weekly.json", "w") as f:
        json.dump(existingWeekly, f, indent=3)

    if today.weekday() == 0:
        weekTop = dict(sorted(existingWeekly.items(), key=lambda item: float(item[0]), reverse=True)[:10])
        with open("videos/monthly.json", "r") as f:
            existingMonthly = json.load(f)

        existingMonthly.update(weekTop)
        existingMonthly = dict(sorted(existingMonthly.items(), key=lambda item: float(item[0]), reverse=True))
        with open("videos/monthly.json", "w") as f:
            json.dump(existingMonthly, f, indent=3)

    if today.day == 1:
        monthTop = dict(sorted(existingMonthly.items(), key=lambda item: float(item[0]), reverse=True)[:5])
        with open("videos/yearly.json", "r") as f:
            existingYearly = json.load(f)

        existingYearly.update(monthTop)
        existingYearly = dict(sorted(existingYearly.items(), key=lambda item: float(item[0]), reverse=True))
        with open("videos/yearly.json", "w") as f:
            json.dump(existingYearly, f, indent=3)


if __name__ == "__main__":
    global channelDF, service, yesterday, today, Videos, searchedChannels, curPageToken

    API_KEY = os.environ.get("YT_API_KEY")
    service = build("youtube", "v3", developerKey=API_KEY)
    channelDF = pd.read_csv("data/channels.csv")
    today = datetime.date.today()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    searchedChannels = []
    curPageToken = None
    channels = []
    Videos = {}

    if len(sys.argv) > 1 and sys.argv[1] == "search":
        search()
        updateInfoChannels()
        exit(0)

    updateInfoChannels() if yesterday.day % 9 == 0 else None
    fetchNewVideos()
    deleteOldVideos()
    storeVideos()
