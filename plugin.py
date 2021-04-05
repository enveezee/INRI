###
# Copyright (c) 2021, nvz <https://github.com/enveezee>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###
from json import loads, JSONDecodeError
from re import findall
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.log as log

# List of lists containing valid book names to match against.
Books = [
    # * Include alternate short names that aren't startswith() of actual name.
    # ! Last entry of the list should be the one you want the API to use.
    ['At','Acts'], ['Amos'], ['Baruch'], ['Canticles'], ['1Chronicles'], 
    ['2Chronicles'], ['Colossians'], ['1Corinthians'], ['2Corinthians'], 
    ['Dn','Daniel'], ['Dt','Deuteronomy'], ['Ecclesiastes'], ['Ephesians'], 
    ['Er','Ezra'], ['Esther'], ['Exodus'], ['Ezekiel'], ['Galatians'], 
    ['Gn','Genesis'], ['Hb','Habakkuk'], ['Hg','Haggai'], ['Hosea'], 
    ['Isaiah'], ['James'], ['Jb','Job'], ['Jd','Jude'], ['Jeremiah'], 
    ['Jg','Judges'], ['Jl','Joel'], ['Jn','John'], ['1Jn','1John'], 
    ['2Jn','2John'], ['3Jn','3John'], ['Jonah'], ['Js','Joshua'], ['1Kings'], 
    ['2Kings'], ['Lm','Lamentations'], ['Lv','Leviticus'], ['Lk','Luke'], 
    ['1Maccabees'], ['2Maccabees'], ['Malachi'], ['Micah'], ['Mk','Mark'], 
    ['Mt','Matthew'], ['Nahum'], ['Nehemiah'], ['Nb','Nm','Numbers'], 
    ['Obadiah'], ['1Peter'], ['2Peter'], ['Philippians'], ['Pm','Philemon'], 
    ['Pv','Prv','Proverbs'], ['Psm','Psalms'], ['Re','Revelation'], ['Romans'], 
    ['Rth','Ruth'], ['Sirach'], ['1Sm','1Samuel'], ['2Sm','2Samuel'], 
    ['SongofSolomon'], ['1Thessalonians'], ['2Thessalonians'], 
    ['1Tm','1Timothy'], ['2Tm','2Timothy'], ['Tobit'], ['Tt','Titus'], 
    ['Wisdom'], ['Zc','Zechariah'], ['Zp','Zephaniah']
]

RegExp = [
    # Regular expression for matching (possible) citations.
    r'(^|[\s]{1}[\d]?[\s]*[\w]{2,}[\s]*)',  # Match group 1 (Book).
    r'([\d]{1,3})[:]{1}',                   # Match group 2 (Chapter).
    r'([\d]{1,3}[-]?[\s]*[\d]{0,3})',       # Match group 3 (Verse).
    r'([\d\s,;:-]*)',                       # Match group 4 (List).
    r'(\([\w]*\))?',                        # Match group 5 (Translation).
]

