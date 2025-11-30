import sys
import os

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
        transformed_pos = round(time, 9)  # Calculate absolute time for note position
        transformed_dur = round(dur * tick, 9)  # Calculate absolute time for note duration
        
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
    with open(file_path, 'r') as f:
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
def write_sng_file(transformed_positions, file_path, song_info, duration,gf1fix):
    with open(file_path, 'w') as f:
        f.write('<?xml version="1.0"?>\n')
        # Comments goes here
        # f.write('<!-- chart2sng - Naonemeu + ChatGPT-->\n')
        # f.write('<!-- Link: https://github.com/naonemeu/chart2sng_py -->\n')
        # f.write('<!-- Nota: Esse script ignora notas forçadas, e le Open Notes como se fosse a nota verde. -->\n')
        # f.write('<!-- Ajuste a linha final se necessario! Ha uma nota filler no final, pois o GF1 nao le a ultima nota -->\n')
        # Write the header of the XML-like file
        f.write('<Song>\n')
        f.write('    <Properties>\n')
        f.write('        <Version>0.1</Version>\n')
        f.write(f'        <Title>{song_info[0]}</Title>\n')
        f.write(f'        <Artist>{song_info[1]} - Charter: {song_info[2]}</Artist>\n')
        f.write('        <Album>Vazio</Album>\n')
        f.write('        <Year>2008</Year>\n')
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
            #f.write(f'        <Note time="{pos}" duration="{dur}" track="{but}" special="{special}" noteppq="{noteppq}" bpm="{bpm}" tick="{tick}"/>\n')
            f.write(f'        <Note time="{pos}" duration="{dur}" track="{but}" special="{special}"/> \n')       
            
        #Filler note
        if gf1fix == True:
            f.write(f'        <Note time="{duration+1000}" duration="0" track="0" special="0"/> <!-- Filler note -->\n ')

        # Write the footer of the XML-like file
        f.write('    </Data>\n')
        f.write('</Song>')
        
import re
        
import re
import os

import re
import os

import re
import os

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
    
    
    
import os
import re
from collections import defaultdict

