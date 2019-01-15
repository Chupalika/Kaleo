#!/usr/bin/python
# -*- coding: utf_8 -*-

from __future__ import division

import os,re,time,datetime

### NEXT WEEK EVENTS FOR LAST CYCLE WEEK (24) ARE NOT SET
curfolder=os.path.dirname(os.path.abspath(__file__))+os.sep
cycle_1_start_time=datetime.datetime.strptime("2018-02-13 06:00","%Y-%m-%d %H:%M").timestamp()
cycles_to_test=1
automoderator_hours_offset=-3

input_weekly_thread_dates_cycle_ended=1
week_duration=7*24*60*60
cycle_duration=24*week_duration
cycles_ended=int((time.time()-cycle_1_start_time)//cycle_duration)
inputpostspath="{}{}{}".format(curfolder,"input-posts",os.sep)
outputpostspath="{}{}{}".format(curfolder,"output-posts",os.sep)
event_date_regex=re.compile("\*\*Event Period\*\*: (20[1-3][0-9]-[0-1][0-9]-[0-3][0-9]) [0-2][0-9]:[0-5][0-9] UTC to (20[1-3][0-9]-[0-1][0-9]-[0-3][0-9]) [0-2][0-9]:[0-5][0-9] UTC \(([0-9]{1,2})")
header_weekly_title_regex=re.compile("\#\#([^\n]{9,})\n")
daily_safari_table_regex=re.compile("\n([^\|\n]{4,})\|([^\|\n]{4,})\|")
yearly_title="Yearly Events!!"
months=["Placeholder","January","February","March","April","May","June","July","August","September","October","November","December"]
monthly_rewards=["Placeholder","Pikachu (Lion Dancer)","Pikachu (Kotatsu)","**Pikachu (Graduate)**","Pikachu (Intern)","Pikachu (Children's Day)","Pikachu (Rainy Season)","Pikachu (Summer Festival)","Pikachu (Beach Walk)","Pikachu (Pastry Chef)","Pikachu (Artist)","Pikachu (Mushroom Harvest)","Pikachu (Year's End)"]
automoderator_indentation=" "*4

#Set "skip_current_cycle" parameter to true if a post was already submitted manually
original_weekly_data=[
	{"title":"Week 1","link":"https://www.reddit.com/r/PokemonShuffle/comments/7x7sya/main_ux_stages_primal_groudon_expert_stage_all/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 2","link":"https://www.reddit.com/r/PokemonShuffle/comments/7z427l/20180220_event_rotation_week_2_daily_2_feat/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 3","link":"https://www.reddit.com/r/PokemonShuffle/comments/80k9xo/20180227_event_rotation_week_3_mega_garchomp_comp/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 4","link":"https://www.reddit.com/r/PokemonShuffle/comments/82krov/latios_escalation_meloettap_yveltal_celebi_golem/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 5","link":"https://www.reddit.com/r/PokemonShuffle/comments/8420wb/20180313_event_rotation_week_5_mega_steelix_comp/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 6","link":"https://www.reddit.com/r/PokemonShuffle/comments/8613g2/giratinaa_escalation_buzzwole_groudon_mimikyu/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 7","link":"https://www.reddit.com/r/PokemonShuffle/comments/87g7bo/20180327_event_rotation_week_7_mega_manectric/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 8","link":"https://www.reddit.com/r/PokemonShuffle/comments/89mgry/latias_escalation_shiny_mewtwo_kyuremb_palkia/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 9","link":"https://www.reddit.com/r/PokemonShuffle/comments/8b5fo4/20180410_event_rotation_week_9_mega_gyarados_comp/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 10","link":"https://www.reddit.com/r/PokemonShuffle/comments/8d8ch5/diancie_escalation_shiny_tyranitar_shiny_hooh/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 11","link":"https://www.reddit.com/r/PokemonShuffle/comments/8ei8v0/20180424_event_rotation_week_11_mega_alakazam/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 12","link":"https://www.reddit.com/r/PokemonShuffle/comments/8gfsbc/winking_turtwig_darkrai_escalation_salamence/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 13","link":"https://www.reddit.com/r/PokemonShuffle/comments/8hug9f/20180508_event_rotation_week_13_mega_pinsir_comp/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 14","link":"https://www.reddit.com/r/PokemonShuffle/comments/8jzzzu/kyurem_escalation_tapu_fini_rayquaza/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 15","link":"https://www.reddit.com/r/PokemonShuffle/comments/8l9pqz/20180522_event_rotation_week_15_mega_camerupt/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 16","link":"https://www.reddit.com/r/PokemonShuffle/comments/8mxdbn/zygarde50_escalation_luxray_solgaleo_winking/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 17","link":"https://www.reddit.com/r/PokemonShuffle/comments/8oood2/20180605_event_rotation_week_17_mega_beedrill/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 18","link":"https://www.reddit.com/r/PokemonShuffle/comments/8r5vsb/dusknoir_winking_oshawott_meloettaa_escalation/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 19","link":"https://www.reddit.com/r/PokemonShuffle/comments/8s6jlf/20180619_event_rotation_week_19_mega_houndoom/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 20","link":"https://www.reddit.com/r/PokemonShuffle/comments/8u8c38/giratinao_escalation_stufful_hitmonlee_tapu_lele/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 21","link":"https://www.reddit.com/r/PokemonShuffle/comments/8vpvib/20180703_event_rotation_week_21_mega_gardevoir/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 22","link":"https://www.reddit.com/r/PokemonShuffle/comments/8y6gqb/magearna_escalation_silvally_goodra_turtonator/","author":"/u/SoItBegins_n","skip_current_cycle":False},
	{"title":"Week 23","link":"https://www.reddit.com/r/PokemonShuffle/comments/8zimv7/20180717_event_rotation_week_23_mega_charizard_x/","author":"/u/Chupalika","skip_current_cycle":False},
	{"title":"Week 24","link":"https://www.reddit.com/r/PokemonShuffle/comments/91efta/event_rotation_finale_take_care_of_yourself/","author":"/u/SoItBegins_n","skip_current_cycle":False},]

original_eb_data=[
	{"title":"Decidueye","link":"https://www.reddit.com/r/PokemonShuffle/comments/7x7okh/decidueye_eb_v3_green_arrow_lost_amid_the_chaos/","author":"/u/PKMN-Rias","duration":1,"skip_current_cycle":False},
	{"title":"Volcanion","link":"https://www.reddit.com/r/PokemonShuffle/comments/7ytpev/volcanion_eb_v3_a_hard_finish/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Latios","link":"https://www.reddit.com/r/PokemonShuffle/comments/82d0ka/latios_eb_v5_flying_dragon_back_so_soon/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Giratina (Altered Form)","link":"https://www.reddit.com/r/PokemonShuffle/comments/85qhyu/giratina_altered_eb_v30_blindsided_by_bad_rewards/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Latias","link":"https://www.reddit.com/r/PokemonShuffle/comments/89aiz6/latias_eb_v4_repeat_ebs_for_eons/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Diancie","link":"https://www.reddit.com/r/PokemonShuffle/comments/8cudko/diancie_eb_v4_a_poisonous_time/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Darkrai","link":"https://www.reddit.com/r/PokemonShuffle/comments/8g6cwg/darkrai_eb_v5_the_darkness_returns/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Kyurem","link":"https://www.reddit.com/r/PokemonShuffle/comments/8jjs13/kyurem_eb_v4_dont_freeze_timed_madness/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Zygarde (50% Form)","link":"https://www.reddit.com/r/PokemonShuffle/comments/8mwvxs/zygarde_50_eb_v3_the_dazzling_dragon/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Meloetta (Aria Form)","link":"https://www.reddit.com/r/PokemonShuffle/comments/8qgtec/meloetta_aria_escalation_battle_v3_i_sing_for/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Giratina (Origin Form)","link":"https://www.reddit.com/r/PokemonShuffle/comments/8ty0uh/giratinaorigin_eb_v3_cross_your_fingers_and_match/","author":"/u/PKMN-Rias","duration":2,"skip_current_cycle":False},
	{"title":"Magearna","link":"https://www.reddit.com/r/PokemonShuffle/comments/8xmuml/magearna_eb_v2_a_poisonous_end/","author":"/u/PKMN-Rias","duration":1,"skip_current_cycle":False},
	{"title":"Incineroar","link":"https://www.reddit.com/r/PokemonShuffle/comments/8zjh9d/incineroar_eb_v3_the_final_flame/","author":"/u/PKMN-Rias","duration":1,"skip_current_cycle":False},
	{"title":"Primarina","link":"https://www.reddit.com/r/PokemonShuffle/comments/91fbti/primarina_eb_v3_fin/","author":"/u/PKMN-Rias","duration":1,"skip_current_cycle":False},]

original_competition_data=[
	{"title":"Mega Banette","link":"https://www.reddit.com/r/PokemonShuffle/comments/7xb7fk/mega_banette_competition_guide/","author":"/u/TheItemGodofShuffle","skip_current_cycle":False},
	{"title":"Mega Garchomp","link":"https://www.reddit.com/r/PokemonShuffle/comments/80mdj3/mega_garchomp_competition_guide/","author":"/u/TheItemGodofShuffle","skip_current_cycle":False},
	{"title":"Mega Steelix","link":"https://www.reddit.com/r/PokemonShuffle/comments/845hai/mega_steelix_competition_guide/","author":"/u/TheItemGodofShuffle","skip_current_cycle":False},
	{"title":"Mega Manectric","link":"https://www.reddit.com/r/PokemonShuffle/comments/87jhlc/mega_manectric_competition_guide/","author":"/u/TheItemGodofShuffle","skip_current_cycle":False},
	{"title":"Mega Gyarados","link":"https://www.reddit.com/r/PokemonShuffle/comments/8b5hmc/rampage_on_the_seas_mega_gyarados_competition/","author":"/u/BunbunMiyu","skip_current_cycle":False},
	{"title":"Mega Alakazam","link":"https://www.reddit.com/r/PokemonShuffle/comments/8ekafq/mega_alakazam_competition_guide_brains_over_brawn/","author":"/u/BunbunMiyu","skip_current_cycle":False},
	{"title":"Mega Pinsir","link":"https://www.reddit.com/r/PokemonShuffle/comments/8hw1yt/mega_pinsir_competition_guide_this_bug_is_on/","author":"/u/BunbunMiyu","skip_current_cycle":False},
	{"title":"Mega Camerupt","link":"https://www.reddit.com/r/PokemonShuffle/comments/8l8l1f/mega_camerupt_competition_a_test_of_resolve_in/","author":"/u/BunbunMiyu","skip_current_cycle":False},
	{"title":"Mega Beedrill","link":"https://www.reddit.com/r/PokemonShuffle/comments/8opngp/mega_beedrill_competition_poisonous_beeatdown/","author":"/u/BunbunMiyu","skip_current_cycle":False},
	{"title":"Mega Houndoom","link":"https://www.reddit.com/r/PokemonShuffle/comments/8s7sme/mega_houndoom_competition_burned_to_ashes/","author":"/u/BunbunMiyu","skip_current_cycle":False},
	{"title":"Mega Gardevoir","link":"https://www.reddit.com/r/PokemonShuffle/comments/8w0vsz/mega_gardevoir_competition_beauty_and_fatality/","author":"/u/BunbunMiyu","skip_current_cycle":False},
	{"title":"Mega Charizard X","link":"https://www.reddit.com/r/PokemonShuffle/comments/8zjqbo/mega_charizard_x_competition_the_final_battle/","author":"/u/BunbunMiyu","skip_current_cycle":False},]

def dates_interval_match(t1start,t1end,t2start,t2end):
	return (t1start<=t2start<t1end) or (t2start<=t1start<t2end)
	
def findnth(haystack,needle,n):
	parts=haystack.split(needle,n+1)
	if len(parts)<=n+1:return -1
	return len(haystack)-len(parts[-1])-len(needle)

for loop_cycles_ended in range(cycles_ended,cycles_ended+cycles_to_test):
#Competitions and EB threads use data obtained from the original posts. Weekly events contains the output of generatemarkuptext_alt2.py with further editing
	automoderator_list=[]
	week_num=0
	cycle_start_time=cycle_1_start_time+cycle_duration*loop_cycles_ended
	for tdata in original_eb_data:
		fpath="{}{}{}".format(inputpostspath,tdata["title"],".txt")
		if os.path.isfile(fpath):
			txt=""
			with open(fpath,"r") as infile:txt=infile.read()
			if len(txt)>99:
				automoderator_list.append({"post_header":"#{} Escalation Battles - Cycle {}\n\n*AUTOMATION INFO*: The **[original post]({})** made by {} can contain more details, you should visit it! If there are errors in the post, please contact /u/Sky-17.\n\n---\n".format(tdata["title"],loop_cycles_ended+[1,2][tdata["skip_current_cycle"]],tdata["link"],tdata["author"]),
					"wiki_header":"#{} Escalation Battles\n\n*AUTOMATION INFO*: The **[original post]({})** made by {} can contain more details, you should visit it! If there are errors in the post, please contact /u/Sky-17.\n\n---\n".format(tdata["title"],tdata["link"],tdata["author"]),
					"txt":txt,"extra":"","type":2,"week":week_num,"timestamp":cycle_start_time+(week_num+[0,24][tdata["skip_current_cycle"]])*week_duration,
					"post_title":"{} Escalation Battles - Cycle {}".format(tdata["title"],loop_cycles_ended+[1,2][tdata["skip_current_cycle"]])})
		week_num+=tdata["duration"]
	for comp_num,tdata in enumerate(original_competition_data):
		fpath="{}{}{}".format(inputpostspath,tdata["title"],".txt")
		if os.path.isfile(fpath):
			txt=""
			with open(fpath,"r") as infile:txt=infile.read()
			if len(txt)>99:
				automoderator_list.append({"post_header":"#{} Competition - Cycle {}\n\n*AUTOMATION INFO*: The **[original post]({})** made by {} can contain more details, you should visit it! If there are errors in the post, please contact /u/Sky-17.\n\n---\n".format(tdata["title"],loop_cycles_ended+[1,2][tdata["skip_current_cycle"]],tdata["link"],tdata["author"]),
					"wiki_header":"#{} Competition\n\n*AUTOMATION INFO*: The **[original post]({})** made by {} can contain more details, you should visit it! If there are errors in the post, please contact /u/Sky-17.\n\n---\n".format(tdata["title"],tdata["link"],tdata["author"]),				
					"txt":txt,"extra":"","type":3,"week":comp_num*2,"timestamp":cycle_start_time+(comp_num*2+[0,24][tdata["skip_current_cycle"]])*week_duration,
					"post_title":"{} Competition - Cycle {}".format(tdata["title"],loop_cycles_ended+[1,2][tdata["skip_current_cycle"]])})
	first_weekly_index=len(automoderator_list)
	for week_num,tdata in enumerate(original_weekly_data):
		fpath="{}{}{}{}".format(inputpostspath,"Week ",week_num+1,".txt")
		if os.path.isfile(fpath):
			txt=""
			with open(fpath,"r") as infile:txt=infile.read()
			if len(txt)>99:
				date_matches=event_date_regex.findall(txt)
				unique_date_matches=[]
				if len(date_matches)>0:
					for dstr in list(set([date_matches[0][0]]+[d[1] for d in date_matches])):txt=txt.replace(dstr,(datetime.date.fromtimestamp(datetime.datetime.strptime(dstr,"%Y-%m-%d").timestamp()+(loop_cycles_ended-input_weekly_thread_dates_cycle_ended+[0,1][tdata["skip_current_cycle"]])*cycle_duration)).strftime("%Y-%m-%d"))
				start_time=cycle_start_time+(week_num+[0,24][tdata["skip_current_cycle"]])*week_duration
				timestamps=[datetime.date.fromtimestamp(int(start_time)),datetime.date.fromtimestamp(int(start_time)+week_duration)]
				yearly_timestamps=[
					[datetime.date(timestamps[0].year,1,6),datetime.date(timestamps[0].year,1,9)],
					[datetime.date(timestamps[0].year,2,13),datetime.date(timestamps[0].year,2,16)],
					[datetime.date(timestamps[0].year,2,18),datetime.date(timestamps[0].year,2,21)],
					[datetime.date(timestamps[0].year,7,6),datetime.date(timestamps[0].year,7,9)],
					[datetime.date(timestamps[0].year,10,17),datetime.date(timestamps[0].year,10,31)],
					[datetime.date(timestamps[0].year,12,11),datetime.date(timestamps[0].year,12,25)],
				]
				extra="\n##Weekly Events\n\n- Skill Booster M Stage! - Eevee - (Tuesday to Friday, 3 days)\n- A Chance for Coins! - Meowth - (Friday to Monday, 3 days)\n- Tons of Exp. Points! - Victini - (Friday to Tuesday, 4 days)\n\n---\n##Monthly Events\n\n"
				if timestamps[0].day>=9 and timestamps[0].day<=18:extra+="- Mid-month Challenge ({} 15 to {} 18, 3 days)\n".format(months[timestamps[1].month],months[timestamps[1].month])
				elif timestamps[1].day<=9:extra+="- Start-of-Month Challenge ({} 1 to {} 4, 3 days)\n".format(months[timestamps[1].month],months[timestamps[1].month])
				if timestamps[0].month!=timestamps[1].month:extra+="- {} Celebration Challenge - {} (check-in 10 times, you'll get 1 Level Up if already caught)\n".format(months[timestamps[0].month],monthly_rewards[timestamps[0].month])
				extra+="- {} Celebration Challenge - {} (check-in 10 times, you'll get 1 Level Up if already caught)\n".format(months[timestamps[1].month],monthly_rewards[timestamps[1].month])
				extra+="\n---\n"
				yearlytxt=""
				if dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[0][0],yearly_timestamps[0][1]) or dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[3][0],yearly_timestamps[3][1]):
					fpath="{}{}".format(inputpostspath,"Yearly_Jirachi.txt")
					jirachi_id=[0,3][dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[3][0],yearly_timestamps[3][1])]
					if os.path.isfile(fpath):
						ytxt=""
						with open(fpath,"r") as infile:ytxt=infile.read()
						if len(ytxt)>99:yearlytxt+="\n"+ytxt.replace("<date1>",yearly_timestamps[jirachi_id][0].strftime("%Y-%m-%d")).replace("<date2>",yearly_timestamps[jirachi_id][1].strftime("%Y-%m-%d")).replace("<date3>","{}".format(abs(yearly_timestamps[jirachi_id][1]-yearly_timestamps[jirachi_id][0]).days))
				if dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[1][0],yearly_timestamps[2][1]):
					if dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[1][0],yearly_timestamps[1][1]):
						fpath="{}{}".format(inputpostspath,"Yearly_Pikachu_Enamored.txt")
						if os.path.isfile(fpath):
							ytxt=""
							with open(fpath,"r") as infile:ytxt=infile.read()
							if len(ytxt)>99:yearlytxt+="\n"+ytxt.replace("<date1>",yearly_timestamps[1][0].strftime("%Y-%m-%d")).replace("<date2>",yearly_timestamps[1][1].strftime("%Y-%m-%d")).replace("<date3>","{}".format(abs(yearly_timestamps[1][1]-yearly_timestamps[1][0]).days))				
					if dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[2][0],yearly_timestamps[2][1]):
						fpath="{}{}".format(inputpostspath,"Yearly_Shaymin_Land.txt")
						if os.path.isfile(fpath):
							ytxt=""
							with open(fpath,"r") as infile:ytxt=infile.read()
							if len(ytxt)>99:yearlytxt+="\n"+ytxt.replace("<date1>",yearly_timestamps[2][0].strftime("%Y-%m-%d")).replace("<date2>",yearly_timestamps[2][1].strftime("%Y-%m-%d")).replace("<date3>","{}".format(abs(yearly_timestamps[2][1]-yearly_timestamps[2][0]).days))
				if dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[4][0],yearly_timestamps[4][1]):
					fpath="{}{}".format(inputpostspath,"Yearly_Spooky.txt")
					if os.path.isfile(fpath):
						ytxt=""
						with open(fpath,"r") as infile:ytxt=infile.read()
						if len(ytxt)>99:yearlytxt+="\n"+ytxt.replace("<date1>",yearly_timestamps[4][0].strftime("%Y-%m-%d")).replace("<date2>",yearly_timestamps[4][1].strftime("%Y-%m-%d")).replace("<date3>","{}".format(abs(yearly_timestamps[4][1]-yearly_timestamps[4][0]).days))
				if dates_interval_match(timestamps[0],timestamps[1],yearly_timestamps[5][0],yearly_timestamps[5][1]):
					fpath="{}{}".format(inputpostspath,"Yearly_Holiday.txt")
					if os.path.isfile(fpath):
						ytxt=""
						with open(fpath,"r") as infile:ytxt=infile.read()
						if len(ytxt)>99:yearlytxt+="\n"+ytxt.replace("<date1>",yearly_timestamps[5][0].strftime("%Y-%m-%d")).replace("<date2>",yearly_timestamps[5][1].strftime("%Y-%m-%d")).replace("<date3>","{}".format(abs(yearly_timestamps[5][1]-yearly_timestamps[5][0]).days))
				if len(yearlytxt)>99:extra+="##{}\n{}\n---\n".format(yearly_title,yearlytxt)
				automoderator_list.append({"post_header":"#Week {} Events - Cycle {}\n\n*AUTOMATION INFO*: The **[original post]({})** made by {} can contain more details, you should visit it! Notice that some events could be different. If there are errors in the post, please contact /u/Sky-17.\n\n---\n".format(week_num+1,loop_cycles_ended+[1,2][tdata["skip_current_cycle"]],tdata["link"],tdata["author"]),
					"wiki_header":"#Week {} Events\n".format(week_num+1),
					"txt":txt,"extra":extra,"week":week_num,"type":1,"timestamp":start_time,
					"post_title":"Week {} Events - Cycle {}".format(week_num+1,loop_cycles_ended+[1,2][tdata["skip_current_cycle"]])})
	for i in range(first_weekly_index,len(automoderator_list)):
		next_week=[automoderator_list[i]["week"]+1,0][automoderator_list[i]["week"]==23]
		if automoderator_list[first_weekly_index+next_week]["week"]==next_week:
			allnexttxt=automoderator_list[first_weekly_index+next_week]["txt"]+automoderator_list[first_weekly_index+next_week]["extra"]
			title_matches=header_weekly_title_regex.findall(allnexttxt)
			try:yearly_event_index=title_matches.index(yearly_title)
			except:yearly_event_index=999
			dailycount=0
			great_challenges_indexes=[]
			great_challenges_names=[]
			for j,t in enumerate(title_matches[yearly_event_index+1:]):title_matches[yearly_event_index+1+j]="**[Yearly]** "+t
			for j,t in enumerate(title_matches):
				if t.lower().startswith("great challenge:"):
					great_challenges_indexes.append(j)
					great_challenges_names.append(t[17:])
			nexttxt=""
			excluding_titles=["old events","weekly events","weekly guide for newbies (recap)","expected heart/coin requirement for farming","monthly events",yearly_title.lower(),"next week events"]
			for j,t in enumerate(title_matches):
				if len([1 for et in excluding_titles if et in t.lower()])>0:continue
				nev=re.sub("\[([^\]]+)]\([^\)]+\)","\\1",t)
				if next_week==0 and "[Yearly]" in nev:continue
				elif "daily pok" in t.lower() or "safari" in t.lower():
					rowid=[1,0]["safari" in t.lower()]
					elemoff=[1,0][rowid==1]
					tsearch=["Daily Pok","Safari"]["safari" in t.lower()]
					try:
						start_off=allnexttxt.find(tsearch)
						if rowid==1:
							if dailycount>0:
								allnexttxt=allnexttxt[start_off+10:]
								start_off=allnexttxt.find(tsearch)
							dailycount+=1
					except:start_off=-1
					try:end_off=start_off+allnexttxt[start_off:].find("Drop Rate")
					except:end_off=-1
					if start_off>=0 and end_off>=0:nev+=": {}".format(", ".join([r[rowid] for r in daily_safari_table_regex.findall(allnexttxt[start_off:end_off])[elemoff:]]))
				elif len(great_challenges_indexes)>0:
					if j==great_challenges_indexes[0]:nev="Great Challenges: {}".format(", ".join(great_challenges_names))
					elif j in great_challenges_indexes:continue
				else:nev=t
				nexttxt+="- {}\n".format(nev)
			automoderator_list[i]["extra"]+="\n##Next Week Events\n\n{}\n---\n".format(nexttxt)
	automoderator_list=sorted(automoderator_list,key=lambda x:x["week"])
	if not os.path.isdir(outputpostspath):os.mkdir(outputpostspath)
	if loop_cycles_ended==cycles_ended:
		eb_txt=""
		comp_txt=""
		for am in automoderator_list:
			if am["type"]==2:eb_txt+="{}\n---\n---\n---\n".format(am["wiki_header"]+am["txt"])
			elif am["type"]==3:comp_txt+="{}\n---\n---\n---\n".format(am["wiki_header"]+am["txt"])
		with open("{}{}".format(outputpostspath,"ebs-schedule.txt"),"w") as infile:txt=infile.write(eb_txt)
		with open("{}{}".format(outputpostspath,"competitions-schedule.txt"),"w") as infile:txt=infile.write(comp_txt)
	automoderator_list=sorted(automoderator_list,key=lambda x:(x["timestamp"],-x["type"]))
	automoderator_txt="##If you edit this page, you must [visit this link, then click \"send\"](http://www.reddit.com/message/compose/?to=AutoModerator&subject=PokemonShuffle&message=schedule) to have AutoModerator re-load the schedule!\n"
	fpath="{}{}".format(inputpostspath,"Automoderator-schedule-original.txt")
	if os.path.isfile(fpath):
		with open(fpath,"r") as infile:automoderator_txt+="\n"+infile.read()
	for am in automoderator_list:
		automoderator_txt+="\n---\n{}first: \"{}\"\n".format(automoderator_indentation,datetime.datetime.fromtimestamp(am["timestamp"]+automoderator_hours_offset*3600).strftime("%Y-%m-%d %H:%M"))
		if "repeat" in am.keys() and len(am["repeat"])>3:automoderator_txt+="{}repeat: {}\n".format(automoderator_indentation,am["repeat"])# Repeat currently not used
		automoderator_txt+="{}link_flair_text: All\n{}link_flair_class: al\n{}title: \"{}\"\n{}text: |\n{}".format(automoderator_indentation,automoderator_indentation,automoderator_indentation,am["post_title"],automoderator_indentation,"\n".join([automoderator_indentation+automoderator_indentation+t for t in (am["post_header"]+am["txt"]+am["extra"]).replace("\n\n\n","\n\n").replace("---\n\n","---\n").strip().split("\n")]))
	with open("{}{}".format(outputpostspath,"automoderator-schedule-cycle-{}.txt".format(loop_cycles_ended+1)),"w") as infile:txt=infile.write(automoderator_txt)
	competition_title_prefix='title: "Mega '
	entry_separator="\n---\n"
	competitions_titles_count=automoderator_txt.count(competition_title_prefix)
	automoderator_txt_fixed=entry_separator.join(automoderator_txt[:findnth(automoderator_txt,competition_title_prefix,0)].split(entry_separator)[:-1])
	toffset=len(automoderator_txt_fixed)
	tcompetitions_offset=2*competitions_titles_count//3+1
	automoderator_txt_first_half=automoderator_txt_fixed+entry_separator.join(automoderator_txt[toffset:][:findnth(automoderator_txt[toffset:],competition_title_prefix,tcompetitions_offset)].split(entry_separator)[:-1])
	automoderator_txt_second_half=automoderator_txt_fixed+entry_separator.join(automoderator_txt[toffset-99:][findnth(automoderator_txt[toffset:],competition_title_prefix,competitions_titles_count-tcompetitions_offset):].split(entry_separator)[:])
	with open("{}{}".format(outputpostspath,"automoderator-schedule-cycle-{}-1st-half-update-on-week-24.txt".format(loop_cycles_ended+1)),"w") as infile:txt=infile.write(automoderator_txt_first_half)
	with open("{}{}".format(outputpostspath,"automoderator-schedule-cycle-{}-2nd-half-update-on-week-{}-{}.txt".format(loop_cycles_ended+1,(competitions_titles_count-tcompetitions_offset)*2+1,tcompetitions_offset*2)),"w") as infile:txt=infile.write(automoderator_txt_second_half)
	print("Ready for cycle {:d}! Check files inside folder {}".format(loop_cycles_ended+1,outputpostspath))