Translations = {
    'Afrikaans': [  ['aov', 'Ou Vertaling']],
    'Albanian': [   ['albanian', 'Albanian']],
    'Amharic': [    ['amharic', 'Amharic NT'],
                    ['hsab', 'Haile Selassie Amharic Bible']],
    'Arabic': [     ['arabicsv', 'Smith and Van Dyke']],
    'Aramaic': [    ['peshitta', 'Peshitta NT']],
    'Armenian': [   ['easternarmenian', 'Eastern Genesis Exodus Gospels'],
                    ['westernarmenian', 'Western NT']],
    'Basque': [     ['basque', 'Navarro Labourdin NT']],
    'Breton': [     ['breton', 'Gospels']],
    'Bulgarian': [  ['bulgarian1940', 'Bulgarian Bible 1940']],
    'Chamorro': [   ['chamorro', 'Psalms Gospels Acts']],
    'Chinese': [    ['cns', 'NCV Simplified'],
                    ['cnt', 'NCV Traditional'],
                    ['cus', 'Union Simplified'],
                    ['cut', 'Union Traditional']],
    'Coptic': [     ['bohairic', 'Bohairic NT'],
                    ['coptic', 'New Testament'],
                    ['sahidic', 'Sahidic NT']],
    'Croatian': [   ['croatia', 'Croatian']],
    'Czech': [      ['bkr', 'Czech BKR'],
                    ['cep', 'Czech CEP'],
                    ['kms', 'Czech KMS'],
                    ['nkb', 'Czech NKB']],
    'Danish': [     ['danish', 'Danish']],
    'Dutch': [      ['statenvertaling', 'Dutch Staten Vertaling']],
    'English': [    ['kjv', 'King James Version'],
                    ['akjv', 'American King James Version'],
                    ['asv', 'American Standard Version'],
                    ['basicenglish', 'Basic English Bible'],
                    ['douayrheims', 'Douay Rheims'],
                    ['wb', 'Websters Bible'],
                    ['weymouth', 'Weymouth NT'],
                    ['web', 'World English Bible'],
                    ['ylt', 'Youngs Literal Translation']],
    'Esperanto': [  ['esperanto', 'Esperanto']],
    'Estonian': [   ['estonian', 'Estonian']],
    'Finnish': [    ['finnish1776', 'Finnish Bible 1776'],
                    ['pyharaamattu1933', 'Pyha Raamattu 1933'],
                    ['pyharaamattu1992', 'Pyha Raamattu 1992']],
    'French': [     ['darby', 'Darby'],
                    ['ls1910', 'Louis Segond 1910'],
                    ['martin', 'Martin 1744'],
                    ['ostervald', 'Ostervald 1996 revision']],
    'Georgian': [   ['Gospels Acts James', 'Georgian']],
    'German': [     ['elberfelder', 'Elberfelder 1871'],
                    ['elberfelder1905', 'Elberfelder 1905'],
                    ['luther1545', 'Luther 1545'],
                    ['luther1912', 'Luther 1912'],
                    ['schlachter', 'Schlachter 1951']],
    'Gothic': [     ['gothic', 'Gothic Nehemiah NT Portions']],
    'Greek': [      ['moderngreek', 'Greek Modern'],
                    ['majoritytext', 'NT Byzantine Majority Text 2000 Parsed'],
                    ['byzantine', 'NT Byzantine Majority Text 2000'],
                    ['textusreceptus', 'NT Textus Receptus 1550 1894 Parsed'],
                    ['text', 'Textus Receptus'],
                    ['tischendorf', 'NT Tischendorf 8th Ed'],
                    ['westcotthort', 'NT Westcott Hort UBS4 variants Parsed'],
                    ['westcott', 'NT Westcott Hort UBS4 variants'],
                    ['lxxpar', 'OT LXX Accented Roots Parsing'],
                    ['lxx', 'OT LXX Accented'],
                    ['lxxunaccentspar', 'OT LXX Unaccented Roots Parsing'],
                    ['lxxunaccents', 'OT LXX Unaccented']],
    'Hebrew': [     ['aleppo', 'Aleppo Codex'],
                    ['modernhebrew', 'Hebrew Modern'],
                    ['bhsnovowels', 'OT BHS Consonants Only'],
                    ['bhs', 'OT BHS Consonants and Vowels'],
                    ['wlcnovowels', 'OT WLC Consonants Only'],
                    ['wlc', 'OT WLC Consonants and Vowels'],
                    ['codex', 'OT Westminster Leningrad Codex']],
    'Hungarian': [  ['karoli', 'Hungarian Karoli']],
    'Italian': [    ['giovanni', 'Giovanni Diodati Bible 1649'],
                    ['riveduta', 'Riveduta Bible 1927']],
    'Kabyle': [     ['kabyle', 'Kabyle NT']],
    'Korean': [     ['korean', 'Korean']],
    'Latin': [      ['newvulgate', 'Nova Vulgata'],
                    ['vulgate', 'Vulgata Clementina']],
    'Latvian': [    ['latvian', 'New Testament']],
    'Lithuanian': [ ['lithuanian', 'Lithuanian']],
    'Manx_Gaelic': [['manxgaelic', 'Manx Gaelic Esther Jonah 4 Gospels']],
    'Maori': [      ['maori', 'Maori']],
    'Myanmar_Burmse': [['judson', 'Judson 1835']],
    'Norwegian': [  ['bibelselskap', 'Det Norsk Bibelselskap 1930']],
    'Portuguese': [ ['almeida', 'Almeida Atualizada']],
    'Potawatomi': [ ['potawatomi', 'Potawatomi Matthew Acts Lykins 1844']],
    'Romani': [     ['rom', 'Romani NT E Lashi Viasta Gypsy']],
    'Romanian': [   ['cornilescu', 'Cornilescu']],
    'Russian': [    ['makarij', 'Makarij Translation Pentateuch 1825'],
                    ['synodal', 'Synodal Translation 1876'],
                    ['zhuromsky', 'Victor Zhuromsky NT']],
    'Scottish_Gaelic': [['gaelic', 'Scots Gaelic Gospel of Mark']],
    'Spanish': [    ['valera', 'Reina Valera 1909'],
                    ['rv1858', 'Reina Valera NT 1858'],
                    ['sse', 'Sagradas Escrituras 1569']],
    'Swahili': [    ['swahili', 'Swahili']],
    'Swedish': [    ['swedish', 'Swedish 1917']],
    'Tagalog': [    ['tagalog', 'Ang Dating Biblia 1905']],
    'Tamajaq': [    ['tamajaq', 'Tamajaq Portions']],
    'Thai': [       ['thai', 'Thai from kjv']],
    'Turkish': [    ['tnt', 'NT 1987 1994'],
                    ['turkish', 'Turkish']],
    'Ukrainian': [  ['ukranian', 'NT P Kulish 1871']],
    'Uma': [        ['uma', 'Uma NT']],
    'Vietnamese': [ ['vietnamese', 'Vietnamese 1934']],
    'Wolof': [      ['wolof', 'Wolof NT']],
    'Xhosa': [      ['xhosa', 'Xhosa']]
}

