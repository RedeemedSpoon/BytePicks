import os, datetime, isodate, json, sys, logging
from collections import defaultdict, OrderedDict
from googleapiclient.discovery import build
from langdetect import detect
from math import log
import pandas as pd

API_KEY = os.environ.get("YT_API_KEY")
MIN_DUR = isodate.parse_duration("PT1M5S")
LANGUAGE = ["EN", "FR", "ES", "RU", "HI"]
THRESHOLD = {"weekly": 7, "monthly": 30, "yearly": 365}
FIELDS = "items(snippet(title,publishedAt,channelTitle,channelId,thumbnails/medium/url), contentDetails(upload/videoId))"

RATING_MAPPING = {None: 1}
CAPTION_MAPPING = {None: 0.975}
DEFINITION_MAPPING = {"sd": 0.90, "fhd": 1.0125, "uhd": 1.025}
SUBSCRIBER_MAPPING = {10_000: 1.05, 100_000: 1.025, 500_000: 1, 1_000_000: 0.975, 5_000_000: 0.95}
DURATIONS_MAPPING = [
    (isodate.parse_duration("PT2M"), 0.950),
    (isodate.parse_duration("PT7M"), 0.975),
    (isodate.parse_duration("PT15M"), 1),
    (isodate.parse_duration("PT30M"), 1.025),
    (isodate.parse_duration("PT45M"), 1.050),
    (isodate.parse_duration("PT1H"), 1.075),
]


def search(cur_page_token=None, first_time=True):
    global quota_usage
    searched_channels = []

    while cur_page_token or first_time:
        request = service.search().list(
            q="Programming | Tech | Computer Science",
            type="channel",
            part="id",
            maxResults=50,
            order="relevance",
            relevanceLanguage="en",
            pageToken=cur_page_token,
        )

        response = request.execute()
        for item in response.get("items", []):
            try:
                searched_channels.append(item["id"]["channelId"])
            except:
                pass

        cur_page_token = response.get("nextPageToken")
        quota_usage -= 100
        first_time = False

    return searched_channels


def update_channels():
    global quota_usage
    channels = []

    for channel in channel_df["ChannelID"]:
        request = service.channels().list(part=["snippet", "statistics", "brandingSettings"], id=channel)
        response = request.execute()
        quota_usage -= 1

        try:
            response = response["items"][0]
            channel_info = {
                "ChannelID": response["id"],
                "ChannelName": response["snippet"]["title"],
                "ChannelIcon": response["snippet"]["thumbnails"]["medium"]["url"],
                "ChannelUrl": f'https://www.youtube.com/{response["snippet"].get("customUrl", "None")}',
                "ExistedSince": response["snippet"]["publishedAt"].split("T")[0],
                "SubscriberCount": int(response["statistics"]["subscriberCount"]),
                "VideoCount": int(response["statistics"]["videoCount"]),
                "ViewCount": int(response["statistics"]["viewCount"]),
                "Country": response["snippet"].get("country", "Unknown"),
                "Language": response["snippet"].get("defaultLanguage", "Unknown"),
            }

            if channel_info["SubscriberCount"] > 10_000:
                channels.append(channel_info)
        except:
            pass

    df = sort_and_filter(pd.DataFrame(channels))
    df.to_csv("data/channels.csv", index=False)


def sort_and_filter(df : pd.DataFrame) -> pd.DataFrame:
    df.dropna(inplace=True)
    df.drop_duplicates(subset=["ChannelID"], inplace=True)
    df.sort_values(by=["SubscriberCount"], ascending=False, inplace=True)
    return df


def sort(dictionary : dict) -> dict:
    results = sorted(dictionary.items(), key=lambda item: float(item[0]), reverse=True)
    return OrderedDict(results)


def mighty_algorithm(video: dict, video_duration: isodate.Duration, subscriber_count: int) -> float:
    normalized_views = log(video["ViewCount"] + 1)
    normalized_likes = log(video["LikeCount"] + 1)
    normalized_comments = log(video["CommentCount"] + 1)

    view_rate = normalized_views * 0.675
    like_rate = (normalized_likes / normalized_views) * 1.125
    comment_rate = (normalized_comments / normalized_views) * 1.375

    def_quality = DEFINITION_MAPPING.get(video["Definition"], 1)
    cap_quality = CAPTION_MAPPING.get(video["Caption"], 1)
    rat_quality = RATING_MAPPING.get(video["ContentRating"], 0.95)
    dur_quality = next((quality for duration, quality in DURATIONS_MAPPING if duration > video_duration), 0.9125)
    subscriber_balance = next((balance for channel, balance in SUBSCRIBER_MAPPING.items() if subscriber_count < channel), 0.9375)

    quality_multiplier = float(subscriber_balance * def_quality * cap_quality * rat_quality * dur_quality)
    rating = round((view_rate + like_rate + comment_rate) * quality_multiplier * 100, 3)

    return rating


