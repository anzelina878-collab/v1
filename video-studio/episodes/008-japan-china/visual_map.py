"""Explicit paragraph-to-visual assignments; documentary source windows are reviewed separately."""
PLAN='''
15:15|section|original|JP|АВІАЦІЯ
16:17|archive|jasdf-f35|JP|F-35A JASDF · KEEN SWORD, 2024
18:18|photo|f35a|JP|F-35A · РОДИНА ЛІТАКІВ
19:19|graphic|sensors|JP|F-35A · ЕЛЕКТРОННІ СИСТЕМИ
20:20|turntable|model-f35b|JP|F-35B · РОДИНА ЛІТАКІВ
21:21|archive|kaga-trials|JP|F-35B · ВИПРОБУВАННЯ НА JS KAGA, 2024
22:22|photo|f15j|JP|F-15J
23:24|archive|j20-anniversary|CN|J-20 · АРХІВ КНР
25:25|photo|j20|CN|CHENGDU J-20
26:26|archive|j20-airshow|CN|J-20 · АВІАСАЛОН У ЧЖУХАЇ, 2018
27:27|photo|pl15|CN|PL-15 · КЕРОВАНА РАКЕТА
28:28|photo|j16|CN|SHENYANG J-16
29:29|photo|j10c-exact|CN|CHENGDU J-10C
30:30|archive|j20-anniversary|CN|J-20 · АРХІВ КНР
31:31|turntable|model-f35b|JP|F-35 · РОДИНА, ВАРІАНТ B
32:32|compare|aircraft|JP|F-35 ТА J-20
33:34|archive|jasdf-arrival|JP|F-35A JASDF · ПІДГОТОВКА ТА ВЗАЄМОДІЯ, 2017
36:36|section|original|JP|ТАНКИ ТА БРОНЕТЕХНІКА
37:38|archive|japan-armor|JP|TYPE 10 · RISING THUNDER, 2014
39:39|graphic|mobility|JP|TYPE 10 · МОБІЛЬНІСТЬ ТА ІНФРАСТРУКТУРА
40:40|photo|type90|JP|TYPE 90
41:42|photo|type99a|CN|TYPE 99A
43:44|photo|type99a|CN|TYPE 99A · 125 ММ
45:45|photo|type96|CN|TYPE 96 · РОДИНА ТАНКІВ
46:47|graphic|land-scale|CN|МАСШТАБ СУХОПУТНИХ СИЛ
48:48|photo|type10|JP|TYPE 10
49:49|compare|tanks|JP|TYPE 10 ТА TYPE 99A
50:50|photo|type96|CN|TYPE 96 · РОДИНА
51:51|map|map-navy|JP|
53:53|section|original|JP|РАКЕТНЕ ОЗБРОЄННЯ
54:55|photo|type12-base|JP|TYPE 12 · БЕРЕГОВИЙ КОМПЛЕКС
56:56|photo|type12|JP|ПОКРАЩЕНИЙ TYPE 12 · ПРОТОТИП
57:58|archive|tomahawk-action|JP|TOMAHAWK · ПРИКЛАД ПУСКУ ВМС США, 2014
59:60|photo|df21|CN|DF-21 · РОДИНА РАКЕТ
61:61|photo|df26|CN|DF-26 · РОДИНА РАКЕТ
62:63|photo|df17|CN|DF-17 · ВИСТАВКОВИЙ ЗРАЗОК
64:64|photo|df26|CN|DF-26
65:65|photo|type12|JP|ПОКРАЩЕНИЙ TYPE 12 · ПРОТОТИП
66:66|compare|missiles|CN|РІЗНІ РАКЕТНІ МОЖЛИВОСТІ
67:67|graphic|uncertainty|CN|ВІДКРИТІ ДАНІ ТА ЇХНІ МЕЖІ
69:69|section|original|JP|ПІХОТНЕ ОЗБРОЄННЯ
70:71|photo|type20|JP|HOWA TYPE 20 · 5,56 ММ
72:73|photo|type20|JP|HOWA TYPE 20
74:74|photo|type89|JP|HOWA TYPE 89
75:77|photo|qbz191|CN|QBZ-191 · 5,8 ММ
78:78|photo|qbz95|CN|QBZ-95 · ПОПЕРЕДНЯ ПЛАТФОРМА
79:80|photo|qbz191|CN|QBZ-191
81:82|compare|rifles|JP|TYPE 20 ТА QBZ-191
83:83|archive|japan-infantry|JP|JGSDF · ПІДГОТОВКА ПІДРОЗДІЛІВ, 2025
84:84|archive|japan-antitank|JP|JGSDF · ПРОТИТАНКОВІ НАВЧАННЯ, 2018
86:86|section|original|JP|АРТИЛЕРІЯ
87:88|photo|type19|JP|TYPE 19 · 155 ММ
89:89|photo|type99sp|JP|TYPE 99 · САМОХІДНА ГАУБИЦЯ
90:92|graphic|pcl181|CN|PCL-181 · КОЛІСНА ГАУБИЦЯ
93:93|photo|phl16|CN|PHL-16 · РЕАКТИВНА АРТИЛЕРІЯ
94:95|photo|type19|JP|TYPE 19
96:97|photo|phl16|CN|PHL-16
98:98|graphic|artillery-system|CN|ЕФЕКТИВНІСТЬ АРТИЛЕРІЇ
100:100|section|original|JP|БЕЗПІЛОТНИКИ
101:102|archive|rq4-action|JP|RQ-4 · ВПС США НА БАЗІ ЙОКОТА, 2019
103:103|graphic|maritime-drones|JP|БЕЗПІЛОТНІ СИСТЕМИ ТА ОБОРОНА ОСТРОВІВ
104:105|photo|wingloong2|CN|WING LOONG II · ВИСТАВКА
106:107|photo|ch4|CN|CH-4 · ВИСТАВКОВИЙ ЗРАЗОК
108:108|graphic|drones-research|CN|ДОСЛІДЖЕННЯ БЕЗПІЛОТНИХ СИСТЕМ
109:110|graphic|readiness|CN|ДЕМОНСТРАТОР ТА СЕРІЙНА СИСТЕМА
111:111|photo|rq4|JP|RQ-4 GLOBAL HAWK · РОДИНА
112:112|compare|drones|CN|РОЗВІДУВАЛЬНІ ТА УДАРНІ ПЛАТФОРМИ
114:114|section|original|JP|ПРОТИПОВІТРЯНА ОБОРОНА
115:115|archive|japan-pac3|JP|PATRIOT PAC-3 · НАВЧАННЯ JASDF, 2017
116:117|archive|japan-sm3|JP|STANDARD MISSILE · ВИПРОБУВАННЯ ЯПОНІЇ, 2010
118:120|photo|hq9|CN|HQ-9 · РОДИНА КОМПЛЕКСІВ
121:121|photo|hq16|CN|HQ-16 · РОДИНА КОМПЛЕКСІВ
122:122|graphic|airdefense-system|JP|ЄДИНА СИСТЕМА ППО
123:123|photo|hq9|CN|HQ-9
124:124|archive|sm3-cooperative|JP|SM-3 BLOCK IIA · СПІЛЬНІ ВИПРОБУВАННЯ США ТА ЯПОНІЇ, 2017
125:125|photo|hq16|CN|HQ-16 · РОДИНА
127:127|section|original|JP|ВЕРТОЛЬОТИ
128:128|photo|ah1s|JP|AH-1S COBRA · ЯПОНІЯ
129:129|photo|oh1|JP|KAWASAKI OH-1
130:130|graphic|future-helo|JP|НОВІ ЗАВДАННЯ БЕЗПІЛОТНИХ СИСТЕМ
131:132|photo|z10|CN|Z-10
133:134|archive|china-helos|CN|Z-10 · АРХІВ НАВЧАНЬ, 2019
135:135|photo|z19|CN|Z-19
136:136|photo|z10|CN|Z-10
137:137|photo|oh1|JP|OH-1 · ПЛАТФОРМА РОЗВІДКИ
139:141|section|original|JP|ВІЙСЬКОВО-МОРСЬКИЙ ФЛОТ
142:143|photo|maya|JP|MAYA · AEGIS
144:145|archive|soryu-video|JP|SORYU · ЯПОНСЬКА НЕАТОМНА СУБМАРИНА
146:147|archive|izumo-trials|JP|JS IZUMO · ВИПРОБУВАННЯ F-35B, 2021
148:148|photo|izumo|JP|JS IZUMO · DDH-183
149:150|archive|jinan-video|CN|TYPE 052C JINAN · АРХІВ ФЛОТУ КНР, 2015
151:151|photo|liaoning|CN|LIAONING
152:152|photo|fujian|CN|FUJIAN · ЕЛЕКТРОМАГНІТНІ КАТАПУЛЬТИ
153:154|photo|type055|CN|TYPE 055 · NANCHANG
155:155|photo|type094|CN|TYPE 094 · РОДИНА АТОМНИХ СУБМАРИН
156:157|archive|jinan-video|CN|ФЛОТ КНР · TYPE 052C JINAN, 2015
158:158|archive|soryu-video|JP|SORYU · ПРОТИЧОВНОВІ МОЖЛИВОСТІ ЯПОНІЇ
159:159|archive|kaga-trials|JP|JS KAGA · ВИПРОБУВАННЯ РАЗОМ ІЗ США, 2024
160:160|map|map-navy|JP|
162:162|section|original|JP|ЯДЕРНИЙ АРСЕНАЛ
163:164|graphic|japan-deterrence|JP|ЯПОНІЯ · РОЗШИРЕНЕ СТРИМУВАННЯ
165:166|photo|df41|CN|DF-41 · СТРАТЕГІЧНИЙ КОМПЛЕКС
167:167|photo|type094|CN|TYPE 094 · МОРСЬКИЙ КОМПОНЕНТ
168:169|graphic|nuclear-estimates|CN|КИТАЙ · ОЦІНКИ ЯДЕРНОГО ЗАПАСУ
170:170|photo|df41|CN|DF-41
171:172|map|map-region|JP|
173:173|graphic|nuclear-risk|JP|СТРАТЕГІЧНІ РИЗИКИ
175:176|section|original|JP|ПІДСУМОК
177:177|compare|aircraft|CN|МАСШТАБ ТА ТЕХНОЛОГІЇ
178:178|archive|j20-anniversary|CN|J-20 · АРХІВ АВІАЦІЙНОЇ ПРОМИСЛОВОСТІ КНР
179:179|photo|df41|CN|DF-41
180:180|turntable|model-f35b|JP|F-35 · РОДИНА ЛІТАКІВ
181:181|archive|kaga-trials|JP|JS KAGA · ВЗАЄМОДІЯ ЯПОНІЇ ТА США, 2024
182:183|graphic|comparison-scope|CN|НАЦІОНАЛЬНІ АРСЕНАЛИ ТА СОЮЗНИКИ
184:185|map|map-navy|JP|
186:186|archive|japan-armor|JP|ЗАБЕЗПЕЧЕННЯ ПІДРОЗДІЛІВ · RISING THUNDER, 2014
187:187|photo|type055|CN|TYPE 055
188:188|archive|jasdf-f35|JP|F-35A JASDF · НАВЧАННЯ, 2024
189:189|compare|carriers|JP|ЯПОНІЯ ТА КИТАЙ
191:192|question|original|JP|ЩО ВАС ВРАЗИЛО НАЙБІЛЬШЕ?
193:193|compare|aircraft|JP|F-35 ЧИ J-20?
194:194|compare|tanks|JP|TYPE 10 ЧИ TYPE 99A?
195:195|compare|carriers|JP|IZUMO ЧИ FUJIAN?
196:197|question|original|JP|ЯКІ ТЕХНОЛОГІЇ НАЙВАЖЛИВІШІ?
198:198|outro|original|JP|АРСЕНАЛ 360°
199:201|ident|channel-ident|JP|АРСЕНАЛ 360°
'''
SPANS=[]
for line in PLAN.strip().splitlines():
 span,kind,key,country,title=line.split('|');a,b=map(int,span.split(':'));SPANS.append(dict(a=a,b=b,kind=kind,asset_id=key,country=country,title=title))
