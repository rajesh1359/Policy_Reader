# import pdfplumber
import fitz

# doc = fitz.Document(r"E:\NewDownloads\DemoDownloads\tata policy\202203090157872_05062022104117.pdf")
# pno = 3
# page = doc.load_page(pno)

# table_title = "Registration"
# search1 = page.search_for(table_title)
# scedule_premium=page.search_for('SCHEDULE OF PREMIUM')
#print(page.get_text("blocks"))
def make_text(words):
    """Return textstring output of get_text("words").

    Word items are sorted for reading sequence left to right,
    top to bottom.
    """
    line_dict = {}  # key: vertical coordinate, value: list of words
    words.sort(key=lambda w: w[0])  # sort by horizontal coordinate
    for w in words:  # fill the line dictionary
        y1 = round(w[3], 1)  # bottom of a word: don't be too picky!
        word = w[4]  # the text of the word
        line = line_dict.get(y1, [])  # read current line content
        line.append(word)  # append new word
        line_dict[y1] = line  # write back to dict
    lines = list(line_dict.items())
    lines.sort()  # sort vertically
    return "\n".join([" ".join(line[1]) for line in lines])

def get_text_iters(box,page):
    registration_num = None
    x0 = box.x0
    x1 = box.x1
    y0 = box.y0
    y1 = box.y1
    stop = False
    old_text = 'Registration'
    txt_1 = ""
    got_once = False
    i = 0
    found_full = False
    while not stop:

        txt_1 = page.get_textbox([0, y0, x1, y1 + i])
        clean_text = " ".join(txt_1.replace(u"\xa0", u" ").split()).replace('Registration', '').strip()
        #print(clean_text)
        if len(clean_text) != 0:
            got_once = True
            if clean_text == 'No.' or clean_text == "Number":
                stop = True
                found_full=True
                #print(clean_text)
            else:
                stop = True
                found_full=False
        # else:
        #     if got_once:
        #         stop = True
        if i>50:
            stop=True
        i += 1
        #print(i)
    finally_found=False
    if not found_full:
        stop= False
        j=0
        while not stop:

            txt_1 = page.get_textbox([0, y0, x1+j, y1+i-2])
            clean_text = " ".join(txt_1.replace(u"\xa0", u" ").split()).replace('Registration', '').strip()
            #print(clean_text)
            if len(clean_text) != 0:
                got_once = True
                if clean_text == 'No.' or clean_text == "Number":
                    stop = True
                    finally_found=True

                    #print(clean_text)
            if j>30:
                stop=True
            j+=1
    if not finally_found:
        None,None,None
    x_0 =box.x0-5
    y_0 = box.y0 - (i/2.0)
    if found_full:
        x_1 = box.x1 + 5
        y_1 = box.y1 + i
    else:
        x_1 = box.x1 + j
        y_1 = y1+i-2

    stop =  False
    txt_1 = page.get_textbox([x_0, y_0, x_1, y_1])
    original_text = " ".join(txt_1.replace(u"\xa0", u" ").split())
    #print('Original Text',original_text)
    i=0
    k=0
    old_clean_text=""
    found_reg = False
    while not stop:

        txt_1 = page.get_textbox([x_0-10, y_0, x_1, y_1+i])
        clean_text = " ".join(txt_1.replace(u"\xa0", u" ").replace(u"\xad", u"").split()).replace(original_text, '').strip()
        # print(clean_text)
        # print('Reg Num',clean_text)
        # print(old_clean_text == clean_text)
        if len(clean_text) != 0:
            if old_clean_text == clean_text:
                k += 1
            else:
                k=0
            if k>8:
                stop = True
                found_reg=True
                # registration_num = clean_text.strip()
            old_clean_text = clean_text

        i+=1
        if i>70:
            stop=True
    # print('Reg Num', found_reg)
    if found_reg:
        # registration_num = clean_text.strip()
    # print('Reg Num', registration_num)
        words = page.get_text("words")
        mywords = [w for w in words if fitz.Rect(w[:4]).intersects(fitz.Rect(x_0-10, y_0, x_1, y_1+i))]
        regnum = " ".join(make_text(mywords).replace(u"\xa0", u" ").split())
        # print('Reg Num', regnum.replace('Registration','').replace('No.','').replace('Number',''))
        registration_num = regnum.replace('Registration','').replace('No.','').replace('Number','').strip()

    # print(txt_1)
    # txt_1 = page.get_textbox([x_1, y_0, x_1 + (x_1-x_0), y_1+i],)
    # new_make = " ".join(txt_1.replace(u"\xa0", u" ").split())
    # print("Make Text ", new_make.replace('&',"").lower().replace('make/','').replace('model/','').replace('make','').replace('model','').replace('type','').replace('body',''))
    # for i in range(1, 10):
    #     page.get_textbox([0, y0, x1, y1 + 5 * i])
    words = page.get_text("words")
    mywords = [w for w in words if fitz.Rect(w[:4]).intersects(fitz.Rect(x_1, y_0, x_1 + (x_1-x_0), y_1+i))]
    make_model = " ".join(make_text(mywords).replace(u"\xa0", u" ").split())
    words_to_replace = ['make /','make/','model /','model/','&','make','type','body',u'\xad']
    for w in words_to_replace:
        make_model=make_model.lower().replace(w,'')
    #print(make_model)
    make_list = make_model.split('/')
    non_emptylist= []
    for itm in make_list:
        if len(itm.strip())!=0:
            non_emptylist.append(itm.strip())
    if len(non_emptylist)>1:
        make = non_emptylist[0]
        model = non_emptylist[1]
    else:
        make = model = make_model

    return registration_num, make,model


def get_registration(page, header,footer, make_model_stat):
    #table_title = "Registration"
    search1 = page.search_for(header)
    # scedule_premium = page.search_for('SCHEDULE OF PREMIUM')
    scedule_premium = page.search_for(footer)
    second_filter = page.search_for('State code')
    reg_num=None

    for s1 in search1:
        #print(s1)
        if second_filter[0].y1 < s1.y1 < scedule_premium[0].y1:
            if page.get_textbox([0, s1.y0, s1.x1, s1.y1]).strip() != page.get_textbox(s1).strip():
                print("Not Eligible")

            else:
                print("Eligible")
                # print(page.get_textbox(s1))
                reg_num,mk,mdl = get_text_iters(s1,page)
                if reg_num is not None:
                    if make_model_stat is not None:
                        return reg_num, make_model_stat[0],make_model_stat[1]
                    else:
                        return reg_num,mk,mdl

    if make_model_stat is not None:
        return None, make_model_stat[0], make_model_stat[1]
    else:
        return None, None, None

    # print(page.get_textbox(s1))
# print(get_registration(page,'Registration','SCHEDULE OF PREMIUM',None))