def fixlength(input_dir):
    """
    Opens four specific .sng files (notes1.sng to notes4.sng) and modifies the 'duration' 
    attribute for notes that share the same 'time' value (if duration > 0). 
    
    The fix sets all durations in that time group to the duration of the *last* note 
    in the group. This implementation uses regex and explicitly preserves 
    leading whitespace and original line endings (CRLF or LF).

    Args:
        input_dir (str): The directory containing the notesX.sng files.
    """

    # List of file names to process
    file_names = [f"notes{i}.sng" for i in range(1, 5)]

    # --- Regular Expression Definitions ---

    # 1. Regex to capture the entire <Note ... /> line, including starting whitespace.
    # Group 1 (named 'leading_ws'): Leading whitespace (for preservation)
    # Group 2: 'time' value
    # Group 3: 'duration' value
    # Group 4: The rest of the attributes
    NOTE_REGEX = re.compile(
        r'^(?P<leading_ws>\s*)'                        # Group 1 (named 'leading_ws'): Leading whitespace 
        r'<Note\s+'                                    # Start of <Note tag
        r'time="([\d\.]+)"\s+'                         # Group 2: time attribute
        r'duration="([\d\.]+)"\s*'                     # Group 3: duration attribute
        r'(.*?)'                                       # Group 4: The rest of the attributes (non-greedy)
        r'/>'                                          # End of the tag (excluding final newline/trailing ws)
    )
    
    # 2. Regex to capture the trailing whitespace/newline, including CRLF or LF.
    LINE_ENDING_REGEX = re.compile(r'(\s*)$') 

    for file_name in file_names:
        file_path = os.path.join(input_dir, file_name)
    #    print(f"Processing file: **{file_name}**")

        try:
            # Read the entire content as a single string to precisely capture all line endings
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split the content into lines, keeping the line endings attached to each line
            lines = content.splitlines(keepends=True)
            
        except FileNotFoundError:
            print(f" Error: File not found at {file_path}. Skipping.")
            continue
        except Exception as e:
            print(f" An error occurred reading {file_path}: {e}. Skipping.")
            continue

        ## 1. Scan and Group Lines by Time
        
        # time_groups will store {time_value: [line_index, ...]}
        time_groups = defaultdict(list)
        
        for i, line in enumerate(lines):
            # We use search() because splitlines(keepends=True) keeps the newline attached
            match = NOTE_REGEX.search(line)
            if match:
                time_val = match.group(2)    # Group 2 is 'time'
                duration_str = match.group(3) # Group 3 is 'duration'
                
                try:
                    duration = float(duration_str)
                    # Filter: Only consider lines with non-zero duration
                    if duration > 0.0:
                        time_groups[time_val].append(i)
                except ValueError:
                    # Ignore notes with invalid duration format
                    continue

        ## 2. Determine the Fixed Duration for Each Time Group
        
        # fix_durations will store {line_index: new_duration_string}
        fix_durations = {}
        for time_val, indices in time_groups.items():
            if len(indices) > 1:
                # The fix is based on the duration of the *last* note in the group.
                last_note_index = indices[-1]
                
                last_note_line = lines[last_note_index]
                last_match = NOTE_REGEX.search(last_note_line)
                
                if last_match:
                    new_duration_str = last_match.group(3) # Group 3 is 'duration'
                    
                    # Store the new duration for all lines in this group if they differ
                    for line_index in indices:
                        current_line = lines[line_index]
                        current_match = NOTE_REGEX.search(current_line)
                        if current_match and current_match.group(3) != new_duration_str:
                             fix_durations[line_index] = new_duration_str

        ## 3. Apply the Replacements Line-by-Line
        
        notes_modified_count = 0
        new_lines = []
        
        for i, line in enumerate(lines):
            # Check if this line needs fixing
            if i in fix_durations:
                new_duration_val = fix_durations[i]
                
                # Capture the line-ending/trailing whitespace for preservation
                ending_match = LINE_ENDING_REGEX.search(line)
                line_ending = ending_match.group(1) if ending_match else ""
                
                # Strip the line ending before substitution to process the tag cleanly
                line_to_process = line[:-len(line_ending)] if line_ending else line
                
                def replacer(match):
                    """Rebuilds the note tag with the new duration, preserving starting whitespace."""
                    
                    # Use named group for leading whitespace
                    leading_ws = match.group('leading_ws') 
                    
                    # Group 2: time, Group 4: rest of attributes
                    time_attr = f'time="{match.group(2)}"'
                    duration_attr = f'duration="{new_duration_val}"'
                    
                    # Reconstruct the entire line tag: 
                    # (Starting Whitespace) + <Note time="..." duration="..." rest.../>
                    return f'{leading_ws}<Note {time_attr} {duration_attr} {match.group(4)}/>'

                # Perform the substitution on the tag (without the line ending)
                modified_line_tag = NOTE_REGEX.sub(replacer, line_to_process)
                
                # Re-attach the original line ending
                modified_line = modified_line_tag + line_ending
                
                new_lines.append(modified_line)
                notes_modified_count += 1
            else:
                # No fix needed, keep the original line (with its original ending and starting whitespace)
                new_lines.append(line)

        # print(f"✅ Successfully processed {file_name}. Modified **{notes_modified_count}** note durations.")

        ## 4. Overwrite the File
        
        final_content = "".join(new_lines)
        
        try:
            # Write in text mode ('w'). Since final_content contains the original line endings, 
            # this preserves them.
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            # print(f"💾 Successfully wrote changes to {file_name}, preserving original line endings.")
        except Exception as e:
            print(f"❌ An error occurred writing to {file_path}: {e}")
    
    
    
    
    
    
    
    

    """
    Opens four specific .sng files and modifies the 'duration' attribute for notes
    that share the same 'time' value (if duration > 0), setting all durations
    in that time group to the duration of the last note in the group.
    
    This version ensures that the original line endings (CRLF or LF) are 
    preserved when overwriting the file.

    Args:
        input_dir (str): The directory containing the notesX.sng files.
    """

    # List of file names to process
    file_names = [f"notes{i}.sng" for i in range(1, 5)]

    # --- Regular Expression Definitions ---

    # Regex to capture the entire <Note ... /> line.
    # Group 1: 'time' value
    # Group 2: 'duration' value
    # Group 3: The rest of the attributes
    NOTE_REGEX = re.compile(
        r'^\s*<Note\s+'                                # Start of line and <Note tag
        r'time="([\d\.]+)"\s+'                         # Group 1: time attribute
        r'duration="([\d\.]+)"\s*'                     # Group 2: duration attribute
        r'(.*?)'                                       # Group 3: The rest of the attributes (non-greedy)
        r'/>'                                          # End of the tag (excluding final whitespace/newline)
    )
    
    # Regex to capture the trailing newline/whitespace, including CRLF or LF.
    # We will use this to re-append the newline after substitution.
    LINE_ENDING_REGEX = re.compile(r'(\s*)$')


    for file_name in file_names:
        file_path = os.path.join(input_dir, file_name)
        print(f"Processing file: **{file_name}**")

        try:
            # Read the entire content as a single string to preserve line endings exactly
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split the content into lines, keeping the line endings attached to each line
            # This is safer than readlines() as it gives us explicit control
            lines = content.splitlines(keepends=True)
            
        except FileNotFoundError:
            print(f"🚫 Error: File not found at {file_path}. Skipping.")
            continue
        except Exception as e:
            print(f"❌ An error occurred reading {file_path}: {e}. Skipping.")
            continue

        # --- 1. Scan and Group Lines by Time ---
        # time_groups will store {time_value: [line_index, ...]}
        time_groups = defaultdict(list)
        
        for i, line in enumerate(lines):
            # We must search for the NOTE_REGEX *before* the line ending
            match = NOTE_REGEX.search(line)
            if match:
                time_val = match.group(1)
                duration_str = match.group(2)
                
                try:
                    duration = float(duration_str)
                    # Filter: Only consider lines with non-zero duration
                    if duration > 0.0:
                        time_groups[time_val].append(i)
                except ValueError:
                    continue

        # --- 2. Determine the Fixed Duration for Each Time Group ---
        # fix_durations will store {line_index: new_duration_string}
        fix_durations = {}
        for time_val, indices in time_groups.items():
            if len(indices) > 1:
                # The fix is based on the duration of the *last* note in the group.
                last_note_index = indices[-1]
                
                last_note_line = lines[last_note_index]
                last_match = NOTE_REGEX.search(last_note_line)
                
                if last_match:
                    new_duration_str = last_match.group(2)
                    
                    # Store the new duration for all lines in this group if they differ
                    for line_index in indices:
                        current_line = lines[line_index]
                        current_match = NOTE_REGEX.search(current_line)
                        if current_match and current_match.group(2) != new_duration_str:
                             fix_durations[line_index] = new_duration_str

        # --- 3. Apply the Replacements Line-by-Line ---

        notes_modified_count = 0
        new_lines = []
        
        for i, line in enumerate(lines):
            # Check if this line needs fixing
            if i in fix_durations:
                new_duration_val = fix_durations[i]
                
                # Capture the line-ending/trailing whitespace for preservation
                ending_match = LINE_ENDING_REGEX.search(line)
                line_ending = ending_match.group(1) if ending_match else ""
                
                # Strip the line ending before substitution to avoid issues
                line_to_process = line[:-len(line_ending)] if line_ending else line
                
                def replacer(match):
                    """Rebuilds the note tag with the new duration."""
                    # Group 1: time, Group 3: rest of attributes
                    time_attr = f'time="{match.group(1)}"'
                    duration_attr = f'duration="{new_duration_val}"'
                    # The replacement must reconstruct the entire tag structure
                    return f'<Note {time_attr} {duration_attr} {match.group(3)}/>'

                # Perform the substitution
                modified_line_tag = NOTE_REGEX.sub(replacer, line_to_process)
                
                # Re-attach the original line ending
                modified_line = modified_line_tag + line_ending
                
                new_lines.append(modified_line)
                notes_modified_count += 1
            else:
                # No fix needed, keep the original line (with its original ending)
                new_lines.append(line)

        # print(f"✅ Successfully processed {file_name}. Modified **{notes_modified_count}** note durations.")

        # --- 4. Overwrite the file ---
        final_content = "".join(new_lines)
        
        try:
            # Writing in text mode ('w') will use the system's default line endings if we don't
            # explicitly include them in `final_content`. Since we used `splitlines(keepends=True)`,
            # `final_content` already contains the original line endings, so 'w' is fine.
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
        #    print(f"💾 Successfully wrote changes to {file_name}, preserving original line endings.")
        except Exception as e:
            print(f"❌ An error occurred writing to {file_path}: {e}")






