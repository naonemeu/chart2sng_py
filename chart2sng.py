import sys
import os
import re

#Do not change this function, only write in the way it is.
def parse_sync_track_section(f, res):
    bpm_sync = []  # Initialize list to store BPM markers

    # Flag to indicate if inside [SyncTrack] section
    in_sync_track_section = False

    for line in f:
        line = line.strip()  # Remove leading/trailing whitespace
        
        # Check if the section ends
        if line == "}":
            break

        # Check if the line contains a BPM marker
        if "= B" in line:
            parts = line.split("=")
            bpm_pos = int(parts[0].strip())
            bpm_value = int(parts[1].split("B")[1].strip())
            tick = 60000 / (bpm_value * res)
            bpm_sync.append((bpm_pos, bpm_value, tick))  # Append BPM marker to list

    return bpm_sync


#Do not change this function, only write in the way it is.
def parse_notes_section(f):
    button_notes = []  # Initialize list to store note positions
    sp_notes = []   # Initialize list to store special notes

    # Flag to indicate if inside [ExpertSingle] section
    in_notes_section = False

    for line in f:
        line = line.strip()  # Remove leading/trailing whitespace
        
        # Check if the section ends
        if line == "}":
            break

        # Check if the line contains a note position
        if "= N" in line:
            parts = line.split("=")
            note_pos = int(parts[0].strip())
            note_but, note_dur = map(int, parts[1].split("N")[1].split())
            if note_but <= 4:  # Ignore forced notes
                button_notes.append((note_pos, note_but, note_dur))  # Append note position to list
            if note_but == 7:  # Open Note
                button_notes.append((note_pos, 0, note_dur))  # Append note position to list
        # Check if the line contains a special note
        elif "= S 2 " in line:
            parts = line.split("=")
            sp_pos = int(parts[0].strip())
            sp_dur = int(parts[1].split("S 2")[1].strip())
            sp_notes.append((sp_pos, sp_dur))  # Append special note to list

    return button_notes, sp_notes


#Do not change this function, only write in the way it is.
def transform_note_positions(note_positions, bpm_markers, sp_notes):
    transformed_positions = []
    bpm_index = 0  # Initialize the index of the current BPM marker
    time = 0  # Initialize absolute time
    prev_pos = None  # Initialize previous note position
    
    for i, (pos, but, dur) in enumerate(note_positions):
        # Calculate delta time since the previous note
        if i > 0:
            delta_ticks = pos - prev_pos
        else:
            delta_ticks = pos - bpm_markers[bpm_index][0]  # First note: calculate delta time since the first BPM marker
        delta_time = delta_ticks * bpm_markers[bpm_index][2]  # Delta time in milliseconds
        
        time += delta_time  # Update absolute time
        
        tick = bpm_markers[bpm_index][2]  # Use the tick value from the current BPM marker
        transformed_pos = round(time, 3)  # Calculate absolute time for note position
        transformed_dur = round(dur * tick, 3)  # Calculate absolute time for note duration
        
        # Check if the note position is under the special line
        note_is_sp = 0
        for sp_pos, sp_dur in sp_notes:
            if sp_pos <= pos <= sp_pos + sp_dur:
                note_is_sp = 1  # Set note_is_sp to 1 if under special line
                break
        
        # Append the transformed position, button, duration, special value,
        # non-transformed note position, current BPM, and current tick
        transformed_positions.append((transformed_pos, but, transformed_dur, note_is_sp, pos,
                                      bpm_markers[bpm_index][1], round(tick * 1000, 3)))
        
        # Update previous note position
        prev_pos = pos
        
        # Move to the next BPM marker if the current position is beyond it
        if bpm_index < len(bpm_markers) - 1 and pos >= bpm_markers[bpm_index + 1][0]:
            bpm_index += 1
            
    return transformed_positions

