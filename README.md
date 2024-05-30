Some tools to translate **Debnosu_works** or **Debo no Su Seisakusho** games.
Still have many bugs.

### HOW TO USE

**Method 1** **(Recommended method)**
1. Use Garbro to extract the game.pak file and from the script folder copy the scb files the any folder.
1. Use [SExtractor](https://github.com/satan53x/SExtractor) to extract the text from scb files by selecting `BIN VIOLENT` in format `name: message` with `Multiple files mode`.
2. Now put those json files you extrcated with SE along with scb files in `input_SE_json_files` and run `ext_off.py` that will give you the files need to translate in `translatable_files`.
3. Translate the `TL Key` (Warning: do not change anything else) and now you can run the `cr_scb.py` to get new files.

Method 2
1. Can only be used on unencrytped games for now (I haven't found any encrypted one yet).
2. Use Garbro to extract the game.pak that will give you some .scb files in a script folder.
3. Copy those files in the `input_scb_files`(Only script files like 01.scb 011a.scb or H011.scb not battle.scb or like that) folder now run `ext_scb.py` that will give you json files in `translatable_files` folder.
4. Translate the text in `TL key` (DO NOT TOUCH ANYTHING ELSE).
5. When translation is done run `cr_scb.py`, You'll get the new files in `new_scb_files` folder.

### Debonosu works game engine supports reading of file from folders so no need to repack files.


### Tested on [Kagura Shinpuuki ～Mikuru no Shou～ / 神楽新風記～みくるの章～]([url](https://vndb.org/v49338)) and [	神楽凌艶譚～沙耶の章～/Kagura Ryouentan ~Saya no Shou~
](https://vndb.org/v49351)
