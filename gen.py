#!/usr/bin/env python3
# import json


def enum(description, enumValues):
    return {
        "type": "string",
        "enum": enumValues,
        "description": description
    }


def integer(description):
    return {"type": "integer", "description": description}


def number(description):
    return {"type": "number",  "description": description}


def boolean(description):
    return {"type": "boolean", "description": description}


def particleTime():
    return {
        "type": "number",
        "description": "Time in normalized particle lifetime (0..1)."
    }


def emitterTime():
    return {
        "type": "number",
        "description": "Time in 'real time' of the emitter's lifetime."
    }


def timeCurveArray(timeType, valueType):
    return {
        "type": "array",
        "items": {
            "type": "array",
            "items": [
                timeType,
                valueType,
            ],
            "minItems": 2,
            "maxItems": 2
        }
    }


def timeCurveObject(timeType, valueType):
    return {
        "type": "object",
        "properties": {
            "keys": timeCurveArray(timeType, valueType),
            "stepped": {
                "type": "boolean",
                "default": False,
                "description": "Control the interpolation between keyframes. Setting stepped to true means values don't change up until the new keyframe time arrives, at which point it snaps immediately. By default values are smoothed linearly between times."
            }
        }
    }


def timeCurve(timeType, valueType):
    return {
        "description": valueType["description"],
        "anyOf": [
            valueType,
            timeCurveArray(timeType, valueType),
            timeCurveObject(timeType, valueType),
        ],
    }


def particleTimeCurve(valueType):
    # , "Particle time curves are normalized to the particle's lifetime.")
    return timeCurve(particleTime(), valueType)


def emitterTimeCurve(valueType):
    # , "A curve in 'real time', matching against the current emitter's lifetime.")
    return timeCurve(emitterTime(), valueType)


def rgbCurve():
    pass


def property(names, default, valueType):
    if isinstance(names, str):
        names = [names]

    properties = {}
    for name in names:
        properties[name] = {
            "default": default,
        }
        properties[name].update(valueType)

    return properties


def merge(*args):
    merged = {}
    for p in args:
        merged.update(p)
    return merged


schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "description": "Planetary Annihilation Particle System.",
    "type": "object",
    "properties": {
        "emitters": {
            "description": "A list of emitter objects in the system.",
            "type": "array",
            "items": {
                "description": "Particle Emitter",
                "type": "object",
                "properties": merge(
                    property("spec", {}, {
                        "description": "Particle spec definition",
                        # particle spec properties
                    }),

                    property("type", "POSITION", enum("Defines the shape of the particle spawn positions, and how the offsetRange* keys are used.", [
                             "POSITION", "SPHEROID", "SHELL", "EMITTER", "CYLINDER_X", "CYLINDER_Y", "CYLINDER_Z", "BOX_X", "BOX_Y", "BOX_Z", "MESH"])),

                    property(
                        "linkIndex", -1, integer("Used with 'EMITTER' type to define which emitter to attached to.")),

                    property("offsetX", 0.0, emitterTimeCurve(
                        number("Define the starting spawn position for particles in emitter space."))),
                    property("offsetY", 0.0, emitterTimeCurve(
                        number("Define the starting spawn position for particles in emitter space."))),
                    property("offsetZ", 0.0, emitterTimeCurve(
                        number("Define the starting spawn position for particles in emitter space."))),

                    property("offsetRangeX", 0.0, emitterTimeCurve(number(
                        "Define the starting spawn position range +/- the start position in emitter space."))),
                    property("offsetRangeY", 0.0, emitterTimeCurve(number(
                        "Define the starting spawn position range +/- the start position in emitter space."))),
                    property("offsetRangeZ", 0.0, emitterTimeCurve(number(
                        "Define the starting spawn position range +/- the start position in emitter space."))),

                    property("offsetAllowNegZ", True, boolean(
                        "Allow particles to spawn with an initial position with a negative Z in emitter space, otherwise flip Z to a positive position. Useful for explosions on the ground.")),

                    property("velocityX", 0.0, emitterTimeCurve(number(
                        "Initial velocity direction in emitter space. Used to define a normalized vector direction."))),
                    property("velocityY", 0.0, emitterTimeCurve(number(
                        "Initial velocity direction in emitter space. Used to define a normalized vector direction."))),
                    property("velocityZ", 0.0, emitterTimeCurve(number(
                        "Initial velocity direction in emitter space. Used to define a normalized vector direction."))),
                    property("velocityRangeX", 0.0, emitterTimeCurve(number(
                        "Initial velocity direction range +/- in emitter space. Used to define a normalized vector direction."))),
                    property("velocityRangeY", 0.0, emitterTimeCurve(number(
                        "Initial velocity direction range +/- in emitter space. Used to define a normalized vector direction."))),
                    property("velocityRangeZ", 0.0, emitterTimeCurve(number(
                        "Initial velocity direction range +/- in emitter space. Used to define a normalized vector direction."))),

                    property("useRadialVelocityDir", False, boolean(
                        "Use the starting location as a normalized vector, added to the velocity direction values.")),
                    property("useShapeVelocityDir", False, boolean(
                        "Use the starting position on the shape from the emitter’s type in addition to the velocity direction values.")),

                    property("velocity", 0.0, emitterTimeCurve(
                        number("Initial particle velocity along velocity dir at spawn."))),
                    property("velocityRange", 0.0, emitterTimeCurve(
                        number("Initial particle velocity range +/- velocity"))),

                    property("inheritedVelocity", 0.0, emitterTimeCurve(number(
                        "Add the system’s velocity multiplied by this value to the initial particle velocity."))),

                    property("gravity", 0.0, emitterTimeCurve(number(
                        "Particle gravity over the emitter lifetime. Always in world space towards the center of the planet. Affects all particles in the emitter. Value is in world units per second with negative numbers going towards the planet center."))),

                    property("accelX", 0.0, emitterTimeCurve(number(
                        "Particle acceleration over the emitter lifetime in emitter space. Affects all particles in the emitter. These values are absolute acceleration values and not normalized like velocity. (May have odd results with world space particles.)"))),
                    property("accelY", 0.0, emitterTimeCurve(number(
                        "Particle acceleration over the emitter lifetime in emitter space. Affects all particles in the emitter. These values are absolute acceleration values and not normalized like velocity. (May have odd results with world space particles.)"))),
                    property("accelZ", 0.0, emitterTimeCurve(number(
                        "Particle acceleration over the emitter lifetime in emitter space. Affects all particles in the emitter. These values are absolute acceleration values and not normalized like velocity. (May have odd results with world space particles.)"))),

                    property("drag", 0.0, emitterTimeCurve(number(
                        "Particle velocity multiplier over the emitter lifetime. Affects all particles in the emitter. Note: a drag of 1.0 is no drag, a drag of 0.0 turns drag off which is the same thing. A real drag of 0.0 would disable all movement. Drag values greater than 1.0 will cause particles to accelerate."))),

                    property("sizeX", 0.0, emitterTimeCurve(
                        number("Defines the particle size in world units."))),
                    property("sizeY", 0.0, emitterTimeCurve(number(
                        "Defines the particle size in world units. Y is the same dimension as the velocity facing."))),
                    property("sizeRangeX", 0.0, emitterTimeCurve(
                        number("Defines the particle size range in world units."))),
                    property("sizeRangeY", 0.0, emitterTimeCurve(
                        number("Defines the particle size range in world units."))),

                    property("sizeRangeFlip", False, boolean(
                        "Defines if the particle’s size can be negated on one or both axis. The result is it randomly chooses how the texture is flipped on particle spawn. Helps randomize the appearance of a particle especially if the texture used has a strong pattern.")),
                    property("sizeRangeFlipX", False, boolean(
                        "Defines if the particle’s size can be negated on one or both axis. The result is it randomly chooses how the texture is flipped on particle spawn. Helps randomize the appearance of a particle especially if the texture used has a strong pattern.")),
                    property("sizeRangeFlipY", False, boolean(
                        "Defines if the particle’s size can be negated on one or both axis. The result is it randomly chooses how the texture is flipped on particle spawn. Helps randomize the appearance of a particle especially if the texture used has a strong pattern.")),

                    property("sizeSquareAspect", False, boolean(
                        "Force particles to be square. Defaults to true if no sizeY is defined.")),

                    property("sizeConstantAspect", False, boolean(
                        "Force particles to have a constant sizeX:sizeY ratio when using sizeRangeX. Defaults to true if no sizeRangeY is defined.")),


                    property("rotation", 0.0, emitterTimeCurve(number(
                        "Defines the initial particle rotation orientation. Value is in radians (about 6.2832 is one full rotation)."))),
                    property("rotationRange", 0.0, emitterTimeCurve(number(
                        "Defines the initial particle rotation orientation range, +/- the initial rotation. Value is in radians (about 3.1416 encompasses the entire possible rotation range)."))),

                    property("rotationRate", 0.0, emitterTimeCurve(number(
                        "Defines the particle rotation rate on spawned. Value is in radians per second (about 6.2832 will cause a particle to rotate one full rotation over a second)."))),
                    property("rotationRateRange", 0.0, emitterTimeCurve(number(
                        "Defines the particle rotation rate range on spawn +/- the rotationRate. Value is in radians per second."))),


                    property("snapToSurface", False, boolean("Option to snap a particle’s spawn position to the ground mesh surface. Takes the offset location and traces towards the center of the planet. If the particle offset is underground it will snap to the surface. Will always snap to the highest point on the land. Does not test against units, only the planet surface mesh. **THIS IS EXPENSIVE, USE ONLY WHEN NEEDED!**")),
                    property("snapToSurfaceOffset", 0.0, emitterTimeCurve(number(
                        "Particle spawn distance from the ground surface when using snapToSurface. Is always in a direction away from the planet center, not the surface normal."))),
                    property("snapToSurface", False, boolean(
                        "Align velocity directions when using snapToSurface to make Z up from the planet center and -Y away from the emitter along the ground (specifically perpendicular from the direction to the planet center).")),


                    property("red", 0.0, emitterTimeCurve(number(
                        "Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),
                    property("green", 0.0, emitterTimeCurve(number(
                        "Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),
                    property("blue", 0.0, emitterTimeCurve(number(
                        "Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),
                    property("alpha", 0.0, emitterTimeCurve(number(
                        "Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),

                )
            }
        }
    }
}

properties = []
