**Question : Comment avez-vous vos tests existants au fait que la carte ne soit plus la même qu’au départ ?**  
**Réponse corrigée :**  
Plutôt que de réutiliser directement une grille fixe, nous testons chaque étape indépendamment :  
1. **`MapLoader._parse_header`** est unitaire testé pour retourner exactement le dict attendu pour un header YAML donné.  
2. **`MapLoader.load`** est testé pour lever un `FileNotFoundError` si le fichier n’existe pas, puis pour produire un tuple `(meta, rows)` où :  
   - `meta["width"]` et `meta["height"]` correspondent au header,  
   - `rows` est la liste des chaînes ASCII pad­dées ou tronquées correctement à `meta["width"]`,  
   - et toute incohérence (trop peu de lignes ou trop larges) déclenche une `ValueError` :contentReference[oaicite:0]{index=0}.  
3. Pour la partie **placement des objets**, on écrit des tests sur `LevelBuilder.build_level` : on fournit un petit fichier de test, on appelle `build_level`, puis on vérifie que chaque sprite (joueur, murs, pièces, pièges, sortie, monstres, plateformes, portails, interrupteurs) se retrouve dans la liste adéquate **et** à la bonne coordonnée (via `helper.grid_to_world`).  

---

**Question : Le code qui gère la lave ressemble-t-il plus à celui de l’herbe, des pièces, ou des blobs ?**  
**Réponse corrigée :**  
La lave (on l'a notée `£`) est traitée comme un piège mortel, exactement comme les autres sprites de la *death_list* en sortie de `LevelBuilder`. Elle n’est ni un sprite “statique” normal ni un blob : elle déclenche un reset du niveau dès qu’on la touche dans `GameView.on_update`. Mais elle est proche des pièces dans le sens où c'est un sprite statique qui déclenche un événement au contact(mort) et proche des blobs dans le sens où elle peut tuer.

---

**Question : Comment détectez-vous les conditions dans lesquelles les blobs doivent changer de direction ?**  
**Réponse :**  
Chaque frame, `Blob.step()` :  
1. Calcule la position future `next_center_x`.  
2. Vérifie la **collision imminente** avec un mur via `_collision_ahead()`.  
3. Vérifie la **présence de sol** sous quatre points d’échantillonnage (¼-largeur du blob) avec `_ground_samples(next_center_x)`.  
4. Si collision ou absence de sol (lava n’est pas incluse dans `_walls`), il inverse sa direction (`reversy()`), sinon il avance de `_speed`. :contentReference[oaicite:2]{index=2}.

---

**Question : Quelles formules utilisez-vous exactement pour l’épée ? Comment passez-vous des coordonnées écran aux coordonnées monde ?**  
**Réponse :**  
- **Conversion écran→monde :** on stocke la position du clic dans `self._mouse_screen` (en pixels écran) et on appelle `camera.unproject(self._mouse_screen)` pour obtenir `(cursor_x, cursor_y)` en coordonnées monde :contentReference[oaicite:3]{index=3}.  
- **Calcul de l’angle :**  
  ```python
  dx = cursor_x - self.center_x
  dy = cursor_y - self.center_y
  self.angle = -math.degrees(math.atan2(dy, dx)) + self._angle_offset
  ```
(Le signe de hand_offset_x dépend du demi-écran) 

---
**Question : Comment transférez-vous le score de la joueuse d’un niveau à l’autre ?**

On le stocke dans GameView, et on le réutilise après.

---
**Question : Avez-vous du code dupliqué entre les cas où la joueuse perd parce qu’elle a touché un monstre ou de la lave ?**
Réponse :
Non : qu’il s’agisse d’un monstre (current_health <= 0 ou collision dans on_update) ou d’un piège (death_list ou y < -300), on retombe dans le même bloc qui réinitialise la position et recharge le niveau via self.setup(self.map_name)

---
**Question : Comment modélisez-vous la “next-map” ? Où la stockez-vous, et comment la traitez-vous quand la joueuse atteint le point E ?**
Réponse:
Actuellement, le chemin de la map suivante est codé en dur dans GameView.on_update :

``` 
if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
    self.setup("maps/map6.txt")
    return
```
Il n’existe pas de champ next_map dans le metadata ; pour rendre cela dynamique, on pourrait ajouter meta["next_map"] en YAML et l’utiliser ici, mais comme les maps se suivent naturellement, nous n'avons pas besoin de l'ajouter. C'est en effet le pouvoir qu'on a en tant que Game Designer, nous savons exactement où ira le joueur.

--- 
**Question : Que se passe-t-il si la joueuse atteint le E mais la carte n’a pas de next-map ?**

Réponse :
Le code appelle self.setup("maps/3.txt") sans contrôle : si ce fichier n’existe pas, MapLoader.load lèvera un FileNotFoundError
 
---
**Question : Quelles formules utilisez-vous exactement pour l’arc et les flèches ?**
Réponse :

À la pression gauche, on normalise le vecteur main→curseur pour obtenir la direction initiale, puis on multiplie par ARROW_SPEED pour la vitesse initiale.

Chaque frame, dans Arrow.step(dt) :
```
self.center_x += vel.x * dt
self.center_y += vel.y * dt
vel.y   -= ARROW_GRAVITY * dt
self.angle = -math.degrees(math.atan2(vel.y, vel.x)) + 42.8
```
Au bout de ARROW_LIFETIME ou si y < -100, on supprime la flèche 

---
**Question : Quelles formules utilisez-vous exactement pour le déplacement des chauves-souris (champ d’action, changements de direction, etc.) ?**
Réponse :

Dans Bat._pick_new_target() :

    def _pick_new_target(self) -> None:
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, self._radius)
        self._target_x = self._spawn_x + r * math.cos(angle)
        self._target_y = self._spawn_y + r * math.sin(angle)
        old_dir = self._direction
        self._direction = 1 if self._target_x >= self.center_x else -1
        if self._direction != old_dir:
            self.reversy()
