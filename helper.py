import re
def get_xy(poi, text, clip=None):
    if clip is not None:
        s1 = poi.search_for(text, clip=clip)
    else:
        s1 = poi.search_for(text)
    if len(s1) != 0:
        return s1
    else:
        return None

def make_text_rows(words):
    """Return textstring output of get_text("words").

    Word items are sorted for reading sequence left to right,
    top to bottom.

    """
    line_dict = {}  # key: vertical coordinate, value: list of words
    words.sort(key=lambda w: w[0])  # sort by horizontal coordinate
    for w in words:  # fill the line dictionary
        y1 = round(w[3], 2)  # bottom of a word: don't be too picky!
        word = w[4]  # the text of the word
        line = line_dict.get(y1, [])  # read current line content
        line.append(word)  # append new word
        line_dict[y1] = line  # write back to dict
    lines = list(line_dict.items())
    lines.sort()  # sort vertically
    return [" ".join(line[1]) for line in lines]

def get_price(pattern, page):
    Own_Damage_Dict = {}
    mode = 'Title'
    # pattern = '.*own\s*damage\s*premium.*'
    valuepattern = '[+-]?([0-9]*[.])?[0-9]+'
    currentTitle = None
    blocks = page.get_text("blocks")
    blocktextlist = []
    # blocks= POI.get_text("blocks",flags = fitz.fitz.TEXT_PRESERVE_LIGATURES | fitz.fitz.TEXT_PRESERVE_WHITESPACE)
    blocks.sort(key=lambda b: (b[3], b[0]))
    start_append = False
    for bl in blocks:
        # if 'premium' in bl[4].lower():
        # print(bl[4].lower())
        if not start_append:
            m = re.match('.*premium\s*details.*', bl[4].lower())
            if m is not None:
                start_append = True
        if start_append and '<image' not in bl[4]:
            blocktextlist.extend(bl[4].replace(u'\xa0', u' ').strip().split("\n"))
    # print(blocktextlist)
    for line in blocktextlist:
        if mode == 'Title':
            m = re.match(pattern, line.lower())
            if m is not None:
                currentTitle = line
                mode = 'value'
        if mode == 'value':
            m = re.match(valuepattern, line.lower())
            if m is not None:
                currentvalue = float(line.replace(',', ''))
                key = currentTitle.strip().replace(u'\xa0', u' ')
                while key in Own_Damage_Dict.keys():
                    key = key + "_"
                Own_Damage_Dict[key] = currentvalue
                mode = 'Title'
            else:
                currentTitle = line
    return Own_Damage_Dict

