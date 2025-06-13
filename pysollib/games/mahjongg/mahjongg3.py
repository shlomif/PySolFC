#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

from pysollib.games.mahjongg.mahjongg import r

# test
# r(5991, "AAA 1", ncards=4, layout="0daa")
# r(5992, "AAA 2", ncards=8, layout="0daadca")
# r(5993, "AAA 3", ncards=20, layout="0daaCabdacKbbdca" +
#    "Ccbdcc")
# r(5994, "AAA 4", ncards=20, layout="0daaDabdacdcaDcb" +
#    "dcc")

# ************************************************************************
# * game definitions
# ************************************************************************

r(5401, "Taipei", layout="0aagabbabdabjabl" +
    "hccacfachhckadba" +
    "ddhdehdghdiadjad" +
    "lhecaefoegaehhek" +
    "afcifehfgvfgifia" +
    "fkagahgcageaggog" +
    "gagihgkagmhhaahc" +
    "ohehhfvhfhhhvhho" +
    "hiahkhhmaiahidai" +
    "eaigoigCigaiihij" +
    "aimhjbajcojehjfv" +
    "jfJjghjhvjhojiaj" +
    "khjlakahkdakeakg" +
    "okgCkgQkgakihkja" +
    "kmhlbalcolehlfvl" +
    "fJlghlhvlholialk" +
    "hllamahmdameamgo" +
    "mgCmgamihmjammhn" +
    "aanconehnfvnfhnh" +
    "vnhoniankhnmaoah" +
    "ocaoeaogoogaoiho" +
    "kaomapcipehpgvpg" +
    "ipiapkhqcaqfoqga" +
    "qhhqkarbardhrehr" +
    "ghriarjarlhscasf" +
    "ashhskatbatdatja" +
    "tlaug")
r(5402, "Hare", layout="0aacaamacabccace" +
    "ackbcmacobeacecb" +
    "eebekcembeoofavf" +
    "cofeofkvfmofobga" +
    "cgcbgebgkcgmbgoa" +
    "iabicbiebikbimai" +
    "oakcakebkhakkakm" +
    "amebmgbmiamkbogo" +
    "ohboicqfcqhcqjas" +
    "ejsfasgjshasijsj" +
    "askCtgCtibuddufd" +
    "uhdujbulovdCvgCv" +
    "iovlbwddwfdwhdwj" +
    "bwlcyfcyhcyjbAhb" +
    "Ch")
r(5403, "Horse", layout="0bafbahbajbcdbch" +
    "bclaedbefbehbeja" +
    "elagfaghagjaifhi" +
    "gaihhiiaijakfhkg" +
    "akhhkiakjbmecmgc" +
    "mibmkcodcofcohco" +
    "jcolcqdcqfvqgcqh" +
    "vqicqjcqlbsbcsfv" +
    "sgcshvsicsjbsnot" +
    "botnbubcudcufvug" +
    "cuhvuicujculbunb" +
    "wbcwdcwfcwhcwjcw" +
    "lbwnbycayfbyhayj" +
    "bymaAbaAnaCaaCo")
r(5404, "Rat", layout="0aaabacoadbaeaag" +
    "bcacccccebcgvddo" +
    "dgbeacecceebegag" +
    "abgcbggagmbicbie" +
    "aigaimckeckgckia" +
    "kmblcblkcmevmfcm" +
    "gvmhcmibmmamobnc" +
    "Cngbnkhnocoevofc" +
    "ogvohcoibomaoobp" +
    "cbpkcqecqgcqiaqm" +
    "bscbseasgasmauab" +
    "ucbugaumbwacwccw" +
    "ebwgvxdoxgbyacyc" +
    "cyebygaAabAcoAdb" +
    "AeaAg")
r(5405, "Tiger", layout="0baabacbambaobca" +
    "bccbcmbcobebaegh" +
    "ehaeibenbgbbggbg" +
    "ibgnaibbidcifcih" +
    "dijbilainakdhkea" +
    "kfokfhkgakhpkhhk" +
    "iakjokjhkkaklbme" +
    "pmfbmgomhbmiomjb" +
    "mkboeoofbogoohbo" +
    "ipojbokbqeoqfbqg" +
    "pqhbqioqjbqkbsdd" +
    "sfcshcsjbslbubbu" +
    "dbuhbulbunbwbbwi" +
    "bwnbybbygbynbAbb" +
    "AibAnbCbbCgbCn")
