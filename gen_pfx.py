#!/usr/bin/env python3
import json


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

def bursts(description):

    burstCount = integer("Number of particles to spawn in this burst")
    burstCountRange = integer("Number of particles to spawn +/- the burstCount")
    burstCountRange["default"] = 0

    burstChance = {
        "type": "number",
        "description": "Chance of spawning this burst.",
        "default": 1.0,
        "min": 0,
        "max": 1
    }

    burstBasic = {
        "type": "array",
        "items": [
            emitterTime(),
            burstCount,
            burstCountRange,
            burstChance
        ],
        "minItems": 2,
        "maxItems": 4
    }

    burstComplete = {
        "type": "object",
        "properties": {
            "time": emitterTime(),
            "count": integer("Number of particles to spawn in this burst"),
            "countRange": integer("Number +- of particles to spawn in this burst"),
            "chance": burstChance
        }
    }

    return {
        "description": description,
        "anyOf": [
            integer("number of particles to emit at time 0."),
            {
                "type": "array",
                "items": {
                    "anyOf": [
                        burstBasic,
                        burstComplete
                    ]
                }
            }
        ]
    }

def sRGBColor(description):
    return {
        "type": "integer",
        "min": 0,
        "max": 255,
        "description": description
    }

def rgbCurveColor():
    return {
        "type": "array",
        "items": [
            sRGBColor("red in sRGB space"),
            sRGBColor("green in sRBG space"),
            sRGBColor("blue in sRBG space"),
            sRGBColor("alpha in sRBG space"),
        ],
        "minItems": 3,
        "maxItems": 4
    }

def rgbCurve(description):
    return {
        "description": description
    }


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

def emitterTypeProperty():
    return {
        "description": "Defines the shape of the particle spawn positions, and how the offsetRange* keys are used.",
        "default": "POSITION",
        "oneOf": [
            { "const": "POSITION", "description": "Particles spawn anywhere in the interior of a box, centered on offset* with size offsetRange*" },
            { "const": "SPHEROID", "description": "Particles spawn anywhere in the interior of a sphere, centered on offset* with size offsetRange*" },
            { "const": "SHELL", "description": "Particles spawn on the shell of a sphere, centered on offset* with size offsetRange*" },
            { "const": "EMITTER", "description": "" },
            { "const": "CYLINDER_X", "description": "Particles spawn in a cylinder around the X axis. The offsetY,Z keys control the size of the cylinder, the offsetRangeY,Z controls the thickness of the cylinder. offsetX and offsetRangeX still control the position and offset range of the particles along the X axis." },
            { "const": "CYLINDER_Y", "description": "Particles spawn in a cylinder around the Y axis. The offsetX,Z keys control the size of the cylinder, the offsetRangeX,Z controls the thickness of the cylinder. offsetY and offsetRangeY still control the position and offset range of the particles along the Y axis." },
            { "const": "CYLINDER_Z", "description": "Particles spawn in a cylinder around the Z axis. The offsetX,Y keys control the size of the cylinder, the offsetRangeX,Y controls the thickness of the cylinder. offsetZ and offsetRangeZ still control the position and offset range of the particles along the Z axis." },
            { "const": "BOX_X", "description": "Like CYLINDER_X but box shaped." },
            { "const": "BOX_Y", "description": "Like CYLINDER_Y but box shaped." },
            { "const": "BOX_Z", "description": "Like CYLINDER_Z but box shaped." },
            { "const": "MESH", "description": "Spawn particles on the surface of a mesh." },
        ]
    }


schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "description": "Planetary Annihilation Particle System.",
    "type": "object",
    "properties": {
        "color": {
            "description": "A system wide color multiplier. Value is RGBA linear floats in array form.",
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": { "type": "number" }
        },
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

                    property("type", "POSITION", emitterTypeProperty()),

                    property( "linkIndex", -1, integer("Used with 'EMITTER' type to define which emitter to attached to.")),

                    property("offsetX", 0.0, emitterTimeCurve(number("Define the starting spawn position for particles in emitter space."))),
                    property("offsetY", 0.0, emitterTimeCurve(number("Define the starting spawn position for particles in emitter space."))),
                    property("offsetZ", 0.0, emitterTimeCurve(number("Define the starting spawn position for particles in emitter space."))),

                    property("offsetRangeX", 0.0, emitterTimeCurve(number("Define the starting spawn position range +/- the start position in emitter space."))),
                    property("offsetRangeY", 0.0, emitterTimeCurve(number("Define the starting spawn position range +/- the start position in emitter space."))),
                    property("offsetRangeZ", 0.0, emitterTimeCurve(number("Define the starting spawn position range +/- the start position in emitter space."))),

                    property("offsetAllowNegZ", True, boolean("Allow particles to spawn with an initial position with a negative Z in emitter space, otherwise flip Z to a positive position. Useful for explosions on the ground.")),

                    property("velocityX", 0.0, emitterTimeCurve(number( "Initial velocity direction in emitter space. Used to define a normalized vector direction."))),
                    property("velocityY", 0.0, emitterTimeCurve(number( "Initial velocity direction in emitter space. Used to define a normalized vector direction."))),
                    property("velocityZ", 0.0, emitterTimeCurve(number( "Initial velocity direction in emitter space. Used to define a normalized vector direction."))),
                    property("velocityRangeX", 0.0, emitterTimeCurve(number( "Initial velocity direction range +/- in emitter space. Used to define a normalized vector direction."))),
                    property("velocityRangeY", 0.0, emitterTimeCurve(number( "Initial velocity direction range +/- in emitter space. Used to define a normalized vector direction."))),
                    property("velocityRangeZ", 0.0, emitterTimeCurve(number( "Initial velocity direction range +/- in emitter space. Used to define a normalized vector direction."))),

                    property("useRadialVelocityDir", False, boolean( "Use the starting location as a normalized vector, added to the velocity direction values.")),
                    property("useShapeVelocityDir", False, boolean( "Use the starting position on the shape from the emitter’s type in addition to the velocity direction values.")),

                    property("velocity", 0.0, emitterTimeCurve( number("Initial particle velocity along velocity dir at spawn."))),
                    property("velocityRange", 0.0, emitterTimeCurve( number("Initial particle velocity range +/- velocity"))),

                    property("inheritedVelocity", 0.0, emitterTimeCurve(number( "Add the system’s velocity multiplied by this value to the initial particle velocity."))),

                    property("gravity", 0.0, emitterTimeCurve(number( "Particle gravity over the emitter lifetime. Always in world space towards the center of the planet. Affects all particles in the emitter. Value is in world units per second with negative numbers going towards the planet center."))),

                    property("accelX", 0.0, emitterTimeCurve(number( "Particle acceleration over the emitter lifetime in emitter space. Affects all particles in the emitter. These values are absolute acceleration values and not normalized like velocity. (May have odd results with world space particles.)"))),
                    property("accelY", 0.0, emitterTimeCurve(number( "Particle acceleration over the emitter lifetime in emitter space. Affects all particles in the emitter. These values are absolute acceleration values and not normalized like velocity. (May have odd results with world space particles.)"))),
                    property("accelZ", 0.0, emitterTimeCurve(number( "Particle acceleration over the emitter lifetime in emitter space. Affects all particles in the emitter. These values are absolute acceleration values and not normalized like velocity. (May have odd results with world space particles.)"))),

                    property("drag", 0.0, emitterTimeCurve(number( "Particle velocity multiplier over the emitter lifetime. Affects all particles in the emitter. Note: a drag of 1.0 is no drag, a drag of 0.0 turns drag off which is the same thing. A real drag of 0.0 would disable all movement. Drag values greater than 1.0 will cause particles to accelerate."))),

                    property("sizeX", 1.0, emitterTimeCurve( number("Defines the particle size in world units."))),
                    property("sizeY", 1.0, emitterTimeCurve(number( "Defines the particle size in world units. Y is the same dimension as the velocity facing."))),
                    property("sizeRangeX", 0.0, emitterTimeCurve( number("Defines the particle size range in world units."))),
                    property("sizeRangeY", 0.0, emitterTimeCurve( number("Defines the particle size range in world units."))),

                    property("sizeRangeFlip", False, boolean( "Defines if the particle’s size can be negated on one or both axis. The result is it randomly chooses how the texture is flipped on particle spawn. Helps randomize the appearance of a particle especially if the texture used has a strong pattern.")),
                    property("sizeRangeFlipX", False, boolean( "Defines if the particle’s size can be negated on one or both axis. The result is it randomly chooses how the texture is flipped on particle spawn. Helps randomize the appearance of a particle especially if the texture used has a strong pattern.")),
                    property("sizeRangeFlipY", False, boolean( "Defines if the particle’s size can be negated on one or both axis. The result is it randomly chooses how the texture is flipped on particle spawn. Helps randomize the appearance of a particle especially if the texture used has a strong pattern.")),

                    property("sizeSquareAspect", False, boolean( "Force particles to be square. Defaults to true if no sizeY is defined.")),
                    property("sizeConstantAspect", False, boolean( "Force particles to have a constant sizeX:sizeY ratio when using sizeRangeX. Defaults to true if no sizeRangeY is defined.")),

                    property("rotation", 0.0, emitterTimeCurve(number( "Defines the initial particle rotation orientation. Value is in radians (about 6.2832 is one full rotation)."))),
                    property("rotationRange", 0.0, emitterTimeCurve(number( "Defines the initial particle rotation orientation range, +/- the initial rotation. Value is in radians (about 3.1416 encompasses the entire possible rotation range)."))),
                    property("rotationRate", 0.0, emitterTimeCurve(number( "Defines the particle rotation rate on spawned. Value is in radians per second (about 6.2832 will cause a particle to rotate one full rotation over a second)."))),
                    property("rotationRateRange", 0.0, emitterTimeCurve(number( "Defines the particle rotation rate range on spawn +/- the rotationRate. Value is in radians per second."))),


                    property("snapToSurface", False, boolean("Option to snap a particle’s spawn position to the ground mesh surface. Takes the offset location and traces towards the center of the planet. If the particle offset is underground it will snap to the surface. Will always snap to the highest point on the land. Does not test against units, only the planet surface mesh. **THIS IS EXPENSIVE, USE ONLY WHEN NEEDED!**")),
                    property("snapToSurfaceOffset", 0.0, emitterTimeCurve(number( "Particle spawn distance from the ground surface when using snapToSurface. Is always in a direction away from the planet center, not the surface normal."))),
                    property("snapToSurface", False, boolean( "Align velocity directions when using snapToSurface to make Z up from the planet center and -Y away from the emitter along the ground (specifically perpendicular from the direction to the planet center).")),

                    property("red", 1.0, emitterTimeCurve(number("Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),
                    property("green", 1.0, emitterTimeCurve(number("Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),
                    property("blue", 1.0, emitterTimeCurve(number("Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),
                    property("alpha", 1.0, emitterTimeCurve(number("Particle initial color multiplier in linear float color. Set at the time of each particle’s spawn."))),
                    
                    property("rgb", [0.0, 1.0, [255, 255, 255]], rgbCurve("Particle initial color multiplier in sRGB binary color form with a brightness.")),

                    property("useArmyColor", 0, integer("Use the system color multiplier (0), the primary team color (1), or secondary team color (2) for this emitter.")),
                    property("rampV", 0.0, emitterTimeCurve(number("Defines the initial V of the UV of the ramp texture in particle shaders that use it. Otherwise used in string particles to define texture repeat distance in world units."))),
                    property("rampRangeV", 0.0, emitterTimeCurve(number("Defines the initial V range of the UV of the ramp texture +/- the rampV in particle shaders that use it. Otherwise used in string particles to define the texture repeat distance +/- the rampV in world units."))),
                    property("rampOffsetV", False, boolean("Randomly offset the texture on string particles.")),

                    property("lifetime", 1.0, emitterTimeCurve(number("Defines initial particle lifetime in seconds."))),
                    property("lifetimeRange", 0.0, emitterTimeCurve(number("Defines initial particle lifetime range +/- the particle lifetime."))),

                    property("emitterLifetime", 1.0, number("Defines the emitter lifetime in seconds. This the length of time a looping emitter will repeat or how long a non-looping emitter will live before ceasing to emit particles. Particles will finish out their own lifetime after the emitterLifetime ends or a looping particle emitter is turned off.")),
                    property("delay", 0.0, number("Defines a delay in seconds before an emitter lifetime begins the first time. Note: if all of a particle system’s emitters are delayed the particle system may shut down before anything spawns.")),
                    property("delayRange", 0.0, number("Defines a delay range in seconds +/- the delay before an emitter lifetime begins the first time.")),

                    property("bLoop", True, boolean("Defines if an emitter should loop or happen only once.")),
                    property("loopCount", 0, integer("Defines how many times an emitter should loop before ending if bLoop is true. A value of 0 loops indefinitely, a value of 1 has the same behavior as bLoop set to false.")),
                    property("startLoop", 0.0, number("The emitter time in seconds at which each loop of the emitter should restart the lifetime at. Note: can be a negative value.")),
                    property("endLoop", 0.0, number("The emitter time in seconds at which each loop of the emitter should end before restarting the lifetime. A value of 0.0, a negative value, or a value greater than the emitterLifetime will use the emitterLifetime instead.")),

                    property("startDistance", 0.0, number("Disables emitter if camera is closer than this distance.")),
                    property("endDistance", 1.0, number("Disables emitter if camera is further than this distance.")),

                    property("useWorldSpace", False, boolean("Use world space instead of emitter space for particle position updates. Allows particles to be 'left behind' on a moving emitter.")),
                    property("useArcLengthSpace", False, boolean("Transform particle positions into arc length space. Effectively wraps positions around the planet surface")),
                    property("interpolateSpawn", False, boolean("Interpolate the position of world space particles on moving particle systems. Spreads the particles across the current and previous particle system positions to keep smooth position distributions.")),
                    property("killOnDeactivate", False, boolean("Immediately remove all particles in the emitter if the particle system is disabled. Mainly used on looping effects in the game. Does not kill particles when the emitter lifetime ends.")),

                    property("emissionBursts", 0, bursts("Define bursts of particles over the emitter's lifetime")),
                    property("emissionRate", 20.0, emitterTimeCurve(number("Define the number of particles per second to spawn. Defaults to 0.0 if emissionBursts is defined."))),
                    property("maxParticles", None, number("Max number of live particles allowed in the emitter at one time. This is not a running total, but a current living count limit. If left undefined it is generally 'smart'; it tries to determine the max number based on emit rate and particle lifetime.")),

                )
            }
        }
    }
}


with open("pfx-schema", "w") as f:
    json.dump(schema, f, indent=2)
