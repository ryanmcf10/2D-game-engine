# 2D-game-engine #
A 2D game engine written in Python.
Quickly create a a navigatable overworld using .tmx map files and .json files for NPC info.

Requires PyGame (http://www.pygame.org/download.shtml), PyTMX (https://github.com/bitcraft/PyTMX), PyScroll (https://github.com/bitcraft/pyscroll)

## HOW TO USE ##
* Create .tmx maps using an editor such as Tiled (www.mapeditor.org)
* Using object layers, create meta data for the world:
    * Blockers - create blocker objects to restrict player movement (walls, trees, rocks, etc)\n
        * object-name: blocker, object-type: blocker\n
    * NPCs - create NPC objects to place NPC spawn positions:\n
        *object-name: npc, object-tpy: npc-ID-number (from npc .json file)\n
    * Signs - create sign objects for players to read:
        * object-name: sign, object-type: message
    * Player - create a player object to set player spawn position:
        * object-name: player, object-type: player

## TO DO ##
LAYERS
* Player does not always appear behind 'Top' layer

NPCs
* Collisions with NPC
* Automated NPC movement
* Interaction with NPCs