r(5406, "Ram", layout="0aacaaeaagaaihbe" +
    "hbghbibccaceocea" +
    "cgaciociackadaod" +
    "chdehdihdkheabec" +
    "aeepeeaeioeiaeka" +
    "faofchfehfihfkhg" +
    "abgcageogeaggagi" +
    "ogiagkahahhehhgh" +
    "hibicaieaigaiibk" +
    "cblgbmcbmeamione" +
    "hniankanmcocboev" +
    "oebogaoiooihokho" +
    "mbooopehpiapkapm" +
    "bqcbqeaqibrgbscb" +
    "ucaueaugauiavahv" +
    "ehvghvihwabwcawe" +
    "oweawgawiowiawka" +
    "xaoxchxehxihxkhy" +
    "abycayepyeayioyi" +
    "aykazaozchzehzih" +
    "zkbAcaAeoAeaAgaA" +
    "ioAiaAkhBehBghBi" +
    "aCcaCeaCgaCi")
r(5407, "Wedges", layout="0aagbaicakdamaca" +
    "acibckccmbeaaeca" +
    "ekbemcgabgcageag" +
    "mdiacicbieaigeka" +
    "dkcckebkgakiakoh" +
    "lofmaemcdmecmgbm" +
    "iamkammamoomohno" +
    "eoaeocdoecogaoia" +
    "oodqadqccqeaqgcs" +
    "acscaseasmbuaauc" +
    "aukbumawaawibwkc" +
    "wmaygbyicykdym")
r(5408, "Monkey", layout="0aaahabaacoachad" +
    "aaeaakbcaaceackh" +
    "clacmocmhcnacood" +
    "abeabeoofoagahgb" +
    "agcaghbgobicbigb" +
    "iiaimhinaioojgbk" +
    "cdkebkgvkgdkibkk" +
    "bkmolgdmebmgvmgd" +
    "miongdoebogvogdo" +
    "iaokholaomaooopg" +
    "hpobqcdqebqgvqgd" +
    "qiaqooqoorghroas" +
    "ahsbascbsgasmaso" +
    "auaaughuhauiawih" +
    "wjawkowkhwlawmby" +
    "maAchAdaAeoAehAf" +
    "vAfaAgoAgCAghAhv" +
    "AhaAioAiCAihAjvA" +
    "jaAkoAkhAlaAmaCa" +
    "hCbaCc")
r(5409, "Rooster", layout="0aaaaagabchcccce" +
    "ccgadcvdfadiceec" +
    "egaeohfoageagoog" +
    "ohhoaiehifaigaim" +
    "aiohjmbkeokfbkgo" +
    "khbkiakkakmamccm" +
    "evmfcmgvmhcmiamk" +
    "anahncCnghoaaoco" +
    "occoevofcogvohco" +
    "iapaopahpchqaaqc" +
    "oqcbqeoqfbqgvqgo" +
    "qhbqiaqkaqmaraor" +
    "ahrchrmhsaascbsg" +
    "oshbsiaskasmasoa" +
    "taotahtohuaaufhu" +
    "gauhauoavabweowf" +
    "bwgowhbwivxgayab" +
    "ycoydbyeoyfbygoy" +
    "hbyihzaaAaaAeaAj" +
    "hAkaAlhBaaCaaCeh" +
    "CfaCgaCl")
r(5410, "Dog", layout="0aaeaaghbehbgacc" +
    "aceoceacgocgacia" +
    "ckhdchdehdghdihd" +
    "kaecoecaeeaegaei" +
    "aekhfcagcaichida" +
    "ieoiehifaigvjebk" +
    "ackcckeckgbkibkk" +
    "vlcoliolkbmacmcc" +
    "mgbmibmkamoonavn" +
    "conkboacoccoecog" +
    "bokaomaooopavpco" +
    "pkbqacqccqgbqibq" +
    "kvrcoriorkbsacsc" +
    "csecsgbsibskvtea" +
    "uchudaueouehufau" +
    "gawchxcaycoycaye" +
    "aygayiaykhzchzeh" +
    "zghzihzkaAcaAeoA" +
    "eaAgoAgaAiaAkhBe" +
    "hBgaCeaCg")
r(5411, "Snake", layout="0bagbaiobhbcgbci" +
    "bdebecbegbfebgcb" +
    "habicbiicikcimbj" +
    "avjlbkcbkebkgbki" +
    "ckkckmakooleolgo" +
    "livllhlobmcbmebm" +
    "gbmicmkcmmamoomo" +
    "vnlhnocokcomaooo" +
    "oovplhpobqcbqebq" +
    "gbqicqkcqmaqoore" +
    "orgorivrlbscbseb" +
    "sgbsicskcsmbtabu" +
    "cbvabwcbwebwgbwi" +
    "bwkbycbyebygbyib" +
    "ykbAjaCj")
