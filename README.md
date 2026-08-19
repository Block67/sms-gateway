# fastapi-sms-gateway

Passerelle SMS (FastAPI + PostgreSQL + RabbitMQ) — réplique en Python du
pipeline d'envoi et de la gestion des Sender ID vus dans le projet Node
`fastermessage-api`, avec le même principe : **chaque client a ses propres
sender IDs, jamais partagés avec les autres clients**.

## Démarrage rapide

Prérequis : Docker + Docker Compose.

```bash
git clone https://github.com/Block67/sms-gateway.git
cd sms-gateway
cp .env.example .env

docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.create_user admin@example.com --admin
# -> note la clé API admin affichée, elle sert à approuver les senders et seed operators/pricing
```

L'API est disponible sur http://localhost:8000/docs — le worker d'envoi
(service `worker`) tourne déjà en arrière-plan, aucune étape en plus.
Pour un test de bout en bout (créer un client, un sender, envoyer un SMS),
voir [Flux complet d'exemple](#flux-complet-dexemple) plus bas.

Pour développer sur l'API en local (rechargement à chaud, sans rebuild
Docker à chaque changement), voir [Développement local](#développement-local).

## Architecture

```
Client  --X-API-Key-->  API FastAPI  --RabbitMQ-->  Worker  --HTTP-->  Gateway SMS (Jasmin ou local)
                              |                         |
                          PostgreSQL <-------------------
```

- **API** (`src/main.py`) : reçoit `/sms/send`, valide (numéro, sender ID,
  solde), enregistre le message, publie une tâche sur RabbitMQ.
- **Worker** (`src/queue/worker.py`, process séparé) : consomme la queue un
  message à la fois, appelle la gateway SMS réelle, met à jour le statut.
  Le débit est contrôlé par `SMS_SEND_INTERVAL_MS` (défaut 1000ms).
- **Gateway** (`src/gateway/`) : abstraction `SMSGateway` avec deux
  implémentations — `LocalGateway` (simule un envoi, pour le dev) et
  `JasminGateway` (vrai appel HTTP vers une instance Jasmin). Bascule via
  `GATEWAY_PROVIDER=local|jasmin` dans `.env`.
- **DLR** (`src/dlr/`) : reçoit les accusés de livraison de la gateway et
  les répercute vers le `dlr_url` fourni par le client à l'envoi.

## Modèle de données (PostgreSQL)

| Table | Rôle | Index clés |
|---|---|---|
| `users` | comptes clients (auth par `api_key`) | `api_key` unique, `email` unique |
| `senders` | sender IDs, **scopés par `owner_id`** | unique `(owner_id, name)` en `CITEXT` (insensible à la casse, sans `LOWER()`), `status` |
| `operators` | table de préfixes (pays/opérateur) | `prefix` unique |
| `user_prices` | tarif par client × opérateur | unique `(user_id, operator_id)` |
| `messages` | journal des SMS | composite `(owner_id, created_at)` pour la pagination, `status`, `to_number`, `provider_message_id` |

Une vue `daily_message_stats` (créée dans la migration) donne un résumé
quotidien par sender/statut, dans le même esprit que les vues de
`init.sql` du premier projet Kannel.

## Gestion du Sender ID (le cœur du sujet)

C'est `src/senders/service.py::check_sender` qui fait tout le travail — au
moment d'envoyer un SMS :

1. Le sender demandé doit exister dans `senders`
2. **avec `owner_id = user.id`** (le client connecté, jamais un autre)
3. **et `status = 'active'`** (validé par un admin via `PATCH /senders/{id}/approve`)

Sinon, l'envoi est refusé (`InvalidSenderId`). C'est cette contrainte
`(owner_id, name)` qui garantit qu'un sender ID est bien la propriété
exclusive d'un client, exactement comme demandé.

## Développement local

Prérequis : Python 3.13+, Docker + Docker Compose (pour Postgres/RabbitMQ).

```bash
cp .env.example .env
docker compose up -d postgres rabbitmq

python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt

alembic upgrade head

# Créer un admin (pour approuver les sender IDs et seed les opérateurs/prix)
python -m scripts.create_user admin@example.com --admin

# Créer un client
python -m scripts.create_user client@example.com
# -> note la clé API affichée

uvicorn src.main:app --reload
# API : http://localhost:8000/docs
```

Dans un second terminal, lancer le worker (indispensable pour que les SMS
mis en queue partent réellement) :

```bash
python -m src.queue.worker
```

## Flux complet d'exemple

```bash
API_KEY="<clé du client>"
ADMIN_KEY="<clé de l'admin>"

# 1. Seed un opérateur (ex: Bénin, préfixe +229 97)
curl -X POST http://localhost:8000/operators \
  -H "X-API-Key: $ADMIN_KEY" -H "Content-Type: application/json" \
  -d '{"prefix":"22997","country_iso":"BJ","mcc":"616","mnc":"04","name":"MTN Benin"}'

# 2. Fixer un tarif client x opérateur
curl -X POST http://localhost:8000/pricing \
  -H "X-API-Key: $ADMIN_KEY" -H "Content-Type: application/json" \
  -d '{"user_id":"<id client>","operator_id":"<id operateur>","price":15}'

# 3. Le client crée son sender ID
curl -X POST http://localhost:8000/senders \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"name":"MOUGNI"}'

# 4. L'admin l'approuve
curl -X PATCH http://localhost:8000/senders/<sender_id>/approve -H "X-API-Key: $ADMIN_KEY"

# 5. Le client envoie un SMS avec SON sender ID
curl -X POST http://localhost:8000/sms/send \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"to":"+22997123456","text":"Bonjour depuis MOUGNI","sender":"MOUGNI"}'
```

## Limites assumées (scaffold volontairement focalisé)

- **Résolution opérateur par préfixe statique** (table `operators` à seeder
  soi-même) — ce n'est pas un vrai lookup HLR/portabilité, comme dans le
  projet Node d'origine (qui faisait la même approximation via une table
  statique `OperatorModel`).
- **Un seul compte gateway global** (`JASMIN_USERNAME`/`JASMIN_PASSWORD`),
  pas de credentials Jasmin par client comme dans l'original — plus simple,
  suffisant pour la plupart des cas d'usage.
- **Pas de hiérarchie multi-tenant** (Brand/AccountManager) ni d'alerting
  Brevo — non demandés dans cette réplication, faciles à ajouter en suivant
  le même pattern de module (`src/<feature>/{models,schemas,service,router}.py`).
- **Logs** : `logging` standard (pas de fichier par compte) — pour éviter
  l'explosion de fichiers qu'on a nettoyée sur le projet Mongo.
