from common import *

with open('token.json', 'r') as token:
    creds_data = json.load(token)
    date = datetime.now()
    update_token(creds_data)

for user in session.query(User).all():
    if (
        user.time == "daily" or
        (user.time == "weekly" and date.weekday() == 0) or
        (user.time == "monthly" and date.day == 1) or
        (user.time == "yearly" and (date.day == 1 and date.month == 1))
    ):
        video_list = []
        all_videos = getVideos(user.time, user.language)
        for rating, video in all_videos.items():
            video_title = video["VideoTitle"]
            video_link = video["VideoUrl"]
            video_thumbnail = video['Thumbnail']
            channel_name = video["ChannelName"]
            channel_link = video["ChannelUrl"]
            video_duration = format_duration(video["Duration"])
            view_count = format_view_count(video["ViewCount"])

            video_template = f"""
            <div class='video'>
              <img class='thumbnail' src='{video_thumbnail}'>
              <div class='details'>
                <p><b>Video :</b><a href='{video_link}'> {video_title}</a><p>
                <p><b>Channel :</b><a href='{channel_link}'> {channel_name}</a><p>
                <p><b>Duration :</b> {video_duration}</p>
                <p><b>Views :</b> {view_count}</p>
              </div>
            </div>
            """

            video_list.append(video_template)
        videos = ''.join(video_list)
        body = f"""
        <html>
        <head>
          <style>
            body {{
              font-family: 'Verdana', sans-serif;
              margin: 30px;
            }}
            center > p {{
              font-size: 20px;
              margin-bottom: 15px;
            }}
            .video {{
              font-size: 16px;
              margin: 50px;
            }}
            .details {{
              diplay: flex;
              flex-direction: column;
              max-width: 450px;
            }}
            .thumbnail {{
              height : 200px;
              border-radius: 10px;
              border: 2px solid #1e1e1e;
              margin-bottom: 20px;
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
          <center>
            <p>Hello there!</p>
            <p>Welcome to Byte Picks, your go-to source for the latest and greatest tech videos scattered across YouTube.</p>
            <p>To change your preferences, please click <a href="https://bytepicks.com/edit?user={user.email}&token={user.token}">Here</a> and choose your preferred time and language, it's that simple!</p>
            <p>If you wish to unsubscribe, click <a href="https://bytepicks.com/drop?user={user.email}&token={user.token}">Here</a>. (Proceed with caution!)</p>
            <p>Without further ado, here's your {user.time} tech video in {user.language}. Enjoy!</p>
            <br>{videos}<br>
            <p>Thanks for choosing Byte Picks!</p>
          </center>
        </body>
        </html>
        """

        subject = f"{str(user.time).title()} Tech Highlights: {datetime.now().date()}"
        send_email(body, subject, user.email, "newsletter@bytepicks.com")
