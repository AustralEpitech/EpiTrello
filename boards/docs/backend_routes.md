# Routes backend EpiTrello

Ce document cartographie les routes nécessaires pour la nouvelle UI Trello-like.

## Vue `boards:board_list`

| Fonction | Méthode | URL | Vue Django | Statut |
| --- | --- | --- | --- | --- |
| Charger la liste des tableaux | GET | `/boards/` | `board_list` | ✅ |
| Créer un tableau (modal) | POST | `/boards/create` | `create_board` | ✅ (auth requise) |
| Renommer un tableau | POST | `/boards/board/<id>/rename` | `rename_board` | ✅ |
| Supprimer un tableau | POST | `/boards/board/<id>/delete` | `delete_board` | ✅ |

## Vue `boards:board_detail`

| Fonction | Méthode | URL | Vue Django | Statut |
| --- | --- | --- | --- | --- |
| Charger un tableau | GET | `/boards/board/<id>/` | `board_detail` | ✅ |
| Créer une liste | POST | `/boards/board/<id>/lists/create` | `create_list` | ✅ |
| Créer une carte | POST | `/boards/board/<id>/cards/create` | `create_card` | ✅ |
| Reorder drag & drop | POST(JSON) | `/boards/board/<id>/reorder` | `reorder_cards` | ✅ |
| Detail carte (modal) | GET | `/boards/board/<id>/cards/<card_id>/` | `card_detail` | ✅ |
| Update carte | POST(JSON) | `/boards/board/<id>/cards/<card_id>/update` | `update_card` | ✅ |
| Toggle label | POST(JSON) | `/boards/board/<id>/cards/<card_id>/labels/toggle` | `toggle_card_label` | ✅ |
| Créer label | POST(JSON) | `/boards/board/<id>/cards/<card_id>/labels/create` | `create_label` | ✅ |
| Supprimer label | POST(JSON) | `/boards/board/<id>/cards/<card_id>/labels/<label_id>/delete` | `delete_label` | ✅ |
| Créer sous-tâche | POST(JSON) | `/boards/board/<id>/cards/<card_id>/subtasks/create` | `create_subtask` | ✅ |
| Toggle sous-tâche | POST(JSON) | `/boards/board/<id>/cards/<card_id>/subtasks/<subtask_id>/toggle` | `toggle_subtask` | ✅ |
| Supprimer sous-tâche | POST(JSON) | `/boards/board/<id>/cards/<card_id>/subtasks/<subtask_id>/delete` | `delete_subtask` | ✅ |
| Créer commentaire | POST(JSON) | `/boards/board/<id>/cards/<card_id>/comments/create` | `create_comment` | ✅ (auth requise) |
| Supprimer carte | POST(JSON) | `/boards/board/<id>/cards/<card_id>/delete` | `delete_card` | ✅ |

## Actions manquantes / à implémenter

- Bouton flottant « + » : interface retirée, mais si réintroduit, prévoir endpoint de création rapide.
- Recherche & filtres côté board_detail : nécessite une vue filtrant les cartes (`board_detail` à étendre ou endpoint AJAX).
- Renommage/suppression label global (actuellement uniquement via cartes).
- (`home`) CTA primaire/secondaire déjà reliés à `boards:board_list`.

