from osrsmath.general.player import Player
import osrsmath.combat.boosts as boosts
import osrsmath.combat.damage as damage
from osrsmath.combat.equipment import Loadout
from osrsmath.combat.special import SPECIAL_EQUIPMENT
from math import floor
from typing import Optional

def bonus_to_triangle(attack_bonus: str):
	""" Converts the attack bonus to the corresponding combat triangle. 

	See source for more details.

	Args:
		attack_bonus: One of stab, slash, crush, ranged, magic.
			or "defensive casting"

	Returns:
		One of melee, ranged, magic.
	"""
	return {
		'stab': 'melee',
		'slash': 'melee',
		'crush': 'melee',
		'ranged': 'ranged',
		'magic': 'magic',
	}[attack_bonus]

def stance_to_style(combat_type: str, stance: dict):
	""" Returns the equipment bonus name of the current stance. 
	
	Returns:
		One of stab, slash, crush, magic, ranged
	"""
	if combat_type in ('ranged', 'magic'):
		return combat_type
	return stance['attack_type']


class Fighter(Player):
	def __init__(self, potion_policy=None):
		self.loadout = Loadout()
		self.stance = None
		self.spell = None

	def set_stance(self, stance: str):
		""" Sets the attack stance.
		
		Raises:
			ValueError If `stance` is not part of `Fighter(..).equipment.stances`.
		"""
		stances = self.loadout.stances
		if stance not in stances:
			raise ValueError(f'''{stance} not a valid stance for the weapon "{self.loadout.gear['weapon']}". Try one of: {list(stances.keys())}.''')
		self.stance = stance


