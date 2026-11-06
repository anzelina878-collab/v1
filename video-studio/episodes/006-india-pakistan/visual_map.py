"""Reviewed paragraph-to-visual assignments. Source ranges are enforced by compiler.
Country flag marks the compared country; archive labels explicitly name other operators.
"""
# a:b | kind | asset | country | optional title. No automatic keyword/random asset picker.
PLAN='''
22:23|section|original|IN|АВІАЦІЯ
24:25|turntable|model-rafale|IN|RAFALE · РОДИНА ЛІТАКІВ
26:26|archive|rafale-action|IN|RAFALE · ФРАНЦІЯ, АРХІВ 2019
27:27|photo|meteor|IN|METEOR
28:28|archive|rafale-indian-action|IN|RAFALE · RED FLAG–ALASKA, 2024
29:30|photo|su30|IN|СУ-30МКІ
31:31|turntable|model-mig29|IN|МІГ-29 · РОДИНА ЛІТАКІВ
32:34|photo|j10|PK|J-10 · РОДИНА ЛІТАКІВ
35:35|photo|pl15|PK|PL-15 · РОДИНА РАКЕТ
36:37|photo|jf17|PK|JF-17 THUNDER
38:40|archive|rafale-action|IN|RAFALE · ФРАНЦІЯ, АРХІВ 2019
41:42|compare|aircraft|IN|RAFALE ТА J-10CE
43:43|archive|rafale-indian-action|IN|RAFALE · RED FLAG–ALASKA, 2024
44:44|photo|rafale-india|IN|DASSAULT RAFALE
45:45|photo|j10ce|PK|J-10CE · ЕКСПОЗИЦІЯ, ЧЖУХАЙ 2024
46:48|turntable|model-rafale|IN|RAFALE · РОДИНА ЛІТАКІВ
50:51|section|original|IN|ТАНКИ ТА БРОНЕТЕХНІКА
52:54|photo|bhishma|IN|Т-90S BHISHMA
55:55|photo|t72|IN|Т-72 · РОДИНА ТАНКІВ
56:58|photo|arjun|IN|ARJUN
59:61|photo|vt4|PK|VT-4
62:63|photo|alkhalid|PK|AL-KHALID
64:66|compare|tanks|IN|Т-90S BHISHMA ТА VT-4
67:67|map|map-north|IN|
68:68|archive|yudh20|IN|БРОНЕТЕХНІКА · НАВЧАННЯ, 2021
69:69|photo|bhishma|IN|Т-90S BHISHMA
70:70|photo|vt4|PK|VT-4
71:71|photo|harop|IN|IAI HAROP
72:73|archive|optics-training|IN|ОПТИКА ТА ЗВ’ЯЗОК · НАВЧАННЯ, 2026
75:76|section|original|IN|РАКЕТНЕ ОЗБРОЄННЯ
77:78|photo|brahmos|IN|BRAHMOS
79:80|archive|brahmos-launch|IN|BRAHMOS · ВИПРОБУВАЛЬНИЙ ПУСК, 2022
81:82|photo|agni|IN|AGNI · РОДИНА РАКЕТ
83:83|photo|prithvi|IN|PRITHVI-II · ВИПРОБУВАННЯ
84:86|photo|shaheen|PK|SHAHEEN · РОДИНА РАКЕТ
87:88|photo|babur|PK|BABUR
89:89|photo|fatah|PK|FATAH · РОДИНА СИСТЕМ
90:91|archive|brahmos-test|IN|BRAHMOS · ВИПРОБУВАЛЬНИЙ ПУСК, 2022
92:92|photo|fatah|PK|FATAH · РОДИНА СИСТЕМ
93:94|map|map-region|IN|
95:96|photo|fatah|PK|FATAH · РОДИНА СИСТЕМ
97:97|photo|brahmos|IN|BRAHMOS
98:99|photo|shaheen|PK|SHAHEEN · РОДИНА РАКЕТ
101:103|section|original|IN|ПІХОТНЕ ОЗБРОЄННЯ
104:105|photo|sig716|IN|SIG716i
106:106|photo|ak203|IN|АК-203
107:107|photo|insas|IN|INSAS
108:108|archive|austrahind|IN|ПІДГОТОВКА ПІХОТИ · AUSTRAHIND, 2022
109:111|photo|g3|PK|G3
112:113|photo|type56|PK|TYPE 56 · РОДИНА АВТОМАТІВ
114:115|archive|yudh20|IN|ПІДГОТОВКА ПІХОТИ · НАВЧАННЯ, 2021
116:118|archive|yudh22|IN|ГІРСЬКА ПІДГОТОВКА · НАВЧАННЯ, 2022
119:119|archive|infantry2019|IN|YUDH ABHYAS · НАВЧАННЯ, 2019
120:120|photo|g3|PK|G3
121:122|archive|yudh20|IN|ВЗАЄМОДІЯ ПІДРОЗДІЛІВ · НАВЧАННЯ, 2021
124:124|section|original|IN|АРТИЛЕРІЯ
125:127|photo|k9|IN|K9 VAJRA-T
128:129|archive|m777-india|IN|M777 · НАВЧАННЯ, 2026
130:130|photo|atags|IN|ATAGS
131:134|photo|sh15|PK|SH-15
135:135|archive|m109-action|PK|M109 · РОДИНА САУ, НАВЧАННЯ США
136:136|map|map-north|IN|
137:138|archive|m777-joint|IN|M777 · СПІЛЬНІ НАВЧАННЯ, 2026
139:139|photo|sh15|PK|SH-15
140:141|map|map-north|PK|
142:142|photo|k9|IN|K9 VAJRA-T
144:144|section|original|IN|БЕЗПІЛОТНИКИ
145:146|photo|heron|IN|HERON
147:148|photo|harop|IN|IAI HAROP
149:149|photo|heron|IN|HERON · РОЗВІДУВАЛЬНА ПЛАТФОРМА
150:153|photo|shahpar|PK|SHAHPAR-II
154:155|compare|drones|IN|БЕЗПІЛОТНІ СИСТЕМИ
156:156|photo|akash|IN|AKASH
157:157|photo|hq9|PK|HQ-9 · РОДИНА КОМПЛЕКСІВ
158:159|photo|shahpar|PK|SHAHPAR-II
160:162|photo|harop|IN|IAI HAROP
163:163|photo|shahpar|PK|SHAHPAR-II
164:165|compare|drones|IN|БЕЗПІЛОТНІ СИСТЕМИ
167:168|section|original|IN|ПРОТИПОВІТРЯНА ОБОРОНА
169:170|photo|s400|IN|С-400 · РОДИНА КОМПЛЕКСІВ
171:172|photo|akash|IN|AKASH
173:173|compare|airdefense|IN|БАГАТОРІВНЕВА ОБОРОНА
174:176|photo|hq9|PK|HQ-9 · РОДИНА КОМПЛЕКСІВ
177:177|photo|ly80|PK|HQ-16 · РОДИНА LY-80
178:180|map|map-region|IN|
181:181|photo|s400|IN|С-400 · РОДИНА КОМПЛЕКСІВ
182:182|photo|brahmos|IN|BRAHMOS
183:184|compare|airdefense|IN|ППО МАЄ ОБМЕЖЕННЯ
185:187|archive|integrated|IN|КОМАНДУВАННЯ ТА КООРДИНАЦІЯ · НАВЧАННЯ, 2026
188:188|photo|akash|IN|AKASH
189:189|photo|hq9|PK|HQ-9 · РОДИНА КОМПЛЕКСІВ
190:190|photo|akash|IN|AKASH
192:192|section|original|IN|ВЕРТОЛЬОТИ
193:194|turntable|model-apache|IN|AH-64 APACHE · РОДИНА
195:195|archive|apache-indian-action|IN|AH-64 · ІНДІЯ, НАВЧАННЯ 2026
196:197|photo|lch|IN|HAL PRACHAND
198:198|archive|austrahind|IN|DHRUV · AUSTRAHIND, 2022
199:201|photo|cobra-pak|PK|AH-1 COBRA · РОДИНА
202:203|photo|cobra-pak|PK|AH-1 COBRA · РОДИНА
204:204|archive|apache-demo|IN|AH-64 · РОДИНА, НАВЧАННЯ США
205:205|photo|cobra-pak|PK|AH-1 COBRA · РОДИНА
206:207|map|map-north|IN|
208:208|turntable|model-apache|IN|AH-64 APACHE · РОДИНА
210:211|section|original|IN|ВІЙСЬКОВО-МОРСЬКИЙ ФЛОТ
212:213|archive|vikrant-video|IN|INS VIKRANT · АРХІВ ФЛОТУ
214:214|photo|vikramaditya|IN|INS VIKRAMADITYA
215:216|photo|kolkata|IN|ЕСМІНЕЦЬ КЛАСУ KOLKATA
217:217|photo|kalvari|IN|ПІДВОДНІ ЧОВНИ КЛАСУ KALVARI
218:218|photo|arihant|IN|INS ARIHANT
219:222|photo|type054|PK|TUGHRIL · TYPE 054A/P
223:224|photo|agosta|PK|AGOSTA · РОДИНА ПІДВОДНИХ ЧОВНІВ
225:226|map|map-navy|IN|
227:227|archive|navy-shakti|IN|INS SHAKTI · MALABAR, 2020
228:228|photo|type054|PK|TUGHRIL · TYPE 054A/P
229:229|archive|malabar|IN|СПІЛЬНИЙ ФЛОТ · MALABAR, 2020
230:230|photo|agosta|PK|AGOSTA · РОДИНА
231:232|photo|kalvari|IN|ПІДВОДНІ ЧОВНИ КЛАСУ KALVARI
234:236|section|original|IN|ЯДЕРНИЙ АРСЕНАЛ
237:239|graphic|nuclear|IN|ЯДЕРНІ АРСЕНАЛИ · ОЦІНКА SIPRI
240:240|photo|agni|IN|AGNI · РОДИНА РАКЕТ
241:241|archive|k4-launch|IN|К-4 · ВИПРОБУВАЛЬНИЙ ПУСК, 2014
242:243|photo|shaheen|PK|SHAHEEN · РОДИНА РАКЕТ
244:246|map|map-region|IN|
247:247|photo|delhi|IN|НЬЮ-ДЕЛІ
248:248|photo|islamabad|PK|ІСЛАМАБАД
249:250|map|map-region|PK|
252:253|section|original|IN|ПІДСУМОК
254:254|turntable|model-rafale|IN|RAFALE · РОДИНА ЛІТАКІВ
255:255|photo|j10|PK|J-10 · РОДИНА ЛІТАКІВ
256:256|photo|bhishma|IN|Т-90S BHISHMA
257:257|photo|vt4|PK|VT-4
258:258|compare|missiles|IN|BRAHMOS ТА SHAHEEN
259:259|archive|m777-india|IN|M777 · НАВЧАННЯ, 2026
260:260|compare|drones|IN|HERON ТА SHAHPAR-II
261:262|compare|airdefense|IN|С-400 ТА HQ-9
263:263|archive|vikrant-video|IN|INS VIKRANT · АРХІВ ФЛОТУ
264:264|photo|agosta|PK|AGOSTA · РОДИНА
265:266|photo|shaheen|PK|SHAHEEN · РОДИНА РАКЕТ
267:268|map|map-region|IN|
269:269|photo|j10ce|PK|J-10CE · ЕКСПОЗИЦІЯ, ЧЖУХАЙ 2024
270:270|turntable|model-rafale|IN|RAFALE · РОДИНА ЛІТАКІВ
271:271|photo|vt4|PK|VT-4
272:272|archive|yudh22|IN|ПІДГОТОВКА ПІДРОЗДІЛІВ · НАВЧАННЯ, 2022
273:273|map|map-region|IN|
275:276|question|original|IN|ЩО ВАС ЗДИВУВАЛО НАЙБІЛЬШЕ?
277:277|compare|aircraft|IN|RAFALE ТА J-10CE?
278:278|compare|missiles|IN|BRAHMOS ТА SHAHEEN?
279:279|compare|navies|IN|АВІАНОСЦІ ЧИ ПІДВОДНІ СИЛИ?
280:281|question|original|IN|ЯКІ ДВІ КРАЇНИ ПОРІВНЯТИ ДАЛІ?
282:282|outro|original|IN|ПІДПИШІТЬСЯ НА АРСЕНАЛ 360°
283:285|ident|channel-ident|IN|АРСЕНАЛ 360°
'''
SPANS=[]
for line in PLAN.strip().splitlines():
 interval,kind,key,country,title=line.split('|');a,b=map(int,interval.split(':'));SPANS.append(dict(a=a,b=b,kind=kind,asset_id=key,country=country,title=title))
