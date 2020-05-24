import coc
import discord
from application.statics.create_message import CreateMessage
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji

class PrepMessage():
    
    @staticmethod
    def get_info_on_defender_bases(defender,star_emoji,attack):
        best_stars = best_destruction = 0
        print(f"\nATTACK {attack}")
        print(f"\nDEFENSES {defender.defenses.remove(attack)}")
        defensive_attack = list()
        if len(defender.defenses)>0:
            
            for member_defenses in defender.defenses:
                if member_defenses.attacker_tag == attack.attacker_tag:
                    continue
                if member_defenses.stars > best_stars :
                    best_stars = member_defenses.stars
                if member_defenses.destruction > best_destruction:
                    best_destruction = member_defenses.destruction
                defensive_attack.append(f"{member_defenses.attacker.map_position}.` {member_defenses.attacker.name} `{str(star_emoji['star'])*member_defenses.stars} {member_defenses.destruction}%")
        else:
            print("No Defenses")
            
        return best_stars, best_destruction, defensive_attack

    @staticmethod 
    def get_attack_info(is_opponent,attacker,defender):
        if is_opponent:
            attack_emoji= str(Emoji.BACKWARD_RED)
            colour = 0xFF0000
            star_emoji = {"star_blank":BotEmoji.STAR_BLANK,"star":BotEmoji.STAR_RED,"star_new":BotEmoji.STAR_RED_NEW}
            type= str("DEFENDED")
            opponent_member = attacker
            ally = defender
        else:
            
            attack_emoji= str(Emoji.FORWARD_GREEN)
            colour = 0x008000
            type=str("ATTACKED")
            star_emoji = {"star_blank":BotEmoji.STAR_BLANK,"star":BotEmoji.STAR_GREEN,"star_new":BotEmoji.STAR_GREEN_NEW}
            opponent_member = defender
            ally=attacker
        return attack_emoji, star_emoji, type, opponent_member, ally, colour

    @staticmethod
    def get_th_emoji(th):
        th = int(th)
        if th == 13:
            return str(Emoji.TH13)
        elif th == 12:
            return str(Emoji.TH12)
        elif th == 11:
            return str(Emoji.TH11)
        elif th == 10:
            return str(Emoji.TH10)
        elif th == 9:
            return str(Emoji.TH9)
        elif th == 8:
            return str(Emoji.TH8)
        elif th == 7:
            return str(Emoji.TH7)
        else:
            return f"TH{th} "
    
    @staticmethod
    def print_war_stars(prev_best_stars,stars,star_emoji):
        if prev_best_stars:
            s_emoji= str(star_emoji['star'])*prev_best_stars
            new_star_count = stars-prev_best_stars
            if new_star_count <0:
                new_star_count = 0
            s_emoji+=str(star_emoji['star_new'])*new_star_count
            blank_star_count = 3-(new_star_count+prev_best_stars)
            s_emoji+=str(star_emoji['star_blank'])*blank_star_count

        else:
            s_emoji = str(star_emoji['star_new'])*stars
            blank_star_count=3-stars
            s_emoji += str(star_emoji['star_blank'])*blank_star_count
        return s_emoji
    
    @staticmethod
    def print_destruction(prev_best_destruction,destruction):
        if prev_best_destruction:
            print("Prev Des",prev_best_destruction)
            change_in_destruction =  destruction - prev_best_destruction
            
            if change_in_destruction >0 :
                msg= f" {destruction} % {BotEmoji.GREEN_UP} {change_in_destruction} "
            else:
                msg= f" {destruction} % {BotEmoji.RED_DOWN} {change_in_destruction} "
        else:
            msg = f"{BotEmoji.GREEN_UP} {destruction} % "

        return str(msg)

    @staticmethod
    def print_hit_type(enemy,th_attacker,th_defender):
        if enemy.best_opponent_attack is None:
            msg = " FRESH HIT - "
        else:
            msg ="NOT A FRESH HIT - "
        if th_attacker == th_defender :
            msg+= " SAME TH HIT "
        elif th_attacker < th_defender:
            msg+= " SCOUT"
        else:
            msg+= " DIP"
        return str(msg)

    @staticmethod
    def print_previous_hit(defesive_attack,star_emoji):
        msg =""
        for attacks in  defesive_attack:
            msg += f"{attacks} \n"
        return str(msg)

    def prepare_on_war_attack_message(self,attack,war):
        embed_args = dict()
        attack_emoji, star_emoji, attack_msg , enemy, ally,colour=self.get_attack_info(attack.attacker.is_opponent,attack.attacker,attack.defender)

        best_stars, best_destruction, defesive_attack = self.get_info_on_defender_bases(attack.defender,star_emoji,attack)
        content = f"`{ally.map_position}`. {ally.name} {self.get_th_emoji(ally.town_hall)} {attack_emoji} {self.get_th_emoji(enemy.town_hall)} `{enemy.map_position}`. {enemy.name}"
        embed_args["author_name"]="Details"
        embed_args["embed_title"]= f"{attack_msg}"
        description=f"**STARS**\n"
        description+=f"{self.print_war_stars(best_stars,attack.stars,star_emoji)} \n\n"
        description+=f"**DESTRUCTION**\n"
        description+=f"{self.print_destruction(best_destruction,attack.destruction)} \n\n"
        description+=f"**HIT TYPE**\n"
        description+=f"{self.print_hit_type(enemy,attack.attacker.town_hall,attack.defender.town_hall)} \n \n"
        if len(defesive_attack)>0:
            description+=f"**PREVIOUS HITS ON THIS BASE**\n"
            description+=f"{self.print_previous_hit(defesive_attack,star_emoji)} \n \n"
        embed_args["embed_description"]=description
        embed_args["embed_colour"]=colour
        create_msg = CreateMessage(content,True)
        return create_msg.create_message(**embed_args)

    def prepare_clan_link_message(self,clan):
        embed_args = dict()
        embed_args["embed_title"]=f"{clan.name} - ({clan.tag})"
        description = f"Level : {clan.level} \n"
        description += f"Location : {clan.location} \n"
        description += f"Win Streak : {clan.war_win_streak} \n"
        embed_args["embed_description"]=description
        embed_args["set_thumbnail_url"]=clan.badge.url
        content = ""
        content, embed=CreateMessage(content,True).create_message(**embed_args)
        return embed
    def prepare_user_message_embed(self,member,description,title=None):
        
        embed_args = dict()
        embed_args["author_name"]=member.display_name
        embed_args["embed_title"]= title or ""
        embed_args["embed_colour"]=0xFFFFFF
        embed_args["author_icon_url"]=str(member.avatar_url)
        embed_args["embed_description"]=description
        content,embed=CreateMessage(is_embed=True).create_message(**embed_args)
        return embed
        
