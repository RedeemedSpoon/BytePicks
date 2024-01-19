from googleapiclient.discovery import build
import os, datetime, isodate, json
from math import sqrt, log
import pandas as pd

with open("videos/daily.json", "r") as file:
    AllVideos = json.load(file)

FIELDS = (
    "items(snippet(title,publishedAt,channelTitle,channelId,thumbnails/medium/url), contentDetails(upload/videoId))"
)
CAPTION_MAPPING = {None: 0.95}
RATING_MAPPING = {None: 1}
DEFINITION_MAPPING = {"sd": 0.75, "fhd": 1.05, "uhd": 1.10}
SUBSCRIBER_MAPPING = {10_000: 1.10, 100_000: 1.05, 500_000: 1, 1_000_000: 0.95, 5_000_000: 0.90}
DURATIONS_MAPPING = [
    (isodate.parse_duration("PT2M"), 0.1),
    (isodate.parse_duration("PT7M"), 0.85),
    (isodate.parse_duration("PT15M"), 0.90),
    (isodate.parse_duration("PT30M"), 1),
    (isodate.parse_duration("PT45M"), 1.10),
    (isodate.parse_duration("PT1H"), 1.05),
]


def updateInfoChannels():
    for channel in channelDF["ChannelID"]:
        request = service.channels().list(part=["snippet", "statistics", "brandingSettings"], id=channel)
        response = request.execute()

        channelInfo = {
            "ChannelID": response["items"][0]["id"],
            "ChannelName": response["items"][0]["snippet"]["title"],
            "ChannelIcon": response["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
            "ChannelUrl": f'https://www.youtube.com/{response["items"][0]["snippet"]["customUrl"]}',
            "ExistedSince": response["items"][0]["snippet"]["publishedAt"].split("T")[0],
            "SubscriberCount": int(response["items"][0]["statistics"]["subscriberCount"]),
            "VideoCount": int(response["items"][0]["statistics"]["videoCount"]),
            "ViewCount": int(response["items"][0]["statistics"]["viewCount"]),
            "Country": response["items"][0]["snippet"].get("country", "Unknown"),
            "Language": channelDF[channelDF["ChannelID"] == channel]["Language"].values[0],
        }

        channels.append(channelInfo)

    df = pd.DataFrame(channels)
    df.to_csv("data/channels.csv", index=False)


def allMightyAlgorithm(video: json, vidDuration: isodate, SubscriberCount: str) -> int:
    NRLLikeCount = log(video["LikeCount"] + 1)
    NRLCommentCount = log(video["CommentCount"] + 1)
    NRLViewCount = log(video["ViewCount"] + 1)

    viewRate = sqrt(NRLViewCount) / 4
    likeRate = NRLLikeCount / NRLViewCount
    commentRate = NRLCommentCount / NRLViewCount * 1.5

    defQuality = DEFINITION_MAPPING.get(video["Definition"], 1)
    capQuality = CAPTION_MAPPING.get(video["Caption"], 1)
    ratQuality = RATING_MAPPING.get(video["ContentRating"], 0.85)
    durQuality = next((quality for duration, quality in DURATIONS_MAPPING if vidDuration < duration), 0.85)
    subBalance = next((balance for channel, balance in SUBSCRIBER_MAPPING.items() if SubscriberCount < channel), 0.90)

    qualityMultiplier = subBalance * defQuality * capQuality * ratQuality * durQuality
    rating = round((viewRate + likeRate + commentRate) * qualityMultiplier * 100, 2)
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
                videoId = item["contentDetails"]["upload"]["videoId"]

            except KeyError:
                pass

            else:
                channelName = item["snippet"]["channelTitle"]
                channelId = item["snippet"]["channelId"]
                videoTitle = item["snippet"]["title"]
                publishedAt = item["snippet"]["publishedAt"][:16].replace("T", " ")
                thumbnailUrl = item["snippet"]["thumbnails"]["medium"]["url"]

                request = service.videos().list(id=videoId, part=["statistics", "snippet", "contentDetails"])
                response = request.execute()

                viewCount = response["items"][0]["statistics"]["viewCount"]
                likeCount = response["items"][0]["statistics"]["likeCount"]
                commentCount = response["items"][0]["statistics"]["commentCount"]
                categoryId = response["items"][0]["snippet"]["categoryId"]
                contentRating = response["items"][0]["contentDetails"]["contentRating"]
                definition = response["items"][0]["contentDetails"]["definition"]
                duration = isodate.parse_duration(response["items"][0]["contentDetails"]["duration"])
                caption = response["items"][0]["contentDetails"]["caption"]
                language = response["items"][0]["snippet"].get(
                    "defaultLanguage", response["items"][0]["snippet"].get("defaultAudioLanguage")
                )

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
                    "Definition": definition,
                    "language": language,
                    "Caption": None if caption == "false" else caption,
                    "ContentRating": None if not contentRating else contentRating,
                    "ViewCount": int(viewCount),
                    "LikeCount": int(likeCount),
                    "CommentCount": int(commentCount),
                    "CategoryId": int(categoryId),
                }

                if int(categoryId) in [27, 28] and int(viewCount) > 1000:
                    videoRating = allMightyAlgorithm(fullVideoDetails, duration, subcriberCount)
                    Videos[videoRating] = fullVideoDetails


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
    dailyTop = dict(sorted(Videos.items(), key=lambda item: float(item[0]), reverse=True)[:20])
    with open("videos/daily.json", "w") as f:
        json.dump(dailyTop, f, indent=3)

    weeklyTop = dict(list(dailyTop.items())[:5])
    with open("videos/weekly.json", "r") as f:
        existingWeekly = json.load(f)

    existingWeekly.update(weeklyTop)
    existingWeekly = dict(sorted(existingWeekly.items(), key=lambda item: float(item[0]), reverse=True)[:5])
    with open("videos/weekly.json", "w") as f:
        json.dump(existingWeekly, f, indent=3)

    if today.weekday() == 0:
        monthlyTop = dict(sorted(existingWeekly.items(), key=lambda item: float(item[0]), reverse=True)[:10])
        with open("videos/monthly.json", "r") as f:
            existingMonthly = json.load(f)

        existingMonthly.update(monthlyTop)
        existingMonthly = dict(sorted(existingMonthly.items(), key=lambda item: float(item[0]), reverse=True)[:10])
        with open("videos/monthly.json", "w") as f:
            json.dump(existingMonthly, f, indent=3)

    if today.day == 1:
        yearlyTop = dict(sorted(existingMonthly.items(), key=lambda item: float(item[0]), reverse=True)[:5])
        with open("videos/yearly.json", "r") as f:
            existingYearly = json.load(f)

        existingYearly.update(yearlyTop)
        existingYearly = dict(sorted(existingYearly.items(), key=lambda item: float(item[0]), reverse=True)[:5])
        with open("videos/yearly.json", "w") as f:
            json.dump(existingYearly, f, indent=3)


if __name__ == "__main__":
    global channelDF, service, yesterday, today, Videos

    API_KEY = os.environ.get("YT_API_KEY")
    today = datetime.date.today()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    service = build("youtube", "v3", developerKey=API_KEY)
    channelDF = pd.read_csv("data/channels.csv")
    channels = []
    Videos = {}

    updateInfoChannels() if yesterday.day % 9 == 0 else None
    fetchNewVideos()
    deleteOldVideos()
    storeVideos()
