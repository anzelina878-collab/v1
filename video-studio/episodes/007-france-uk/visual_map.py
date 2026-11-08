"""Explicit semantic montage. Every assignment is tied to the supplied narration."""
PLAN='''
12:12|turntable|model-rafale|FR|DASSAULT RAFALE · РОДИНА
13:13|archive|rafale-tlp|FR|RAFALE · НАВЧАННЯ, 2022
14:14|turntable|model-rafale|FR|RAFALE · RBE2 ТА SPECTRA
15:15|photo|meteor|FR|METEOR · КЕРОВАНА РАКЕТА
16:16|archive|cdg-operations|FR|RAFALE M · CHARLES DE GAULLE, НАВЧАННЯ 2024
17:18|turntable|model-typhoon|GB|EUROFIGHTER TYPHOON · РОДИНА
19:19|photo|scalp|GB|STORM SHADOW · ВИСТАВКОВИЙ ЗРАЗОК
20:21|archive|typhoon-walk|GB|TYPHOON FGR4 · ТЕХНІЧНИЙ ОГЛЯД, 2026
22:22|turntable|model-f35b|GB|F-35B · РОДИНА ЛІТАКІВ
23:23|archive|qe-embark|GB|F-35B · ПАЛУБНІ ОПЕРАЦІЇ, 2020
24:24|archive|rafale-action|FR|RAFALE · ФРАНЦІЯ, АРХІВ 2019
25:25|archive|typhoon-action|GB|RAF TYPHOON · RED FLAG, 2026
26:26|compare|aircraft|FR|АВІАЦІЙНІ АРСЕНАЛИ
28:29|photo|leclerc|FR|LECLERC · 120 ММ
30:30|archive|leclerc-action|FR|LECLERC · STRONG EUROPE TANK CHALLENGE, 2018
31:31|photo|leclerc|FR|LECLERC · РОДИНА ТАНКІВ
32:32|photo|griffon|FR|VBMR GRIFFON
33:34|archive|challenger-action|GB|CHALLENGER 2 · НАВЧАННЯ, 2018
35:36|archive|challenger-training|GB|CHALLENGER 2 · НАВЧАННЯ, 2017
37:38|photo|challenger3|GB|CHALLENGER 3 · ДЕМОНСТРАТОР / ВИПРОБУВАННЯ
39:39|photo|challenger3|GB|CHALLENGER 3 · ПРОГРАМА МОДЕРНІЗАЦІЇ
40:40|archive|leclerc-fire|FR|LECLERC · НАВЧАЛЬНІ СТРІЛЬБИ, 2018
41:41|photo|ajax|GB|AJAX · РОДИНА БРОНЕМАШИН
42:42|graphic|survival|FR|ЗАХИСТ НА ПОЛІ БОЮ
44:45|photo|scalp|FR|SCALP-EG / STORM SHADOW · РОДИНА
46:48|turntable|model-typhoon|GB|TYPHOON · ПЛАТФОРМА ДЛЯ STORM SHADOW
49:49|photo|scalp|GB|STORM SHADOW · ВИСТАВКОВИЙ ЗРАЗОК
50:50|photo|exocet|FR|EXOCET · ПРОТИКОРАБЕЛЬНА РАКЕТА
51:51|archive|tomahawk-launch|GB|TOMAHAWK · АРХІВ ВМС США, 2014
52:53|photo|brimstone|GB|BRIMSTONE · КЕРОВАНА РАКЕТА
54:55|photo|scalp|FR|SCALP-EG / STORM SHADOW · РОДИНА
57:58|archive|french-infantry|FR|ФРАНЦУЗЬКА ПІХОТА · НАВЧАННЯ, 2022
59:59|photo|famas|FR|FAMAS · ПОПЕРЕДНЄ ПОКОЛІННЯ
60:60|photo|minimi|FR|FN MINIMI
61:62|photo|l85a3|GB|L85A3 · 5,56 ММ
63:63|archive|british-infantry|GB|L85A2 · РОДИНА SA80, НАВЧАННЯ 2018
64:64|photo|l85a3|GB|L85A3 · МОДЕРНІЗОВАНА ГВИНТІВКА
65:65|photo|nlaw|GB|NLAW · ПРОТИТАНКОВИЙ КОМПЛЕКС
66:66|photo|hk416|FR|HK416 · РОДИНА, ЗРАЗОК HK416N
67:67|photo|l85a3|GB|L85A3 · БУЛПАП
68:69|archive|french-exercise|FR|ФРАНЦУЗЬКО-АМЕРИКАНСЬКІ НАВЧАННЯ DELAYEN, 2025
71:71|photo|caesar|FR|CAESAR · 155 ММ
72:72|archive|caesar-action|FR|CAESAR · DYNAMIC FRONT, 2026
73:73|photo|caesar|FR|CAESAR · РОДИНА ГАУБИЦЬ
74:74|archive|caesar-night|FR|CAESAR · НАВЧАННЯ DYNAMIC FRONT, 2023
75:76|photo|as90|GB|AS90 · 155 ММ
77:79|archive|archer-action|GB|ARCHER · БРИТАНСЬКА АРТИЛЕРІЯ, 2024
80:80|photo|caesar|FR|CAESAR
81:81|photo|archer|GB|ARCHER · РОДИНА ГАУБИЦЬ
82:82|graphic|artillery|FR|СУЧАСНА АРТИЛЕРІЯ
84:84|photo|reaper|FR|MQ-9 REAPER · РОДИНА БПЛА
85:85|photo|patroller|FR|SAFRAN PATROLLER
86:87|photo|protector|GB|MQ-9B SKYGUARDIAN · РОДИНА PROTECTOR
88:89|graphic|drones|FR|БЕЗПІЛОТНІ СИСТЕМИ
90:90|graphic|readiness|FR|ПРОЄКТ ТА ГОТОВА СИСТЕМА
91:91|photo|patroller|FR|SAFRAN PATROLLER
92:92|photo|protector|GB|MQ-9B SKYGUARDIAN · РОДИНА
94:94|photo|sampt|FR|SAMP/T · НАЗЕМНА ППО
95:95|photo|aster|FR|ASTER · РОДИНА РАКЕТ
96:96|photo|sampt|FR|SAMP/T · РОДИНА КОМПЛЕКСІВ
97:98|photo|skysabre|GB|SKY SABRE · ППО ВЕЛИКОЇ БРИТАНІЇ
99:99|photo|type45|GB|TYPE 45 · SEA VIPER
100:100|compare|airdefense|FR|НАЗЕМНА ТА МОРСЬКА ППО
101:101|photo|sampt|FR|SAMP/T
102:102|photo|type45|GB|TYPE 45
103:103|graphic|airdefense|FR|ППО ЯК ЄДИНА СИСТЕМА
105:106|photo|tiger-fr|FR|TIGER · ФРАНЦУЗЬКИЙ ВЕРТОЛІТ
107:108|photo|tiger-fr|FR|TIGER · ФРАНЦУЗЬКИЙ ВЕРТОЛІТ
109:109|turntable|model-apache|GB|AH-64 APACHE · РОДИНА
110:110|archive|apache-demo|GB|AH-64 APACHE · НАВЧАННЯ США, 2022
111:111|photo|nh90|FR|NH90 · РОДИНА ВЕРТОЛЬОТІВ
112:112|photo|chinook|GB|CH-47 CHINOOK · РОДИНА
113:113|turntable|model-apache|GB|AH-64 APACHE · РОДИНА
114:114|photo|tiger-fr|FR|TIGER
115:115|graphic|helicopters|FR|ВЕРТОЛІТ У СУЧАСНОМУ БОЮ
117:117|photo|charles|FR|CHARLES DE GAULLE · R91
118:119|archive|cdg-operations|FR|RAFALE M · КАТАПУЛЬТНИЙ ЗЛІТ, НАВЧАННЯ 2024
120:120|photo|qe|GB|HMS QUEEN ELIZABETH · R08
121:122|photo|pow|GB|HMS PRINCE OF WALES · R09
123:123|archive|qe-embark|GB|F-35B · HMS QUEEN ELIZABETH, 2020
124:124|photo|charles|FR|CHARLES DE GAULLE · АТОМНИЙ АВІАНОСЕЦЬ
125:125|archive|qe-embark|GB|F-35B · HMS QUEEN ELIZABETH, 2020
126:126|map|map-region|FR|
127:127|photo|fremm-fr|FR|FREMM · ФРАНЦУЗЬКИЙ ФРЕГАТ
128:128|photo|astute|GB|ASTUTE · РОДИНА АТОМНИХ СУБМАРИН
129:129|photo|vanguard|GB|VANGUARD · СТРАТЕГІЧНА СУБМАРИНА
130:130|archive|rafale-tlp|FR|RAFALE · НАВЧАННЯ, 2022
131:131|turntable|model-f35b|GB|F-35B · РОДИНА ЛІТАКІВ
132:132|graphic|navy|GB|ГОТОВНІСТЬ ФЛОТУ
134:134|map|map-region|FR|
135:136|graphic|nuclear|FR|ВІЙСЬКОВІ ЯДЕРНІ ЗАПАСИ · ОЦІНКА
137:138|photo|triomphant|FR|TRIOMPHANT · РОДИНА СУБМАРИН
139:139|turntable|model-rafale|FR|RAFALE · ПОВІТРЯНИЙ КОМПОНЕНТ
140:141|photo|vanguard|GB|VANGUARD · СТРАТЕГІЧНА СУБМАРИНА
142:142|graphic|future-sub|GB|DREADNOUGHT · ПРОЄКТ МАЙБУТНЬОЇ СУБМАРИНИ
143:143|compare|french-deterrence|FR|ФРАНЦІЯ · МОРЕ ТА ПОВІТРЯ
144:144|archive|trident-test|GB|TRIDENT II D5 · ВИПРОБУВАЛЬНИЙ ПУСК США, 2019
145:146|graphic|deterrence|FR|ЯДЕРНЕ СТРИМУВАННЯ
148:148|map|map-region|FR|
149:149|turntable|model-rafale|FR|ФРАНЦУЗЬКИЙ АРСЕНАЛ
150:150|archive|caesar-action|FR|CAESAR · ФРАНЦУЗЬКА АРТИЛЕРІЯ, 2026
151:151|turntable|model-typhoon|GB|БРИТАНСЬКИЙ АРСЕНАЛ
152:152|archive|qe-embark|GB|HMS QUEEN ELIZABETH · ПАЛУБНА АВІАЦІЯ, 2020
153:153|compare|tanks|FR|МОДЕРНІЗАЦІЯ БРОНЕТЕХНІКИ
154:154|photo|scalp|FR|SCALP-EG / STORM SHADOW
155:155|compare|carriers|FR|ДВА ПІДХОДИ ДО ПАЛУБНОЇ АВІАЦІЇ
156:156|compare|french-deterrence|FR|КОМПОНЕНТИ СТРИМУВАННЯ
157:157|graphic|system|FR|МОЖЛИВОСТІ ВИЗНАЧАЄ СИСТЕМА
158:158|archive|leclerc-action|FR|LECLERC · ФРАНЦІЯ, НАВЧАННЯ 2018
159:159|archive|typhoon-action|GB|RAF TYPHOON · НАВЧАННЯ, 2026
160:160|map|map-region|FR|
162:163|question|original|FR|ЩО ВАС НАЙБІЛЬШЕ ВРАЗИЛО?
164:164|compare|aircraft|FR|RAFALE ЧИ EUROFIGHTER?
165:165|compare|tanks|FR|LECLERC ЧИ CHALLENGER?
166:166|compare|carriers|FR|ЯКИЙ ФЛОТ ОБРАЛИ Б ВИ?
167:168|question|original|FR|ЯКА КАТЕГОРІЯ НАЙВАЖЛИВІША?
'''
SPANS=[]
for line in PLAN.strip().splitlines():
 span,kind,key,country,title=line.split('|');a,b=map(int,span.split(':'));SPANS.append(dict(a=a,b=b,kind=kind,asset_id=key,country=country,title=title))