class Fighter(Player):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.loadout = Loadout()
		self.stance = None
		self.spell = None

	def set_stance(self, stance: str):
		""" Sets the attack stance.
		
		Raises:
			ValueError If `stance` is not part of `Fighter(..).equipment.stances`.
		"""
		stances = self.loadout.stances
		if stance not in stances:
			raise ValueError(f'''{stance} not a valid stance for the weapon "{self.loadout.gear['weapon']}". Try one of: {list(stances.keys())}.''')
		self.stance = stance

	def set_spell(self, spell: Optional[str]=None):
		""" Sets the attack spell.

		None will clear the spell.
		"""
		self.spell = spell

	def get_combat_type(self):  # rename to combat class
		""" Returns Melee, Ranged, or Magic based on experience gained.
	
		Raises:
			ValueError if the current stance is not set. See `Fighter.set_stance`.

		Returns:
			One of melee, ranged, magic
		"""
		stances = self.loadout.stances
		if self.stance is None:
			raise ValueError('The current stance is None, did you forget to set the stance by using Fighter.set_stance()?')
		if 'ranged' in stances[self.stance]['experience']:
			return 'ranged'
		if 'magic' in stances[self.stance]['experience']:
			return 'magic'
		return bonus_to_triangle(stances[self.stance]['attack_type'])

	def get_attack_style(self):
		""" Returns the equipment bonus name of the current stance. 
		
		Returns:
			One of stab, slash, crush, magic, ranged
		"""
		return stance_to_style(self.get_combat_type(), self.loadout.stances[self.stance])

	def get_attack_speed(self):
		attack_speed = self.loadout.attack_speed
		boost = self.loadout.stances[self.stance]['boosts']
		if boost == 'attack speed by 1 tick':
			attack_speed -= 0.6
		return attack_speed

	def get_max_hit(self, potion, prayer, arena):
		combat_class = self.get_combat_type()
		attack_style = 'aggressive' ##
		if combat_class == 'melee':
			equipment_strength_bonus = 12 

			potion_bonus = {
				'Strength potion': int(self.levels['strength']*(10/100) + 3),
				'Super strength potion': int(self.levels['strength']*(15/100) + 5),
				'Overload (+)': int(self.levels['strength']*(16/100) + 6)
			}[potion]

			prayer_bonus = {
				'Burst of Strength': 0.05,
				'Superhuman Strength': 0.10,
				'Ultimate 2': 0.15,
				'Chivalry': 0.18,
				'Piety': 0.23,
			}[prayer]

			style_bonus = {
				'aggressive': 11,
				'controlled': 9
			}.get(attack_style, 8)

			void_bonus = 1.1 if wearing_melee_void else 1
			visable_strength_level = self.levels['strength'] + potion_bonus
			effective_strength = int(int(int(visable_strength_level*prayer_bonus)*style_bonus)*void_bonus)
			m_base = int(0.5 + effective_strength*(64 + equipment_strength_bonus)/640)


		# combat_type = self.get_combat_type()
		# stances = self.loadout.stances
		# if combat_type == 'melee':
		# 	style_bonus = {'aggressive': 3, 'controlled': 1}.get(stances[self.stance]['attack_style'], 0)
		# 	strength = self.levels['strength']
			
		# 	effective_strength = floor(strength + potion(strength))
		# 	effective_strength += {'aggressive': 11, 'controlled': 8}.get(stances[self.stance]['attack_style'], 0)
		# 	for name, special_equipment in SPECIAL_EQUIPMENT.items():
		# 		if special_equipment.applies(arena):
		# 			effective_strength = floor(effective_strength * special_equipment.melee_damage_pre(arena))
			
		# 	base_damage = floor(0.5 + effective_strength * (64 + self.loadout.bonuses.melee_strength)/640)

		# 	for name, special_equipment in SPECIAL_EQUIPMENT.items():
		# 		if special_equipment.applies(arena):
		# 			base_damage = floor(base_damage * special_equipment.melee_damage_post(arena))

		# 	return floor(base_damage)

		# elif combat_type == 'ranged':
		# 	style_bonus = {'accurate': 3}.get(stances[self.stance]['attack_style'], 0)
		# 	ranged = self.levels['ranged']
		# 	other = 1

		# 	if self.is_wearing_void_range:
		# 		other *= 1.1
		# 	if self.is_wearing_elite_void_range:
		# 		other *= 1.125
		# 	if self.is_wearing_slayer_helm:
		# 		other *= 1.15

		# 	effective_strength = floor(
		# 		(ranged + potion(ranged)) * prayer(ranged) * other + style_bonus
		# 	)

		# 	base_damage = sum([
		# 		1.3,
		# 		effective_strength / 10,
		# 		self.loadout.bonuses.ranged_strength / 80,
		# 		effective_strength * self.loadout.bonuses.ranged_strength / 640
		# 	])

		# 	# Ignore dark bow & bolt effects
		# 	if self.is_wearing_twisted_bow:
		# 		M = max(opponent.magic_level, opponent.magic_accuracy)
		# 		D = 250 + (3*M - 14)/100 - (3*M/10 - 100)**2 / 100
		# 		base_damage *= D / 100
		# 	return floor(base_damage)




		# dmg = self.get_damage_parameters()

		# other = boosts.Equipment.none()
		# other.update(boosts.other(self.equipment.get_names(), self))
		# special_attack_bonus = 1  # Special attacks are not implemented
		# multipler = 1  # Ignoring flooring order, since there is no official documentation
		
		# if self.get_combat_type() == 'magic':
		# 	if self.spell is None:
		# 		raise ValueError("The fighter's spell is None, consider using `Fighter.set_spell`.")
		# 	return damage.Magic().max_hit(
		# 		self.spell,
		# 		dmg['offensive_equipment_bonus'],
		# 		self.levels[dmg['offensive_skill']],
		# 		potion(self.levels[dmg['offensive_skill']]),
		# 		prayer(dmg['offensive_skill']),
		# 		other[dmg['offensive_skill']],
		# 		# dmg['offensive_stance_bonus'],
		# 		special_attack_bonus, multipler
		# 	)

		# if self.spell is not None:
		# 	raise ValueError(f"The fighter's spell is '{self.spell}', for {self.get_combat_type()} use `Fighter.set_spell(None)`.")
		# return damage.Standard().max_hit(
		# 	dmg['offensive_equipment_bonus'],
		# 	self.levels[dmg['offensive_skill']],
		# 	potion(self.levels[dmg['offensive_skill']]),
		# 	prayer(dmg['offensive_skill']),
		# 	other[dmg['offensive_skill']],
		# 	dmg['offensive_stance_bonus'],
		# 	special_attack_bonus, multipler
		# )


	def get_damage_parameters(self):
		self.get_attack_style()
		stances = self.equipment.stances
		if self.get_combat_type() == 'melee':
			return {
				'offensive_equipment_bonus': self.equipment.melee_strength,
				'offensive_skill': 'strength',
				'offensive_stance_bonus': {'aggressive': 3, 'controlled': 1}.get(stances[self.stance]['attack_style'], 0),
				'accuracy_equipment_bonus': getattr(self.equipment, 'attack_' + stances[self.stance]['attack_type']),
				'accuracy_skill': 'attack',
				'accuracy_stance_bonus': {'accurate': 3, 'controlled':1}.get(stances[self.stance]['attack_style'], 0),
			}
		elif self.get_combat_type() == 'ranged':
			return {
				'offensive_equipment_bonus': self.equipment.ranged_strength,
				'offensive_skill': 'ranged',
				'offensive_stance_bonus': {'accurate': 3}.get(stances[self.stance]['attack_style'], 0),
				'accuracy_equipment_bonus': self.equipment.attack_ranged,
				'accuracy_skill': 'ranged',
				'accuracy_stance_bonus': {'accurate': 3}.get(stances[self.stance]['attack_style'], 0),
			}
		elif self.get_combat_type() == 'magic':
			return {
				'offensive_equipment_bonus': self.equipment.magic_damage,
				'offensive_skill': 'magic',
				'offensive_stance_bonus': 0,
				'accuracy_equipment_bonus': self.equipment.attack_magic,
				'accuracy_skill': 'magic',
				'accuracy_stance_bonus': 0,
			}
		else:
			raise ValueError("Could not identify combat type")

	def get_attack_roll(self, potion, prayer):
		dmg = self.get_damage_parameters()
		stances = self.equipment.stances

		other = boosts.Equipment.none()
		other.update(boosts.other(self.equipment.get_names(), self))
		multipler = 1  # Ignoring flooring order, since there is no official documentation

		if self.get_combat_type() == 'magic':
			return damage.Magic().max_attack_roll(
				dmg['accuracy_equipment_bonus'],
				self.levels[dmg['accuracy_skill']],
				potion(self.levels[dmg['accuracy_skill']]),
				prayer(dmg['accuracy_skill']),
				other[dmg['accuracy_skill']],
				dmg['accuracy_stance_bonus'],
				multipler
			)
		return damage.Standard().max_attack_roll(
			dmg['accuracy_equipment_bonus'],
			self.levels[dmg['accuracy_skill']],
			potion(self.levels[dmg['accuracy_skill']]),
			prayer(dmg['accuracy_skill']),
			other[dmg['accuracy_skill']],
			dmg['accuracy_stance_bonus'],
			multipler
		)

	def get_defence_roll(self):
		assert False
		# assert not using_special, "Special attacks are not implemented"
		# stats = self.equipment.get_stats()
		# stances = self.equipment.stances

		# other = boosts.Equipment.none()
		# other.update(boosts.other(self.equipment.get_names()))
		# multipler = 1  # Ignoring flooring order, since there is no official documentation
		# if self.get_combat_type() in ('melee', 'ranged'):
		# 	return damage.Standard().max_defence_roll(
		# 		stats['defence_' + attacker_attack_type],
		# 		self.levels['defence'],
		# 		potion(self.levels['defence']),
		# 		prayer('defence'),
		# 		other['defence'],
		# 		{'longrange': 3, 'defensive': 3, 'controlled': 1,}.get(stances[self.combat_style]['attack_style'], 0),
		# 		multipler
		# 	)
		# elif self.get_combat_type() == 'magic':
		# 	raise ValueError("Magic defence roll is not supported")
		# else:
		# 	raise ValueError("Could not identify combat type")



if __name__ == '__main__':
	from pprint import pprint
	from osrsmath.combat.boosts import Potions, Prayers
	
	fighter = Fighter({'attack': 70, 'strength': 99, 'defence': 70, 'ranged': 70})
	fighter.loadout.wear(
		'Dragon sword', 'Void melee helm', 'Void knight top', 'Void knight robe', 'Void knight gloves', 'fire cape'
	)
	fighter.set_stance('lunge')

	arena = Arena(fighter, None)
	print(fighter.get_max_hit(Potions.none, Prayers.none, arena))
