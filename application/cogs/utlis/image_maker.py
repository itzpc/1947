import discord
import asyncio
import requests
from io import BytesIO
import logging
import os
import coc 
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime
from application.constants.bot_const import BotImage,BotFont
from application.constants.emoji import Emoji

class ImageMaker():
    def __init__(self,font_loc,bg_image_loc):
        self.directory=os.getcwd()
        self.font =os.path.join(self.directory+ font_loc)
        self.background_image=os.path.join(self.directory+ bg_image_loc)

    async def draw_image(self,image,url,x,y,resize_x=100,resize_y=100):
        response = requests.get(url)
        url_image = Image.open(BytesIO(response.content))
        url_image = url_image.resize((resize_x, resize_y))
        image.paste(url_image,(x,y))


    async def draw_text(self,draw,font=None,font_size=20,message=None,color='rgb(127,255,0)',x=10,y=10,relative_position=None):
        if font is None:
            font = self.font
        if message is None:
            message = ""
        message=str(message[:15])
        len_msg = len(message)
        w, h = draw.textsize(message)
        font_ = ImageFont.truetype(font,size =font_size)
        if relative_position:
            if relative_position=="Left":
                draw.text((x-(w*2),y), message, fill=color, font=font_)
            else:
                draw.text((x+(w*2),y), message, fill=color, font=font_)
        else:
            draw.text((x,y), message, fill=color, font=font_)

    async def make_stats_image(self,war):
        logging.info("INFO: image_maker.py - make_stats_image() started")
        out=os.path.join(self.directory+ "/images/temp/temp_war_status.png")
        bg_image = Image.open(self.background_image)
        draw = ImageDraw.Draw(bg_image)
        message = war.clan.name
        color = 'rgb(127,255,0)' 
        await self.draw_text(draw,self.font,55,message,color,380,45,"Left")
        message = war.clan.tag
        await self.draw_text(draw,self.font,20,message,color,500,120,"Left")
        message=f"{war.clan.stars}/{war.clan.max_stars}"
        await self.draw_text(draw,self.font,40,message,color,80,260)
        message=f"{war.clan.attacks_used}"
        await self.draw_text(draw,self.font,40,message,color,80,360)
        message=f"{war.clan.destruction}"
        await self.draw_text(draw,self.font,40,message,color,80,470)

        message = war.opponent.name
        color = 'rgb(255,69,0)' 
        await self.draw_text(draw,self.font,55,message,color,600,45)
        message = war.opponent.tag
        await self.draw_text(draw,self.font,20,message,color,600,120)
        message=f"{war.opponent.stars}/{war.clan.max_stars}"
        await self.draw_text(draw,self.font,40,message,color,305,260)
        message=f"{war.opponent.attacks_used}"
        await self.draw_text(draw,self.font,40,message,color,305,360)
        message=f"{war.opponent.destruction}"
        await self.draw_text(draw,self.font,40,message,color,305,470)
        await self.draw_image(bg_image,war.clan.badge.url,10,30)
        await self.draw_image(bg_image,war.opponent.badge.url,900,30)
        
        bg_image.save(out, quality=95)
        logging.info("INFO: image_maker.py - make_stats_image() ended")
    
    @staticmethod
    def make_war_info_dict(members):
        war_info_dict=dict()
        for member in members:
            th_details = war_info_dict.get(member.town_hall,None)
            if th_details:
                if member.best_opponent_attack:
                    def_info = th_details.get(member.best_opponent_attack.stars,None)
                    if def_info:
                        th_details[member.best_opponent_attack.stars]=def_info+1
                    else:
                        th_details[member.best_opponent_attack.stars]=1          
                else:
                    def_info = th_details.get('NotAttacked',None)
                    if def_info:
                        th_details['NotAttacked']=def_info+1
                    else:
                        th_details['NotAttacked']=1

            else:
                if member.best_opponent_attack:
                    war_info_dict[member.town_hall]={member.best_opponent_attack.stars  :1}
                else:
                    war_info_dict[member.town_hall]={'NotAttacked'  :1}
        return war_info_dict
    
    
    @staticmethod
    def make_bd(war_info_dict):
        break_down = dict()
        for k,v in sorted(war_info_dict.items(),reverse=True):
            break_down[k]=sum(v.values())
        return break_down
    
    @staticmethod
    def make_remaining_bd(war_info_dict):
        break_down = dict()
        for k,v in sorted(war_info_dict.items(),reverse=True):
            count=0
            for star,count_ in v.items():
                if star==3:
                    continue
                count+=count_
            break_down[k]=count
        return break_down

    async def prepare_th_info_for_inWar_image(self,image,break_down,font,font_size,color,x,y):
        for k,v in break_down.items():
            if k == 13:
                await self.draw_text(image,font,30,str(v),color,x,y)
                #continue
            if k == 12:
                await self.draw_text(image,font,30,str(v),color,x+(1*90),y)
                continue
            if k == 11:
                await self.draw_text(image,font,30,str(v),color,x+(2*90),y)
                continue
            if k == 10:
                await self.draw_text(image,font,30,str(v),color,x+(3*85),y)
                continue
            if k == 9:
                await self.draw_text(image,font,30,str(v),color,x+(4*85),y)
                continue
            if k == 8:
                await self.draw_text(image,font,30,str(v),color,x+(5*80),y)
                continue
            if k == 7:
                await self.draw_text(image,font,30,str(v),color,x+(6*80),y)
                continue
            if k == 6:
                await self.draw_text(image,font,30,str(v),color,x+(7*80),y)
                continue
            if k == 5:
                await self.draw_text(image,font,30,str(v),color,x+(8*80),y)
                continue

    async def make_inWar_image(self,war):
        logging.info("INFO: image_maker.py - make_inWar_image() started")
        home_war_info_dict = self.make_war_info_dict(war.clan.members)
        away_war_info_dict = self.make_war_info_dict(war.opponent.members)
        home_bd= self.make_bd(home_war_info_dict)
        away_bd=self.make_bd(away_war_info_dict)
        #home_bd= self.make_bd(war)
        home_rm_bd= self.make_remaining_bd(home_war_info_dict)
        away_rm_bd= self.make_remaining_bd(away_war_info_dict)
        out=os.path.join(self.directory+ "/images/temp/temp_inWar_status.png")
        bg_image = Image.open(self.background_image)
        draw = ImageDraw.Draw(bg_image)
        message = f"{war.clan.name}"
        color = 'rgb(127,255,0)' 
        await self.draw_text(draw,self.font,55,message,color,380,45,"Left")
        message = war.clan.tag
        await self.draw_text(draw,self.font,20,message,color,500,120,"Left")
        await self.prepare_th_info_for_inWar_image(draw,home_bd,self.font,20,color,265,310)
        await self.prepare_th_info_for_inWar_image(draw,home_rm_bd,self.font,20,color,265,500)

        message = f"{war.opponent.name}"
        color = 'rgb(255,69,0)' 
        await self.draw_text(draw,self.font,55,message,color,600,45)
        message = war.opponent.tag
        await self.draw_text(draw,self.font,20,message,color,600,120)
        await self.prepare_th_info_for_inWar_image(draw,away_bd,self.font,20,color,265,360)
        await self.prepare_th_info_for_inWar_image(draw,away_rm_bd,self.font,20,color,265,550)
        await self.draw_image(bg_image,war.clan.badge.url,10,30)
        await self.draw_image(bg_image,war.opponent.badge.url,900,30)
        
        bg_image.save(out, quality=95)
        logging.info("INFO: image_maker.py - make_inWar_image() ended")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(ImageMaker(os.getcwd(),BotFont.HAVTICA_FONT,BotImage.STATUS_IMAGE_LOC).make_stats_image())
    finally:
        loop.close()
    
 