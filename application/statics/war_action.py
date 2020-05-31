import coc
import discord
from application.statics.create_message import CreateMessage
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji
from datetime import datetime 

class WarAction():
    @staticmethod
    def war_state_prep_updates(war):
        home_clan_members=""
        for war_mem in war.clan.members:
            home_clan_members+=f"{war_mem.tag},"
        home_clan_members=home_clan_members[:-1]    
        opponent_clan_members=""
        for war_mem in war.opponent.members:
            opponent_clan_members+=f"{war_mem.tag},"
        opponent_clan_members=opponent_clan_members[:-1]
        war_table_insert = tuple()
        war_table_insert +=(war.clan_tag,)
        war_table_insert +=(war.opponent.tag,)
        war_table_insert +=(war.preparation_start_time.time,False,)
        war_table_insert +=(war.start_time.time,False,)
        war_table_insert +=(war.end_time.time,False,)
        war_table_insert +=(home_clan_members,)
        war_table_insert +=(opponent_clan_members,)
        war_table_insert +=(war.type,)
        war_table_insert +=(war.clan.stars,)
        war_table_insert +=(war.clan.destruction,)
        war_table_insert +=(war.clan.exp_earned or 0,)
        war_table_insert +=(war.opponent.stars,)
        war_table_insert +=(war.opponent.destruction,)
        war_table_insert +=(war.opponent.exp_earned or 0,)
        war_table_insert +=(war.clan.max_stars,)
        war_table_insert +=(war.clan.attacks_used,)
        war_table_insert +=(war.opponent.attacks_used,)
        return war_table_insert
    
    @staticmethod
    def war_state_end_updates(war):
        war_table_insert = tuple()
        war_table_insert +=(war.clan_tag,)
        war_table_insert +=(war.opponent.tag,)
        war_table_insert +=(war.clan.stars,)
        war_table_insert +=(war.clan.destruction,)
        war_table_insert +=(war.clan.exp_earned,)
        war_table_insert +=(war.opponent.stars,)
        war_table_insert +=(war.opponent.destruction,)
        war_table_insert +=(war.opponent.exp_earned,)
        war_table_insert +=(war.clan.attacks_used,)
        war_table_insert +=(war.opponent.attacks_used,)
        return war_table_insert
    '''    
    @staticmethod
    def attack_updates(war,attack,attack_table):
        attack_table+=(attack.order,)
        alley=enemy=None
        prev_attack_hit_count = prev_attack_best_stars=prev_attack_best_dest = prev_defense_hit_count = prev_defense_best_stars= prev_defense_best_dest = 0
        if attack.attacker.is_opponent: # It is a defensive attack
            attack_table+=("DEFENCE",)
            enemy=attack.attacker
            alley=attack.defender
            #if attack.order >1:
            if len(alley.defenses) >1:
                prev_defense_hit_count = 1
                prev_defense_best_stars= 0
                prev_defense_best_dest = 0
                for defense in alley.defenses:
                    if defense.stars>prev_defense_best_stars:
                        prev_defense_best_stars = defense.stars
                    if defense.destruction>prev_defense_best_dest:
                        prev_defense_best_dest = defense.destruction
                    prev_defense_hit_count +=1
            attack_table+=(None,)
            attack_table+=(None,)
            attack_table+=(None,)
            attack_table+=(prev_defense_hit_count,)
            attack_table+=(prev_defense_best_stars,)
            attack_table+=(prev_defense_best_dest,)

        else:  # It is an attack from home clan
            attack_table+=("ATTACK",)
            alley=attack.attacker
            enemy=attack.defender
            
            #if attack.order >1:
            
            if len(enemy.defenses) >1:
                prev_attack_hit_count = 1
                prev_attack_best_stars= 0
                prev_attack_best_dest = 0
                for defense in enemy.defenses:
                    if defense.stars>prev_attack_best_stars:
                        prev_attack_best_stars = defense.stars
                    if defense.destruction>prev_attack_best_dest:
                        prev_attack_best_dest = defense.destruction
                    prev_attack_hit_count +=1
            attack_table+=(prev_attack_hit_count,)
            attack_table+=(prev_attack_best_stars,)
            attack_table+=(prev_attack_best_dest,)
            attack_table+=(None,)
            attack_table+=(None,)
            attack_table+=(None,)
        
        attack_table+=(alley.map_position,)
        attack_table+=(alley.town_hall,)
        attack_table+=(alley.name,)    
        attack_table+=(alley.tag,)
        attack_table+=(enemy.map_position,)
        attack_table+=(enemy.town_hall,)
        attack_table+=(enemy.name,)    
        attack_table+=(enemy.tag,)
        attack_table+=(war.clan.tag,)
        attack_table+=(war.clan.name,)
        attack_table+=(war.clan.level,)
        attack_table+=(war.opponent.tag,)
        attack_table+=(war.opponent.name,)
        attack_table+=(war.opponent.level,)
        attack_table+=(attack.stars,)
        attack_table+=(attack.destruction,)
        if attack.attacker.town_hall < attack.defender.town_hall:
            attack_table+=("SCOUT",)
        elif attack.attacker.town_hall > attack.defender.town_hall:
            attack_table+=("DIP",)
        else:
            attack_table+=("SAME TH HIT",)

        if len(attack.defender.defenses)<=1:
            attack_table+=(True,) # Fresh Hit
            if attack.attacker.town_hall == attack.defender.town_hall:
                if attack.stars ==3:
                    if attack.attacker.is_opponent:
                        remark="VERY WEAK DEFENSE - CHANGE YOUR BASE"
                    else:
                        remark="VERY GOOD ATTACK - SKILLED PLAYER"
                else:
                    if attack.attacker.is_opponent:
                        remark="DEFENSE IS OK "
                    else:
                        remark="ATTACK NEEDS IMPROVEMENT"
                    
            elif attack.attacker.town_hall < attack.defender.town_hall:
                if attack.stars >1:
                    if attack.attacker.is_opponent:
                        remark="EXTREMELY POOR DEFENSE - CHANGE YOUR BASE IMMEDIATELY"
                    else:
                        remark="EXTREMELY GOOD ATTACK - HIGHLY SKILLED PLAYER"
                else:
                    if attack.attacker.is_opponent:
                        remark="POOR DEFENSE"
                    else:
                        remark="GOOD ATTACK"
            else:
                    if attack.attacker.is_opponent:
                        remark="EXTREMELY GOOD DEFENSE"
                    else:
                        remark="EXTREMELY POOR ATTACK - NOT RECOMMENDED TO STAY"
        else:
            attack_table+=(False,) # Not a Fresh Hit
            if attack.attacker.town_hall == attack.defender.town_hall:
                if attack.stars ==3:
                    if attack.attacker.is_opponent:
                        remark="DEFENSE NEEDS IMPROVEMENTS"
                    else:
                        remark="ATTACK IS OK"
                else:
                    if attack.attacker.is_opponent:
                        remark="DEFENSE IS OK "
                    else:
                        remark="ATTACK NEEDS IMPROVEMENT"
                    
            elif attack.attacker.town_hall < attack.defender.town_hall:
                if attack.stars >1:
                    if attack.attacker.is_opponent:
                        remark=" POOR DEFENSE - CHANGE YOUR BASE "
                    else:
                        remark="EXTREMELY GOOD ATTACK -  SKILLED PLAYER"
                else:
                    if attack.attacker.is_opponent:
                        remark="POOR DEFENSE"
                    else:
                        remark="GOOD ATTACK"
            else:
                    if attack.attacker.is_opponent:
                        remark="EXTREMELY GOOD DEFENSE"
                    else:
                        remark="EXTREMELY POOR ATTACK - KICK THIS PLAYER OUT"
        attack_table+=(remark,)
        
        return attack_table
    '''
    @staticmethod
    def attack_updates(war,attack,attack_table):
        attack_table['attack_order']=attack.order
        home=away=None
        best_stars = best_destruction = 0
        remark=""
        attack_table['hit_category']=f"{attack.attacker.town_hall}VS{attack.defender.town_hall}"
        if attack.attacker.town_hall == attack.defender.town_hall:
            attack_table['hit_type']="SAME TH HIT"
        elif attack.attacker.town_hall > attack.defender.town_hall:
            attack_table['hit_type']="DIP"
        else:
            attack_table['hit_type']="SCOUT"


        if attack.attacker.is_opponent: # It is a defensive attack
            attack_table['attack_type']="DEFENCE"
            away=attack.attacker
            home=attack.defender
            home_defenses=home.defenses.remove(attack)
            if home_defenses:
                attack_table['prev_attack_hit_count']= None
                attack_table['prev_defense_hit_count']=len(home.defenses)
            else:
                attack_table['prev_attack_hit_count']= None
                attack_table['prev_defense_hit_count']=0

            if attack_table['prev_defense_hit_count']==0:
                attack_table['is_fresh_hit']=True
                attack_table['prev_defense_best_stars']=None
                attack_table['prev_defense_best_dest']=None
                if attack.stars==3:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="EXTREMELY POOR DEFENSE - CHANGE YOUR BASE"
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="EXTREMELY POOR DEFENSE - CHANGE YOUR BASE ASAP"
                    else:
                        remark="DEFENSE IS OK"
                else:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="DEFENSE IS GOOD"
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="DEFENSE SEEMS OK"
                    else:
                        remark="DEFENSE IS VERY GOOD"
            else:
                attack_table['is_fresh_hit']=False
                for member_defenses in home.defenses:
                    if member_defenses.attacker_tag == attack.attacker_tag:
                        continue
                    if member_defenses.stars > best_stars :
                        best_stars = member_defenses.stars
                    if member_defenses.destruction > best_destruction:
                        best_destruction = member_defenses.destruction
                attack_table['prev_defense_best_stars']=best_stars
                attack_table['prev_defense_best_dest']=best_destruction
                
                if attack.stars==0:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="DEFENCE IS EXTREMELY GOOD "
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="DEFENCE SEEMS GOOD"
                    else:
                        remark="DEFENSE IS EXTREMELY GOOD - KEEP THIS BASE"
                else:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="DEFENCE IS NICE - CONSIDER CHANGING BASE"
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="POOR DEFENSE - CHANGE YOUR BASE ASAP"
                    else:
                        remark="DEFENSE SEEMS VERY GOOD"
            attack_table['prev_attack_best_stars']=None
            attack_table['prev_attack_best_dest']=None


        else:
            attack_table['attack_type']="ATTACK"
            away=attack.defender
            home=attack.attacker
            home_attacks=home.attacks.remove(attack)
            print(f"CHECK {home_attacks} \n")
            if home_attacks:
                attack_table['prev_attack_hit_count']=len(home_attacks)
                attack_table['prev_defense_hit_count']= None
            else:
                attack_table['prev_attack_hit_count']=0
                attack_table['prev_defense_hit_count']= None
            if attack_table['prev_attack_hit_count']==0:
                attack_table['is_fresh_hit']=True
                attack_table['prev_attack_best_stars']=None
                attack_table['prev_attack_best_dest']=None
                if attack.stars==3:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="EXTREMELY GOOD ATTACK - SKILLED PLAYER"
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="EXTREMELY GOOD ATTACK - HIGHLY SKILLED PLAYER"
                    else:
                        remark="EXTREMELY POOR ATTACK"
                else:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="ATTACK NEEDS IMPROVEMENTS - CHANGE STRATAGIES"
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="ATTACK SEEMS OK"
                    else:
                        remark="EXTREMELY POOR ATTACK - NOT RECOMMENDED "
            else:
                attack_table['is_fresh_hit']=False
                for member_attack in home.attacks:
                    if member_attack.defender_tag == attack.defender_tag:
                        continue
                    if member_attack.stars > best_stars :
                        best_stars = member_attack.stars
                    if member_attack.destruction > best_destruction:
                        best_destruction = member_attack.destruction
                attack_table['prev_attack_best_stars']=best_stars
                attack_table['prev_attack_best_dest']=best_destruction
                
                
                if attack.stars==0:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="EXTREMELY POOR ATTACK - NOT RECOMMENDED - PRACTISE REQUIRED"
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="ATTACKS SEEMS FAILURE"
                    else:
                        remark="ATTACK IS BELOW STANDARD - NOT RECOMMENDED TO STAY"
                else:
                    if attack_table['hit_type'] == "SAME TH HIT":
                        remark="ATTACK IS OK - GOOD PLAYER"
                    elif attack_table['hit_type'] == "SCOUT":
                        remark="ATTACK IS GOOD - NICE HIT"
                    else:
                        remark="ATACK SEEMS OK - SCOPE FOR IMPROVEMENT"
            attack_table['prev_defense_best_stars']=None
            attack_table['prev_defense_best_dest']=None

        attack_table['home_player_map_pos']=home.map_position
        attack_table['home_player_th_level']=home.town_hall
        attack_table['home_player_name']=home.name
        attack_table['home_player_tag']=home.tag
        attack_table['away_player_map_pos']=away.map_position
        attack_table['away_player_th_level']=away.town_hall
        attack_table['away_player_name']=away.name
        attack_table['away_player_tag']=away.tag
        attack_table['home_clan_tag']=war.clan.tag
        attack_table['home_clan_name']=war.clan.name
        attack_table['home_clan_level']=war.clan.level
        attack_table['away_clan_tag']=war.opponent.tag
        attack_table['away_clan_name']=war.opponent.name
        attack_table['away_clan_level']=war.opponent.level
        attack_table['stars']=attack.stars
        attack_table['destruction']=attack.destruction
        attack_table['remark']=remark
        attack_table['attack_time']=datetime.utcnow()
        attack_table['star_contribution']=attack.stars-best_stars
        attack_table['dest_contribution']=attack.destruction-best_destruction
        return attack_table