r(5412, "Boar", layout="0aacaaehafaagoag" +
    "hahaaiaakhbchbka" +
    "ccoccaciackockac" +
    "mhdchdkhdmaecaee" +
    "aekoekaemoemhfkh" +
    "fmagiagkogkagmhh" +
    "kaiiaikakcbkgbki" +
    "akmolgolibmcbmeb" +
    "mgbmibmkbmmoncon" +
    "epngpnionkonmano" +
    "aoabocvocboevoeb" +
    "ogboibokvokbomvo" +
    "mhooopcopeppgppi" +
    "opkopmapobqcbqeb" +
    "qgbqibqkbqmorgor" +
    "iascbsgbsiasmaui" +
    "aukhvkawiawkowka" +
    "wmhxkhxmaycayeay" +
    "koykaymoymhzchzk" +
    "hzmaAcoAcaAiaAko" +
    "AkaAmhBchBkaCcaC" +
    "ehCfaCgoCghChaCi" +
    "aCk")
r(5413, "Ox", layout="0aahabeabkbcgoch" +
    "bciaeaaecbegbeia" +
    "emaeohfbhfnagaag" +
    "cagebggbgiagkagm" +
    "agoaicbiebigbiib" +
    "ikaimakcbkeckgck" +
    "ibkkakmbmecmgcmi" +
    "bmkaodioeaofjoga" +
    "ohjoiaojiokaolcq" +
    "edqgdqicqkcsedsg" +
    "dsicskaucbuecugc" +
    "uibukaumawcbwecw" +
    "gcwibwkawmayaayc" +
    "ayebygbyiaykayma" +
    "yohzbhznaAaaAcaA" +
    "haAmaAo")
r(5414, "Bridge 2", layout="0daadacdaedagdai" +
    "dakdamdaocccccec" +
    "cgccicckccmbeebe" +
    "gbeibekaggagiaih" +
    "hjhakhokhhlhvlha" +
    "mfamhomhCmhhnhvn" +
    "hJnhanjaofaohooh" +
    "Cohhphvphaqhoqhh" +
    "rhashaugauibwebw" +
    "gbwibwkcyccyecyg" +
    "cyicykcymdAadAcd" +
    "AedAgdAidAkdAmdA" +
    "o")
r(5415, "Spider", layout="0aaebcfaclacqbea" +
    "begbelbeqbgabghb" +
    "glbgqbibbidbihbi" +
    "lbipbkdbkhbklbko" +
    "alfaljhmgamhhmih" +
    "mkamlbmnampbnban" +
    "fanjonjonlaodhog" +
    "aohoohhoihokaolh" +
    "omaonoonhooaopao" +
    "rhpeapfapjopjvpk" +
    "oplhpqaptaqdhqga" +
    "qhoqhhqihqkaqlhq" +
    "maqnoqnhqoaqpaqr" +
    "brbarfarjorjorlh" +
    "sgashhsihskaslbs" +
    "naspatfatjbudbuh" +
    "bulbuobwbbwdbwhb" +
    "wlbwpbyabyhbylby" +
    "qbAabAgbAlbAqbCf" +
    "aClaCqaEe")
r(5416, "Waves", layout="0eafeahabmacadcf" +
    "dchadmaeacefcehh" +
    "emhfaafmagacgfcg" +
    "higmihaahmaiabif" +
    "bihiimijaajmakab" +
    "kfbkhikmilaalmam" +
    "aamfamhhmmhnaanm" +
    "aoaaofaohapmaqab" +
    "qfbqharmasabsfbs" +
    "hatmauacufcuhhum" +
    "hvaavmawacwfcwhi" +
    "wmixaaxmayadyfdy" +
    "hiymizaazmaAaeAf" +
    "eAhiAmiBaaBmaCah" +
    "CmhDaaDmaEaaFmaG" +
    "a")
r(5417, "Hot Coffee", layout="0aarbcradfadhadj" +
    "adlaeaaencerbffb" +
    "fhbfjbflafpagbbg" +
    "ndgrchfchhchjchl" +
    "bhpcindircjfcjhc" +
    "jjcjlcjpCjrckndk" +
    "ralaclfclhcljcll" +
    "clpClrcmndmranbc" +
    "nfcnhcnjcnlbnpbo" +
    "ndorbpfbphbpjbpl" +
    "appaqncqrarfarha" +
    "rjarlbsratgatlau" +
    "ravgavlaxhaxjaxl")
r(5418, "Zigzag", layout="0aabaajaaracahcb" +
    "accacihcjackacqh" +
    "cracsaebiecaedae" +
    "hieiaejvejiekael" +
    "aepieqaeragcigda" +
    "gehgfaggighagihg" +
    "jagkiglagmhgnago" +
    "igpagqaidiieaifv" +
    "ifiigaihailiimai" +
    "nviniioaipakehkf" +
    "akgakmhknakoamfa" +
    "mnaqbaqjaqrasahs" +
    "bascasihsjaskasq" +
    "hsrassaubiucauda" +
    "uhiuiaujvujiukau" +
    "laupiuqaurawciwd" +
    "awehwfawgiwhawih" +
    "wjawkiwlawmhwnaw" +
    "oiwpawqaydiyeayf" +
    "vyfiygayhayliyma" +
    "ynvyniyoaypaAehA" +
    "faAgaAmhAnaAoaCa" +
    "aCfaCnaCs")
