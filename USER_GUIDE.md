# Guide Utilisateur - EpiTrello

## Table des matieres

- [Introduction](#introduction)
- [Premiers pas](#premiers-pas)
  - [Creer un compte](#creer-un-compte)
  - [Se connecter](#se-connecter)
  - [Se deconnecter](#se-deconnecter)
  - [Changer son mot de passe](#changer-son-mot-de-passe)
- [Gestion des tableaux](#gestion-des-tableaux)
  - [Creer un tableau](#creer-un-tableau)
  - [Renommer un tableau](#renommer-un-tableau)
  - [Supprimer un tableau](#supprimer-un-tableau)
  - [Rechercher et filtrer ses tableaux](#rechercher-et-filtrer-ses-tableaux)
- [Gestion des listes](#gestion-des-listes)
  - [Creer une liste](#creer-une-liste)
  - [Reorganiser les listes](#reorganiser-les-listes)
  - [Replier et deplier une liste](#replier-et-deplier-une-liste)
  - [Supprimer une liste](#supprimer-une-liste)
- [Gestion des cartes](#gestion-des-cartes)
  - [Creer une carte](#creer-une-carte)
  - [Modifier une carte](#modifier-une-carte)
  - [Deplacer et reorganiser les cartes](#deplacer-et-reorganiser-les-cartes)
  - [Trier les cartes](#trier-les-cartes)
  - [Filtrer les cartes](#filtrer-les-cartes)
  - [Archiver une carte](#archiver-une-carte)
- [Labels (Etiquettes)](#labels-etiquettes)
  - [Creer un label](#creer-un-label)
  - [Associer ou retirer un label](#associer-ou-retirer-un-label)
  - [Supprimer un label](#supprimer-un-label)
- [Checklists et sous-taches](#checklists-et-sous-taches)
  - [Creer une checklist](#creer-une-checklist)
  - [Ajouter des elements](#ajouter-des-elements)
  - [Cocher et decocher un element](#cocher-et-decocher-un-element)
  - [Supprimer une checklist ou un element](#supprimer-une-checklist-ou-un-element)
- [Commentaires](#commentaires)
  - [Ajouter un commentaire](#ajouter-un-commentaire)
  - [Consulter les commentaires](#consulter-les-commentaires)
- [Collaboration](#collaboration)
  - [Inviter un membre sur un tableau](#inviter-un-membre-sur-un-tableau)
  - [Gerer les membres](#gerer-les-membres)
  - [Retirer un membre](#retirer-un-membre)
  - [Assigner un utilisateur a une carte](#assigner-un-utilisateur-a-une-carte)
- [Notifications](#notifications)
  - [Consulter ses notifications](#consulter-ses-notifications)
  - [Marquer comme lu](#marquer-comme-lu)
- [Recherche globale](#recherche-globale)
- [Export des donnees](#export-des-donnees)
  - [Exporter en JSON](#exporter-en-json)
  - [Exporter en CSV](#exporter-en-csv)
- [Mises a jour en temps reel](#mises-a-jour-en-temps-reel)
- [Profil utilisateur](#profil-utilisateur)

---

## Introduction

EpiTrello est une application web collaborative de gestion de projet, inspiree de Trello. Elle vous permet d'organiser votre travail a l'aide d'un systeme de **tableaux**, **listes** et **cartes** selon la methode Kanban.

### Concepts cles

| Concept | Description |
|---------|-------------|
| **Tableau** | Un espace de travail qui regroupe des listes. Chaque tableau correspond a un projet ou un theme. |
| **Liste** | Une colonne dans un tableau qui represente une etape ou une categorie (ex : "A faire", "En cours", "Termine"). |
| **Carte** | Une tache ou un element a suivre. Les cartes sont placees dans les listes et contiennent des details, des labels, des checklists et des commentaires. |

---

## Premiers pas

### Creer un compte

1. Rendez-vous sur la page d'accueil d'EpiTrello.
2. Cliquez sur **S'inscrire** dans la barre de navigation.
3. Remplissez le formulaire d'inscription :
   - **Nom d'utilisateur** (obligatoire)
   - **Email** (obligatoire)
   - **Mot de passe** (obligatoire, a saisir deux fois pour confirmation)
4. Cliquez sur **Creer mon compte**.

Vous pouvez egalement vous inscrire directement via un compte tiers :
- Cliquez sur **Continuer avec Google** pour utiliser votre compte Google.
- Cliquez sur **Continuer avec GitHub** pour utiliser votre compte GitHub.

### Se connecter

1. Rendez-vous sur la page de connexion.
2. Saisissez votre **nom d'utilisateur ou email** et votre **mot de passe**.
3. (Facultatif) Cochez **Se souvenir de moi** pour rester connecte.
4. Cliquez sur **Se connecter**.

Vous pouvez aussi vous connecter via **Google** ou **GitHub** en cliquant sur le bouton correspondant.

Si vous avez oublie votre mot de passe, cliquez sur **Mot de passe oublie ?** pour lancer la procedure de reinitialisation.

### Se deconnecter

- Depuis la page d'accueil ou votre profil, cliquez sur le bouton **Deconnexion** dans la barre de navigation.

### Changer son mot de passe

1. Accedez a votre **Profil** en cliquant sur votre avatar (initiale de votre nom) dans la barre de navigation.
2. Dans la section **Actions rapides**, cliquez sur **Changer mon mot de passe**.
3. Saisissez votre ancien mot de passe, puis le nouveau mot de passe (deux fois).
4. Validez. Une notification vous confirme le changement.

---

## Gestion des tableaux

### Creer un tableau

1. Depuis la page **Mes tableaux**, cliquez sur le bouton **+ Nouveau tableau** en haut a droite.
2. Une fenetre modale s'ouvre. Saisissez le **titre** de votre tableau (100 caracteres maximum).
3. Cliquez sur **Creer**.

Vous etes automatiquement redirige vers votre nouveau tableau.

### Renommer un tableau

1. Depuis la page **Mes tableaux**, cliquez sur le bouton **Renommer** (icone crayon) sur la carte du tableau concerne.
2. Saisissez le nouveau nom dans la fenetre modale.
3. Cliquez sur **Renommer** pour confirmer.

> Seul le proprietaire du tableau peut le renommer.

### Supprimer un tableau

1. Depuis la page **Mes tableaux**, cliquez sur le bouton **Supprimer** (icone corbeille) sur la carte du tableau concerne.
2. Confirmez la suppression dans la boite de dialogue.

> **Attention** : la suppression d'un tableau est definitive. Toutes les listes, cartes, labels, checklists et commentaires associes seront supprimes.

> Seul le proprietaire du tableau peut le supprimer.

### Rechercher et filtrer ses tableaux

La page **Mes tableaux** propose une barre de filtres en haut de la page :

- **Recherche** : saisissez un terme dans le champ de recherche pour filtrer les tableaux par nom. Le filtrage est instantane.
- **Tri** : utilisez le menu deroulant pour choisir un mode de tri :
  - **Plus recents** : les tableaux les plus recemment crees en premier.
  - **A → Z** : tri alphabetique par titre.
  - **Activite** : tri par activite recente.
- **Proprietaire** : filtrez par proprietaire :
  - **Tous les proprietaires** : affiche tous les tableaux auxquels vous avez acces.
  - **Mes tableaux** : affiche uniquement les tableaux dont vous etes proprietaire.

---

## Gestion des listes

### Creer une liste

1. Ouvrez un tableau en cliquant dessus depuis la page **Mes tableaux**.
2. Dans le panneau **Ajouter une liste** a droite des listes existantes :
   - Saisissez un **titre** pour la liste.
   - Cliquez sur **Creer**.

La nouvelle liste apparait immediatement sur le tableau.

### Reorganiser les listes

Les listes peuvent etre reorganisees par **glisser-deposer** (drag & drop) :

1. Cliquez et maintenez le clic sur l'en-tete d'une liste.
2. Deplacez-la vers la position souhaitee (a gauche ou a droite des autres listes).
3. Relachez. L'ordre est automatiquement sauvegarde.

### Replier et deplier une liste

Chaque liste dispose d'un bouton de repli (fleche vers le bas) a gauche de son titre :

1. Cliquez sur le bouton **fleche** pour replier la liste (masquer les cartes).
2. Cliquez a nouveau pour deplier la liste et afficher les cartes.

Cela permet de gagner de l'espace visuel lorsque vous travaillez avec de nombreuses listes.

### Supprimer une liste

1. Cliquez sur le bouton **X** (croix rouge) a droite du titre de la liste.
2. Confirmez la suppression.

> La suppression d'une liste entraine la suppression de toutes les cartes qu'elle contient.

---

## Gestion des cartes

### Creer une carte

1. Dans la liste souhaitee, cliquez sur le bouton **+ Nouvelle carte** en bas de la liste.
2. Un formulaire apparait :
   - Saisissez un **Titre** (obligatoire).
   - (Facultatif) Ajoutez une **Description**.
3. Cliquez sur **Ajouter**.

La carte apparait aussitot dans la liste. Vous pouvez aussi utiliser le bouton **+** dans l'en-tete de la liste.

### Modifier une carte

1. Cliquez sur une carte pour ouvrir sa vue detaillee (fenetre modale).
2. Dans la modale, vous pouvez modifier :
   - **Titre** : editez le champ titre.
   - **Date limite** : selectionnez une date et heure via le selecteur de date.
   - **Description** : redigez ou modifiez la description dans la zone de texte.
3. Cliquez sur **Sauvegarder** pour enregistrer vos modifications.

Les modifications sont immediatement visibles sur le tableau.

### Deplacer et reorganiser les cartes

Les cartes supportent le **glisser-deposer** :

- **Au sein d'une meme liste** : cliquez et maintenez une carte, puis deplacez-la vers la position souhaitee dans la meme liste.
- **Entre les listes** : cliquez et maintenez une carte, puis deplacez-la vers une autre liste pour changer sa categorie.

L'ordre et le placement sont sauvegardes automatiquement.

### Trier les cartes

En haut du tableau, un menu deroulant permet de trier toutes les cartes :

| Option | Description |
|--------|-------------|
| **Tri manuel** | L'ordre par defaut, defini par vos deplacements manuels. |
| **Titre (A-Z)** | Tri alphabetique par titre de carte. |
| **Date d'echeance** | Les cartes avec une date limite proche en premier. |
| **Plus recentes** | Les cartes les plus recemment creees en premier. |
| **Label (A-Z)** | Tri par le nom du premier label associe. |

### Filtrer les cartes

Le bouton **Filtrer** en haut du tableau ouvre un panneau de filtrage avec deux criteres :

**Par labels :**
- Cliquez sur un ou plusieurs labels pour n'afficher que les cartes portant au moins un de ces labels.
- Les labels selectionnes sont mis en surbrillance (bordure verte).

**Par echeance :**
- **En retard** : affiche les cartes dont la date limite est depassee.
- **Aujourd'hui** : affiche les cartes dont la date limite est aujourd'hui.
- **Sans date** : affiche les cartes sans date limite.

Pour reinitialiser tous les filtres, cliquez sur **Effacer les filtres**.

La barre de recherche en haut du tableau permet aussi de filtrer les cartes par titre en temps reel.

### Archiver une carte

Deux methodes :

- **Depuis le tableau** : survolez une carte et cliquez sur l'icone **corbeille** qui apparait.
- **Depuis la modale** : ouvrez la carte, puis cliquez sur le bouton **Archiver la carte** dans le panneau lateral droit.

Une confirmation vous sera demandee avant la suppression.

---

## Labels (Etiquettes)

Les labels permettent de categoriser visuellement vos cartes avec des couleurs et des noms.

### Creer un label

1. Ouvrez une carte en cliquant dessus.
2. Dans le panneau lateral droit, section **Labels** :
   - Saisissez un **nom** pour le label.
   - Choisissez une **couleur** via le selecteur de couleur.
3. Cliquez sur **Creer un label**.

Le label est cree et automatiquement associe a la carte. Il sera disponible pour toutes les cartes du meme tableau.

### Associer ou retirer un label

1. Ouvrez une carte.
2. Dans la section **Labels**, les labels existants du tableau sont affiches.
3. Cliquez sur **Ajouter** a cote d'un label pour l'associer a la carte.
4. Cliquez sur **Retirer** pour dissocier un label de la carte.

Les labels associes sont visibles directement sur la carte dans le tableau, sous forme de pastilles colorees.

### Supprimer un label

1. Ouvrez une carte qui possede le label a supprimer.
2. Cliquez sur **Retirer** a cote du label. Si ce label n'est plus utilise par aucune autre carte, il sera automatiquement supprime du tableau.

---

## Checklists et sous-taches

Les checklists vous permettent de decomposer une carte en sous-etapes et de suivre leur progression.

### Creer une checklist

1. Ouvrez une carte en cliquant dessus.
2. Dans le panneau lateral droit, cliquez sur le bouton **Checklist**.
3. Saisissez un **titre** pour la checklist (ex : "Etapes de validation").
4. Cliquez sur **Ajouter**.

Vous pouvez creer plusieurs checklists par carte.

### Ajouter des elements

1. Dans une checklist, cliquez sur **+ Ajouter un element**.
2. Saisissez le nom de l'element (sous-tache).
3. Cliquez sur **Ajouter**.

L'element apparait dans la checklist avec une case a cocher.

### Cocher et decocher un element

- Cliquez sur la **case a cocher** a gauche d'un element pour le marquer comme termine. L'element apparait barre.
- Cliquez a nouveau pour le remettre en attente.

Une **barre de progression** en haut de chaque checklist indique le pourcentage d'elements termines.

### Supprimer une checklist ou un element

- **Supprimer un element** : survolez l'element et cliquez sur le bouton **X** qui apparait a droite.
- **Supprimer une checklist** : cliquez sur le lien **Supprimer** a droite du titre de la checklist. Tous les elements de la checklist seront supprimes.

---

## Commentaires

### Ajouter un commentaire

1. Ouvrez une carte.
2. En bas de la modale, dans la section **Commentaires** :
   - Redigez votre commentaire dans la zone de texte.
   - Cliquez sur **Envoyer**.

Le commentaire est publie avec votre nom d'utilisateur et la date/heure.

### Consulter les commentaires

Les commentaires apparaissent dans l'ordre chronologique inverse (les plus recents en premier) dans la section **Commentaires** de la modale de carte.

Chaque commentaire affiche :
- Le **nom de l'auteur**.
- La **date et l'heure** de publication.
- Le **contenu** du commentaire.

---

## Collaboration

### Inviter un membre sur un tableau

> Cette action est reservee au **proprietaire** du tableau.

1. Ouvrez le tableau concerne.
2. Dans la barre d'en-tete, reperez le champ **Inviter (pseudo)**.
3. Saisissez le **nom d'utilisateur** de la personne a inviter.
4. Cliquez sur **Inviter**.

Le membre invite recoit une notification et peut desormais acceder au tableau. Il peut voir et modifier les listes, cartes, labels et commentaires.

### Gerer les membres

1. Depuis le tableau, cliquez sur le bouton **Membres** dans la barre d'en-tete.
2. La page de gestion des membres s'affiche. Elle montre :
   - Le **proprietaire** du tableau (avec le badge "Owner").
   - La liste des **membres invites** avec leur nom d'utilisateur et email.

### Retirer un membre

1. Sur la page de gestion des membres, cliquez sur le bouton **Retirer** a cote du membre concerne.
2. Confirmez la suppression dans la boite de dialogue.

Le membre perd immediatement l'acces au tableau.

### Assigner un utilisateur a une carte

1. Ouvrez une carte.
2. Dans la section **Membres assignes**, vous voyez les membres deja assignes.
3. Dans la sous-section **Assigner un membre**, cliquez sur le nom d'un membre pour l'assigner a la carte. Le bouton devient vert.
4. Cliquez a nouveau pour le desassigner.

Les membres assignes apparaissent sous forme d'avatars (initiales) directement sur la carte dans le tableau.

Lorsqu'un membre est assigne par quelqu'un d'autre, il recoit une notification.

---

## Notifications

### Consulter ses notifications

1. Cliquez sur l'icone **cloche** dans la barre de navigation. Un badge vert indique le nombre de notifications non lues.
2. La page des notifications s'affiche avec la liste de toutes vos notifications.

Les notifications sont envoyees dans les cas suivants :
- Vous etes **invite** sur un tableau.
- Vous etes **assigne** a une carte par un autre utilisateur.
- Votre **mot de passe** a ete change.

Les notifications non lues sont mises en evidence avec une bordure verte et un texte en gras.

### Marquer comme lu

- **Une notification** : cliquez sur l'icone **coche** (check) a droite de la notification concernee.
- **Toutes les notifications** : cliquez sur le lien **Tout marquer comme lu** en haut de la page.

Chaque notification contenant un lien (ex : vers un tableau) dispose d'un bouton **Voir** pour y acceder directement.

---

## Recherche globale

La recherche globale vous permet de trouver des tableaux et des cartes a travers tous vos espaces de travail.

1. Cliquez sur l'icone **loupe** dans la barre de navigation (disponible depuis la page des tableaux ou depuis un tableau).
2. Saisissez un terme de recherche dans le champ.
3. Cliquez sur **Rechercher**.

Les resultats sont affiches en deux sections :
- **Tableaux** : les tableaux dont le titre correspond a votre recherche, avec le nombre de resultats.
- **Cartes** : les cartes dont le titre ou la description correspondent, avec l'indication du tableau et de la liste d'origine.

Cliquez sur un resultat pour y acceder directement.

---

## Export des donnees

> L'export est reserve au **proprietaire** du tableau.

### Exporter en JSON

1. Ouvrez le tableau concerne.
2. Cliquez sur le bouton **Exporter** dans la barre d'en-tete.
3. Selectionnez **Exporter en JSON**.

Un fichier JSON est telecharge contenant la structure complete du tableau : listes, cartes, labels, checklists, sous-taches et commentaires, sous forme hierarchique.

### Exporter en CSV

1. Ouvrez le tableau concerne.
2. Cliquez sur le bouton **Exporter** dans la barre d'en-tete.
3. Selectionnez **Exporter en CSV**.

Un fichier CSV est telecharge avec une ligne par carte, contenant les colonnes : titre de la carte, description, liste associee, labels, date d'echeance, etc. Ce format est adapte pour l'ouverture dans un tableur (Excel, Google Sheets, LibreOffice Calc).

---

## Mises a jour en temps reel

EpiTrello utilise une connexion temps reel (WebSocket) pour synchroniser automatiquement les modifications entre les utilisateurs qui consultent le meme tableau.

Concretement, si un autre membre du tableau :
- Cree, modifie ou supprime une **carte**
- Supprime une **liste**
- Reorganise les **cartes** ou les **listes**

...vous verrez les changements apparaitre automatiquement sur votre ecran, sans avoir a rafraichir la page. Un indicateur **"Synchronisation..."** s'affiche brievement lors de la mise a jour.

Si la connexion est interrompue, l'application tente de se reconnecter automatiquement.

---

## Profil utilisateur

Pour acceder a votre profil, cliquez sur votre **avatar** (initiale de votre nom d'utilisateur, cercle vert) dans la barre de navigation.

La page de profil affiche :

- **Votre nom d'utilisateur** et la date d'inscription.
- **Statistiques** : nombre de tableaux et date de derniere connexion.
- **Informations personnelles** : email, prenom et nom.
- **Notifications recentes** : un apercu de vos dernieres notifications avec un lien vers la page complete.
- **Actions rapides** :
  - **Acceder a mes tableaux** : lien direct vers la page de vos tableaux.
  - **Changer mon mot de passe** : lien vers le formulaire de changement de mot de passe.

---

*EpiTrello - Construit avec Django, Tailwind CSS et SortableJS, inspire de Trello.*
