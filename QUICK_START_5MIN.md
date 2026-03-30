# ⚡ DÉMARRAGE EN 5 MINUTES

Lancer CTAMS maintenant!

---

## Step 1️⃣: Préparer (1 min)

```bash
cd atelierProjet
```

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

---

## Step 2️⃣: Créer utilisateur (1 min)

```bash
cd src
python manage.py createsuperuser
```

Entrez:
- Email: `admin@ctams.fr`
- Password: `votre_choix` (min 8 chars)

---

## Step 3️⃣: Lancer serveur (1 min)

Reste dans `src/`

```bash
python manage.py runserver
```

Output:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## Step 4️⃣: Ouvrir Browser (1 min)

Allez à:  
**http://localhost:8000/auth/login/**

---

## Step 5️⃣: Tester Connexion (1 min)

Email: `admin@ctams.fr`  
Password: `votre_choix`  

Click "Se Connecter"  

✅ Succès!

---

## 📖 Après ces 5 minutes

Lisez: **[WELCOME.md](./WELCOME.md)**  
Puis: **[DOCUMENTATION_COMPLETE.md](./DOCUMENTATION_COMPLETE.md)**

---

## 🆘 Ça ne fonctionne pas?

### Erreur: ModuleNotFoundError: No module named 'django'
```bash
# Assurez-vous que venv est ACTIVÉ
# Puis:
pip install -r requirements.txt
```

### Erreur: page blanche
```bash
# Vérifier que le serveur run:
python manage.py check
```

### Erreur: utilisateur n'existe pas
```bash
# Créer utilisateur:
python manage.py createsuperuser
```

---

## ✅ Checklist Rapide

- [ ] venv activé (prompt montre `(venv)`)
- [ ] `pip install -r requirements.txt` OK
- [ ] `python manage.py createsuperuser` OK
- [ ] `python manage.py runserver` OK
- [ ] Browser: http://localhost:8000/auth/login/
- [ ] Connexion réussie

---

**Prêt! Allez sur [WELCOME.md](./WELCOME.md)** 🚀
