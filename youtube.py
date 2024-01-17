from googleapiclient.discovery import build
import os, datetime, isodate, logging, json
from itertools import islice
from math import sqrt, log
import pandas as pd

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


def updateChannel(channelID: str):
    global channelDF
    request = service.channels().list(part=["snippet", "statistics", "brandingSettings"], id=channelID)
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
        "Language": channelDF[channelDF["ChannelID"] == channelID]["Language"].values[0],
    }

    df = pd.DataFrame([channelInfo])
    channelDF = channelDF[channelDF["ChannelID"] != response["items"][0]["id"]]
    channelDF = pd.concat([channelDF, df], ignore_index=True)
    channelDF.to_csv("Channels.csv", index=False)


def fetchNewVideos(channelID: str, subcriberCount: int):
    global allVideos
    fields = (
        "items(snippet(title,publishedAt,channelTitle,channelId,thumbnails/medium/url),"
        "contentDetails(upload(videoId)))"
    )

    request = service.activities().list(
        part=["snippet", "id", "contentDetails"],
        channelId=channelID,
        publishedAfter=yesterday.isoformat() + "T00:00:00Z",
        maxResults=5,
        fields=fields,
    )

    response = request.execute()
    for item in response["items"]:
        try:
            channelName = item["snippet"]["channelTitle"]
            channelId = item["snippet"]["channelId"]
            videoTitle = item["snippet"]["title"]
            publishedAt = item["snippet"]["publishedAt"][:16].replace("T", " ")
            videoId = item["contentDetails"]["upload"]["videoId"]
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
                "Duration": str(duration),
                "Definition": definition,
                "language": language,
                "Caption": None if caption == "false" else caption,
                "ContentRating": None if not contentRating else contentRating,
                "ViewCount": int(viewCount),
                "LikeCount": int(likeCount),
                "CommentCount": int(commentCount),
                "CategoryId": int(categoryId),
            }
            if int(categoryId) in [27, 28] or viewCount > 1000:
                videoRating = allMightyAlgorithm(fullVideoDetails, duration, subcriberCount)
                allVideos[videoRating] = fullVideoDetails

        except Exception as error:
            logging.error(error)


def allMightyAlgorithm(video: json, vidDuration: isodate, SubscriberCount: str) -> int:
    global channelDF

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


def rankVideos():
    rankedVideos = dict(sorted(allVideos.items(), key=lambda item: item[0], reverse=True))
    with open("videos/daily.json", "w") as f:
        json.dump(dict(islice(rankedVideos.items(), 15)), f, indent=4)


def initialize():
    for channel in channelDF["ChannelID"]:
        subcriberCount = channelDF[channelDF["ChannelID"] == channel]["SubscriberCount"].values[0]
        fetchNewVideos(channel, subcriberCount)
        if yesterday.day % 7 == 0:
            updateChannel(channel)


if __name__ == "__main__":
    API_KEY = os.environ.get("YT_API_KEY")
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    service = build("youtube", "v3", developerKey=API_KEY)
    channelDF = pd.read_csv("Channels.csv")
    allVideos = {}
    initialize()
    rankVideos()
