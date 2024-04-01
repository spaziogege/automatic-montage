import opentimelineio as otio

def dr_zoom(x, y, keyframes = None):
  if keyframes is None:
    keyframes = {'x': [], 'y': []}
  if keyframes['x'] is None:
    keyframes['x'] = []
  if keyframes['y'] is None:
    keyframes['y'] = []
  
  key_frames_x = {}
  key_frames_y = {}

  for keyframe in keyframes['x']:
    key_frames_x[keyframe.time] = {
      "Value": keyframe.value,
      "Variant Type": "Double",
    }
  for keyframe in keyframes['y']:
    key_frames_y[keyframe.time] = {
      "Value": keyframe.value,
      "Variant Type": "Double",
    }

  return otio.schema.Effect(
      name="",
      effect_name="Resolve Effect",
      metadata={
          "Resolve_OTIO": {
              "Effect Name": "Transform",
              "Enabled": True,
              "Name": "Transform",
              "Parameters": [
                  {
                      "Default Parameter Value": 1.0,
                      "Key Frames": key_frames_x,
                      "Parameter ID": "transformationZoomX",
                      "Parameter Value": x, # 1.2199997901916505,
                      "Variant Type": "Double",
                      "maxValue": 100.0,
                      "minValue": 0.0
                  },
                  {
                      "Default Parameter Value": 1.0,
                      "Key Frames": key_frames_y,
                      "Parameter ID": "transformationZoomY",
                      "Parameter Value": y, # 1.2199997901916505,
                      "Variant Type": "Double",
                      "maxValue": 100.0,
                      "minValue": 0.0
                  }
              ],
              "Type": 2
          }
      },
  )

"""
{
                                "OTIO_SCHEMA": "Effect.1",
                                "metadata": {
                                    "Resolve_OTIO": {
                                        "Effect Name": "Transform",
                                        "Enabled": true,
                                        "Name": "Transform",
                                        "Parameters": [
                                            {
                                                "Default Parameter Value": 1.0,
                                                "Key Frames": {},
                                                "Parameter ID": "transformationZoomX",
                                                "Parameter Value": 1.2199997901916505,
                                                "Variant Type": "Double",
                                                "maxValue": 100.0,
                                                "minValue": 0.0
                                            },
                                            {
                                                "Default Parameter Value": 1.0,
                                                "Key Frames": {},
                                                "Parameter ID": "transformationZoomY",
                                                "Parameter Value": 1.2199997901916505,
                                                "Variant Type": "Double",
                                                "maxValue": 100.0,
                                                "minValue": 0.0
                                            }
                                        ],
                                        "Type": 2
                                    }
                                },
                                "name": "",
                                "effect_name": "Resolve Effect"
                            }
"""