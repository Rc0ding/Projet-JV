# Programmation orientée objet
## Course
This repository follows the 2025's autumn ICC (*CS-112(j)*) project. The course was taught by [Sébastien Doeraene](https://people.epfl.ch/sebastien.doeraene).
It follows instructions and guidance from [this](https://epfl-cs-112-ma.github.io/) website.

## How to play / use
Clone this git repo
```sh
git clone https://github.com/Rc0ding/Projet-JV
```

Make sure to have [UV](https://astral.sh/uv/) installed. Then :
```sh
cd icc-poo
uv sync
```

To run the game :
```sh
uv run main.py
```

### MyPy

This porject asked for mypy type-checking. If you wish to run mypy :
```sh
uv run mypy .
```

It was taught over [here](https://epfl-cs-112-ma.github.io/) mainly.

## Usage
This projects uses, as prescribed by the course :
- [UV](https://astral.sh/uv/) as a project / version manager
- [PyTest](https://pytest.org/) for testing / coverage
- [MyPy](https://mypy-lang.org/) for a stronger typing system
- [Arcade](https://api.arcade.academy/en/latest/index.html) for the game engine

## Extensions
We added two extensions to this project:
- A life system with knockback; the character doesn't die immediately, but is set backwards when encoutering mobs (blobs and bats)
- an entire redesign of the Sprites : Remi and Noah wanted the visual aspect of the game to stand out, and manually redesigned everything. We first had sketches made on procreate by Remi, and Noah would polish the designs on Photoshop, using its very nifty Pixelize filter that would help getting the desired look. No AI was used to create the images, but it is noteworthy that Photoshop now uses inbuilt AI features, so we unfortunately cannot say that it's fully devoid of AI (although we strongly doubt that the Photoshop brush tool and a pixelize filter use any AI, we still wanted to be  fully transparent, considering the no AI-Policy of the course.)