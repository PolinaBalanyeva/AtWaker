import discord
import pandas as pd
import numpy as np
import os
from discord.ext import tasks
from datetime import datetime ,timedelta
# from dotenv import load_dotenv
import time
import asyncio

# .envファイルの内容を読み込みます
# load_dotenv()
# TOKEN = os.environ['TOKEN']
TOKEN='ODA3ODY5MTcxNDkxNjY4MDIw.YB-Qyw.ug72aycHBOcB4Zw9Xx0hWWdxWYM'

intents = discord.Intents.all()
# 接続に必要なオブジェクトを生成
client = discord.Client(intents=intents)
# channelid=os.environ['CHANNEL']
# serverid=os.environ['SERVER']
# thisbotid=os.environ['THISBOT']
channelid=805672534523379733
serverid=805058528485965894
thisbotid=807869171491668020
print(client.get_channel(channelid))
emj=<:ohayo:805676181328232448>
z=86400*((365.25*50)//1+5/8)//1
hs=6
ms=0
interv=15
clen=360
v=None
contesting=False
rk=1

def renew_db(serverid):
  guild=client.get_guild(serverid)
  db=pd.read_csv('AtWaker_data_'+str(serverid)+'.csv',header=0,index_col=0)
  for xx in {str(aa.id) for aa in guild.members}-set(db.index.astype(str)):
    db[xx]=[np.nan for _ in range(len(db))]
  db.to_csv('AtWaker_data_'+str(serverid)+'.csv')
  dbr=pd.read_csv('AtWaker_rate_'+str(serverid)+'.csv',header=0,index_col=0)
  for xx in {str(aa.id) for aa in guild.members}-set(dbr.index.astype(str)):
    dbr[xx]=[np.nan for _ in range(len(dbr))]
  dbr.to_csv('AtWaker_rate_'+str(serverid)+'.csv')
  
def make_db(serverid):
  guild=client.get_guild(serverid)
  db=pd.DataFrame(columns=[str(xx.id) for xx in guild.members],index=[])
  db.to_csv('AtWaker_data_'+str(serverid)+'.csv')
  dbr=pd.DataFrame(columns=[str(xx.id) for xx in guild.members],index=[])
  dbr.to_csv('AtWaker_rate_'+str(serverid)+'.csv')
  
# async def repeat1(start,msg):
#   while time.time()-start<60*(clen+1):
#     print('rep1s')
#     reaction, user = await client.wait_for('reaction_add', check=lambda r, u: 
#                                            (r.message.id==msg.id) and ((r.emoji==emj) or ((r.emoji==emj2) and (u.id==807869171491668020))))
#     print('rep1')
#     if r.emoji==emj:
#       v=record_rank(user,rk,v)
#       rk+=1
#     elif r.emoji==emj2:
#       break


# async def repeat2(msg):
#   await asyncio.sleep(60*clen)
#   print('rep2')
#   await msg.add_reaction(emoji=emj2)

  
async def contest():
  channel = client.get_channel(channelid)
  global v
  db=pd.read_csv('AtWaker_data_'+str(serverid)+'.csv',header=0,index_col=0)
  v=pd.DataFrame([[np.nan,np.nan] for _ in range(len(db.columns))],columns=['rank','time'],index=db.columns)
  dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
  global rk
  rk=1
  start=time.time()
  msg=await channel.send('おはようございます！ Good morning!\n'+dt
                                            +'のAtWaker Contest開始です。\n起きた人は'
                                            +emj+'でリアクションしてね。')
  await msg.add_reaction(emoji=emj)
  global contesting
  contesting=True
  print('Contest started')
  
  
async def contest_end():
  print('Contest ended')
  db=pd.read_csv('AtWaker_data_'+str(serverid)+'.csv',header=0,index_col=0)
  channel = client.get_channel(channelid)
  dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
  global contesting
  contesting=False
  if rk>1:
      await channel.send(dt+'のAtWaker Contestは終了しました。\n参加者は'
                                    +str(rk-1)+'人でした。')
      db.loc[dt]=[np.nan for _ in range(len(db.columns))]
      db=perf_calc(db,v)
      rate_calc(db,dt)
      vs=v.dropna().sort_values(by='rank')
      for j in range(1,min(11,rk)):
        jthuser=client.get_guild(serverid).get_member(int(vs.index[j-1]))
        await channel.send(str(j)+'位:'+jthuser.display_name+' '
                                        +vs.iloc[j-1].loc['time']+' パフォーマンス:'
                                        +str(int(db.loc[dt,vs.index[j-1]])))
  else:
    await channel.send('ほんでーかれこれまぁ'+str(clen)+'分くらい、えー待ったんですけども参加者は誰一人来ませんでした。')
  db.to_csv('AtWaker_data_'+str(serverid)+'.csv')
  return
  
def record_rank(user,rk,v):
  vc=v.copy()
  if vc.loc[str(user.id),'rank']!=vc.loc[str(user.id),'rank']:
    vc.loc[str(user.id),'time']=(datetime.now()+timedelta(hours=9)).strftime('%H:%M:%S')
    vc.loc[str(user.id),'rank']=rk
  return vc

def perf_calc(db,v):
  dbc=db.copy()
  vc=v['rank'].dropna().sort_values()
  print(vc)
  aperf=pd.Series([np.nan]*len(vc),index=vc.index)
  for user in vc.index:
    past=dbc[user].dropna().values[::-1]
    if(len(past)==0):
      aperf[user]=1200
    else:
      aperfnom=0
      aperfden=0
      for i in range(len(past)):
        aperfnom+=past[i]*(0.9**(i+1))
        aperfden+=0.9**(i+1)
      aperf[user]=aperfnom/aperfden
  xx=0
  s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
  print(list(1/(1+6.0**((xx-aperf.values)/400))))
  for j in range(len(vc))[::-1]:
    print(s)
    while s>=j+0.5:
      xx+=1
      s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
    dbc.iloc[-1].loc[vc.index[j]]=int(xx)
  if len(dbc)==1:
    dbc.iloc[-1]=((dbc.iloc[-1]-1200)*3)//2+1200
  return dbc

def rate_calc(db,dt):
  dbr=pd.read_csv('AtWaker_rate_'+str(serverid)+'.csv',header=0,index_col=0)
  if len(dbr)>0:
    vlast=dbr.iloc[-1]
    dbr.loc[dt]=vlast
  else:
    dbr.loc[dt]=[0]*len(dbr.columns)
  for xx in db.columns:
    if db.loc[dt,xx]==db.loc[dt,xx]:
      vperf=db[xx].dropna().values[::-1]
      ratenom=0
      rateden=0
      for i in range(len(vperf)):
        ratenom+=2.0**(vperf[i]/800)*(0.9**(i+1))
        rateden+=0.9**(i+1)
      dbr.loc[dt,xx]=int(800*np.log(ratenom/rateden)/np.log(2))
  dbr.to_csv('AtWaker_rate_'+str(serverid)+'.csv')
  return






# 起動時に動作する処理
@client.event
async def on_ready():
  # 起動したらターミナルにログイン通知が表示される
  print('ログインしました。')
  return

# リアクション受信時に動作する処理
@client.event
async def on_reaction_add(reaction,user):
  global v
  global rk
  if contesting and (user.id!=807869171491668020):
    dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
    bool1=(str(reaction.emoji)==str(emj))
    bool2=(reaction.message.author.id==807869171491668020) 
    bool3=(reaction.message.content=='おはようございます！ Good morning!\n'+dt+'のAtWaker Contest開始です。\n起きた人は'+emj+'でリアクションしてね。')
    print(bool1,bool2,bool3)
    if bool1 and bool2 and bool3:
      print(rk,user.display_name)
      v=record_rank(user,rk,v)
      rk+=1
  return
  

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
  # global serverid
  # global channelid
  # if not contesting:
    # serverid=message.channel.guild.id
    # channelid=message.channel.id
  channel = client.get_channel(channelid)
  if message.content.startswith("!atw ") and (message.author.id!=thisbotid):
    if message.content.startswith("!atw start "):
      global emj
      emj=message.content[11:]
      print(emj)
      if os.path.exists('AtWaker_data_'+str(serverid)+'.csv') and os.path.exists('AtWaker_rate_'+str(serverid)+'.csv'):
        renew_db(serverid)
      else:
        make_db(serverid)
      await channel.send('起動しました。')
    elif message.content.startswith("!atw rating "):
      if os.path.exists('AtWaker_data_'+str(serverid)+'.csv') and os.path.exists('AtWaker_rate_'+str(serverid)+'.csv'):
        dbr=pd.read_csv('AtWaker_rate_'+str(serverid)+'.csv',header=0,index_col=0)
        dbd=pd.read_csv('AtWaker_data_'+str(serverid)+'.csv',header=0,index_col=0)
        num=0
        print(len(channel.guild.members))
        for xx in channel.guild.members:
          if message.content[12:] in xx.display_name:
            zant=""
            num+=1
            if len(dbr)>0:
              rate=int(dbr.iloc[-1].loc[str(xx.id)])
              if(len(dbd.loc[:,str(xx.id)].dropna())<14):
                zant="(暫定)"
            else:
              rate=0
            await channel.send(xx.display_name+':'+str(rate)+zant)
        if num==0:
          await channel.send('ユーザーが見つかりません。')
      else:
        await channel.send('初めに!atw start (絵文字)を実行してください。')
    elif message.content=="!atw help":
      f = open('help.txt', 'r')
      helpstr = f.read()
      f.close()
      await channel.send(helpstr)
    else:
      await channel.send('そのコマンドは存在しません。')
  return 
    
@client.event
async def on_member_join(member):
  if not (serverid==None) and not (channelid==None):
    renew_db(serverid)
  return

@tasks.loop(seconds=60*interv)
async def loop():
  # 現在の時刻
  now=(time.time()+3600*9)%86400
  print(now)
  print((3600*hs+60*ms<=now<3600*hs+60*(ms+interv)) ,not (serverid==None) ,not (channelid==None))
  if (3600*hs+60*ms<=now<3600*hs+60*(ms+interv)) and (not (serverid==None) and not (channelid==None)):
    await contest()
  elif(3600*hs+60*(ms+clen)<=now<3600*hs+60*(ms+interv+clen)) and contesting:
    await contest_end()
  return
#ループ処理実行
loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)  


