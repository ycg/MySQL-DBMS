# -*- coding: utf-8 -*-

import json

import entity

B = 1024
KB = B * 1024
M = KB * 1024
G = M * 1024
T = G * 1024


def convert_for_byte(byte_value):
    if (byte_value == 0):
        return "0"
    if (byte_value < B):
        return str(byte_value) + "B"
    elif (byte_value < KB):
        return str(int(byte_value / B)) + "KB"
    elif (byte_value < M):
        return str(int(byte_value / KB)) + "M"
    elif (byte_value < G):
        return str(round(float(byte_value) / float(M), 2)) + "G"
    elif (byte_value < T):
        return str(round(float(byte_value) / float(G), 2)) + "T"


def convert_to_object_from_post_data(post_data):
    if (post_data is None or len(post_data) <= 0):
        return None
    obj = entity.Entity()
    for key, value in json.loads(post_data).items():
        if (len(str(value)) <= 0):
            setattr(obj, key, value)
        elif (str(value).isdigit()):
            setattr(obj, key, int(value))
        else:
            if (value == "null"):
                setattr(obj, key, None)
            else:
                setattr(obj, key, value)
    return obj