r(5419, "Lizard", layout="0aadaafaahaajhbe" +
    "hbghbibccaceacga" +
    "ciackidjbebaejae" +
    "laeqheraesifkbga" +
    "agehgfaggagkagmb" +
    "grihlaiabifailai" +
    "nbirijmojqakaakg" +
    "hkhakiokihkjakko" +
    "kkvklakmvknakook" +
    "ohkpakqhllolmhln" +
    "ambamkammamohnlo" +
    "nmhnnaokaomaoohp" +
    "lopmhpnaqjaqlaqn" +
    "hrkorlhrmasjasla" +
    "snhtkotlhtmaujau" +
    "launhvkovlhvmawi" +
    "awkawmhxjpxkhxla" +
    "yiaykaymazehzfaz" +
    "gozghzhozihzjvzj" +
    "ozkhzlvzlozmhzna" +
    "zoozohzpazqaAiaA" +
    "kaAmbBdiBkbBraCj" +
    "aClaDchDdaDehDka" +
    "DqhDraDsaEjaElaF" +
    "daFraGk")
r(5420, "Candy", layout="0daadaccaebagbai" +
    "aakdcbccdbcfbcha" +
    "cjcecbeebegaeibg" +
    "dbgfaghbieaigakc" +
    "akeakgakiamaamcb" +
    "mebmgamiamkaoabo" +
    "cboebogboiaokopf" +
    "aqabqcbqebqgbqia" +
    "qkorfasabscbsebs" +
    "gbsiaskauaaucbue" +
    "bugauiaukawcawea" +
    "wgawiayebygaAdbA" +
    "fbAhaCcbCebCgcCi" +
    "aEbbEdbEfcEhdEja" +
    "GabGcbGecGgdGidG" +
    "k")


# ----------------------------------------------------------------------

r(5801, "Faro", name="Double Mahjongg Faro", ncards=288, layout="0aaaha" +
    "baachadaae" +
    "oaehafaagiahaaih" +
    "ajaakoakhalaamha" +
    "naaoobcvbhobmacb" +
    "hccvccacdacgichC" +
    "chaciaclhcmvcmac" +
    "nodcCdcvdhodmCdm" +
    "aebhecvecaedheea" +
    "efcehCehaejhekae" +
    "lhemvemaenofcvfh" +
    "ofmbgcagfhggagho" +
    "ghhgiagjbgmahaah" +
    "ohiahioajapjaajc" +
    "cjebjhcjkajmajop" +
    "johkahkcokhhkmhk" +
    "oalaalcqlcalfhlg" +
    "alhvlhhlialjalmq" +
    "lmalohmcomhCmhhm" +
    "manbqncandhneanf" +
    "bnhvnhanjhnkanlq" +
    "nmannhocooeoohoo" +
    "khomapcppcCpdbpe" +
    "vpebphwphbpkvpkC" +
    "plapmppmhqcoqeoq" +
    "hoqkhqmarbqrcard" +
    "hrearfbrhvrharjh" +
    "rkarlqrmarnhscos" +
    "hCshhsmataatcqtc" +
    "atfhtgathvthhtia" +
    "tjatmqtmatohuahu" +
    "couhhumhuoavapva" +
    "avccvebvhcvkavma" +
    "vopvohwahwoaxaax" +
    "obycayfhygayhoyh" +
    "hyiayjbymozcvzho" +
    "zmaAbhAcvAcaAdhA" +
    "eaAfcAhCAhaAjhAk" +
    "aAlhAmvAmaAnoBcC" +
    "BcvBhoBmCBmaCbhC" +
    "cvCcaCdaCgiChCCh" +
    "aCiaClhCmvCmaCno" +
    "DcvDhoDmaEahEbaE" +
    "chEdaEeoEehEfaEg" +
    "iEhaEihEjaEkoEkh" +
    "ElaEmhEnaEo")
r(5803, "Two Squares", name="Double Mahjongg Two Squares", ncards=288,
        layout="0daadacdaedagdai" +
    "dakdcadccdcedcgd" +
    "cidckdeadecdeede" +
    "gdeidekdgadgcdge" +
    "dggdgidgkdiadicd" +
    "iedigdiidikdkadk" +
    "cdkedkgdkidkkdoa" +
    "docdoedogdoidokd" +
    "qadqcdqedqgdqidq" +
    "kdsadscdsedsgdsi" +
    "dskduaducduedugd" +
    "uidukdwadwcdwedw" +
    "gdwidwkdyadycdye" +
    "dygdyidyk")