Puis step() normalise (dx, dy) vers la cible et avance de speed pixels/par frame

---

**Question : Comment avez-vous structuré votre programme pour que les flèches puissent poursuivre leur vol ?**
Réponse :

La classe Bow maintient une liste self.arrows. À chaque GameView.on_update, on appelle bow.updating(...) qui, pour chaque flèche, exécute arrow.step(dt, camera) et met à jour position, gravité et angle 

---

**Question : Comment gérez-vous le fait que vous avez maintenant deux types de monstres, et deux types d’armes ? Comment faites-vous pour ne pas dupliquer du code entre ceux-ci ?**

Réponse :
On définit une super-classe abstraite Enemy (dans base_entity.py) pour les blobs, chauves-souris, etc., et une super-classe Weapon (dans weapon.py) pour l’épée et l’arc. Chaque type spécialisé hérite de ces classes, profitant du même cycle de vie et des mêmes helpers .

---

**Question : Quel algorithme utilisez-vous pour identifier tous les blocs d’une plateformes, et leurs limites de déplacement ?**
Réponse :
Nous utilisons un flood-fill (BFS) dans _label_blocks, qui parcourt le tableau ASCII pour regrouper les cellules connectées en “bloc continu”.

---

***Question : Sur quelle structure travaille cet algorithme ? Quels sont les avantages et inconvénients de votre choix ?**
Réponse :
L’algorithme opère sur :

rows: List[str] (liste de lignes ASCII),

blocks: Dict[int, List[Tuple[col, row]]].
Avantages : simple à implémenter, typé statiquement, lecture directe de rows[r][c].
Inconvénients : les chaînes immuables forcent la copie pour toute modification, accès O(1) mais BFS utilise beaucoup de tuples et listes, pas optimisé pour très grandes cartes.

---

**Question : Quelle bibliothèque utilisez-vous pour lire les instructions des interrupteurs ? Dites en une ou deux phrases pourquoi vous avez choisi celle-là.**
Réponse :
PyYAML pour sa simplicité à parser un header YAML, sa maturité et sa bonne compatibilité avec safe_load 

---
**Question : Comment votre design général évolue-t-il pour tenir compte des interrupteurs et des portails ?**
Réponse :

LevelBuilder instancie les Gate et Switch à partir de meta["gates"] et meta["switches"], lie chaque switch à ses gates.

GameView.on_update synchronise la liste wall_list selon gate.is_open (ajout/suppression).

Switch.trigger() bascule l’état des gates et met à jour visuel + collision via Gate.toggle() .