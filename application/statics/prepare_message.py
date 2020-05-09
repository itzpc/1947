from application.statics.create_message import CreateMessage
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji
class PrepMessage():
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
    def print_war_stars(enemy,star_emoji,stars):
        if enemy.best_opponent_attack:
            count= enemy.best_opponent_attack.stars 
            s_emoji= str(star_emoji['star'])*count
            new_star_count = stars-count
            if new_star_count <0:
                new_star_count = 0
            s_emoji+=str(star_emoji['star_new'])*new_star_count
            blank_star_count = 3-(new_star_count+count)
            s_emoji+=str(star_emoji['star_blank'])*blank_star_count

        else:
            s_emoji = str(star_emoji['star_new'])*stars
            count=3-stars
            s_emoji += str(star_emoji['star_blank'])*count
        return s_emoji
    
    @staticmethod
    def print_destruction(enemy,destruction):
        if enemy.best_opponent_attack:
            prev_destruction = enemy.best_opponent_attack.destruction
            change_in_destruction = prev_destruction - destruction
            change_in_destruction = '{0:.2f}'.format(float(change_in_destruction))
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
        if th_attacker == th_defender :
            msg+= " SAME TH HIT "
        elif th_attacker < th_defender:
            msg+= " SCOUT"
        else:
            msg+= " DIP"
        return str(msg)
    @staticmethod
    def print_previous_hit(enemy,star_emoji):
        msg =""
        if enemy.best_opponent_attack:
            for defensive_attacks in  enemy.best_opponent_attack:
                msg += f"`Hit No : {defensive_attacks.order}`{defensive_attacks.attacker.name} - {str(star_emoji['star'])*defensive_attacks.stars} - {defensive_attacks.destruction} % \n"
        return str(msg)

    def prepare_on_war_attack_message(self,attack,war):
        embed_args = dict()
        attack_emoji, star_emoji, attack_msg , enemy, ally,colour=self.get_attack_info(attack.attacker.is_opponent,attack.attacker,attack.defender)
        content = f"`{ally.map_position}`. {ally.name} {self.get_th_emoji(ally.town_hall)} {attack_emoji} {self.get_th_emoji(enemy.town_hall)} `{enemy.map_position}`. {enemy.name}"
        embed_args["author_name"]="Details"
        embed_args["embed_title"]= f"{attack_msg}"
        description=f"**STARS**\n"
        description+=f"{self.print_war_stars(enemy,star_emoji,attack.stars)} \n\n"
        description+=f"**DESTRUCTION**\n"
        description+=f"{self.print_destruction(enemy,attack.destruction)} \n\n"
        description+=f"**HIT TYPE**\n"
        description+=f"{self.print_hit_type(enemy,attack.attacker.town_hall,attack.defender.town_hall)} \n \n"
        description+=f"**PREVIOUS HITS ON THIS BASE**\n"
        description+=f"{self.print_previous_hit(enemy,star_emoji)} \n \n"
        embed_args["embed_description"]=description
        embed_args["embed_colour"]=colour
        create_msg = CreateMessage(content,True)
        return create_msg.create_message(**embed_args)