def fetch_new_videos():
    global quota_usage
    for channel in channel_df["ChannelID"]:
        subscriber_count = channel_df[channel_df["ChannelID"] == channel]["SubscriberCount"].values[0]
        request = service.activities().list(
            part=["snippet", "id", "contentDetails"],
            channelId=channel,
            publishedAfter=yesterday.isoformat() + "T00:00:00Z",
            maxResults=5,
            fields=FIELDS,
        )

        response = request.execute()
        quota_usage -= 1
        for item in response["items"]:
            try:
                channel_name = item["snippet"]["channelTitle"]
                channel_id = item["snippet"]["channelId"]
                video_title = item["snippet"]["title"]
                video_id = item["contentDetails"]["upload"]["videoId"]
                published_at = item["snippet"]["publishedAt"][:16].replace("T", " ")
                thumbnail_url = item["snippet"]["thumbnails"]["medium"]["url"]

                request = service.videos().list(id=video_id, part=["statistics", "snippet", "contentDetails"])
                response = request.execute()
                response = response['items'][0]
                quota_usage -= 1

                view_count = int(response["statistics"]["viewCount"])
                like_count = int(response["statistics"]["likeCount"])
                comment_count = int(response["statistics"].get("commentCount", 0))
                category_id = int(response["snippet"]["categoryId"])
                content_rating = response["contentDetails"]["contentRating"]
                definition = response["contentDetails"]["definition"]
                duration = isodate.parse_duration(response["contentDetails"]["duration"])
                caption = response["contentDetails"]["caption"]
                language = str(response["snippet"].get("defaultLanguage", response["snippet"].get("defaultAudioLanguage", "NONE"))).upper()
                language = "HI" if "HI" in language else language[:2]
                language = "HI" if channel_df[channel_df["ChannelID"] == channel]["Country"].values[0] == "IN" else language
                language = detect(video_title).upper() if language in ["NONE", "ZXX"] else language

                if (video_id not in viewed_videos and view_count > 400 and MIN_DUR < duration and language in LANGUAGE):
                    full_video_details = {
                        "ChannelName": channel_name,
                        "ChannelId": channel_id,
                        "ChannelIcon": channel_df[channel_df["ChannelID"] == channel]["ChannelIcon"].values[0],
                        "ChannelUrl": channel_df[channel_df["ChannelID"] == channel]["ChannelUrl"].values[0],
                        "VideoUrl": f"https://www.youtube.com/watch?v={video_id}",
                        "VideoTitle": video_title,
                        "VideoId": video_id,
                        "PublishedDate": published_at,
                        "Thumbnail": thumbnail_url,
                        "Duration": str(duration).split(", ")[1] if ", " in str(duration) else str(duration),
                        "Definition": str(definition).upper(),
                        "Language": language,
                        "Caption": False if caption == "false" else True,
                        "ContentRating": False if not content_rating else True,
                        "ViewCount": int(view_count),
                        "LikeCount": int(like_count),
                        "CommentCount": int(comment_count),
                        "CategoryId": int(category_id),
                    }

                    video_rating = mighty_algorithm(full_video_details, duration, subscriber_count)
                    videos[language][video_rating] = full_video_details
                    viewed_videos.append(video_id)
            except:
                pass