import os
import re
from collections import defaultdict
import math # Although simple int() cast would work, math.floor is often clearer for this purpose

def fixnotetimes(input_dir):
    """
    Opens four specific .sng files (notes1.sng to notes4.sng) and modifies the 'time' 
    attribute of each <Note> tag by applying the operation: time = int(time * 24) / 24. 
    
    This function uses regex, preserves leading whitespace, and original line endings 
    (CRLF or LF) when overwriting the files.

    Args:
        input_dir (str): The directory containing the notesX.sng files.
    """

    # List of file names to process
    file_names = [f"notes{i}.sng" for i in range(1, 5)]

    # --- Regular Expression Definitions ---

    # Regex to capture the entire <Note ... /> line, including starting whitespace.
    # Group 1 (named 'leading_ws'): Leading whitespace (for preservation)
    # Group 2: 'time' value
    # Group 3: The rest of the attributes (duration, track, special, etc.)
    # Note: The time attribute is the first, followed by others.
    NOTE_REGEX = re.compile(
        r'^(?P<leading_ws>\s*)'                        # Group 1 (named 'leading_ws'): Leading whitespace 
        r'<Note\s+'                                    # Start of <Note tag
        r'time="([\d\.]+)"\s*'                         # Group 2: time attribute
        r'(.*?)'                                       # Group 3: The rest of the attributes (non-greedy)
        r'/>'                                          # End of the tag (excluding final newline/trailing ws)
    )
    
    # Regex to capture the trailing whitespace/newline, including CRLF or LF.
    LINE_ENDING_REGEX = re.compile(r'(\s*)$') 

    for file_name in file_names:
        file_path = os.path.join(input_dir, file_name)
        print(f"Processing file: **{file_name}**")

        try:
            # Read the entire content as a single string to precisely capture all line endings
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split the content into lines, keeping the line endings attached to each line
            lines = content.splitlines(keepends=True)
            
        except FileNotFoundError:
            print(f"🚫 Error: File not found at {file_path}. Skipping.")
            continue
        except Exception as e:
            print(f"❌ An error occurred reading {file_path}: {e}. Skipping.")
            continue

        
        modified_lines = []
        notes_modified_count = 0
        
        # --- Apply the Time Fix Line-by-Line ---
        
        for i, line in enumerate(lines):
            
            # Capture the line-ending/trailing whitespace for preservation
            ending_match = LINE_ENDING_REGEX.search(line)
            line_ending = ending_match.group(1) if ending_match else ""
            
            # Strip the line ending before substitution to process the tag cleanly
            line_to_process = line[:-len(line_ending)] if line_ending else line
            
            match = NOTE_REGEX.search(line_to_process)

            if match:
                original_time_str = match.group(2) # Group 2 is 'time'
                
                try:
                    original_time = float(original_time_str)
                    
                    # 1. Apply the fixing calculation: time = int(time * 24) / 24
                    new_time_val_float = int(original_time * 24) / 24.0
                    
                    # Format the new time value as a string, ensuring enough precision 
                    # for the snap to 1/24th (e.g., 3 decimal places for 0.041666...).
                    # We will use f-string formatting to control the output.
                    new_time_val_str = f"{new_time_val_float:.7f}"
                    
                    # Check if the time was actually changed
                    # (Comparing floats directly can be risky, but comparing strings is fine here 
                    # if the string formatting is consistent. A small epsilon check is safer for floats.)
                    if abs(new_time_val_float - original_time) > 1e-9:
                        
                        def replacer(m):
                            """Rebuilds the note tag with the new time, preserving leading whitespace and attributes."""
                            
                            # Use named group for leading whitespace
                            leading_ws = m.group('leading_ws') 
                            
                            # Group 3 contains everything after the time attribute
                            rest_of_attrs = m.group(3) 
                            
                            # Reconstruct the entire line tag: 
                            # (Starting WS) + <Note time="..." (Rest of Attrs)/>
                            return f'{leading_ws}<Note time="{new_time_val_str}" {rest_of_attrs} />'

                        # Perform the substitution on the tag (without the line ending)
                        modified_line_tag = NOTE_REGEX.sub(replacer, line_to_process)
                        
                        # Re-attach the original line ending
                        modified_line = modified_line_tag + line_ending
                        
                        modified_lines.append(modified_line)
                        notes_modified_count += 1
                    else:
                        # Time was calculated to be the same, append original line
                        modified_lines.append(line)

                except ValueError:
                    # Line matched NOTE_REGEX but time wasn't a valid float, append original line
                    modified_lines.append(line)
            else:
                # Line did not match NOTE_REGEX (e.g., XML declaration, blank line), append original line
                modified_lines.append(line)

        print(f"✅ Successfully processed {file_name}. Modified **{notes_modified_count}** note times.")

        ## 4. Overwrite the File
        
        final_content = "".join(modified_lines)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"💾 Successfully wrote changes to {file_name}, preserving original format.")
        except Exception as e:
            print(f"❌ An error occurred writing to {file_path}: {e}")










def main():
    print("\n\n...chart2sng (Freetar) 0.1 - Naonemeu + ChatGPT\n")

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
    
    gf1fix = False

    write_sng_file(transformed_positions_expert, os.path.join(input_dir, "notes4.sng"), song_info, duration,gf1fix)
    write_sng_file(transformed_positions_hard, os.path.join(input_dir, "notes3.sng"), song_info, duration,gf1fix)
    write_sng_file(transformed_positions_medium, os.path.join(input_dir, "notes2.sng"), song_info, duration,gf1fix)
    write_sng_file(transformed_positions_easy, os.path.join(input_dir, "notes1.sng"), song_info, duration,gf1fix)
    
    fixlength(input_dir)
    fixnotetimes(input_dir)

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
    
