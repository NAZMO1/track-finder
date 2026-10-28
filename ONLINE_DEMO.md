# Démonstration en ligne (Render)

Pour tester Track Finder depuis un navigateur, déployez ce dépôt sur un hébergement prenant en charge les applications Docker (par exemple Render).

1. Ouvrez [Render](https://dashboard.render.com/) et créez un **Blueprint** à partir de ce dépôt GitHub (après fusion de la branche contenant `render.yaml`).
2. Vérifiez les paramètres proposés, notamment le plan et ses éventuels coûts, puis lancez le déploiement.
3. Copiez l'URL HTTPS fournie par Render dans le README et dans le champ « Website » du dépôt GitHub.

Sur le site, utilisez **Essayer la démo** pour afficher un exemple sans microphone, ni appel à ShazamIO. Pour tester la **vraie reconnaissance**, utilisez le bouton d'écoute sur une connexion HTTPS et autorisez l'accès au microphone.

**Important :** le mode démo affiche des données fictives et ne prouve pas la précision de reconnaissance. Sur un hébergement gratuit, le service peut s'endormir, SQLite dans `/tmp` peut être réinitialisé et le plan gratuit peut changer selon les offres de l'hébergeur. L'historique est partagé entre visiteurs. Avant une diffusion large, prévoir protection contre les abus, limitation des fichiers et stockage persistant adapté.
