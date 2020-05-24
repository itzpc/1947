import discord
from application.constants.guild1947 import Guild1947Image
from datetime import datetime
class Message():

    def __init__(self,kwargs):
        self.content=self.if_embed =self.embed_title=self.embed_description=self.embed_colour=self.embed_title_url=self.title_timestamp=self.set_image_url=self.set_thumbnail_url=self.author_name=self.author_url=self.author_icon_url=self.footer_text=self.footer_icon_url = None
        if kwargs['content']:
            self.content= kwargs['content']
        if kwargs['if_embed']:
            self.if_embed = True
            if kwargs['embed_title']:
                self.embed_title =kwargs['embed_title']
            if kwargs['embed_description']:
                self.embed_description=kwargs['embed_description']
            if kwargs['embed_colour']:
                self.embed_colour = kwargs['embed_colour']
            else:
                self.embed_colour = 0xFFD700
            if kwargs['embed_title_url']:
                self.embed_title_url =kwargs['embed_title_url']
            if kwargs['title_timestamp']:
                self.title_timestamp = kwargs['title_timestamp']
            else:
                self.title_timestamp = datetime.utcnow()
            #if kwargs['set_image_url']
            #    self.set_image_url = kwargs['set_image_url']
            if kwargs['set_thumbnail_url']:
                self.set_thumbnail_url = kwargs['set_thumbnail_url']
            if kwargs['author_name']:
                self.author_name = kwargs['author_name']
            if kwargs['author_url']:
                self.author_url =kwargs['author_url']
            if kwargs['author_icon_url']:
                self.author_icon_url=kwargs['author_icon_url']
            if kwargs['footer_text']:
                self.footer_text=kwargs['footer_text']
            else:
                self.footer_text="1947"
            if kwargs['footer_icon_url']:
                self.footer_icon_url = kwargs['footer_icon_url']
            else:
                self.footer_icon_url = Guild1947Image.EKA_ICON_URL
    
    def create_message(self,add_field =None):
        if self.if_embed:
            embed = discord.Embed(title=f"{self.embed_title}", colour=discord.Colour(self.embed_colour), url=self.embed_title_url, description=f"{self.embed_description}", timestamp=self.title_timestamp)
            #embed.set_image(url=f"{self.set_image_url}")
            embed.set_thumbnail(url=self.set_thumbnail_url)
            embed.set_author(name=f"{self.author_name} " )
            embed.set_footer(text=f"{self.footer_text}",icon_url=self.footer_icon_url)
            if add_field:
                for field in add_field:
                    embed.add_field(name=f"{field[0]}",value=f"{field[1]}",inline=f"{field[2]}")
            return self.content,embed
        else:
            return self.content,None

class CreateMessage():
    def __init__(self,content=None, is_embed=False):
        self.is_embed = is_embed
        if content is None:
            content = ""
        self.content = content
        self.embed_colour = 0x808080
        self.timestamp = datetime.utcnow()
        self.footer_icon_url = Guild1947Image.EKA_ICON_URL
        self.footer_text="1947-BOT"

    def create_message(self,**kwargs):
        title =kwargs.get('embed_title',"")
        self.embed_colour= kwargs.get('embed_colour',self.embed_colour)
        title_url = kwargs.get('embed_title_url',False)
        description = kwargs.get('embed_description',"")
        set_thumbnail_url = kwargs.get('set_thumbnail_url',False)
        self.timestamp = kwargs.get('embed_timestamp',self.timestamp)
        author_name = kwargs.get('author_name',"")
        author_url = kwargs.get('author_url',False)
        author_icon_url = kwargs.get('author_icon_url',False)
        self.footer_text = kwargs.get('footer_text',self.footer_text)
        self.footer_icon_url = kwargs.get('footer_icon_url',self.footer_icon_url)
        fileds = kwargs.get('add_field',False)
        if title_url:
            embed = discord.Embed(title=title,colour=discord.Colour(self.embed_colour),url=title_url,description=description,timestamp=self.timestamp)
        else:
            embed = discord.Embed(title=title,colour=discord.Colour(self.embed_colour),description=description,timestamp=self.timestamp)
        if set_thumbnail_url:
            embed.set_thumbnail(url=set_thumbnail_url)
        if author_url and author_icon_url:
            embed.set_author(name=author_name, url=author_url, icon_url=author_url)
        elif author_url:
            embed.set_author(name=author_name, url=author_url)
        elif author_icon_url:
            embed.set_author(name=author_name, icon_url=author_icon_url)
        else:
            embed.set_author(name=author_name)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon_url)

        if fileds:
            for field in fileds:
                embed.add_field(name=field[0], value=field[1], inline=field[2])
        return self.content,embed