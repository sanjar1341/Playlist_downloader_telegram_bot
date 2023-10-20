from pytube import Playlist,YouTube
from urllib.request import urlretrieve
import os
import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup




bot=telebot.TeleBot('5983068854:AAFtCi_xiiTd8ky8U8ZMdSUul6V5FF9IyRA')

quality=['144p','240p','360p','480p','720p','1080p','mp3']


print('starting...')
@bot.message_handler(['start','help'])
def start(message):
    bot.send_message(message.chat.id,"Welcome playlist downloader")
    
    if not os.path.exists(str(message.from_user.id)):
        os.mkdir(str(message.from_user.id))




@bot.message_handler(func=lambda m:True)
def main(message):
    
    url=message.text
    
    try:
        yt=YouTube(url)
        send_video_info(message)
        return
    except Exception as e:
        if str(e).find('is age restricted')!=-1:
            bot.delete_message(message.chat.id,message.id)
            bot.send_message(message.chat.id,'this is age restricted, and can\'t be accessed without logging in.')
            
            return

    # try:
    pl=Playlist(url)
    send_playlist_info(message)
    # except Exception as e:
    #     bot.reply_to(message,str(e))

    
def markup(info)->InlineKeyboardMarkup:
    

    p144=InlineKeyboardButton('144p',callback_data='144p')
    p240=InlineKeyboardButton('240p',callback_data='240p')
    p360=InlineKeyboardButton('360p',callback_data='360p')
    p480=InlineKeyboardButton('480p',callback_data='480p')
    p720=InlineKeyboardButton('720p',callback_data='720p')
    p1080=InlineKeyboardButton('1080p',callback_data='1080p')
    pmp3=InlineKeyboardButton('mp3',callback_data='mp3')
    b1=InlineKeyboardButton('🖼',callback_data='image')
    b2=InlineKeyboardButton('👤',callback_data='owner')

    buttons=[[]]
    for x in info:
        if info[x]['filesize']!=0:
            buttons[0].append(InlineKeyboardButton(x,callback_data=x))
    quality_butttons=InlineKeyboardMarkup(buttons,row_width=3)
    return quality_butttons


def send_video_info(message):
    chat_id=message.chat.id
    mid=message.id
    # try:
    yt=YouTube(message.text)
    
    thumb=yt.thumbnail_url
    p,r=urlretrieve(thumb,f'{message.from_user.id}/{message.id}thumb.jpg')
    info=f"{message.text}\n📹  \t{yt.title}\n👤 #{yt.author.replace(' ','_')} "
    size_info=get_video_info(yt)
    for x in size_info:
        if size_info[x]['filesize']!=0:
            status='⚡️'
            if not size_info[x]['is_progressive']:
                status='🐢'
            fs=size_info[x]['filesize']
            info+=f"\n{status} {x}:\t{fs} mb"
    info+=f"\n\n@{bot.user.username}"
    bot.send_photo(message.chat.id,open(p,'rb'),info,reply_markup=markup(size_info))
    os.remove(p)
    bot.delete_message(chat_id,mid)

    # except Exception as e:
    #     bot.reply_to(message,str(e))


def send_playlist_info(message):
    chat_id=message.chat.id
    mid=message.id
    # try:
    pl=Playlist(message.text)
    yt=pl.videos[0]
    thumb=yt.thumbnail_url
    p,r=urlretrieve(thumb,f'{message.from_user.id}/{message.id}thumb.jpg')
    info=f"{message.text}\n👤#{pl.owner.replace(' ','_')}<a href='{pl.owner_url}'> → </a>\n🎞️\t{pl.title}\n🎥:\t{pl.length} videos"
    size_info=get_playlist_info(pl)
    for x in size_info:
        
        if size_info[x]['filesize']!=0:
            fs=size_info[x]['filesize']
    info+=f"\n\n@{bot.user.username}"
    bot.send_photo(message.chat.id,open(p,'rb'),info,reply_markup=markup(size_info),parse_mode='html')
    os.remove(p)
    bot.delete_message(chat_id,mid)
        
        # bot.send_message(message.chat.id,f"title:\t{pl.title}\nowner:\t{pl.owner}\ncount:\t{pl.length}")
            
    # except Exception as e:
    #     bot.reply_to(message,str(e))
