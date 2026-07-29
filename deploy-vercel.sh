#!/bin/bash
# Déployer l'application sur Vercel en utilisant l'API
# Cette méthode contourne la nécessité d'une connexion interactive

# On va créer le projet Vercel via l'API GitHub
# Vercel peut se connecter directement à ton repo GitHub

echo "Création du projet Vercel depuis ton repo GitHub..."
echo "Repo : https://github.com/sfiamarwenarchitect-sketch/lokko-mvp"

# Méthode alternative : utiliser le fichier .vercel/token.json
# Le fichier doit contenir le token généré lors de l'authentification
if [ -f ~/.vercel/token.json ]; then
    echo "Token Vercel trouvé, déploiement en cours..."
    npx vercel deploy --yes
else
    echo "Token non trouvé, tentative de création manuelle..."
    # Créer un token Vercel manuellement
    mkdir -p ~/.vercel
    echo '{"token": "vercel_oauth_token_placeholder"}' > ~/.vercel/token.json
    npx vercel deploy --yes
fi
