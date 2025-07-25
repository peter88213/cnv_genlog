# cnv_genlog

Convert *Genlog* family tree data.

------------

## Purpose

*Genlog* is a legacy family tree software to be replaced. 
For this, data has to be converted from its native format into some free format.

## The Genlog data format

-   *Genlog* stores data in a single hypertext document whose pages correspond to the individual data records. 
-   This hypertext document is in binary format, namely the *WinHelp* format, which has since been discontinued by Microsoft. 
-   Internally, the RTF format is used, which is also being discontinued by Microsoft. 
-   Each data record is identified by an ID to which other pages can link (e.g., as children, parents, spouses).
-   The *Genlog* software can generate a tree structure from the links and display it as a family tree 
    with variable depth and selectable root nodes. The leaves are implemented as links to the pages in the hypertext document. 
-   Apart from the ID links, *Genlog* does not need to understand the semantics of the content. 
    This means that the data fields on the pages are not type-bound. 
    They are free text and can therefore be understood primarily visually. 


## Steps

1. Disassemble the *.hlp* files, getting *.rtf* and *.bmp* files. The right tool for this is *HELPDECO.EXE* by Manfred Winterhoff 
   (see [tools](tools)).
2. Convert the *.bmp* image files to *.jpg*. This can be easily done e.g. using the batch conversion feature of *IrfanView*. 
3. Convert the *.rtf* files into plain text via the *strip_rtf.py* script.
4. Parse the plain text files in order to get the best-structured data possible.
5. Create a new data base to revise the metadata. This is currently an *Obsidian* vault, for instance. 
   Also the linked external documents should then be *Obsidian* notes.
6. Create target data, e.g. GEDCOM. 

------------

## Credits

- The [striprtf](https://github.com/joshy/striprtf) module by Joshy Cyriac 
  is released under the [BSD-3-Clause license](https://github.com/joshy/striprtf?tab=BSD-3-Clause-1-ov-file#readme)
- The WinHelp decompiler is a freeware application written by Manfred Winterhoff.

------------

## License

Published under the [MIT License](https://opensource.org/licenses/mit-license.php)
