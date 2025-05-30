Object : racine polymorphe du gameplay : Object étend arcade.Sprite et regroupe tout ce qu’une entité « vivante » doit avoir : points de vie, barre de vie embarquée, gestion de l’invincibilité, méthodes take_damage(), heal(), etc. 
Grâce à cela, n’importe quelle sous-classe bénéficie gratuitement de ces capacités sans les réimplémenter ; un même appel sprite.take_damage(10) fonctionne sur un joueur, un blob ou une chauve-souris.
Enemy dérive de Object et ajoute son “intelligence” générique : vitesse, direction, inversion (reversy) et surtout l’abstract method step() que chaque ennemi doit redéfinir.


Bat Enemy dérive de Object et ajoute l’I.A. générique : vitesse, direction, inversion (reversy) et surtout la méthode abstraite step() que chaque ennemi doit redéfinir. base_entity
Blob redéfinit step() pour marcher en sécurité sur les plates-formes (prédiction de terrain + détection de mur). blob


Bat redéfinit step() fournit un vol aléatoire dans un rayon donné. 


Dans la boucle de jeu (GameView.on_update), la liste monster_list est typée SpriteList[Enemy]; appeler simplement monster.update(dt) déclenche la bonne version de step().

Joueur
Player hérite aussi de Object, réutilise santé/invincibilité, puis ajoute des constantes de mouvement et un léger système de knock-back. Notre ajout personnel consistait en effet à ajouter un système de vie, ce qui implique trivialement que notre joueur ne meurt pas au contact des monstres. Nous voulions tout de même que le contact soit ressenti, c’est pour ça que nous avons ajouté le knock-back. L’API reste cohérente (même take_damage, heal)

Armes : Weapon → Sword
Weapon encapsule la géométrie d’un objet pivotant autour de la main ; toutes les armes futures n’auront qu’à renseigner la texture, le pivot et quelques offsets. C’était particulièrement utile car nous changions souvent les textures au fur à mesure de nos redesign des sprites, et leur centre de gravité changeait énormément. Sword montre un premier cas concret. Ici encore, le jeu manipule des références génériques (liste de Weapon) sans connaître le détail de chaque arme.

Environnement

Plateformes mobiles : Platform
Typing : signatures explicites (Tuple[float,float], str, bool), ce qui donne à mypy un contrat clair.
Design : l’axe de déplacement (« x » ou « y »), le sens et deux bornes montrent que la plateforme est une brique élémentaire ; un bloc de plusieurs tiles est simplement un groupe de Platform.
Polymorphisme d’usage : dans LevelBuilder, la liste platforms est de type arcade.SpriteList[Platform]; elle est ensuite concaténée à wall_list (type SpriteList[Sprite]). Pour le moteur, une plateforme est donc « un mur qui bouge ».




Fabrication et chargement
LevelBuilder regroupe dans des SpriteList acceptant plusieurs classes d’objets différents (walls, monsters, switches…) puis les renvoie sous forme d’un TypedDict. Le code qui consomme ces listes n’a pas à distinguer la sous-classe précise ; il applique les opérations offertes par la classe de base (Sprite).


platform_build et map_loader restent fonctionnels ; ils génèrent des instances concrètes mais ne participent pas eux-mêmes à la hiérarchie.