def renew_video(video: dict) -> tuple[dict, isodate.duration]:
    global quota_usage
    try:
        request = service.videos().list(id=video["VideoId"], part=["statistics", "snippet", "contentDetails"])
        response = request.execute()
        response = response['items'][0]
        quota_usage -= 1

        full_video_details = {
            "ChannelName": video["ChannelName"],
            "ChannelId": video["ChannelId"],
            "ChannelIcon": video["ChannelIcon"],
            "ChannelUrl": video["ChannelUrl"],
            "VideoUrl": video["VideoUrl"],
            "VideoTitle": response["snippet"]["title"],
            "VideoId": video["VideoId"],
            "PublishedDate": video["PublishedDate"],
            "Thumbnail": response["snippet"]["thumbnails"]["medium"]["url"],
            "Duration": video["Duration"],
            "Definition": video["Definition"],
            "Language": video["Language"],
            "Caption":  False if response["contentDetails"]["caption"] == "false" else True,
            "ContentRating": False if not response["contentDetails"]["contentRating"] else True,
            "ViewCount": int(response["statistics"]["viewCount"]),
            "LikeCount": int(response["statistics"]["likeCount"]),
            "CommentCount": int(response["statistics"].get("commentCount", 0)),
            "CategoryId": int(video["CategoryId"]),
        }

        duration = isodate.parse_duration(response["contentDetails"]["duration"])
        return full_video_details, duration
    except:
        return video, None


def check_old_video(time: str, date: datetime.datetime) -> bool:
    timeline = datetime.timedelta(days=THRESHOLD[time])
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
    return (datetime.datetime.now() - date) < timeline


def update_videos(all_videos: dict, time: str) -> dict:
    result = {}

    for video in all_videos.items():
        if (check_old_video(time, video[1]["PublishedDate"]) and video[1]["VideoId"] not in viewed_videos):
            video, duration = renew_video(video[1])
            if video is None or duration is None:
                continue

            viewed_videos.append(video["VideoId"])
            subscriber_count = channel_df[channel_df["ChannelID"] == video["ChannelId"]]["SubscriberCount"].values[0]
            video_rating = mighty_algorithm(video, duration, subscriber_count)
            result[video_rating] = video

    return result


def sort_videos(all_videos: dict) -> dict:
    sorted_videos = {}
    monopolizing_channels = []
    all_videos = sort(all_videos) 

    for video in all_videos.items():
        if video[1]["ChannelId"] in monopolizing_channels:
            rating = float(video[0]) * 0.75
        else:
            monopolizing_channels.append(video[1]["ChannelId"])
            rating = video[0]

        sorted_videos[rating] = video[1]

    return sort(sorted_videos)


def store_videos():
    top_day, top_week, top_month = {}, {}, {}
    for lang, specific_videos in videos.items():
        for time in ["daily", "weekly", "monthly", "yearly"]:
            with open(f"data/{time}.json", "r") as f:
                data = json.load(f)

            if time == "daily":
                top_day = sort(specific_videos)
                data[lang] = OrderedDict(list(top_day.items()))

            elif time == "weekly":
                top_week = update_videos(data[lang], time)
                top_week.update(OrderedDict(list(top_day.items())[:35]))
                top_week = sort_videos(top_week)
                data[lang] = top_week

            elif time == "monthly":
                if yesterday.weekday() == 0:
                    top_month = update_videos(data[lang], time)
                    top_month.update(OrderedDict(list(top_week.items())[:125]))
                    top_month = sort_videos(top_month)
                    data[lang] = top_month

            elif time == "yearly":
                if yesterday.day == 1:
                    if yesterday.weekday() != 0:
                        with open("data/monthly.json", "r") as f:
                            new_data = json.load(f)
                            top_month = new_data[lang]

                    top_year = update_videos(data[lang], time)
                    top_year.update(OrderedDict(list(top_month.items())[:65]))
                    data[lang] = sort_videos(top_year)

            with open(f"data/{time}.json", "w") as f:
                json.dump(data, f, indent=4)


if __name__ == "__main__":
    logging.basicConfig(filename="app.log", level=logging.WARN, format="%(asctime)s - %(message)s")

    service = build("youtube", "v3", developerKey=API_KEY)
    channel_df = pd.read_csv("data/channels.csv")
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    videos = defaultdict(dict)
    quota_usage = 10_000
    viewed_videos = []

    if len(sys.argv) > 1 and sys.argv[1] == "search":
        new_channels = search()
        with open("data/channels.csv", "a") as f:
            f.writelines(f"{channel_id}\n" for channel_id in new_channels)

        logging.warning(f"Remaining quota after the search : {quota_usage}")
        exit(0)

    try:
        print("Fetching New Videos...")
        fetch_new_videos()
        print("Storing And Ranking Videos...")
        store_videos()
        print("Updating Channels...")
        update_channels()

    except Exception as error:
        logging.error(f"An error occurred : {error}")

    else:
        logging.warning(f"Remaining quota : {quota_usage}")
