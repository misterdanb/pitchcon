#!/usr/bin/env python3

import aubio
import numpy as np
import pyaudio
import sys
import time
import uinput
import toml
import argparse

CHANNELS = 1
FORMAT = pyaudio.paFloat32
METHOD = "default"

NOTE_MAP = {
    "C0": 16.35,
    "C#0": 17.32,
    "Db0": 17.32,
    "D0": 18.35,
    "D#0": 19.45,
    "Eb0": 19.45,
    "E0": 20.60,
    "F0": 21.83,
    "F#0": 23.12,
    "Gb0": 23.12,
    "G0": 24.50,
    "G#0": 25.96,
    "Ab0": 25.96,
    "A0": 27.50,
    "A#0": 29.14,
    "Bb0": 29.14,
    "B0": 30.87,
    "C1": 32.70,
    "C#1": 34.65,
    "Db1": 34.65,
    "D1": 36.71,
    "D#1": 38.89,
    "Eb1": 38.89,
    "E1": 41.20,
    "F1": 43.65,
    "F#1": 46.25,
    "Gb1": 46.25,
    "G1": 49.00,
    "G#1": 51.91,
    "Ab1": 51.91,
    "A1": 55.00,
    "A#1": 58.27,
    "Bb1": 58.27,
    "B1": 61.74,
    "C2": 65.41,
    "C#2": 69.30,
    "Db2": 69.30,
    "D2": 73.42,
    "D#2": 77.78,
    "Eb2": 77.78,
    "E2": 82.41,
    "F2": 87.31,
    "F#2": 92.50,
    "Gb2": 92.50,
    "G2": 98.00,
    "G#2": 103.83,
    "Ab2": 103.83,
    "A2": 110.00,
    "A#2": 116.54,
    "Bb2": 116.54,
    "B2": 123.47,
    "C3": 130.81,
    "C#3": 138.59,
    "Db3": 138.59,
    "D3": 146.83,
    "D#3": 155.56,
    "Eb3": 155.56,
    "E3": 164.81,
    "F3": 174.61,
    "F#3": 185.00,
    "Gb3": 185.00,
    "G3": 196.00,
    "G#3": 207.65,
    "Ab3": 207.65,
    "A3": 220.00,
    "A#3": 233.08,
    "Bb3": 233.08,
    "B3": 246.94,
    "C4": 261.63,
    "C#4": 277.18,
    "Db4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "Eb4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "Gb4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "Ab4": 415.30,
    "A4": 440.00,
    "A#4": 466.16,
    "Bb4": 466.16,
    "B4": 493.88,
    "C5": 523.25,
    "C#5": 554.37,
    "Db5": 554.37,
    "D5": 587.33,
    "D#5": 622.25,
    "Eb5": 622.25,
    "E5": 659.25,
    "F5": 698.46,
    "F#5": 739.99,
    "Gb5": 739.99,
    "G5": 783.99,
    "G#5": 830.61,
    "Ab5": 830.61,
    "A5": 880.00,
    "A#5": 932.33,
    "Bb5": 932.33,
    "B5": 987.77,
    "C6": 1046.50,
    "C#6": 1108.73,
    "Db6": 1108.73,
    "D6": 1174.66,
    "D#6": 1244.51,
    "Eb6": 1244.51,
    "E6": 1318.51,
    "F6": 1396.91,
    "F#6": 1479.98,
    "Gb6": 1479.98,
    "G6": 1567.98,
    "G#6": 1661.22,
    "Ab6": 1661.22,
    "A6": 1760.00,
    "A#6": 1864.66,
    "Bb6": 1864.66,
    "B6": 1975.53,
    "C7": 2093.00,
    "C#7": 2217.46,
    "Db7": 2217.46,
    "D7": 2349.32,
    "D#7": 2489.02,
    "Eb7": 2489.02,
    "E7": 2637.02,
    "F7": 2793.83,
    "F#7": 2959.96,
    "Gb7": 2959.96,
    "G7": 3135.96,
    "G#7": 3322.44,
    "Ab7": 3322.44,
    "A7": 3520.00,
    "A#7": 3729.31,
    "Bb7": 3729.31,
    "B7": 3951.07,
    "C8": 4186.01,
    "C#8": 4434.92,
    "Db8": 4434.92,
    "D8": 4698.63,
    "D#8": 4978.03,
    "Eb8": 4978.03,
    "E8": 5274.04,
    "F8": 5587.65,
    "F#8": 5919.91,
    "Gb8": 5919.91,
    "G8": 6271.93,
    "G#8": 6644.88,
    "Ab8": 6644.88,
    "A8": 7040.00,
    "A#8": 7458.62,
    "Bb8": 7458.62,
    "B8": 7902.13
}

def handle_args(args):
    parser = argparse.ArgumentParser(prog="Pitchcon", description="Pitchcon Simple tool using uinput to create an input device driven by pitch")
    parser.add_argument("-c", "--choose-input", help="Show a prompt to choose an input device", action="store_true")

    return parser.parse_args(args)

def choose_input_device(pa):
    info = pa.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    devices_list_str = ""
    for i in range(0, numdevices):
        if pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            devices_list_str += "{}: {}\n".format(i, pa.get_device_info_by_host_api_device_index(0, i)["name"])

    print("Choose input device:")
    print(devices_list_str)

    return int(input("Which one? "))

def main(args):
    parsed_args = handle_args(args[1:])
    print(parsed_args)

    pa = pyaudio.PyAudio()
    
    config = toml.load("Pitchcon.toml")
    used_keys = list(map(lambda x: getattr(uinput, x), config["Keys"].keys()))
    note_key_tuples = list(map(lambda x: (NOTE_MAP[x[1]], getattr(uinput, x[0])), config["Keys"].items()))

    hopsize = 1024

    if parsed_args.choose_input:
        chosen_input = choose_input_device(pa)
        mic = pa.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=config["Input"]["samplerate"],
                      input=True,
                      input_device_index=chosen_input,
                      frames_per_buffer=hopsize)
    else:
        mic = pa.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=config["Input"]["samplerate"],
                      input=True,
                      frames_per_buffer=hopsize)

    pDetection = aubio.pitch(METHOD,
                             2 * hopsize,
                             hopsize,
                             config["Input"]["samplerate"])
    pDetection.set_unit("Hz")
    pDetection.set_silence(-40)

    last_down = False
    last_key = None
    last_time = time.time()
    with uinput.Device(used_keys) as device:
        while True:
            current_time = time.time()

            data = mic.read(hopsize)
            samples = np.fromstring(data, dtype=aubio.float_type)

            pitch = pDetection(samples)[0]
            volume = np.sum(samples**2) / len(samples)

            if current_time - last_time > config["Input"]["clickinterval"] / 1000:
                hit_note = False
                for note, key in note_key_tuples:
                    if abs(pitch - note) < config["Input"]["tolerance"]:
                        if not last_down:
                            last_key = key
                            device.emit(key, 1)
                            time.sleep(config["Input"]["clickinterval"] / 5000)
                            current_time = time.time()

                        hit_note = True

                if not hit_note and last_down:
                    last_down = False
                    device.emit(last_key, 0)
                elif hit_note:
                    last_down = True

                last_time = current_time
        
if __name__ == "__main__":
    main(sys.argv)
