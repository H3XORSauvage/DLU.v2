print("Just try to avoid skid...")
import os
import sys
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
from PyQt5.QtGui import QColor

class RechercheDBApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dossier_parent = ''

    def initUI(self):
        self.setWindowTitle('Tool By Saucisson')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1a2b3c; color: #333333;")

        layout = QVBoxLayout()

        input_layout = QHBoxLayout()

        self.batabase_input = QLineEdit(self)
        self.batabase_input.setPlaceholderText("Entrez la db à rechercher")
        self.batabase_input.setStyleSheet("background-color: #ffffff; color: #333333;")

        self.dossier_button = QPushButton("Choisir Dossier (Db/database)", self)
        self.dossier_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.dossier_button.clicked.connect(self.choisir_dossier)

        self.rechercher_button = QPushButton("Rechercher", self)
        self.rechercher_button.setStyleSheet("background-color: #008CBA; color: white;")
        self.rechercher_button.clicked.connect(self.lancer_recherche)

        input_layout.addWidget(QLabel("Data:"))
        input_layout.addWidget(self.batabase_input)
        input_layout.addWidget(self.dossier_button)
        input_layout.addWidget(self.rechercher_button)

        self.resultats_text = QTextEdit(self)
        self.resultats_text.setReadOnly(True)
        self.resultats_text.setStyleSheet("background-color: #1a1d21; color: #ffffff;")

        layout.addLayout(input_layout)
        layout.addWidget(self.resultats_text)

        self.setLayout(layout)

    def choisir_dossier(self):
        self.dossier_parent = QFileDialog.getExistingDirectory(self, "Choisir le dossier principal")

    def lancer_recherche(self):
        batabase = self.batabase_input.text()
        if self.dossier_parent and batabase:
            self.resultats_text.clear()
            try:
                resultats = self.dossiersDb_recherche(self.dossier_parent, batabase)
                if resultats:
                    for nom_fichier, ligne_numero, ligne in resultats:
                        self.resultats_text.append(f"<span style='color:green'><b>[NEW]</b></span> {nom_fichier}, ligne {ligne_numero}: {ligne.strip()}")
                        self.resultats_text.append(f"    {ligne}\n \n")
                else:
                    self.resultats_text.setText(f"Aucune Db trouvée pour '<b>{batabase}</b>'.")
            except Exception as e:
                self.resultats_text.setText(f"Erreur lors de la recherche: {str(e)}")
        else:
            self.resultats_text.setText("Veuillez sélectionner un dossier et entrer un Id,Ip,Steamid....")

    def recherche_DB(self, nom_fichier, batabase):
        resultats = []
        try:
            if nom_fichier.endswith('.csv'):
                with open(nom_fichier, 'r', encoding='utf-8') as fichier:
                    lecteur = csv.reader(fichier)
                    for index, ligne in enumerate(lecteur, start=1):
                        if any(batabase in champ for champ in ligne):
                            resultats.append((nom_fichier, index, ' | '.join(ligne)))
            else:
                with open(nom_fichier, 'r', encoding='utf-8') as fichier:
                    for index, ligne in enumerate(fichier, start=1):
                        if batabase in ligne:
                            resultats.append((nom_fichier, index, ligne.strip()))
        except Exception as e:
            resultats.append((nom_fichier, 0, f"Erreur lors de la lecture: {str(e)}"))
        return resultats

    def dossiersDb_recherche(self, dossier_parent, batabase):
        resultats = []
        exten = ['.txt', '.sql', '.csv']
        for dossier_racine, _, fichiers in os.walk(dossier_parent):
            for nom_fichier in fichiers:
                if any(nom_fichier.endswith(ext) for ext in exten):
                    chemin_fichier = os.path.join(dossier_racine, nom_fichier)
                    resultats.extend(self.recherche_DB(chemin_fichier, batabase))
        return resultats

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = RechercheDBApp()
    ex.show()
    sys.exit(app.exec_())
