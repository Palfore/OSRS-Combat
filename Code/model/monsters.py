""" This file provides an interface for non-playable characters (aka monsters) through the Monster class.
	In addition, several function are provided to load details about monsters.

	Note that at this point, there are a few assumptions / restrictions:
		1) Assume Melee combat. For simplicity, melee combat is first to be modeled.
		      later on, the other combat styles will be added.
		2) Be careful about loading by name, since multiple monsters might have the same name.
		        More likely, the same monster may have different forms that are stored separately.
		        Verify the stats with the wiki to ensure you have the correct model.
		        Perhaps a "by_wiki_url" method would be helpful.
		3) I do not know what the "attack_accuracy" property does or how it factors into combat.
		        I am ignoring it.
		4) The listed style is sometimes "melee" (instead of slash, stab, crush). I'm not sure how to
		        interpret this. I assume crush because the monsters I've seen with this use their fist.
"""
from pprint import pprint
import requests
import json
import os

from . import damage

MONSTER_LIST_BASE_URL = "https://raw.githubusercontent.com/osrsbox/osrsbox-db/master/docs"

def get_monster_data(force_update=False):
	file_name = f'monsters-complete.json'
	file_path = os.path.join('data', file_name)
	if not os.path.exists(file_path) or force_update:
		r = requests.get(os.path.join(MONSTER_LIST_BASE_URL, file_name))
		with open(file_path, 'w') as f:
			f.write(r.text)

	with open(file_path, 'r') as f:
		 return json.load(f)

def get_monster_by_id(id, monster_data=None):
	if monster_data is None:
		monster_data = get_monster_data()

	for item_id, data in monster_data.items():
		if int(item_id) == int(id):
			return data
	raise ValueError(f"monster with id {id} could not be found.")

def get_monster_by_name(name, monster_data=None):
	if monster_data is None:
		monster_data = get_monster_data()
	for item_id, data in monster_data.items():
		if name.lower() == data['name'].lower():
			return data
	raise ValueError(f"monster with name {name} could not be found.")

def filter_monster(data):
	if data is None:
		return None
	features_to_collect = [
		'name', 'id', 'combat_level', 'size',
		'attack_level', 'ranged_level', 'strength_level', 'defence_level', 'hitpoints', 'magic_level',
		'attack_crush', 'attack_magic', 'attack_ranged', 'attack_slash',  'attack_stab',
		'defence_crush', 'defence_magic', 'defence_ranged', 'defence_slash', 'defence_stab',
		'melee_strength', 'ranged_strength', 'attack_speed', 'attack_type', 'magic_damage',
		'poisonous', 'immune_poison', 'immune_venom', 'weakness',
		'attack_accuracy', 'max_hit',
	]
	filtered_data = {feature: data[feature] for feature in features_to_collect}
	filtered_data['attack_speed'] *= 0.6  # Convert attack_speed into [attacks/second]
	return filtered_data


class Monster:
	@staticmethod
	def from_id(id, monster_data=None):
		data = filter_monster(get_monster_by_id(id, monster_data))

		level_names = ['attack_level', 'ranged_level', 'strength_level', 'defence_level', 'hitpoints', 'magic_level']
		stat_names = ['attack_crush', 'attack_magic', 'attack_ranged', 'attack_slash',  'attack_stab',
				'defence_crush', 'defence_magic', 'defence_ranged', 'defence_slash', 'defence_stab',
				'melee_strength', 'ranged_strength', 'magic_damage', 'attack_speed']

		levels = {level.replace('_level', ''): data[level] for level in level_names}
		monster = Monster(levels)
		monster.stats = {stat: data[stat] for stat in stat_names}
		monster.other = {name: data[name] for name in data.keys() if name not in (level_names+stat_names)}

		assert len(data['attack_type']) == 1, f"Cannot handle multiple attack types for monster with id {id}"
		attack_type = data['attack_type'][0]

		# I'm assuming 'melee' means crush, it might be an average or something like that.
		# This assumption is okay for now, since their offensive capabilities are important yet.
		monster.attack_style = 'crush' if attack_type == 'melee' else attack_type
		return monster

	def from_name(name, monster_data=None):
		id = get_monster_by_name(name, monster_data)['id']
		return Monster.from_id(id, monster_data)

	def __init__(self, levels):
		self.levels = levels
		self.stats = {
			'attack_stab': 0,
			'attack_slash': 0,
			'attack_crush': 0,
			'attack_magic': 0,
			'attack_ranged': 0,
			'defence_stab': 0,
			'defence_slash': 0,
			'defence_crush': 0,
			'defence_magic': 0,
			'defence_ranged': 0,
			'melee_strength': 0,
			'ranged_strength': 0,
			'magic_damage': 0,
			'attack_speed': 2.4
		}
		self.attack_style = None

	def get_max_hit(self, strength_potion_boost, strength_prayer_boost, strength_other_boost, multiplier, using_special=False):
		raise NotImplementedError("Max hit for monsters has not been implemented")

	def get_attack_roll(self, attack_potion_boost, attack_prayer_boost, attack_other_boost, multiplier, using_special=False):
		raise NotImplementedError("Max hit for monsters has not been implemented")

	def get_defence_roll(self, attacker_attack_type, defence_potion_boost, defence_prayer_boost, defence_other_boost, multiplier, using_special=False):
		assert not using_special, "Special attacks are not yet implemented"
		# Assumes the opponent is using melee
		return damage.Melee().max_defence_roll(
			self.stats['defence_' + attacker_attack_type],
			self.levels['defence'],
			0,
			1,
			1,
			1,
			1,
		)

	def get_accuracy(self, attack_roll, opponent_defence_roll):
		return damage.Melee().accuracy(attack_roll, opponent_defence_roll)


if __name__ == '__main__':
	data = get_monster_data()


	# # for i in data.keys():
	# # 	count_draynor = get_monster_by_id(i, data)
	# # 	# pprint(count_draynor)
	# # 	pprint(filter_monster(count_draynor))
	# pprint(filter_monster(get_monster_by_name("Count Draynor")))


	# # defender = Monster({'attack': 30, 'strength': 25, 'defence': 30, 'prayer': 1, 'hitpoints': 35, 'magic': 1, 'ranged': 1})
	# # defender.stats['defence_stab'] = 2
	# # defender.stats['defence_slash'] = 1
	# # defender.stats['defence_crush'] = 3
	# # defender.attack_style = 'crush'
	# defender = Monster.from_name("Black Demon (hard)")
	# D = defender.get_defence_roll(attacker.get_stances()[attacker.combat_style]['attack_type'], 0, 1, 1)
	# a = defender.get_accuracy(A, D)
	# print(m, A, D, a)

	# Use this to check you have the correct id for the monster you want.
	defender = Monster.from_id(8042)
	pprint(defender.levels)
	pprint(defender.stats)
	pprint(defender.other)
	print(defender.get_defence_roll('slash', 0, 1, 1, 1))
	print('='*10)
	exit()





















