# INRI
Supybot/Limnoria Bible plugin.

INRI matches all sorts of citations in chat including ranges like 1John 3:1-4, lists Gal 6:12,15 etc.. and dosen't require an API key or any 3rd party dependencies.

It makes use of https://github.com/getbible/v2 hosted at https://api.getbible.net/

Examples:

16:07 ( nvz) ,bibles

16:07 ( BoydW) afrikaans, albanian, amharic, arabic, aramaic, armenian, basque, breton, bulgarian, chamorro, chinese, coptic, croatian, czech, 
               danish, dutch, english, esperanto, estonian, finnish, french, georgian, german, gothic, greek, hebrew, hungarian, italian, kabyle,
               korean, latin, latvian, lithuanian, manx_Gaelic, maori, myanmar_Burmse, norwegian, portuguese, potawatomi, romani, romanian,
               russian, scottish_Gaelic, spanish, swahili, swedish, tagalog,  |&1

16:07 ( nvz) ,bibles german

16:07 ( BoydW) Elberfelder 1871 (elberfelder), Elberfelder 1905 (elberfelder1905), Luther 1545 (luther1545), Luther 1912 (luther1912), Schlachter
               1951 (schlachter)

16:08 ( nvz) ,bibles English

16:08 ( BoydW) King James Version (kjv), American King James Version (akjv), American Standard Version (asv), Basic English Bible (basicenglish),
               Douay Rheims (douayrheims), Websters Bible (wb), Weymouth NT (weymouth), World English Bible (web), Youngs Literal Translation (ylt)

16:11 ( nvz) Ezekiel25:17(web)

16:11 ( BoydW) Ezekiel 25: "17. I will execute great vengeance on them with wrathful rebukes; and they shall know that I am Yahweh, when I shall
               lay my vengeance on them." (web)

16:18 ( nvz) If I am talking about spiritual warfare and I happen to mention Eph 6:12-15 (asv) the bot will pull up those verses I cited

16:18 ( BoydW) Ephesians 6: "12. For our wrestling is not against flesh and blood, but against the principalities, against the powers, against the 
               world-rulers of this darkness, against the spiritual [hosts] of wickedness in the heavenly [places]." (asv)

16:18 ( BoydW) Ephesians 6: "13. Wherefore take up the whole armor of God, that ye may be able to withstand in the evil day, and, having done all, 
               to stand." (asv)

16:18 ( BoydW) Ephesians 6: "14. Stand therefore, having girded your loins with truth, and having put on the breastplate of righteousness," (asv)

16:18 ( BoydW) Ephesians 6: "15. and having shod your feet with the preparation of the gospel of peace;" (asv)

Issues:

As of this commit of the API v2 update, I'm aware of the fact that if you say something like:

In the beginning, Gen 1:1, and Jn 3:16 (   )

neither verse will appear, because in both cases they will be caught as a citation by the regex however it things the former is a list and the latter is asking for a particular translation, and I am not going to bother with that right now, all the correct usage seems to work.
