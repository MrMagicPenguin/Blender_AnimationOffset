# Rakas

Blender add-on to perform object duplication and offset animations.

In essence, this is an upgrade to Blender 2.8+ of the add-on [ARewO](https://www.blenderdiplom.com/en/downloads/537-arewo-gui-a-detailed-description.html) by Frederik Steinmetz.
At this time, *Rakas* supports linear offset of objects and animation offset for Action and Shapekey animation.

This plugin was originally designed as a work-around for moving the Array modifier into Unity since the modifier did not 
bake down in the way I had hoped. *Rakas* makes it easier to achieve similar functionality to Array keyframe animation
inside Blender, but without needing to use more expensive export formats like .OBJ sequences, or formats with limited
support like Alembic.

Planned future capabilities include UV Offsets for subsequent objects, and the Object and Path offset seen in the original ARewO plugin