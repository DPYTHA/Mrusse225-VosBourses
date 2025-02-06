from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Charger les variables d'environnement (si nécessaire)
load_dotenv()

app = Flask(__name__)
app.secret_key =  "a3b1c9d8e7f6g5h4i3j2k1l0m9n8o7p6" # Clé secrète pour les notifications flash

# 📧 Configuration Flask-Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "pythamoua@gmail.com")  # Ton adresse e-mail
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "dpfxmjvvnawpnrzq")  # Mot de passe ou App Password
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)

# 📁 Dossier de stockage des fichiers uploadés
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crée le dossier si inexistant


@app.route("/")
def index():
    return render_template("Formulaire.html")

@app.route('/entrance')
def entrance():
    return render_template('entrance.html')


@app.route("/upload", methods=["POST"])
def upload():
    try:
        # ✅ Récupération des données utilisateur
        prenom = request.form["prenom"]
        nom = request.form["nom"]
        email = request.form["email"]
        telephone = request.form["telephone"]

        contact_nom = request.form["contact_nom"]
        contact_prenom = request.form["contact_prenom"]
        contact_naissance = request.form["contact_naissance"]
        contact_lien = request.form["contact_lien"]
        contact_telephone = request.form["contact_telephone"]
        contact_email = request.form["contact_email"]

        # 📁 Récupération des fichiers
        fichiers = {}
        for file_key in ["passeport", "diplome", "releves"]:
            file = request.files.get(file_key)
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                fichiers[file_key] = filepath

        # 📧 Envoi de l'e-mail à l'administrateur
        subject_admin = f"Nouveau formulaire soumis par {prenom} {nom}"
        body_admin = f"""
        Nom : {nom}
        Prénom : {prenom}
        E-mail : {email}
        Téléphone : {telephone}

        📌 Contact d'urgence :
        Nom : {contact_nom}
        Prénom : {contact_prenom}
        Date de naissance : {contact_naissance}
        Lien parental : {contact_lien}
        Téléphone : {contact_telephone}
        E-mail : {contact_email}
        """

        msg_admin = Message(subject_admin, recipients=["pythamoua@gmail.com"])
        msg_admin.body = body_admin

        # 📎 Ajout des fichiers en pièce jointe
        for file_key, filepath in fichiers.items():
            with open(filepath, "rb") as f:
                msg_admin.attach(os.path.basename(filepath), "application/octet-stream", f.read())

        mail.send(msg_admin)

        # 📧 Envoi d'un e-mail de confirmation à l'utilisateur
        subject_user = "Confirmation de votre soumission"
        body_user = f"""
        Bonjour {prenom},

        Nous avons bien reçu votre formulaire ainsi que vos documents.
          Notre équipe va examiner votre dossier.Nous pouvons vous demander des documents supplementaires
          via whatssap
        Merci de nous faire confiance.
        visitez notre site internet https://flaskblock.onrender.com/

        Cordialement,
        L'équipe de support
        """

        msg_user = Message(subject_user, recipients=[email])
        msg_user.body = body_user
        mail.send(msg_user)

        # ✅ Afficher un message de succès
        flash("Votre formulaire a été envoyé avec succès ! Vous recevrez un e-mail de confirmation.", "success")
        return redirect(url_for("index"))

    except Exception as e:
        flash(f"Une erreur s'est produite : {str(e)}", "error")
        return redirect(url_for("Formulaire"))


if __name__ == "__main__":
    app.run(debug=True)
