import re
import hashlib
import os
import requests
import unicodedata

EMOJI_TEST_URL = 'https://unicode.org/Public/emoji/latest/emoji-test.txt'
EMOJI_TEST_FILE = 'data/emoji-test.txt'
DART_OUTPUT_FILE = 'lib/src/emoji_enum.dart'

def download_emoji_test_file(url, file_path):
    response = requests.get(url)
    response.raise_for_status()

    # Save the content to a temporary file
    with open(file_path + '.tmp', 'wb') as f:
        f.write(response.content)

def calculate_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def remove_accents(input_str):
    # Decompose Unicode characters and remove combining marks
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii

number_word_map = {
    '0': 'zero',
    '1': 'one',
    '1st': 'first',
    '2': 'two',
    '2nd': 'second',
    '3': 'three',
    '3rd': 'third',
    '4': 'four',
    '4th': 'fourth',
    '5': 'five',
    '5th': 'fifth',
    '6': 'six',
    '6th': 'sixth',
    '7': 'seven',
    '7th': 'seventh',
    '8': 'eight',
    '8th': 'eighth',
    '9': 'nine',
    '9th': 'ninth',
    '10': 'ten',
    '10th': 'tenth',
}

symbol_replacements = {
    '#': 'Hash',
    '*': 'Asterisk',
    '!': 'ExclamationMark',
    '?': 'QuestionMark',
    '©': 'Copyright',
    '®': 'Registered',
    '™': 'Trademark',
    '&': 'And',
    '+': 'Plus',
    '-': 'Minus',
    '/': 'Slash',
    '\\': 'Backslash',
    '=': 'Equals',
    '@': 'At',
    '^': 'Caret',
    '_': 'Underscore',
    '%': 'Percent',
    '$': 'Dollar',
    '€': 'Euro',
    '£': 'Pound',
    '¥': 'Yen',
}

def replace_symbols(s):
    # Replace symbols with their word equivalents
    for symbol, word in symbol_replacements.items():
        s = s.replace(symbol, word)
    return s

def sanitize_enum_name(name):
    # Remove accents
    name = remove_accents(name)
    # Replace symbols
    name = replace_symbols(name)
    # Replace any non-word characters (except spaces) with space
    name = re.sub(r'[^\w\s]', '', name)
    # Replace multiple spaces with a single space
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    # Split the name into words
    words = name.split(' ')
    # Replace numbers at the start and in the words
    for i, word in enumerate(words):
        if word.lower() in number_word_map:
            words[i] = number_word_map[word.lower()]
    # Convert words to lowerCamelCase
    if not words:
        return ''
    first_word = words[0].lower()
    other_words = [word.capitalize() for word in words[1:]]
    enum_name = first_word + ''.join(other_words)
    # Ensure the identifier does not start with a digit
    if re.match(r'^\d', enum_name):
        enum_name = '_' + enum_name
    # Remove any remaining invalid characters
    enum_name = re.sub(r'[^\w]', '', enum_name)
    return enum_name

def parse_emoji_test_file(file_path):
    emojis = []
    groups = set()
    subgroups = set()
    enum_names_set = set()
    current_group = ''
    current_subgroup = ''
    name_counters = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Check for group
            group_match = re.match(r'# group: (.+)', line)
            if group_match:
                current_group = group_match.group(1)
                groups.add(current_group)
                continue

            # Check for subgroup
            subgroup_match = re.match(r'# subgroup: (.+)', line)
            if subgroup_match:
                current_subgroup = subgroup_match.group(1)
                subgroups.add(current_subgroup)
                continue

            # Skip comments and empty lines
            if line.startswith('#') or line == '':
                continue

            # Extract the codepoints and the emoji description
            match = re.match(
                r'^([0-9A-F ]+);\s*fully-qualified\s*#\s*([\S]+)\s*E\d+\.\d+\s*(.+)',
                line)
            if match:
                codepoints = match.group(1).strip()
                emoji_char = match.group(2)
                emoji_name = match.group(3).strip()

                enum_name = sanitize_enum_name(emoji_name)

                # Ensure enum_name is unique
                original_enum_name = enum_name
                count = 1
                while enum_name in enum_names_set:
                    enum_name = f"{original_enum_name}{count}"
                    count += 1
                enum_names_set.add(enum_name)

                emojis.append({
                    'codepoints': codepoints,
                    'char': emoji_char,
                    'name': emoji_name,
                    'enum_name': enum_name,
                    'group': current_group,
                    'subgroup': current_subgroup,
                })

    return emojis, groups, subgroups

def generate_dart_code(emojis, groups, subgroups, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        # Generate Group enum
        f.write('enum EmojiGroup {\n')
        for group in sorted(groups):
            enum_name = sanitize_enum_name(group)
            f.write(f"  {enum_name},\n")
        f.write('}\n\n')

        # Generate Subgroup enum
        f.write('enum EmojiSubgroup {\n')
        for subgroup in sorted(subgroups):
            enum_name = sanitize_enum_name(subgroup)
            f.write(f"  {enum_name},\n")
        f.write('}\n\n')

        # Generate Emoji enum
        f.write('enum Emoji {\n')
        for emoji in emojis:
            # Escape single quotes in names
            emoji_name_escaped = emoji['name'].replace("'", r"\'")

            group_enum_name = sanitize_enum_name(emoji['group'])
            subgroup_enum_name = sanitize_enum_name(emoji['subgroup'])

            line = f"  {emoji['enum_name']}(\n" \
                   f"    '{emoji['char']}',\n" \
                   f"    '{emoji_name_escaped}',\n" \
                   f"    EmojiGroup.{group_enum_name},\n" \
                   f"    EmojiSubgroup.{subgroup_enum_name}\n" \
                   f"  ),\n"
            f.write(line)
        f.write(';\n\n')
        f.write('  final String character;\n')
        f.write('  final String name;\n')
        f.write('  final EmojiGroup group;\n')
        f.write('  final EmojiSubgroup subgroup;\n\n')
        f.write('  const Emoji(this.character, this.name, this.group, this.subgroup);\n')
        f.write('}\n')

def main():
    print('Downloading the latest emoji-test.txt file...')
    download_emoji_test_file(EMOJI_TEST_URL, EMOJI_TEST_FILE)

    new_checksum = calculate_checksum(EMOJI_TEST_FILE + '.tmp')
    old_checksum = None

    if os.path.exists(EMOJI_TEST_FILE):
        old_checksum = calculate_checksum(EMOJI_TEST_FILE)

    if old_checksum == new_checksum:
        print('No changes detected in emoji-test.txt. No update needed.')
        # Remove the temporary file
        os.remove(EMOJI_TEST_FILE + '.tmp')
    else:
        print('Changes detected in emoji-test.txt. Proceeding with update.')
        # Replace the old file with the new one
        os.replace(EMOJI_TEST_FILE + '.tmp', EMOJI_TEST_FILE)

        # Parse the emoji-test.txt file
        print('Parsing emoji-test.txt...')
        emojis, groups, subgroups = parse_emoji_test_file(EMOJI_TEST_FILE)
        print(f'Total emojis parsed: {len(emojis)}')
        print(f'Total groups: {len(groups)}')
        print(f'Total subgroups: {len(subgroups)}')

        # Generate the Dart code
        print('Generating Dart code...')
        generate_dart_code(emojis, groups, subgroups, DART_OUTPUT_FILE)
        print(f'Dart code has been generated successfully in {DART_OUTPUT_FILE}.')

if __name__ == '__main__':
    main()
