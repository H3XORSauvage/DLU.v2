import os
import sys
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QProgressBar
from PyQt5.QtCore import Qt

class RechercheDBApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dossier_parent = ''

    def initUI(self):
        self.setWindowTitle('DLU - V2.4')
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

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setStyleSheet("background-color: #1a1d21; color: #ffffff;")
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.progress_label = QLabel("Prêt")
        self.progress_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.progress_label)

        self.setLayout(layout)

    def update_text(self, text):
        self.resultats_text.append(text)
        QApplication.processEvents()


    def choisir_dossier(self):
        self.dossier_parent = QFileDialog.getExistingDirectory(self, "Choisir le dossier principal")

    def lancer_recherche(self):
        batabase = self.batabase_input.text()
        if self.dossier_parent and batabase:
            self.resultats_text.clear()
            self.progress_bar.setValue(0)
            try:
                self.progress_label.setText("Recherche en cours...")
                QApplication.processEvents()
                self.dossiersDb_recherche(self.dossier_parent, batabase)
                self.progress_label.setText("Recherche terminée")
            except Exception as e:
                self.resultats_text.setText(f"Erreur lors de la recherche: {str(e)}")
        else:
            self.resultats_text.setText("Veuillez sélectionner un dossier et entrer un Id,Ip,Steamid....")

    def afficher_resultat(self, nom_fichier, ligne_numero, ligne):
        self.resultats_text.append(f"<span style='color:green'><b>[NEW]</b></span> {nom_fichier}, ligne {ligne_numero}: {ligne.strip()}")
        self.resultats_text.append(f"    {ligne}\n \n")
        QApplication.processEvents()

    def recherche_DB(self, nom_fichier, batabase):
        resultats = []
        encodings = ['utf-8', 'latin-1']

        for encoding in encodings:
            try:
                if nom_fichier.endswith('.csv'):
                    with open(nom_fichier, 'r', encoding=encoding) as fichier:
                        lecteur = csv.reader(fichier)
                        for index, ligne in enumerate(lecteur, start=1):
                            if any(batabase in champ for champ in ligne):
                                resultats.append((nom_fichier, index, ' | '.join(ligne)))
                                self.afficher_resultat(nom_fichier, index, ' | '.join(ligne))
                else:
                    with open(nom_fichier, 'r', encoding=encoding) as fichier:
                        for index, ligne in enumerate(fichier, start=1):
                            if batabase in ligne:
                                resultats.append((nom_fichier, index, ligne.strip()))
                                self.afficher_resultat(nom_fichier, index, ligne.strip())
                break
            except UnicodeDecodeError as e:
                if encoding == encodings[-1]:
                    self.resultats_text.append(f"Erreur lors de la lecture de {nom_fichier}: {str(e)}\n")
            except Exception as e:
                self.resultats_text.append(f"Erreur lors de la lecture de {nom_fichier}: {str(e)}\n")
                break

        return resultats

    def dossiersDb_recherche(self, dossier_parent, batabase):
        resultats = []
        extensions_autorisees = ['.txt', '.sql', '.csv']
        fichiers_a_traiter = []
        max_threads = min(32, os.cpu_count())

        for dossier_racine, _, fichiers in os.walk(dossier_parent):
            for nom_fichier in fichiers:
                if any(nom_fichier.endswith(ext) for ext in extensions_autorisees):
                    chemin_fichier = os.path.join(dossier_racine, nom_fichier)
                    fichiers_a_traiter.append(chemin_fichier)

        self.progress_bar.setMaximum(len(fichiers_a_traiter))
        self.progress_bar.setValue(0)

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(self.recherche_DB, fichier, batabase): fichier for fichier in fichiers_a_traiter}
            for future in as_completed(futures):
                self.progress_bar.setValue(self.progress_bar.value() + 1)
                fichier = futures[future]
                self.progress_label.setText(f"Traitement de {os.path.basename(fichier)}...")
                QApplication.processEvents()

                try:
                    resultats.extend(future.result())
                except Exception as e:
                    print(f"Erreur lors du traitement du fichier {fichier}: {str(e)}")

        return resultats

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = RechercheDBApp()
    ex.show()
    sys.exit(app.exec_())
