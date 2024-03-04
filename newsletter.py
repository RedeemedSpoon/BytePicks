from common import *

updateToken()
date = datetime.now()
for user in session.query(User).all():
    if (
        user.time == "daily" or
        (user.time == "weekly" and date.weekday() == 0) or
        (user.time == "monthly" and date.day == 1) or
        (user.time == "yearly" and (date.day == 1 and date.month == 1))
    ):
        videoList = []
        allVideos = getVideos(user.time, user.language)

        for videoId, video in allVideos.items():
            videoTitle = video["VideoTitle"]
            videoLink = video["VideoUrl"]
            channelName = video["ChannelName"]
            channelLink = video["ChannelUrl"]
            duration = formatDuration(video["Duration"])
            viewCount = formatViewCount(video["ViewCount"])
            videoInfo = f"<div class='video'><img src='{video['Thumbnail']}'><br><strong>Video :</strong> <a href='{videoLink}'>{videoTitle}</a><br><strong>Channel :</strong> <a href='{channelLink}'>{channelName}</a><br><strong>Duration :</strong> {duration}<br><strong>Views :</strong> {viewCount}</div>"
            videoList.append(videoInfo)

        videos = "<br><br>".join(videoList)
        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Verdana', sans-serif;
                    margin: 20px;
                    padding: 20px;
                }}

                p {{
                    font-size: 18px;
                    margin-bottom: 15px;
                }}

                img {{
                    border-radius: 10px;
                    border: 2px solid #1e1e1e;
                    box-shadow: 2px 2px 5px #0a0a0a;
                    margin-bottom: 20px;
                }}

                .video {{
                    margin: 20px;
                    font-size: 15px;
                }}

                a {{
                    color: #007bff;
                    text-decoration: none;
                    font-weight: bold;
                }}

                a:hover {{
                    text-decoration: underline;
                    color: #0056b3;
                }}

            </style>
        </head>
        <body>
            <p>Hello there!</p>

            <p>Welcome to Byte Picks, your go-to source for the latest and greatest tech videos scattered across YouTube.</p>

            <p>To change your preferences, please click <a href="https://bytepicks.com/Edit?user={user.email}&token={user.token}">Here</a> and choose your preferred time and language, it's that simple!</p>

            <p>If you wish to unsubscribe, click <a href="https://bytepicks.com/Drop?user={user.email}&token={user.token}">Here</a>. (Proceed with caution!)</p>

            <p>Without further ado, here's your {user.time} tech video in {user.language}. Enjoy!</p><br>

            {videos}

            <br><p>Thanks for choosing Byte Picks!</p>
        </body>
        </html>
        """

        recipientEmail = user.email
        subject = f"{str(user.time).title()} Tech Highlights: {datetime.now().date()}"
        sendEmail(body, subject, recipientEmail, "newsletter@bytepicks.com")