r(5805, "Twin Picks", name="Double Mahjongg Twin Picks", ncards=288,
        layout="0aacaaeaagaaiaak" +
    "aamhbdhbfhbhhbjh" +
    "blacaaccaceoceac" +
    "gocgaciociackock" +
    "acmacohdbhddhdfv" +
    "dfhdhvdhhdjvdjhd" +
    "lhdnaeaaecoecaee" +
    "oeeaegoegCegaeio" +
    "eiCeiaekoekaemoe" +
    "maeohfbhfdvfdhff" +
    "vffhfhvfhhfjvfjh" +
    "flvflhfnagaagcog" +
    "cageogeCgeaggogg" +
    "CggagiogiCgiagko" +
    "gkCgkagmogmagohh" +
    "bhhdvhdhhfvhfhhh" +
    "vhhhhjvhjhhlvhlh" +
    "hnaiaaicoicaieoi" +
    "eaigoigCigaiioii" +
    "Ciiaikoikaimoima" +
    "iohjbhjdhjfvjfhj" +
    "hvjhhjjvjjhjlhjn" +
    "akaakcakeokeakgo" +
    "kgakiokiakkokkak" +
    "makohldhlfhlhhlj" +
    "hllamcameamgamia" +
    "mkammapaapcapeap" +
    "gapiapkapmapoasc" +
    "aseasgasiaskasmh" +
    "tdhtfhthhtjhtlau" +
    "aaucaueoueaugoug" +
    "auiouiaukoukauma" +
    "uohvbhvdhvfvvfhv" +
    "hvvhhvjvvjhvlhvn" +
    "awaawcowcaweowea" +
    "wgowgCwgawiowiCw" +
    "iawkowkawmowmawo" +
    "hxbhxdvxdhxfvxfh" +
    "xhvxhhxjvxjhxlvx" +
    "lhxnayaaycoycaye" +
    "oyeCyeaygoygCyga" +
    "yioyiCyiaykoykCy" +
    "kaymoymayohzbhzd" +
    "vzdhzfvzfhzhvzhh" +
    "zjvzjhzlvzlhznaA" +
    "aaAcoAcaAeoAeaAg" +
    "oAgCAgaAioAiCAia" +
    "AkoAkaAmoAmaAohB" +
    "bhBdhBfvBfhBhvBh" +
    "hBjvBjhBlhBnaCaa" +
    "CcaCeoCeaCgoCgaC" +
    "ioCiaCkoCkaCmaCo" +
    "hDdhDfhDhhDjhDla" +
    "EcaEeaEgaEiaEkaE" +
    "m")
r(5806, "Roost", name="Double Mahjongg Roost", ncards=288,
        layout="0aaahabaacoachad" +
    "vadaaeoaehafvafa" +
    "agoaghahvahaaioa" +
    "ihajaakaamaaoCbf" +
    "hblhbnacbhccacdo" +
    "cdhcevceacfocfhc" +
    "gvcgachochhciacj" +
    "aclocmacnhdkhdma" +
    "eiaekoelaemaeoaf" +
    "aafcafehfjhflvfl" +
    "hfnhgchgeaghagjo" +
    "gkaglCglogmagnah" +
    "bohcahdoheahfhhi" +
    "hhkvhlhhmhibhidv" +
    "iehifaiioijaikoi" +
    "laimajaajcojdaje" +
    "Cjeojfajghjjvjkh" +
    "jlajohkcvkdhkevk" +
    "fhkgakjokkaklalb" +
    "olcaldolealfClfo" +
    "lgalhhlkblnhmbhm" +
    "dvmehmfvmghmhamk" +
    "omnanaancondaneo" +
    "nfangCngonhanian" +
    "mhnnanohochoevof" +
    "hogvohhoiapbapdo" +
    "peapfopgaphCphop" +
    "iapjhpkaploplhpm" +
    "apnhqchqevqfhqgv" +
    "qhhqiaraarcordar" +
    "eorfargCrgorhari" +
    "armhrnarohsbhsdv" +
    "sehsfvsghshaskos" +
    "natbotcatdoteatf" +
    "Ctfotgathhtkbtnh" +
    "ucvudhuevufhugau" +
    "joukaulavaavcovd" +
    "aveCveovfavghvjv" +
    "vkhvlavohwbhwdvw" +
    "ehwfawiowjawkowl" +
    "awmaxboxcaxdoxea" +
    "xfhxihxkvxlhxmhy" +
    "chyeayhayjoykayl" +
    "Cyloymaynazaazca" +
    "zehzjhzlvzlhznaA" +
    "iaAkoAlaAmaAohBk" +
    "hBmaCbhCcaCdoCdh" +
    "CevCeaCfoCfhCgvC" +
    "gaChoChhCiaCjaCl" +
    "oCmaCnCDfhDlhDna" +
    "EahEbaEcoEchEdvE" +
    "daEeoEehEfvEfaEg" +
    "oEghEhvEhaEioEih" +
    "EjaEkaEmaEo")
