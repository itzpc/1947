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

