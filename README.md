Koncept "Universal Object Storage"
==================================

Co je Universal Object Storage
------------------------------
Universal Object Storage je backend server (daemon), který poskytuje přístup k různým úložištím pod jedním společným
protokolem. Hlavní funkcí tohoto backendu je sjednotit rozhraní pro přístup k úložištím typu key-value nebo NoSQL
a to takovým, které usnadní replikaci/failover ukládaných dat a rozložení zátěže. Backend by měl být napsán tak,
aby tyto jednotlivé úložiště fungovaly jako moduly, a šlo tak dopsat jednoduše další modul pro další úložiště.
Společným přístupovým protokolem by mělo být REST HTTP rozhraní. O tom, do jakého úložiště bude objekt uložen
rozhodne jeho content-type.

Příklady úložišť
----------------
* CEPH (pro ukládání obrázků, videí a jiných větších souborů)
* Disk Folder (pro jednoduché ukládání souborů do adresářové struktury)
* CouchBase nebo CouchDB (pro ukládání databázových dat formou JSON objektů a agregace nad nimi)
* Redis (jenoduchá key-value databáze)

Co by měl Universal Object Storage umět
---------------------------------------
* Velmi rychle vydávat uložená data po HTTP protokolu
* Poskytovat ETagy pro cachování vydaných dat na klientech a proxy serverech
* Podporovat resume funkci u HTTP transferů
* Spravovat práva k jednotlivým objektům, umožnit různým uživatelům různé úrovně přístupu (např. veřejný read only přístup k obrázkům a informacím o produktech)
* Poskytovat rozhraní pro vytváření schémat objektů formou WADL a validaci objektů při ukládání dle těchto schémat
* Umožnit dělat snapshoty (verzování) u úložišť, které je podporují (CEPH, ZFS)
* Dělat statistiky přístupů k jednotlivým objektům, nebo skupinám objektů

Jakým způsobem bude backend využíván
------------------------------------
* Přístup frontend aplikací formou ActiveResource nebo DataMapper
* Přímý přístup k veřejným JSON objektům Javascriptem
* Přímý výdej obrázků a jiných videí pomocí nginx nebo jiného serveru který budě sloužit jako proxy s cache

Procesory dat
-------------
Procesory dat jsou moduly, které při ukládání určitých typů objektů zajistí jejich zpracování ještě před uložením.
Např. u obrázků můžeme použít procesor na vytvoření miniatur požadovaných rozměrů a watermarking. Tyto moduly by
měly být rovněž univerzální a snadno dopsatelné.



Priority
--------
1. Hlavním smyslem Universal Object Storage je vydávat objekty různého Content-Type z různých úložišť pomocí jednotného HTTP REST rozhraní.
2. Universal Object Storage k těmto objektům ukládá metadata a ACL. Při práci s objekty ověřuje ACL.
3. Universal Object Storage má v configu nastaven jeden z backendů typu databáze jako své interní úložiště pro tzv. "bucket map". Když přijde request, zjistí z "bucket map" podle cílové domény requestu, jaký bucket použít pro získání informací o objektu.