r(5807, "Big Castle", name="Double Mahjongg Big Castle", ncards=288,
        layout="0eaadacdaeeageai" +
    "dakdameaodcadcoc" +
    "ddvdecdfvdgcdhCd" +
    "hvdicdjvdkcdldea" +
    "deoafdaflcgacgoa" +
    "hdahlciacioajdaj" +
    "lckahkdhklckoald" +
    "elfblheljallcmah" +
    "mdhmlcmoandbnfbn" +
    "janleoahodoofooj" +
    "holeooapdbpfvpfb" +
    "pjvpjapleqahqdoq" +
    "foqjhqleqoardbrf" +
    "brjarlcsahsdhslc" +
    "soatdetfbthetjat" +
    "lcuahudhulcuoavd" +
    "avlcwacwoaxdaxlc" +
    "yacyoazdazldAadA" +
    "ocBdvBecBfvBgcBh" +
    "CBhvBicBjvBkcBld" +
    "CadCoeEadEcdEeeE" +
    "geEidEkdEmeEo")
r(5808, "Eight Squares", name="Double Mahjongg Eight Squares", ncards=288,
        layout="0daadacdaedahdaj" +
    "daldcadccdcedchd" +
    "cjdcldeadecdeede" +
    "hdejdeldhadhcdhe" +
    "dhhdhjdhldjadjcd" +
    "jedjhdjjdjldladl" +
    "cdledlhdljdlldoa" +
    "docdoedohdojdold" +
    "qadqcdqedqhdqjdq" +
    "ldsadscdsedshdsj" +
    "dsldvadvcdvedvhd" +
    "vjdvldxadxcdxedx" +
    "hdxjdxldzadzcdze" +
    "dzhdzjdzl")
r(5809, "Big Traditional", name="Double Mahjongg Big Traditional",
        ncards=288, layout="0aajacaaciackacs" +
    "aeaaegaeihejaeka" +
    "emaesagaageaggbg" +
    "ibgkagmagoagsaia" +
    "aicaiebigbiibikb" +
    "imaioaiqaisakabk" +
    "cbkebkgbkibkkbkm" +
    "bkobkqaksbmabmcc" +
    "mecmgcmicmkcmmcm" +
    "obmqbmsboaboccoe" +
    "dogdoidokdomcoob" +
    "oqbosbqabqccqedq" +
    "geqieqkdqmcqobqq" +
    "bqsJrjbsabsccsed" +
    "sgesieskdsmcsobs" +
    "qbssbuabuccuedug" +
    "duidukdumcuobuqb" +
    "usbwabwccwecwgcw" +
    "icwkcwmcwobwqbws" +
    "ayabycbyebygbyib" +
    "ykbymbyobyqaysaA" +
    "aaAcaAebAgbAibAk" +
    "bAmaAoaAqaAsaCaa" +
    "CeaCgbCibCkaCmaC" +
    "oaCsaEaaEgaEihEj" +
    "aEkaEmaEsaGaaGia" +
    "GkaGsaIaaIjaIsaK" +
    "j")
r(5810, "Sphere", name="Double Mahjongg Sphere", ncards=288,
        layout="0aajaalaanabhhbk" +
    "hbmabpacfhciacjo" +
    "ckaclocmacnhcoac" +
    "raddhdgadhodivdk" +
    "hdlvdmodoadphdqa" +
    "dtaefoegveihejae" +
    "koekaemoemhenveo" +
    "oeqaerafchfdhffh" +
    "fhafiafohfphfrhf" +
    "tafuageogeaggpgg" +
    "pgihgjpgkbglpgmh" +
    "gnpgoagqpgqagsog" +
    "sahbhhchhfhhhahj" +
    "ahnhhphhrhhuahva" +
    "idoidvieaifoigai" +
    "hoiihijoikbiloim" +
    "hinoioaipoiqairv" +
    "isaitoitajahjbhj" +
    "dhjfhjhvjlhjphjr" +
    "hjthjvajwakcokcv" +
    "kdakeokeakgokgak" +
    "iokiakkokkakmokm" +
    "akookoakqokqakso" +
    "ksvktakuokualahl" +
    "bhldhlfvlfhlhvlh" +
    "hljvljhllvllhlnv" +
    "lnhlpvlphlrvlrhl" +
    "thlvalwamcomcvmd" +
    "ameomeamgomgamio" +
    "miamkomkammommam" +
    "oomoamqomqamsoms" +
    "vmtamuomuanahnbh" +
    "ndhnfhnhvnlhnphn" +
    "rhnthnvanwaodood" +
    "voeaofoogaohooih" +
    "ojookboloomhonoo" +
    "oaopooqaorvosaot" +
    "ootapbhpchpfhpha" +
    "pjapnhpphprhpuap" +
    "vaqeoqeaqgpqgpqi" +
    "hqjpqkbqlpqmhqnp" +
    "qoaqqpqqaqsoqsar" +
    "chrdhrfhrhariaro" +
    "hrphrrhrtaruasfo" +
    "sgvsihsjaskoskas" +
    "mosmhsnvsoosqasr" +
    "atdhtgathotivtkh" +
    "tlvtmotoatphtqat" +
    "taufhuiaujoukaul" +
    "oumaunhuoauravhh" +
    "vkhvmavpawjawlaw" +
    "n")