class INRI(callbacks.Plugin):
    def __init__(self, irc):
        self.__parent = super(INRI, self)
        self.__parent.__init__(irc)

 
    def doPrivmsg(self, irc, msg):
        '''Look for Bible citations made in the channel.'''
        channel = msg.args[0]

        # Ignore the message if it came from the bot.
        if msg.nick.casefold() == irc.nick.casefold():
            return
        # Ignore the message if it isn't in a channel.
        if not irc.isChannel(channel):
            return
        # Ignore the message if it is addressed to the bot.
        if callbacks.addressed(irc.nick, msg):
            return
        # Ignore the message if it is an action.
        if ircmsgs.isCtcp(msg) or ircmsgs.isAction(msg):
            return

        self.iam(irc, msg)


    def getbible(self, p, v):
        '''Make a request to getbible.net JSON API and parse response.'''
        # JSON API query URL.
        url = f'http://getbible.net/json?p={p}&v={v}'
        log.error(f'Requesting {url}')
        # Form API request for passage and version.
        request = Request(url)
        # Set a User-Agent header.
        request.add_header('User-Agent', 'Mozilla/5.0')
        try:
            # Make the request and capture the response.
            response = urlopen(request)
        except HTTPError as e:
            # Log and errors during the request and return.
            log.error(f'HTTPError opening {url}: {e.code} {e.msg}')
            log.debug(f'{e.hdr}')
            return None

        # Extract headers from the HTTPResponse.
        headers = dict(response.getheaders())
        # Check to see if the response is JSON.
        # ! Most this code is meaningless, the API doesn't return properly.
        if 'text/html' in headers['Content-Type']:
            try:
                # Parse the JSON response.
                bible = loads(response.read()[1:-2]) # ! Sliced to remove ();
            except JSONDecodeError as e:
                # Log JSON parsing errors and return.
                log.error(f'JSONDecodeError: {e.msg}')
                log.debug(f'Pos:{e.pos} Line:{e.lineno} Col:{e.colno}')
                log.debug(f'{e.doc}')
                return None
            # Return successfully parsed JSON.
            return bible
        else:
            # ! Log error if response wasn't JSON and return.
            log.error(f'Error making Bible API call to {url}:')
            log.error('API request succeeded but response was not JSON.')
            return None


    def iam(self, irc, msg, text=None):
        '''Before Jesus was...'''
        channel = msg.args[0]
        message = msg.args[1]

        # Search message for (possible) Bible citations.
        citations = findall(''.join(RegExp), message)

        # Iterate over each possible citation found.
        for citation in citations:
            # Strip matches, casefold, and extract them.
            bk, ch, vs, ls, tr = [s.strip().casefold() for s in citation]

            # Check bk against Books list, assign it to book if found.
            book = None
            # Each valid book in Books list.
            for Book in Books:
                # Each matchable title for that book.
                for title in Book:
                    # If bk matches a title.
                    if title.casefold().startswith(bk):
                        # Set book to last title in this list of titles.
                        book = Book[-1]
                        break
                if book:
                    break

            if not book:
                return

            # If translation is specified, check to make sure its available.
            translate = None
            if tr:
                translate = None
                for lang in Translations:
                    for translation in lang:
                        if tr == translation[0].casefold():
                            translate = tr
                            break
                    if translate:
                        break

            if not translate:
                translate = self.registryValue('defaultBible', channel=channel)

            bible = self.getbible(f'{bk}{ch}:{vs}{ls}', translate)

            if bible:

                versesText=[]
                for book in bible['book']:
                    verses = list(book['chapter'].keys())
                    for verse in verses:
                        text = book['chapter'][verse]['verse'].replace('\r\n','')
                        irc.reply(f'"{verse}. {text}"', prefixNick=False)


Class = INRI
