from common import *

initializeEmail()
users = session.query(User).all()

for user in users:
    videoList = []
    allVideos = getVideos(user.time, user.language)

    for vide in allVideos:
        videoTitle = allVideos["VideoTitle"]
        videoLink = allVideos["VideoUrl"]
        channelName = allVideos["ChannelName"]
        channelLink = allVideos["ChannelUrl"]
        duration = formatDuration(allVideos["Duration"])
        viewCount = formatViewCount(allVideos["ViewCount"])
        videoInfo = f"Video : <a href='{videoLink}'>{videoTitle}</a><br>Channel : <a href='{channelLink}'>{channelName}</a><br>Duration : {duration}<br>Views : {viewCount}"
        videoList.append(videoInfo)

    videos = "<br><br>".join(videoList)

    body = f"""
        Hello, There!
        
        This is your best place to receive the best videos scattered across YouTube related to technology. 
        
        To update your preferences, please visit our <a href="https://bytepicks.com/Newsletter">Newsletter</a> page, input your email and select your preferred time and language. Simple As it is.
        
        To unsubscribe from our service, just click here : <a href="https://bytepicks.com/drop/user?token={user.token}">Dangerous!</a>
        
        Without further ado, here your {user.time} Video in {user.language}. Enjoy! 
        
        {videos}
        
        Thanks,
        Byte Picks
        
        """

    recipientEmail = user.email
    subject = f"Here's the best tech {user.time} videos of YouTube"
    email = f"Subject: {subject}\n\n{body}"

    server.sendmail(senderEmail, recipientEmail, email)

server.close()
