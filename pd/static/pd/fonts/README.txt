Put the licensed font files here, with exactly these names:

  Milker-Regular.woff2   (or Milker-Regular.otf)    - headings   (Brandsemut: brandsemut.com/product/milker)
  YDYoonche-M.woff2      (or YDYoonche-M.otf)       - body text  (Yoon Design: YD Yoonche, weight M)

No code changes needed: tailwind.css already points at these files.
Until they're here, the page falls back to Archivo (expanded black) and Outfit from Google Fonts.
To turn an .otf/.ttf into .woff2 you can use any converter, e.g.  pip install fonttools brotli
then: python -m fontTools.ttLib.woff2 compress Milker-Regular.otf
