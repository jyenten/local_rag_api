<a id="top"></a>

# AI RAG Project Development Guide

[Česky](cs/DEVELOPMENT_GUIDE.md#cz) · [English](en/DEVELOPMENT_GUIDE.md#en) · [Dokumentace / Documentation](README.md)

Tento dokument má samostatnou [českou](cs/DEVELOPMENT_GUIDE.md#cz) a [anglickou](en/DEVELOPMENT_GUIDE.md#en) verzi. Otevři vybraný jazyk pro úplný text, obsah a příklady.

This document has separate [Czech](cs/DEVELOPMENT_GUIDE.md#cz) and [English](en/DEVELOPMENT_GUIDE.md#en) versions. Open a language for the full text, contents and examples.

<a id="obsah"></a>

## Starší odkazy na kapitoly / Legacy chapter links

Starší záložky vedou na příslušný řádek níže. Odkaz v řádku otevře úplnou kapitolu. / Older bookmarks lead to the matching row below; follow its link to the full chapter.

| Jazyk / Language | Kapitola / Chapter |
| --- | --- |
| EN | <a id="en"></a><a id="en--english"></a>[EN — English](en/DEVELOPMENT_GUIDE.md#en) |
| EN | <a id="en-documentation-responsibilities"></a><a id="documentation-responsibilities"></a>[Documentation responsibilities](en/DEVELOPMENT_GUIDE.md#en-documentation-responsibilities) |
| EN | <a id="en-development-workflow"></a><a id="development-workflow"></a>[Development workflow](en/DEVELOPMENT_GUIDE.md#en-development-workflow) |
| EN | <a id="en-code-and-module-design"></a><a id="code-and-module-design"></a>[Code and module design](en/DEVELOPMENT_GUIDE.md#en-code-and-module-design) |
| EN | <a id="en-errors-side-effects-and-diagnostics"></a><a id="errors-side-effects-and-diagnostics"></a>[Errors, side effects and diagnostics](en/DEVELOPMENT_GUIDE.md#en-errors-side-effects-and-diagnostics) |
| EN | <a id="en-verification-and-regression-tests"></a><a id="verification-and-regression-tests"></a>[Verification and regression tests](en/DEVELOPMENT_GUIDE.md#en-verification-and-regression-tests) |
| EN | <a id="en-retrieval-and-evaluation-discipline"></a><a id="retrieval-and-evaluation-discipline"></a>[Retrieval and evaluation discipline](en/DEVELOPMENT_GUIDE.md#en-retrieval-and-evaluation-discipline) |
| EN | <a id="en-git-review-and-integration"></a><a id="git-review-and-integration"></a>[Git, review and integration](en/DEVELOPMENT_GUIDE.md#en-git-review-and-integration) |
| EN | <a id="en-security-and-dependency-management"></a><a id="security-and-dependency-management"></a>[Security and dependency management](en/DEVELOPMENT_GUIDE.md#en-security-and-dependency-management) |
| EN | <a id="en-collaboration-and-learning"></a><a id="collaboration-and-learning"></a>[Collaboration and learning](en/DEVELOPMENT_GUIDE.md#en-collaboration-and-learning) |
| EN | <a id="en-completion-and-documentation-updates"></a><a id="completion-and-documentation-updates"></a>[Completion and documentation updates](en/DEVELOPMENT_GUIDE.md#en-completion-and-documentation-updates) |
| CZ | <a id="cz"></a><a id="cz--česká-verze"></a>[CZ — Česká verze](cs/DEVELOPMENT_GUIDE.md#cz) |
| CZ | <a id="cz-odpovědnosti-dokumentace"></a><a id="odpovědnosti-dokumentace"></a>[Odpovědnosti dokumentace](cs/DEVELOPMENT_GUIDE.md#cz-odpovědnosti-dokumentace) |
| CZ | <a id="cz-vývojový-postup"></a><a id="vývojový-postup"></a>[Vývojový postup](cs/DEVELOPMENT_GUIDE.md#cz-vývojový-postup) |
| CZ | <a id="cz-návrh-kódu-a-modulů"></a><a id="návrh-kódu-a-modulů"></a>[Návrh kódu a modulů](cs/DEVELOPMENT_GUIDE.md#cz-návrh-kódu-a-modulů) |
| CZ | <a id="cz-chyby-vedlejší-účinky-a-diagnostika"></a><a id="chyby-vedlejší-účinky-a-diagnostika"></a>[Chyby, vedlejší účinky a diagnostika](cs/DEVELOPMENT_GUIDE.md#cz-chyby-vedlejší-účinky-a-diagnostika) |
| CZ | <a id="cz-ověřování-a-regresní-testy"></a><a id="ověřování-a-regresní-testy"></a>[Ověřování a regresní testy](cs/DEVELOPMENT_GUIDE.md#cz-ověřování-a-regresní-testy) |
| CZ | <a id="cz-disciplína-retrievalu-a-evaluace"></a><a id="disciplína-retrievalu-a-evaluace"></a>[Disciplína retrievalu a evaluace](cs/DEVELOPMENT_GUIDE.md#cz-disciplína-retrievalu-a-evaluace) |
| CZ | <a id="cz-git-revize-a-integrace"></a><a id="git-revize-a-integrace"></a>[Git, revize a integrace](cs/DEVELOPMENT_GUIDE.md#cz-git-revize-a-integrace) |
| CZ | <a id="cz-bezpečnost-a-správa-závislostí"></a><a id="bezpečnost-a-správa-závislostí"></a>[Bezpečnost a správa závislostí](cs/DEVELOPMENT_GUIDE.md#cz-bezpečnost-a-správa-závislostí) |
| CZ | <a id="cz-spolupráce-a-učení"></a><a id="spolupráce-a-učení"></a>[Spolupráce a učení](cs/DEVELOPMENT_GUIDE.md#cz-spolupráce-a-učení) |
| CZ | <a id="cz-dokončení-a-aktualizace-dokumentace"></a><a id="dokončení-a-aktualizace-dokumentace"></a>[Dokončení a aktualizace dokumentace](cs/DEVELOPMENT_GUIDE.md#cz-dokončení-a-aktualizace-dokumentace) |

[↑ Nahoru / Back to top](#top)
