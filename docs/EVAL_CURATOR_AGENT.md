<a id="top"></a>

# Evaluation Curator Agent

[Česky](cs/EVAL_CURATOR_AGENT.md#cz) · [English](en/EVAL_CURATOR_AGENT.md#en) · [Dokumentace / Documentation](README.md)

Tento dokument má samostatnou [českou](cs/EVAL_CURATOR_AGENT.md#cz) a [anglickou](en/EVAL_CURATOR_AGENT.md#en) verzi. Otevři vybraný jazyk pro úplný text, obsah a příklady.

This document has separate [Czech](cs/EVAL_CURATOR_AGENT.md#cz) and [English](en/EVAL_CURATOR_AGENT.md#en) versions. Open a language for the full text, contents and examples.

<a id="obsah"></a>

## Starší odkazy na kapitoly / Legacy chapter links

Starší záložky vedou na příslušný řádek níže. Odkaz v řádku otevře úplnou kapitolu. / Older bookmarks lead to the matching row below; follow its link to the full chapter.

| Jazyk / Language | Kapitola / Chapter |
| --- | --- |
| EN | <a id="en"></a><a id="en--english"></a>[EN — English](en/EVAL_CURATOR_AGENT.md#en) |
| EN | <a id="en-goal"></a><a id="goal"></a>[Goal](en/EVAL_CURATOR_AGENT.md#en-goal) |
| EN | <a id="en-allowed-output"></a><a id="allowed-output"></a>[Allowed output](en/EVAL_CURATOR_AGENT.md#en-allowed-output) |
| EN | <a id="en-existing-datasets"></a><a id="existing-datasets"></a>[Existing datasets](en/EVAL_CURATOR_AGENT.md#en-existing-datasets) |
| EN | <a id="en-source-material"></a><a id="source-material"></a>[Source material](en/EVAL_CURATOR_AGENT.md#en-source-material) |
| EN | <a id="en-candidate-creation-method"></a><a id="candidate-creation-method"></a>[Candidate creation method](en/EVAL_CURATOR_AGENT.md#en-candidate-creation-method) |
| EN | <a id="en-candidate-schema"></a><a id="candidate-schema"></a>[Candidate schema](en/EVAL_CURATOR_AGENT.md#en-candidate-schema) |
| EN | <a id="en-gold-evidence-rules"></a><a id="gold-evidence-rules"></a>[Gold evidence rules](en/EVAL_CURATOR_AGENT.md#en-gold-evidence-rules) |
| EN | <a id="en-topic-diversity"></a><a id="topic-diversity"></a>[Topic diversity](en/EVAL_CURATOR_AGENT.md#en-topic-diversity) |
| EN | <a id="en-prohibited-behavior"></a><a id="prohibited-behavior"></a>[Prohibited behavior](en/EVAL_CURATOR_AGENT.md#en-prohibited-behavior) |
| EN | <a id="en-batch-size"></a><a id="batch-size"></a>[Batch size](en/EVAL_CURATOR_AGENT.md#en-batch-size) |
| EN | <a id="en-validation"></a><a id="validation"></a>[Validation](en/EVAL_CURATOR_AGENT.md#en-validation) |
| EN | <a id="en-human-approval-boundary"></a><a id="human-approval-boundary"></a>[Human approval boundary](en/EVAL_CURATOR_AGENT.md#en-human-approval-boundary) |
| CZ | <a id="cz"></a><a id="cz--česká-verze"></a>[CZ — Česká verze](cs/EVAL_CURATOR_AGENT.md#cz) |
| CZ | <a id="cz-cíl"></a><a id="cíl"></a>[Cíl](cs/EVAL_CURATOR_AGENT.md#cz-cíl) |
| CZ | <a id="cz-povolený-výstup"></a><a id="povolený-výstup"></a>[Povolený výstup](cs/EVAL_CURATOR_AGENT.md#cz-povolený-výstup) |
| CZ | <a id="cz-existující-datasety"></a><a id="existující-datasety"></a>[Existující datasety](cs/EVAL_CURATOR_AGENT.md#cz-existující-datasety) |
| CZ | <a id="cz-zdrojový-materiál"></a><a id="zdrojový-materiál"></a>[Zdrojový materiál](cs/EVAL_CURATOR_AGENT.md#cz-zdrojový-materiál) |
| CZ | <a id="cz-postup-tvorby-kandidátů"></a><a id="postup-tvorby-kandidátů"></a>[Postup tvorby kandidátů](cs/EVAL_CURATOR_AGENT.md#cz-postup-tvorby-kandidátů) |
| CZ | <a id="cz-schéma-kandidáta"></a><a id="schéma-kandidáta"></a>[Schéma kandidáta](cs/EVAL_CURATOR_AGENT.md#cz-schéma-kandidáta) |
| CZ | <a id="cz-pravidla-gold-evidence"></a><a id="pravidla-gold-evidence"></a>[Pravidla gold evidence](cs/EVAL_CURATOR_AGENT.md#cz-pravidla-gold-evidence) |
| CZ | <a id="cz-různorodost-témat"></a><a id="různorodost-témat"></a>[Různorodost témat](cs/EVAL_CURATOR_AGENT.md#cz-různorodost-témat) |
| CZ | <a id="cz-zakázané-chování"></a><a id="zakázané-chování"></a>[Zakázané chování](cs/EVAL_CURATOR_AGENT.md#cz-zakázané-chování) |
| CZ | <a id="cz-velikost-dávky"></a><a id="velikost-dávky"></a>[Velikost dávky](cs/EVAL_CURATOR_AGENT.md#cz-velikost-dávky) |
| CZ | <a id="cz-validace"></a><a id="validace"></a>[Validace](cs/EVAL_CURATOR_AGENT.md#cz-validace) |
| CZ | <a id="cz-hranice-lidského-schválení"></a><a id="hranice-lidského-schválení"></a>[Hranice lidského schválení](cs/EVAL_CURATOR_AGENT.md#cz-hranice-lidského-schválení) |

[↑ Nahoru / Back to top](#top)
