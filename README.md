This repository contains code from a part-time research project on mathematical and
algorithmic models of crystal aggregates for computer graphics. A crystal aggregate is a
group of crystals that have grown together - geodes, the crystal-lined hollows in rocks
common in souvenir stores, are a good example of a crystal aggregate.

The project has evolved over a number of years and a number of contributors, most of them
undergraduate students. During that evolution, my own ideas have changed, and I've
encouraged my students to explore their own questions when they wanted to. So the project
has lots of semi-independent lines of inquiry. Each line is more or less a separate branch
for Git, but that intention hasn't always been strictly enforced or respected - the branch
structure is, by now, something of a mess. But the following list of branches may help
people interested in this code understand what they're seeing:
* master. The latest version of the project - but "latest" isn't necessarily "best working."
* Lognormal. Explores the idea that the sizes of crystals tend to follow lognormal probability distributions. Also demonstrates that clipping crystals' shapes to their neighbors is not a good way to make them butt up against each other in natural-looking ways.
* AdaptiveSize. One of several explorations of adjusting crystal's sizes so that they butt up to neighbors in natural-looking ways.
* BSPTree. Explores Binary Space Partitioning Trees for tracking what regions of space a crystal occupies.
* NaiveTree. Explores other, less sophisticated, tree structures for tracking region occupancy.
* GrownCrystals. Explores using a model of how crystals grow to make them butt up against each other in natural-looking ways.

For more information on this project see

[https://www.geneseo.edu/~baldwin/CrystalGraphics/](https://www.geneseo.edu/~baldwin/CrystalGraphics/)