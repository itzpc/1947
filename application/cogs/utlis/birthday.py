import discord
import asyncio
import requests
from io import BytesIO
import logging
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime
from application.constants.bot_const import BotImage,BotFont
from application.constants.emoji import Emoji


class Birthday():
    def __init__(self,channel,user):
        self.wish_channel = channel
        self.userObj = user
        self.bday_file_path= os.path.join(os.getcwd())+BotImage.BIRTHDAY_IMAGE
        self.bday_file_name=BotImage.BIRTHDAY_IMAGE_NAME
        self.bday_temp_file_path= os.path.join(os.getcwd())+BotImage.BIRTHDAY_TEMP_IMAGE
        self.bday_temp_file_name=BotImage.BIRTHDAY_TEMP_IMAGE_NAME
        self.bday_temp_file_loc= os.path.join(os.getcwd())+BotImage.BIRTHDAY_TEMP_IMAGE_LOC
        self.font = os.path.join(os.getcwd())+BotFont.CJK_FONT2
    
    async def wish_birthday(self):
        birthday_wishes = f" Wish {self.userObj.mention}, Happy Birthday !"
        try:
            await self.image_maker()
            file = discord.File(self.bday_temp_file_path)
            msg = await self.wish_channel.send(content=birthday_wishes,file=file)
            logging.info(f"INFO: birthday.py - wish_birthday() - member_id {self.userObj.id}")
            await msg.add_reaction(Emoji.BIRTHDAY)
        except Exception as Ex:
            logging.error(f"ERROR: birthday.py - Exception {Ex}")
        
        

    async def image_maker(self):
        logging.info("INFO: birthday.py - image_maker() started")
        temp_image_loc = self.bday_temp_file_loc
        poster= self.bday_file_path
        response = requests.get(self.userObj.avatar_url)
        cjk_font = os.path.join(os.getcwd())+"/fonts/DejaVuSans-Bold.ttf"
        poster_image = Image.open(poster)
        user_avatar = Image.open(BytesIO(response.content))
        
        draw = ImageDraw.Draw(poster_image)

        # draw = ImageDraw.Draw(poster_image)
        unicode_font = ImageFont.truetype(cjk_font,size =45)
        message = f"{self.userObj.name}"
        message=str(message[:21])
        color = 'rgb(0,255,255)' 
        w, h = draw.textsize(message,font=unicode_font)
        draw.text (((450-(w/2)),238-60), message, font=unicode_font, fill=color )
        user_avatar = user_avatar.resize((200, 200))
        bigsize = (user_avatar.size[0] * 3, user_avatar.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(user_avatar.size, Image.ANTIALIAS)
        user_avatar.putalpha(mask)
        output = ImageOps.fit(user_avatar, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        poster_image.paste(user_avatar, (19, 19), user_avatar)
        poster_image.save(temp_image_loc+"temp.png", quality=95)
        logging.info("INFO: birthday.py - image_maker() ended")
        #poster_image.save(temp_image_loc+"temp.png")
