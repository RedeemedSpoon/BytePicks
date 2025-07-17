from utils import get_videos, format_duration, format_view_count, send_email, session, User
import datetime

date = datetime.datetime.now() - datetime.timedelta(days=1)
for user in session.query(User).all():
    if (
        user.time == "daily"
        or (user.time == "weekly" and date.weekday() == 0)
        or (user.time == "monthly" and date.day == 1)
        or (user.time == "yearly" and (date.day == 1 and date.month == 1))
    ):
        video_list = []
        all_videos = get_videos(user.time, user.language)
        for rating, video in all_videos.items():
            video_title = video["VideoTitle"]
            video_link = video["VideoUrl"]
            video_thumbnail = video["Thumbnail"]
            channel_name = video["ChannelName"]
            channel_link = video["ChannelUrl"]
            video_duration = format_duration(video["Duration"])
            view_count = format_view_count(video["ViewCount"])

            video_template = f"""
            <div class='video' style="font-size: 16px; margin: 50px auto; max-width: 450px;">
              <img class='thumbnail' src='{video_thumbnail}' alt="Video Thumbnail" style="display: block; margin-left: auto; margin-right: auto; height: 200px; border-radius: 10px; border: 2px solid #1e1e1e; margin-bottom: 20px;">
              <ul style="list-style-type: none; max-width: 400px; text-align: left; padding: 0; margin: 0 auto;">
                <li style="margin-bottom: 8px;"><b>Video:</b><a href='{video_link}' target='_blank' style='color: #007bff; text-decoration: none; font-weight: bold;'> {video_title}</a></li>
                <li style="margin-bottom: 8px;"><b>Channel:</b><a href='{channel_link}' target='_blank' style='color: #007bff; text-decoration: none; font-weight: bold;'> {channel_name}</a></li>
                <li style="margin-bottom: 8px;"><b>Duration:</b> {video_duration}</li>
                <li style="margin-bottom: 8px;"><b>Views:</b> {view_count}</li>
              </ul>
            </div>
            """

            video_list.append(video_template)
        videos = "".join(video_list)
        
        body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
          <title>Your Byte Picks Newsletter</title>
        </head>
        <body style="margin: 0; padding: 0; width: 100%;">
          <div style="font-family: 'Verdana', sans-serif; padding: 30px; text-align: center;">
            <p style="font-size: 20px; margin-bottom: 15px;">Hello there!</p>
            <p style="font-size: 20px; margin-bottom: 15px;">Welcome to Byte Picks, your go-to source for the latest and greatest tech videos scattered across YouTube.</p>
            <p style="font-size: 20px; margin-bottom: 15px;">To change your preferences, please click <a href="https://bytepicks.com/newsletter/edit?user={user.email}&token={user.token}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: bold;">Here</a> and choose your preferred time and language, it's that simple!</p>
            <p style="font-size: 20px; margin-bottom: 15px;">If you wish to unsubscribe, click <a href="https://bytepicks.com/newsletter/delete?user={user.email}&token={user.token}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: bold;">Here</a>. (Proceed with caution!)</p>
            <p style="font-size: 20px; margin-bottom: 15px;">Without further ado, here's your {user.time} tech video in {user.language}. Enjoy!</p>
            <br>{videos}<br>
            <p style="font-size: 20px; margin-bottom: 15px;">Thanks for choosing Byte Picks!</p>
          </div>
        </body>
        </html>
        """

        subject = f"{str(user.time).title()} Tech Highlights: {datetime.datetime.now().date() - datetime.timedelta(days=1)}"
        send_email(body, subject, user.email, "newsletter@bytepicks.com")