# ----------------------------------------------------------------------

r(5901, "Happy New Year", name="Half Mahjongg Happy New Year", ncards=72,
        layout="0aafaajaanaceaci" +
    "acmbedbehaelofdo" +
    "fhhflbgdbghagloh" +
    "dohhaibbidaighih" +
    "aiiailhimainojma" +
    "kaakeckhakjbkmbk" +
    "oolmambbmdamghmh" +
    "amiamlhmmamnondo" +
    "nhbodbohaolopdop" +
    "hhplbqdbqhaqlase" +
    "asiasmaufaujaun")

r(5904, "Smile", name="Half Mahjongg Smile", ncards=72,
        layout="0bagoahbaibbebbk" +
    "bccbcmbebbenaffb" +
    "fjbgahgfbgoahfbh" +
    "kbiabiobjlbkabko" +
    "bllbmabmoanfbnkb" +
    "oahofbooapfbpjbq" +
    "bbqnbscbsmbtebtk" +
    "bugouhbui")
r(5905, "Wall", name="Half Mahjongg Wall", ncards=72,
        layout="0eaabacbaebagbai" +
    "bakbameaoacaacoa" +
    "eaaeoagaagoaiaai" +
    "oakaakoamaamoaoa" +
    "aooaqaaqoasaasoa" +
    "uaauoawaawoayaay" +
    "oaAaaAoaCaaCoeEa" +
    "bEcbEebEgbEibEkb" +
    "EmeEo")
r(5906, "Star", name="Half Mahjongg Star", ncards=72,
        layout="0aaeaceacghdgaef" +
    "aehhfgbfoafqagfa" +
    "ghagmhhhahkhhlhh" +
    "nahoaigaiiaimaje" +
    "hjgojhhjiojjbjka" +
    "kcakgakialahldal" +
    "ehlfilhvliiljalk" +
    "amcamgamianehngo" +
    "nhhnionjbnkaogao" +
    "iaomhphapkhplhpn" +
    "apoaqfaqhaqmhrgb" +
    "roarqasfashhtgau" +
    "eaugawe")


# ----------------------------------------------------------------------