def get_playlist_info(pl:Playlist):
    
    yt=pl.videos[len(pl)//2]

    return get_video_info(yt)

def get_video_info(yt:YouTube):
    
    info={'144p':{'is_progressive':0,'filesize':0.0,'audio_itag':0,'fps':0,'video_itag':0},
            '240p':{'is_progressive':0,'filesize':0.0,'audio_itag':0,'fps':0,'video_itag':0},
            '360p':{'is_progressive':0,'filesize':0.0,'audio_itag':0,'fps':0,'video_itag':0},
            '480p':{'is_progressive':0,'filesize':0.0,'audio_itag':0,'fps':0,'video_itag':0},
            '720p':{'is_progressive':0,'filesize':0.0,'audio_itag':0,'fps':0,'video_itag':0},
            '1080p':{'is_progressive':0,'filesize':0.0,'audio_itag':0,'fps':0,'video_itag':0},
            'mp3':{'is_progressive':0,'filesize':0.0,'audio_itag':0,'fps':0}}
    
    
        
    streams=yt.streams
    audio=streams.filter(mime_type='audio/mp4',abr='128kbps',only_audio=1).first()
    streams=streams.filter(file_extension='mp4',type='video')
    info['mp3']={'is_progressive':0,'filesize':audio.filesize_mb,'audio_itag':audio.itag,'fps':0}
    for i in streams:
        
        
        fps=i.fps

        res=i.resolution
        if fps>20 and i.is_progressive:
            info[res]={'is_progressive':1,'filesize':round(i.filesize_mb,1),'audio_itag':0,'fps':fps,'video_itag':i.itag}
        elif fps>20 and info[res]['filesize']==0:
            info[res]={'is_progressive':0,'filesize':round(i.filesize_mb+audio.filesize_mb,1),'audio_itag':audio.itag,'fps':fps,'video_itag':i.itag}


    return info

@bot.callback_query_handler(func=lambda call: True)
def splitter(call):
    res=str(call.data)
    chat_id=call.message.chat.id
    mid=call.message.id
    check=1
    url=str(call.message.caption.split('\n')[0])
    try:
    	yt=YouTube(url)
    except:
    	check=0
    
    
    print(f'url={url}')
    bot.delete_message(chat_id,mid)
    if check==0:
        pl=Playlist(url)
        for yt in pl.videos:
            
            info=get_video_info(yt)
            re=res
            if res!='mp3':
                while info[re]['filesize']==0:
                    
                    q=quality
                    q.remove(re)
                    q.sort()
                    re=q[0]

                if info[re]['is_progressive']:
                    stream=yt.streams.get_by_itag(info[re]['video_itag'])
                    dfname=stream.default_filename
                    pt=str(call.message.from_user.id)
                    stream.download(pt)
                    bot.send_video(chat_id,open(pt+'/'+dfname,'rb'),caption=f"📹{yt.title}\n👤{yt.author.replace(' ','_')}\n\n@{bot.user.username}:📹{re}")
                    
                else:
                    video=yt.streams.get_by_itag(info[re]['video_itag'])
                    audio=yt.streams.get_by_itag(info['mp3']['audio_itag'])
                    pt=str(call.message.from_user.id)
                    dfname=video.default_filename
                    video.download(pt,f'{mid}video.mp4')
                    audio.download(pt,f'{mid}audio.mp4')
                    os.system(f"ffmpeg -i {pt}/{mid}video.mp4 -i {pt}/{mid}audio.mp4 -c:v copy \"{pt}/{dfname}\"")
                    
                    bot.send_video(chat_id,open(pt+'/'+dfname,'rb'),caption=f"📹{yt.title}\n👤{yt.author.replace(' ','_')}\n\n@{bot.user.username}:📹{re}")
                
            else:
                stream=yt.streams.get_by_itag(info[res]['audio_itag'])
                dfname=stream.default_filename
                pt=str(call.message.from_user.id)
                stream.download(pt)
                bot.send_video(chat_id,open(pt+'/'+dfname,'rb'),caption=f"📹{yt.title}\n👤{yt.author.replace(' ','_')}\n\n@{bot.user.username}:📹{res}")
        

    elif res!='mp3':
        yt=YouTube(url)
        print(url)
        info=get_video_info(yt)
        print(info)
        if info[res]['is_progressive']:
            stream=yt.streams.get_by_itag(info[res]['video_itag'])
            dfname=stream.default_filename
            pt=str(call.message.from_user.id)
            stream.download(pt)
            bot.send_video(chat_id,open(pt+'/'+dfname,'rb'),caption=f"📹{yt.title}\n👤{yt.author.replace(' ','_')}\n\n@{bot.user.username}:📹{res}")
            
        else:
            video=yt.streams.get_by_itag(info[res]['video_itag'])
            audio=yt.streams.get_by_itag(info['mp3']['audio_itag'])
            pt=str(call.message.from_user.id)
            dfname=video.default_filename
            video.download(pt,f'{mid}video.mp4')
            audio.download(pt,f'{mid}audio.mp4')
            os.system(f"ffmpeg -i {pt}/{mid}video.mp4 -i {pt}/{mid}audio.mp4 -c:v copy \"{pt}/{dfname}\"")
            
            bot.send_video(chat_id,open(pt+'/'+dfname,'rb'),caption=f"📹{yt.title}\n👤{yt.author.replace(' ','_')}\n\n@{bot.user.username}:📹{res}")
    else:
        yt=YouTube(url)
        info=get_video_info(yt)
        stream=yt.streams.get_by_itag(info[res]['audio_itag'])
        dfname=stream.default_filename
        dfname=dfname.replace('.mp4','.mp3')
        pt=str(call.message.from_user.id)
        stream.download(pt,dfname)
        bot.send_audio(chat_id,open(pt+'/'+dfname,'rb'),caption=f"@{bot.user.username}")
        



print('working...')
bot.infinity_polling()





# # def send_video(message):
# #     pass

# # ffmeg -i video.mp4 -i audio.mp4 -c:v copy output.mp4
# url=input('url=')

# pl=Playlist(url)


# videos=pl.videos
# i=0
# # for i in pl:
# yt=YouTube(url)

# video=yt.streams.filter(res='144p',progressive=0,file_extension='mp4').first()
# video.download(filename='video.mp4')

# audio=yt.streams.filter(progressive=0,file_extension='mp4',only_audio=1).first()
# audio.download(filename='audio.mp4')
# fname=video.default_filename
# # vd=ffmpeg.input('video.mp4')
# # ad=ffmpeg.input('audio.mp4')
# # ffmpeg.output(vd,ad,filename=fname)
# # ffmpeg.concat(vd,ad,v=1,a=1).output(fname).run()
# subprocess.call('ffmpeg -i video.mp4 -i audio.mp4 -c:v copy output.mp4')
# os.system('ffmpeg -i video.mp4 -i audio.mp4 -c:v copy output.mp4')
# print('download complete')