#Do not make drastic changes in the way this function works.
def parse_chart_file(file_path):
    bpm_sync = []  # Initialize list to store BPM markers
    button_notes_expert = []  # Initialize list to store note positions for Expert difficulty
    sp_notes_expert = []   # Initialize list to store special notes for Expert difficulty
    button_notes_hard = []  # Initialize list to store note positions for Hard difficulty
    button_notes_medium = []  # Initialize list to store note positions for Medium difficulty
    button_notes_easy = []  # Initialize list to store note positions for Easy difficulty
    res = None  # Initialize resolution variable

    # Open the .chart file for reading
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()  # Remove leading/trailing whitespace
            
            if line.startswith("Resolution"):
                # Parse the resolution value
                res = int(line.split("=")[1].strip())
            elif line == "[SyncTrack]":
                # Parse the [SyncTrack] section
                bpm_sync = parse_sync_track_section(f, res)
            elif line == "[ExpertSingle]":
                # Parse the [ExpertSingle] section
                button_notes_expert, sp_notes_expert = parse_notes_section(f)
            elif line == "[HardSingle]":
                # Parse the [HardSingle] section
                button_notes_hard, _ = parse_notes_section(f)
            elif line == "[MediumSingle]":
                # Parse the [MediumSingle] section
                button_notes_medium, _ = parse_notes_section(f)
            elif line == "[EasySingle]":
                # Parse the [EasySingle] section
                button_notes_easy, _ = parse_notes_section(f)

    return res, bpm_sync, button_notes_expert, sp_notes_expert, button_notes_hard, button_notes_medium, button_notes_easy

#Do not change this function, only write in the way it is.
def write_sng_file(transformed_positions, file_path, song_info, duration):
    with open(file_path, 'w', encoding="utf-8") as f:
        # Comments goes here
        f.write('<!-- chart2sng - Naonemeu + ChatGPT-->\n')
        f.write('<!-- Link: https://github.com/naonemeu/chart2sng_py -->\n')
        f.write('<!-- Nota: Esse script ignora notas forcadas, e le Open Notes como se fosse a nota verde. -->\n')
        f.write('<!-- Ajuste a linha final se necessario! Ha uma nota filler no final, pois o GF1 nao le a ultima nota -->\n')
        f.write('<?xml version="1.0"?>\n')
        # Write the header of the XML-like file
        f.write('<Song>\n')
        f.write('    <Properties>\n')
        f.write('        <Version>0.1</Version>\n')
        f.write(f'        <Title>{song_info[0]}</Title>\n')
        f.write(f'        <Artist>{song_info[1]} - Charter: {song_info[2]}</Artist>\n')
        f.write('        <Album>Vazio</Album>\n')
        f.write('        <Year>Vazio</Year>\n')
        f.write('        <BeatsPerSecond>24.0</BeatsPerSecond>\n')
        f.write('        <BeatOffset>0.0</BeatOffset>\n')
        f.write('        <HammerOnTime>0.25</HammerOnTime>\n')
        f.write('        <PullOffTime>0.25</PullOffTime>\n')
        f.write('        <Difficulty>EXPERT</Difficulty>\n')
        f.write('        <AllowableErrorTime>0.25</AllowableErrorTime>\n')
        f.write(f'        <Length>{duration}</Length>\n')
        f.write('        <MusicFileName>song.mp3</MusicFileName>\n')
        f.write('        <MusicDirectoryHint>C:/</MusicDirectoryHint>\n')
        f.write('    </Properties>\n')
        f.write('\n    <Data>\n')

        # Write the transformed note positions
        for pos, but, dur, special, noteppq, bpm, tick in transformed_positions:
            f.write(f'        <Note time="{pos}" duration="{dur}" track="{but}" special="{special}" noteppq="{noteppq / 192}" bpm="{bpm}" tick="{tick}"/>\n')
            
        #Filler note
        f.write(f'        <Note time="{duration+1000}" duration="0" track="0" special="0"/> <!-- Filler note -->\n ')

        # Write the footer of the XML-like file
        f.write('    </Data>\n')
        f.write('</Song>')
        
def parse_song_info(file_path):
    song_info = ['', '', '']  # Initialize list to store song information

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        # Flag to indicate if inside [Song] section
        in_song_section = False

        for line in f:
            line = line.strip()  # Remove leading/trailing whitespace

            if line == "[Song]":
                in_song_section = True
                continue
            elif line == "}":
                break

            if in_song_section:
                # Extract and store information using regex
                match = re.match(r'\s{0,2}(.*?)\s*=\s*"(.*?)"\s*', line)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if key == "Name":
                        song_info[0] = value
                    elif key == "Artist":
                        song_info[1] = value
                    elif key == "Charter":
                        song_info[2] = value

    return song_info

    
