#!/bin/bash
# Créer un projet Vercel directement via l'API
# 1. Créer le projet
# 2. Déployer le fichier

# On va utiliser le site Vercel pour déployer en drag & drop
# Ou alors on utilise l'API directe avec un token

# Laissez-moi essayer de créer un token Vercel directement
echo "Tentative de déploiement sur Vercel..."

# On essaie de se connecter avec le compte Vercel existant
npx vercel login 2>&1
