#!/usr/bin/env python3
import subprocess
import os

def process_file_phase1(filename, min_volume):
    output_file = f"/home/atom/Dropbox/FLAX/upsampled/{filename}.wav"
    input_file = f"{filename}.flac"
    restart_required = True

    while restart_required:
        # Upsample FLAC to WAV with volume reduction
        print(f"Phase 1: Upsampling {filename} to .wav with a high-tap sinc filter:")
        sox_command = f'sox -V3 "{input_file}" -b 24 -r 2822400 "{output_file}" upsample 64 sinc -22050 -n 16777216 -L -b 0 vol "{min_volume}"'

        # Run the sox command and capture stdout in real-time
        process = subprocess.Popen(sox_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        # Read and print each line of the output
        for line in process.stdout:
            print(line, end='')

            # Check for clipping in the output
            if "clipped" in line.lower():
                # Clipping detected, decrease volume and set restart flag
                min_volume -= 1
                print(f"Clipping detected in {input_file}. Decreasing volume to {min_volume}x and restarting...")
                restart_required = True
                break

        # Wait for the process to finish
        process.wait()

        if not restart_required:
            break  # Exit the loop if no restart is required

    return min_volume  # Return the updated volume

def process_file_phase2(filename):
    dsf_output_file = f"/home/atom/Dropbox/FLAX/upsampled/{filename}.dsf"
    wav_input_file  = f"/home/atom/Dropbox/FLAX/upsampled/{filename}.wav"

    # Phase 2: Convert WAV to DSD with extreme settings
    print(f"Phase 2: Converting {wav_input_file} to DSD:")
    sox_command = f'sox -V3 "{wav_input_file}" "{dsf_output_file}" rate -v 2822400 sdm -f clans-8 -t 24 -n 32'

    # Run the sox command and capture stdout in real-time
    process = subprocess.Popen(sox_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    while True:
        # Read and print each line of the output
        line = process.stdout.readline()
        if not line:
            break
        print(line, end='')

    # Wait for the process to finish
    process.wait()

    print(f"Finished processing {dsf_output_file}!")

    # Remove the WAV file after Phase 2 completion
    os.remove(wav_input_file)

def process_files():
    files = [f[:-5] for f in os.listdir('.') if f.endswith('.flac')]  # Get all .flac files in the current directory
    start_volume = 64

    min_volume = start_volume

    # Phase 1: Convert all FLAC files to WAV with volume reduction
    restart_required = True
    while restart_required:
        restart_required = False

        for filename in files:
            min_volume, restart = process_file_phase1(filename, min_volume)
            restart_required = restart_required or restart  # Update restart flag

    # Phase 2: Convert WAV to DSD with extreme settings and remove WAV files
    for filename in files:
        process_file_phase2(filename, min_volume)

# Start processing
process_files()
