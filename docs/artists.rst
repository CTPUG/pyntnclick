Artists HOWTO
=============

This is a guide to contributing artwork to Suspended Sentence.

Suspended Sentence is a point-and-click adventure game. It is set on a derelict
spaceship carrying prisoners in cryosleep to a prison planet. The ship has
experienced a catastrophic accident and after drifting for many years the AI
has begun to effect repairs. Some repairs the AI cannot perform itself so it
has been waking the prisoners up one by one to effect repairs. A few such
prisoners have died or gone insane. The adventure starts with the latest
prisoner being awakened from cryo sleep. The AI's name is Jim.

Broadly artwork for the game can be divided into artwork for Scenes, Things and
Items.

Scenes are the background against which all the other action takes place.  Each
scene consists primarily of a 24-bit colour, 800x600 pixel image. For example,
our first scene is a room filled with cryogenic chambers.

Things are rendered on top of a particular scene and are used to add animation
and areas for the user to interact with. A Thing might be a door the player can
open, a puddle of dripping water or something for the player to pick up. A Thing
can be any size up to the full size of the Scene and may use an alpha channel
for transparency. For example, the cryochamber scene has individual cryochambers
that can be inspected, a corpse with a titanium prosthetic leg and a door that
needs to be levered open using the prostethic leg.

Items are objects the player has picked up and which can appear in his or her
inventory. Typically Items are picked up by clicking on a Thing. Items require
two different images: an inventory bar icon and a cursor. The inventory bar
icon should be a 50x50 pixel image on a transparent background. The cursor should
be a similar size and will often use the same image as the inventory icon.

Complex Items that the user might need to interact with (for example, to repair
it or change its settings) are handled by associating a Scene with the object. The
Scene background is then an enlarged view of the object.

Our preferred image formats are PNG and SVG. PNGs are what Suspended Sentence
loads images from. SVGs are more of a pain to produce but are convenient for
generating multiple PNGs at different sizes.
