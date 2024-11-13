# Emoji Enum Generator

This package provides a Python script and a GitHub Actions workflow to automatically generate and update a Dart enum containing all the emojis defined in the latest Unicode standard. The enum includes each emoji's character, name, group, and subgroup, adhering to Dart best practices.

## Features

- **Automated Emoji Data Extraction**: Downloads the latest `emoji-test.txt` file from the Unicode Consortium.
- **Dart Enum Generation**: Parses the emoji data and generates an `emoji_enum.dart` file with all emojis, including their characters, names, groups, and subgroups.


## Usage

import 'emoji_enum.dart';

```
void main() {
  // Access an emoji
  Emoji emoji = Emoji.grinningFace;

  print('Character: ${emoji.character}');     // Output: 😀
  print('Name: ${emoji.name}');               // Output: grinning face
  print('Group: ${emoji.group}');             // Output: EmojiGroup.smileysEmotion
  print('Subgroup: ${emoji.subgroup}');       // Output: EmojiSubgroup.faceSmiling

  // Filter emojis by group
  var smileyEmojis = Emoji.values.where((e) => e.group == EmojiGroup.smileysEmotion);
  print('Total smileys and emotions: ${smileyEmojis.length}');
}
```

## Acknowledgements
- Unicode Consortium: Emoji data provided by the Unicode Consortium.
- GitHub Actions: Automation powered by GitHub Actions.
- peter-evans/create-pull-request: For simplifying the pull request creation process.