# r(5601, "Skomoroh 1", ncards=28, layout="0aacaaeaaghbdhbf" +
#    "acaacdoceacfacih" +
#    "ddhdfaebaeeoeeae" +
#    "hhfdhffagaagdoge" +
#    "agfagihhdhhfaica" +
#    "ieaig")
# r(5602, "Skomoroh 2", ncards=116, layout="0aaeaaghahaaiaak" +
#    "abaaboacfbchacja" +
#    "daadoaeghehaeiaf" +
#    "aafocghahaahcahf" +
#    "vhhahjahmahohidc" +
#    "ihhilajaajdajfwj" +
#    "hajjajlajohkdhkg" +
#    "akhokhhkihklalaa" +
#    "lcalewlhalkalmal" +
#    "ohmfamgimhamihmj" +
#    "anaancanewnhanka" +
#    "nmanohodhogaohoo" +
#    "hhoiholapaapdapf" +
#    "wphapjaplapohqdc" +
#    "qhhqlaraarcarfvr" +
#    "harjarmarocshata" +
#    "atoaughuhauiavaa" +
#    "voawfbwhawjaxaax" +
#    "oayeayghyhayiayk")
# r(5603, "Skomoroh 3", ncards=132, layout="0aachadaaeoaeXae" +
#    "hafyafaagoagXagh" +
#    "ahaaiabaabkhcahc" +
#    "kadaadeadgadkhea" +
#    "hefhekafaafeafga" +
#    "fkhgahgfhgkahaah" +
#    "eahgahkhiahifhik" +
#    "ajaajeajgajkhkah" +
#    "kfhkkalaalealgal" +
#    "khmahmfhmkanaane" +
#    "onfangankhofXofa" +
#    "pbapdapfspfaphap" +
#    "jhqfXqfaraareorf" +
#    "argarkhsahsfhska" +
#    "taateatgatkhuahu" +
#    "fhukavaaveavgavk" +
#    "hwahwfhwkaxaaxea" +
#    "xgaxkhyahyfhykaz" +
#    "aazeazgazkhAahAf" +
#    "hAkaBaaBeaBgaBkh" +
#    "CahCkaDaaDkaEchE" +
#    "daEeoEeXEehEfyEf" +
#    "aEgoEgXEghEhaEi")
# r(5604, "Skomoroh 4", ncards=52, layout="0aajaalaanabhabp" +
#    "acfacnacraddadla" +
#    "dtaejafcafuagiah" +
#    "bbhoahvaiiajaajw" +
#    "akjalaalwamkamma" +
#    "naanwaonapaapwaq" +
#    "oarbbriarvasoatc" +
#    "atuaunavdavlavta" +
#    "wfawjawraxhaxpay" +
#    "jaylayn")
# r(5605, "Skomoroh 5", ncards=208, layout="0aahaajaalaanaap" +
#    "hbihbkoblhbmhboa" +
#    "ccaceacgaciackac" +
#    "macoacqacsacuaec" +
#    "aeuagdagjaglagna" +
#    "gthhkhhmaieaijai" +
#    "loilainaishjkhjm" +
#    "akfakjakloklakna" +
#    "krhlkhlmameamgam" +
#    "jamlomlamnamqams" +
#    "anchndhnkhnmhnta" +
#    "nuaoeaohaojaoloo" +
#    "laonaopaosapchpd" +
#    "hpkhpmhptapuaqea" +
#    "qhaqjaqlaqnaqpaq" +
#    "saraarchrdhrtaru" +
#    "arwaseasgasiaska" +
#    "smasoasqassataht" +
#    "batchtdhtfithitj" +
#    "itlitnitphtrhtta" +
#    "tuhtvatwaueaugau" +
#    "iaukaumauoauqaus" +
#    "avaavchvdhvtavua" +
#    "vwaweawhawjawlaw" +
#    "nawpawsaxchxdhxk" +
#    "hxmhxtaxuayeayha" +
#    "yjayloylaynaypay" +
#    "sazchzdhzkhzmhzt" +
#    "azuaAeaAgaAjaAlo" +
#    "AlaAnaAqaAshBkhB" +
#    "maCfaCjaCloClaCn" +
#    "aCrhDkhDmaEeaEja" +
#    "EloElaEnaEshFkhF" +
#    "maGdaGjaGlaGnaGt" +
#    "aIcaIuaKcaKeaKga" +
#    "KiaKkaKmaKoaKqaK" +
#    "saKuhLihLkoLlhLm" +
#    "hLoaMhaMjaMlaMna" +
#    "Mp")
# r(5606, "Skomoroh 6", layout="0aadaafaahaajaal" +
#    "aanaapadaaddadfa" +
#    "dhadjadladnadpad" +
#    "sheehegheihekhem" +
#    "heoafaafdaffoffa" +
#    "fhofhafjofjaflof" +
#    "lafnofnafpafshge" +
#    "hggvgghgivgihgkv" +
#    "gkhgmvgmhgoahaCh" +
#    "hChjChlahsaidaif" +
#    "oifaihoihJiiaijo" +
#    "ijJikailoilainoi" +
#    "naipajahjehjgvjg" +
#    "CjhhjivjihjkvjkC" +
#    "jlhjmvjmhjoajsak" +
#    "dakfokfakhokhJki" +
#    "akjokjJkkaklokla" +
#    "knoknakpalaClhCl" +
#    "jCllalshmehmgvmg" +
#    "hmivmihmkvmkhmmv" +
#    "mmhmoanaandanfon" +
#    "fanhonhanjonjanl" +
#    "onlannonnanpansh" +
#    "oehoghoihokhomho" +
#    "oapaapdapfaphapj" +
#    "aplapnappapsasda" +
#    "sfashasjaslasnas" +
#    "p")
# r(5607, "Skomoroh 7", ncards=56, layout="0aabaadaafaahaaj" +
#    "aapaaraatablabwa" +
#    "daadmadwafaafnaf" +
#    "wahaahnahwajfajh" +
#    "ajmajwakdakjalbd" +
#    "llalvamnamtanaan" +
#    "kanpanrapaapjapw" +
#    "araarjarwataatka" +
#    "twavaavlawdawfaw" +
#    "hawnawpawrawtawv")
