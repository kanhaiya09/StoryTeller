import urllib
import mechanize
import nltk
from nltk.corpus import brown
from bs4 import BeautifulSoup
from urlparse import urlparse
from nltk.tokenize import sent_tokenize,word_tokenize
from PIL import Image,ImageTk
import glob
import tkMessageBox
import Tkinter
import os
import pyttsx
#################################################################
        # sentence to meaning extractor #

brown_train = brown.tagged_sents(categories='news')
regexp_tagger = nltk.RegexpTagger(
    [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),
     (r'(-|:|;)$', ':'),
     (r'\'*$', 'MD'),
     (r'(The|the|A|a|An|an)$', 'AT'),
     (r'.*able$', 'JJ'),
     (r'^[A-Z].*$', 'NNP'),
     (r'.*ness$', 'NN'),
     (r'.*ly$', 'RB'),
     (r'.*s$', 'NNS'),
     (r'.*ing$', 'VBG'),
     (r'.*ed$', 'VBD'),
     (r'.*', 'NN')
])
unigram_tagger = nltk.UnigramTagger(brown_train, backoff=regexp_tagger)
bigram_tagger = nltk.BigramTagger(brown_train, backoff=unigram_tagger)
#############################################################################


# This is our semi-CFG; Extend it according to your own needs
#############################################################################
cfg = {}
cfg["NNP+NNP"] = "NNP"
cfg["NN+NN"] = "NNI"
cfg["NNI+NN"] = "NNI"
cfg["JJ+JJ"] = "JJ"
cfg["JJ+NN"] = "NNI"
#############################################################################


class NPExtractor(object):

    def __init__(self, sentence):
        self.sentence = sentence

    # Split the sentence into singlw words/tokens
    def tokenize_sentence(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        return tokens

    # Normalize brown corpus' tags ("NN", "NN-PL", "NNS" > "NN")
    def normalize_tags(self, tagged):
        n_tagged = []
        for t in tagged:
            if t[1] == "NP-TL" or t[1] == "NP":
                n_tagged.append((t[0], "NNP"))
                continue
            if t[1].endswith("-TL"):
                n_tagged.append((t[0], t[1][:-3]))
                continue
            if t[1].endswith("S"):
                n_tagged.append((t[0], t[1][:-1]))
                continue
            n_tagged.append((t[0], t[1]))
        return n_tagged

    # Extract the main topics from the sentence
    def extract(self):

        tokens = self.tokenize_sentence(self.sentence)
        tags = self.normalize_tags(bigram_tagger.tag(tokens))

        merge = True
        while merge:
            merge = False
            for x in range(0, len(tags) - 1):
                t1 = tags[x]
                t2 = tags[x + 1]
                key = "%s+%s" % (t1[1], t2[1])
                value = cfg.get(key, '')
                if value:
                    merge = True
                    tags.pop(x)
                    tags.pop(x)
                    match = "%s %s" % (t1[0], t2[0])
                    pos = value
                    tags.insert(x, (match, pos))
                    break

        matches = []
        for t in tags:
            if t[1] == "NNP" or t[1] == "NNI":
            #if t[1] == "NNP" or t[1] == "NNI" or t[1] == "NN":
                matches.append(t[0])
        return matches

##############################################################
            # save pic  #
def savePic(url,cnt):
    dest = "Images/download"
    uri = "";
    uri  = dest+str(cnt)+'.jpg'
    urllib.urlretrieve(url,uri)


#################################################################
        # download pic #
def getPic(search,cnt):
    try:
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0')]
        htmltext = browser.open("https://www.google.com/search?site=&tbm=isch&source=hp&biw=1536&bih=732&q="+search+"&oq="+search)
        img_urls = []
        soup = BeautifulSoup(htmltext,"html.parser")
        results = soup.findAll("a")
        urls = str(results)
        a=urls.find("data-src=\"")
        b=urls.find("\"",a+11)
        final= urls[a+10:b]
       # print final
        savePic(final,cnt)
           
    except:
        print "No internet connection"

#################################################################
        # readig file sentence by sentence#

b = open('C:/Users/ompra/Desktop/Solution.txt','r')
sentence = b.read()
content = sent_tokenize(str(sentence))


#################################################################
       # main programme #
text_list = []
cnt = 0
for sen in content:
    print sen
    text_list.append(sen)
    np_extractor = NPExtractor(sen)
    result = np_extractor.extract()
    for tag in result:
        p = tag.split()
        s = "+".join(p)
    print s
    getPic(s,cnt)
    cnt = cnt+1

#################################################################
        #Making imageList 
        
src = 'C:\\Python27\\Images'

image_list = []

for jpgfile in glob.iglob(os.path.join(src, "*.jpg")):
    image_list.append(jpgfile)

#################################################################
        #GUI programme  

root = Tkinter.Tk()

current = 0

def move(delta):
    engine = pyttsx.init()
    engine.setProperty('rate', 100)
    global current, image_list,text_list
    if not (0 <= current + delta < len(image_list)):
        tkMessageBox.showinfo('End', 'No more image.')
        return
    current += delta
    image = Image.open(image_list[current])
    photo = ImageTk.PhotoImage(image)
    label['text'] = text_list[current]
    label['image'] = photo
    label.photo = photo
    engine.say(text_list[current])
    engine.runAndWait()
    

label = Tkinter.Label(root, compound=Tkinter.TOP)
label.pack()

frame = Tkinter.Frame(root)
frame.pack()

Tkinter.Button(frame, text='Previous picture', command=lambda: move(-1)).pack(side=Tkinter.LEFT)
Tkinter.Button(frame, text='Next picture', command=lambda: move(+1)).pack(side=Tkinter.LEFT)
Tkinter.Button(frame, text='Quit', command=root.quit).pack(side=Tkinter.LEFT)

move(0)

root.mainloop()

