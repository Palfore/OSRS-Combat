from osrsmath.apps.optimize.gui_single import Ui_MainWindow
from pathlib import Path

from osrsmath.model.player import Player, get_equipment_data
from pprint import pprint as pp
from PyQt5 import QtCore, QtGui, QtWidgets

DATA_PATH = Path().absolute() / 'data'

class GUI(Ui_MainWindow):
	def setupUi(self, MainWindow):
		super().setupUi(MainWindow)
		self.load_defaults()
		self.monster_panel.add.clicked.connect(self.add_monster)
		self.optimize_panel.evaluate.clicked.connect(self.on_evaluate)

		self.optimize_panel.xp_rate.setStyleSheet("color: white;")
		self.optimize_panel.attack_stance.setStyleSheet("color: white;")

		import textwrap
		self.menuHelp.triggered.connect(lambda: QtWidgets.QMessageBox(
			QtWidgets.QMessageBox.Information,
			'Help - Overview',

			textwrap.dedent("""\
			This app allows you to determine the optimal equipment to wear against a set of opponents.

			There are three main sections:
			  1. Player (top left):
			      a) Enter combat levels. Prompts appear if others are needed.
			      b) Ignore equipment you don't want to consider.
			      c) Adjust equipment requirements (if inaccurate or self-imposed)

			  2. Monster (bottom left):
			      a) Lookup by name and (crudely) filter by NMZ bosses.
			      b) If inaccurate or cannot be found, modify values.

			  3. Optimize (right)
			      a) View fighting pool (ie. multiple enemies - useful for NMZ)
			      b) Choose training skill
			      c) Choose potions and how you use them.
			      d) Choose prayers (always on).
			      == Output ==
			      e) Optimal equipment (dropdowns are for possible future use).
			      f) Attack stance, xp/h, and offensive bonuses are also shown.

			Note that there are a lot of exceptions in this game, so the interface is designed to have slack.
			""")
		).exec())



		# self.on_evaluate()

	def add_monster(self):
		name = self.monster_panel.custom_name.text()
		if name:
			self.optimize_panel.add_monster(name, self.monster_panel.get_monster_as_dict())

	def update_status(self, message):
		self.MainWindow.statusBar().showMessage(message)

	def on_evaluate(self):
		from osrsmath.apps.optimize.logic.optimize import get_sets, get_best_set, load_opponent
		from osrsmath.model.monsters import Monster
		from osrsmath.model.boosts import BoostingSchemes, Prayers, Potions
		import time

		try:
			equipment_data = get_equipment_data()
			monsters = {name: Monster(**m) for name, m in self.optimize_panel.data.monsters.items()}
			if not monsters:
				QtWidgets.QMessageBox(
					QtWidgets.QMessageBox.Warning, 'Invalid Number of Monsters', "You haven't selected enough monsters."
				).exec()
				return

			training_skill = self.optimize_panel.get_training_skill()
			stats = self.player_panel.get_stats()
			ignore = self.ignore_adjust_panel.get_ignore()
			adjust = self.ignore_adjust_panel.get_adjust()

			potion = getattr(Potions, self.optimize_panel.potions.currentText())
			potion_attributes = self.optimize_panel.potion_attributes.currentText()

			prayer = getattr(Prayers, self.optimize_panel.prayers.currentText())
			prayer_attributes = self.optimize_panel.prayer_attributes.currentText()

			if self.optimize_panel.boosting_scheme.currentText() == 'Dose After':
				skill = self.optimize_panel.below_skill.currentText()
				redose_level = int(self.optimize_panel.redose_level.text())
				boost = lambda p: BoostingSchemes(p, prayer, prayer_attributes).potion_when_skill_under(
					potion, skill, redose_level, potion_attributes
				)
			else:
				boost = lambda p: BoostingSchemes(p, prayer, prayer_attributes).constant(potion, potion_attributes)



			t0 = time.time()
			self.update_status(f'Step (1/2). Generating Sets...')
			sets = get_sets(stats, monsters, ignore, adjust, equipment_data)#progress_callback=lambda i: self.optimize_panel.progressBar.setValue(i))
			self.update_status(f'Step (2/2). Evaluating {len(sets)} Sets...')
			s, xp, stance = get_best_set(
				stats,
				training_skill,
				boost,
				monsters,
				sets,
				include_shared_xp=False,
				progress_callback=lambda i: self.optimize_panel.progressBar.setValue(i)
			)

			t1 = time.time()
			self.update_status('Finished ...')
			print(f"Solved in {t1-t0:.2f}s using {len(sets)} sets.")

			player = Player({})
			for slot, item_name in s.items():
				player.equip_by_name(item_name)
			stats = player.get_stats()

			tab = self.optimize_panel.best_in_slot_bonuses

			# tab.verticalHeaderItem(0).text().lower()
			tab.setItem(0, 0, QtWidgets.QTableWidgetItem(str(stats['attack_stab'])))
			tab.setItem(1, 0, QtWidgets.QTableWidgetItem(str(stats['attack_slash'])))
			tab.setItem(2, 0, QtWidgets.QTableWidgetItem(str(stats['attack_crush'])))
			tab.setItem(3, 0, QtWidgets.QTableWidgetItem(str(stats['attack_ranged'])))
			tab.setItem(4, 0, QtWidgets.QTableWidgetItem(str(stats['attack_magic'])))
			tab.setItem(5, 0, QtWidgets.QTableWidgetItem(str(stats['melee_strength'])))
			tab.setItem(6, 0, QtWidgets.QTableWidgetItem(str(stats['ranged_strength'])))
			tab.setItem(7, 0, QtWidgets.QTableWidgetItem(str(stats['magic_damage'])))
			tab.setItem(8, 0, QtWidgets.QTableWidgetItem(str(stats['attack_speed'])))
			tab.setItem(9, 0, QtWidgets.QTableWidgetItem(str("Not Supported")))

			slots = ['head', 'cape', 'neck', 'ammo', 'weapon', 'body', 'shield', 'legs', 'hands', 'feet', 'ring']
			for slot in slots:
				equipment_list = getattr(self.optimize_panel, slot)
				equipment_list.clear()
				if slot == 'weapon':
					equipment_list.addItem(s.get('weapon') if 'weapon' in s else s.get('2h'))
				else:
					equipment_list.addItem(s.get(slot))

			self.optimize_panel.xp_rate.setText(f"{xp/1000:,.2f}k")
			self.optimize_panel.attack_stance.setText(f"{stance}")

			# pp(sets)
			print(s, xp, stance)
			self.update_status('')
		except Exception as e:
			import traceback
			tb = traceback.format_exc()
			print(e)
			print(tb)
			self.update_status('Error Encountered')
			QtWidgets.QMessageBox(
				QtWidgets.QMessageBox.Critical,
				'Error Encountered',
				f"{e}\n{tb}"
			).exec()

	def load_defaults(self):
		self.player_panel.import_defaults(DATA_PATH/'player.json')
		self.ignore_adjust_panel.import_defaults(DATA_PATH/'ignore.json')
		self.optimize_panel.import_defaults(DATA_PATH/'monsters.json')

		self.ignore_adjust_panel.set_text(self.ignore_adjust_panel.get_checked('data').get())

	def save_defaults(self):
		self.player_panel.export_defaults(DATA_PATH/'player.json')
		self.ignore_adjust_panel.export_defaults(DATA_PATH/'ignore.json')
		self.optimize_panel.export_defaults(DATA_PATH/'monsters.json')


if __name__ == '__main__':
	from osrsmath.apps.GUI.shared.application import run
	run(GUI)