def main():
    print("\n...chart2sng (Freetar) 0.1 - Naonemeu + ChatGPT")
    print("\nIMPORTANTE!\nAbra o notes.sng para realizar ajustes finais, como remover a ultima nota, para o GF2 ou GF3")
    print("\IMPORTANT!\nOpen the notes.sng file to do final adjustment, such as removing the last note if you play GF2 or GF3")


    if len(sys.argv) != 2:
        print("Arraste um .chart ou digite pelo prompt de comando: chart2sng.py (arquivo).chart")
        input()
        return

    chart_file_path = sys.argv[1]
    
    # Get the directory path of the input file
    input_dir = os.path.dirname(chart_file_path)

    resolution, bpm_markers, note_positions_expert, sp_notes_expert, note_positions_hard, note_positions_medium, note_positions_easy = parse_chart_file(chart_file_path)

    transformed_positions_expert = transform_note_positions(note_positions_expert, bpm_markers, sp_notes_expert)
    transformed_positions_hard = transform_note_positions(note_positions_hard, bpm_markers, sp_notes_expert)
    transformed_positions_medium = transform_note_positions(note_positions_medium, bpm_markers, sp_notes_expert)
    transformed_positions_easy = transform_note_positions(note_positions_easy, bpm_markers, sp_notes_expert)

    song_info = parse_song_info(chart_file_path)

    duration = 0

    if transformed_positions_expert:
        last_note_pos_expert, _, last_note_dur_expert, _, _, _, _ = transformed_positions_expert[-1]
        duration = int(last_note_pos_expert + last_note_dur_expert + 3)

    print("Song Information:", song_info)
    print("Duration of Expert track:", duration)

    write_sng_file(transformed_positions_expert, os.path.join(input_dir, "notes4.sng"), song_info, duration)
    write_sng_file(transformed_positions_hard, os.path.join(input_dir, "notes3.sng"), song_info, duration)
    write_sng_file(transformed_positions_medium, os.path.join(input_dir, "notes2.sng"), song_info, duration)
    write_sng_file(transformed_positions_easy, os.path.join(input_dir, "notes1.sng"), song_info, duration)

if __name__ == "__main__":
    main()

# # Example usage:
# chart_file_path = "example.chart"
# resolution, bpm_markers, note_positions_expert, sp_notes_expert, note_positions_hard, note_positions_medium, note_positions_easy = parse_chart_file(chart_file_path)

# # Transform note positions for each difficulty level
# transformed_positions_expert = transform_note_positions(note_positions_expert, bpm_markers, sp_notes_expert)
# transformed_positions_hard = transform_note_positions(note_positions_hard, bpm_markers, sp_notes_expert)
# transformed_positions_medium = transform_note_positions(note_positions_medium, bpm_markers, sp_notes_expert)
# transformed_positions_easy = transform_note_positions(note_positions_easy, bpm_markers, sp_notes_expert)

# # Song information
# song_info = parse_song_info(chart_file_path)
# print("Song Information:", song_info)

# song_info = ["This part is not done yet","you'll have to do it manually"]

# # Initialize variable to store the duration of the track
# duration = 0

# # Find the position of the last note and its duration for the expert level
# if transformed_positions_expert:
    # last_note_pos_expert, _, last_note_dur_expert, _, _, _, _ = transformed_positions_expert[-1]
    # duration = int(last_note_pos_expert + last_note_dur_expert + 3)  

# # Print the duration of the expert track
# print("Duration of Expert track:", duration)

# # Write .sng files for each difficulty level
# write_sng_file(transformed_positions_expert, "notes4.sng", song_info)
# write_sng_file(transformed_positions_hard, "notes3.sng", song_info)
# write_sng_file(transformed_positions_medium, "notes2.sng", song_info)
# write_sng_file(transformed_positions_easy, "notes1.sng", song_info)

# # Print parsed data
# # print("\nResolution (ppq):", resolution)
# # print("BPM markers (Position, BPM in beats per ms, tick in ms):",
      # # [(pos, bpm, round(tick * 1000, 3)) for pos, bpm, tick in bpm_markers])
# # print("\nFirst 50 note positions (Position, button, sustain) in ppq:\n", note_positions[:50])
# # print("\nFirst 50 transformed positions (Position, button, sustain, special, noteppq, bpm, tick) in seconds:\n", transformed_positions[:50])
    
