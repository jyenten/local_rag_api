# ChromaDB: nálezy a omezení lokálního provozu

[English](../en/CHROMA_SECURITY.md) · [Provozní příručka](OPERATIONS.md) · [Dokumentace](../README.md)

Datum posouzení: **2026-11-07** (navazuje na kontrolu z 4. 11.). Zkontrolovaný základ projektu:
`a94150b0723df94cac5ea47a12fa364edb2e4798`; PR #10 mění pouze sestavení BM25.
Toto posouzení neuděluje výjimku z bezpečnostního auditu.

## Co je potvrzené

[Audit PR #10](https://github.com/jyenten/local_rag_api/actions/runs/41788293914)
hlásí pět položek pro nově vyřešenou ChromaDB **1.5.9**. Jde o čtyři unikátní CVE:
`PYSEC-2026-311` je ve výpisu dvakrát. Stejné řádky jsou v
[auditu main z 2. 11. 2026](https://github.com/jyenten/local_rag_api/actions/runs/41445441166).
Nejde o zjištění skutečně nainstalované verze na vlastníkově počítači.

K datu posouzení je na [PyPI](https://pypi.org/project/chromadb/) nejnovější stabilní
verze 1.5.9. Níže uvedené GitHub Reviewed advisories neuvádějí opravenou verzi.
Pouhé připnutí 1.5.9, downgrade nebo přechod na vývojový build není doložená oprava.

| CVE / advisory | Popisovaná útočná cesta | Publikovaný zasažený rozsah |
| --- | --- | --- |
| [CVE-2026-45829](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c) | Načtení škodlivého modelu přes vytvoření kolekce s `trust_remote_code=true`, bez předchozí autentizace. | 1.0.0 až 1.5.9 |
| [CVE-2026-45833](https://github.com/advisories/GHSA-36p7-vc44-83pf) | Podobné spuštění kódu přes aktualizaci kolekce s oprávněním `UPDATE_COLLECTION`. | 0.4.17 až 1.5.9 |
| [CVE-2026-45830](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr) | Nedostatečné ověření přístupu mezi tenanty/kolekcemi. | 0.4.17 až 1.5.9 |
| [CVE-2026-45831](https://github.com/advisories/GHSA-xph7-9rjv-w5fr) | SimpleRBAC kontroluje akci bez dostatečného omezení na tenant/databázi/kolekci. | 0.5.0 až 1.5.9 |

## Použití v tomto projektu a hranice závěru

Zkontrolované volání v `app/retrieval.py`, `app/retrievers/vector.py`,
`app/retrievers/bm25.py`, `scripts/ingest.py` a `scripts/create_test_db.py`
používá `chromadb.PersistentClient(path=...)`. Vlastní API v `app/main.py`
přijímá u `/ask` otázku; neposkytuje Chroma endpoint pro vytváření či aktualizaci
kolekcí a nepřebírá od HTTP klienta konfiguraci embedding funkce.
Compose definuje pouze RAG API, bez služby Chroma serveru. Projekt sám nenastavuje
`trust_remote_code=true` ani SimpleRBAC/multitenantový server.

To omezuje přímou dosažitelnost popsaných serverových scénářů v tomto profilu.
**Neprokazuje to nepřítomnost zranitelnosti v knihovně ani bezpečnost libovolného
nasazení.** Upstream [issue #6717](https://github.com/chroma-core/chroma/issues/6717)
popisuje také klientský scénář. Kód klienta v tagu 1.5.9 obnovuje embedding funkce
z konfigurace kolekce; databáze a modelová konfigurace proto musí zůstat důvěryhodné.
Nenačítej cizí Chroma index, nedovol jiným účtům měnit jeho adresář a nepřipojuj
aplikaci k cizímu Chroma serveru bez nového posouzení.

Posouzení zahrnuje kód a publikované advisories, nikoli reprodukci RCE,
průnikový test ani kontrolu všech služeb běžících na Windows. Skutečná verze,
konfigurace prostředí, firewall, jiné kontejnery a tunely vyžadují ověření.

## Zpevnění publikovaného portu

Compose nyní používá `127.0.0.1:8001:8000` místo `8001:8000`. Omezuje tím
publikovaný port RAG API na loopback hostitele při standardním Docker bridge/NAT
nastavení. Uvicorn uvnitř kontejneru dál naslouchá na `0.0.0.0:8000`.
Tato změna není opravou čtyř CVE a nepřidává autentizaci aplikace.
Jiné lokální procesy a kontejnery zůstávají součástí důvěryhodného prostředí.

[Docker dokumentace](https://docs.docker.com/engine/network/port-publishing/)
upozorňuje na přístup ze stejného L2 segmentu u localhost portů v Engine před 28.0.0.
Ověř skutečnou serverovou verzi, nejen verzi CLI. Nestandardní direct-routing/NAT
konfigurace vyžaduje zvláštní síťovou kontrolu.

Bez změny běžících služeb spusť v PowerShellu:

```powershell
docker version --format "{{.Server.Version}}"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

Pro službu vytvořenou z tohoto Compose očekávej
`127.0.0.1:8001->8000/tcp`. `0.0.0.0` nebo `[::]` u jiného API kontejneru znamená,
že samotná úprava tohoto YAML jeho publikování neomezila. n8n na portu 5678 a
dev-loop na 8765 jsou samostatné služby. Dev-loop pro přímý BM25 příkaz není potřeba.

Před znovuvytvořením API identifikuj jeho skutečný Compose projekt a původní
`chroma_db`/model-cache mounty. **Nespouštěj nový Compose naslepo z jiného worktree**:
relativní cesty by mohly vybrat jiný index. Změna portu vyžaduje znovuvytvoření
správného kontejneru; pouhé uložení YAML existující proces neovlivní. Ingest ani
mazání kolekcí nejsou součástí této změny.

## Doložený lokální stav při posouzení

Vlastník doložil výstupy místních příkazů; nejde o vzdálenou kontrolu jeho počítače:

- Docker Engine hlásí serverovou verzi **29.9.2**.
- Staré API publikované na všech rozhraních na portu 8000 je zastavené
  (`Status=exited`) a má `Restart=no`. Nemá mounty (`[]`); jeho data nebyla smazána.
- Ve výpisu běžících kontejnerů zůstalo pouze n8n s publikováním
  `127.0.0.1:5678->5678/tcp`.
- Windows kontrola TCP listenerů na portech 8000, 8001 a 8765 nevrátila žádný řádek:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,8001,8765 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

To dokládá tehdejší stav uvedených služeb a portů, nikoli opravu ChromaDB,
celkovou bezpečnost počítače nebo stav po příštím spuštění služeb.
Omezení Compose se projeví až u kontejneru vytvořeného z upravené konfigurace.
Přímé CLI laboratoře funguje bez dev-loop API; n8n úlohy volající port 8765
potřebují tuto samostatnou službu znovu bezpečně zpřístupnit.

## Stav auditu a podmínky dalšího rozhodnutí

`requirements.txt` ani `.github/workflows/pip-audit.yml` se touto úpravou nemění.
Audit zůstává aktivní a nálezy zůstávají viditelné. Nejsou přidána `ignore-vuln`,
`continue-on-error` ani VEX tvrzení o nezasaženém produktu.

Před sloučením je potřeba doložit skutečný lokální profil a rozhodnout o zbývajícím
riziku. Toto posouzení takové přijetí rizika samo neuděluje. Pro zelený audit bez
výjimky je potřeba ověřená opravená verze či samostatně schválená změna závislosti.
Nové Chroma HTTP API, sdílené databáze, nedůvěryhodné modely nebo veřejné nasazení
vyžadují nové posouzení před spuštěním.
