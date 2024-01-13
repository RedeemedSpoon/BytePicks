from googleapiclient.discovery import build
import os, datetime, isodate, logging, json
import pandas as pd


def updateChannel(channelID):
    global channelDF
    request = service.channels().list(
        part=["snippet", "statistics", "brandingSettings"], id=channelID
    )

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
        "Language": response["items"][0]["brandingSettings"]["channel"].get(
            "defaultLanguage",
            channelDF[channelDF["ChannelID"] == channelID]["Language"].values[0],
        ),
    }

    df = pd.DataFrame([channelInfo])
    channelDF = channelDF[channelDF["ChannelID"] != response["items"][0]["id"]]
    channelDF = pd.concat([channelDF, df], ignore_index=True)
    channelDF.to_csv("Channels.csv", index=False)


def fetchNewVideos(channelID, index):
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

            request = service.videos().list(
                id=videoId, part=["statistics", "snippet", "contentDetails"]
            )

            response = request.execute()
            viewCount = response["items"][0]["statistics"]["viewCount"]
            likeCount = response["items"][0]["statistics"]["likeCount"]
            commentCount = response["items"][0]["statistics"]["commentCount"]
            categoryId = response["items"][0]["snippet"]["categoryId"]
            videoLabel = response["items"][0]["contentDetails"]["contentRating"]
            definition = response["items"][0]["contentDetails"]["definition"]
            duration = isodate.parse_duration(
                response["items"][0]["contentDetails"]["duration"]
            )

            fullVideoDetails = {
                (index + 1): {
                    "ChannelName": channelName,
                    "ChannelId": channelId,
                    "VideoTitle": videoTitle,
                    "VideoId": videoId,
                    "PublishedDate": publishedAt,
                    "Thumbnail": thumbnailUrl,
                    "Definition": definition,
                    "Duration": str(duration),
                    "VideoLabel": None if not videoLabel else videoLabel,
                    "ViewCount": int(viewCount),
                    "LikeCount": int(likeCount),
                    "CommentCount": int(commentCount),
                    "CategoryId": int(categoryId),
                }
            }
            allVideos.append(fullVideoDetails)

        except Exception as error:
            logging.error(error)


if __name__ == "__main__":
    API_KEY = os.environ.get("YT_API_KEY")
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    service = build("youtube", "v3", developerKey=API_KEY)
    channelDF = pd.read_csv("Channels.csv")
    allVideos = []

    for index, channel in enumerate(channelDF["ChannelID"]):
        fetchNewVideos(channel, index)
        if yesterday.day % 7 == 5:
            updateChannel(channel)

    with open("AllVideos.json", "w") as f:
        json.dump(allVideos, f)
