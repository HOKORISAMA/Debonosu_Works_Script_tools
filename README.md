Some tools to translate **Debnosu_works** or **Debo no Su Seisakusho** games.
Still have many bugs.

### HOW TO USE
Method 1
1. Can only be used on unencrytped games for now.
2. Use Garbro to extract the game.pak that will give you some .scb files in a script folder.
3. Copy those files in the `input_scb_files`(Only script files like 01.scb 011a.scb or H011.scb not battle.scb or like that) folder now run `ext_scb.py` that will give you json files in `translatable_files` folder.
4. Translate the text in `TL key` (DO NOT TOUCH ANYTHING ELSE).
5. When translation is done run `cr_scb.py`, You'll get the new files in `new_scb_files` folder.

##This game engine can read the files from folders so no need to repack files back.

Method 2
1. Use [SExtractor](https://github.com/satan53x/SExtractor) to extract the text from scb files by selecting `BIN VIOLENT` in format `name: message` with `Multiple files mode`.
2. Now put those files in any folder and run `ext_offv2.py` that will give you the files need to translate.
3. Translate the `TL Key` 
