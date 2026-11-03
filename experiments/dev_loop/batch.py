"""Measured sequential runs and a shareable report without raw logs or paths."""

from __future__ import annotations

import base64
import html
import json
import platform
import statistics
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .adapters import TASK_ID
from .workflow import Checker, Worker, run_job

MAX_CYCLES = 20
STOP_STATUSES = {"infrastructure_error", "scope_violation", "baseline_failed"}


def run_batch(count: int, output: Path, worker: Worker, checker: Checker) -> dict:
    if not 1 <= count <= MAX_CYCLES:
        raise ValueError("A batch must contain between 1 and 20 independent runs")
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    task_id = getattr(worker, "task_id", TASK_ID)
    for cycle in range(1, count + 1):
        result = run_job(str(uuid.uuid4()), task_id, output / "runs", worker, checker)
        verifications = [event for event in result["trace"] if event["node"] == "verify"]
        measured = result.get("model_usage_measured", False)
        tokens = ({key: sum(record["usage"][key] for record in result["worker_attempts"])
                   for key in ("input_tokens", "cached_input_tokens", "output_tokens")}
                  if measured else None)
        rows.append({
            "cycle": cycle, "request_id": result["request_id"], "backend": result["backend"],
            "task_id": task_id,
            "status": result["status"], "attempts": result["attempts"],
            "repairs": max(0, result["attempts"] - 1), "duration_s": result["duration_s"],
            "verification_returncodes": [event.get("returncode") for event in verifications],
            "model_usage_measured": measured, "cli_reported_tokens": tokens,
        })
        if result["status"] in STOP_STATUSES:
            break  # Do not spend the remaining batch budget on an unsafe/broken environment.
    durations = sorted(row["duration_s"] for row in rows)
    completed = len(rows)
    is_demo = worker.name in {"demo", "demo-docker"}
    report = {
        "schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "backend": worker.name,
        "task_id": task_id,
        "measurement": "scripted-demo" if is_demo else "live-codex",
        "isolation": getattr(worker, "isolation", "host"),
        "checker_isolation": getattr(checker, "isolation", "host"),
        "runner_image": getattr(checker, "image_id", None),
        "worker_image": getattr(worker, "image_id", None),
        "requested_cycles": count, "completed_cycles": completed,
        "stopped_early": completed < count,
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "total_attempts": sum(row["attempts"] for row in rows),
        "total_repairs": sum(row["repairs"] for row in rows),
        "total_duration_s": round(sum(durations), 6),
        "mean_duration_s": statistics.mean(durations),
        "median_duration_s": statistics.median(durations),
        "max_duration_s": max(durations),
        "worker_invocations": sum(row["attempts"] for row in rows),
        "model_calls": 0 if is_demo else None,
        "model_usage_measured": all(row["model_usage_measured"] for row in rows),
        "cli_reported_tokens": ({key: sum(row["cli_reported_tokens"][key] for row in rows)
                                 for key in ("input_tokens", "cached_input_tokens", "output_tokens")}
                                if all(row["model_usage_measured"] for row in rows) else None),
        "model_cost": None,
        "committed": False, "applied_to_rag": False, "rows": rows,
    }
    (output / "batch.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def render_report(report: dict, output: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    rows = report["rows"]
    cycles = [row["cycle"] for row in rows]
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.2), constrained_layout=True, sharex=True)
    is_demo = report["backend"] in {"demo", "demo-docker"}
    docker_isolated = report.get("isolation") == report.get("checker_isolation") == "docker"
    container_codex = report["backend"] == "codex-docker"
    label = "DEMO - bez volání modelu" if is_demo else "Živý Codex"
    if docker_isolated:
        label += " | Docker"
    fig.suptitle(f"Opravná smyčka: {len(rows)} samostatných běhů | {label}", fontsize=15)
    axes[0].plot(cycles, [row["duration_s"] for row in rows], marker="o", color="#285A89")
    axes[0].set_ylabel("Doba běhu (s)")
    axes[0].set_ylim(bottom=0)
    axes[1].step(cycles, [row["attempts"] for row in rows], where="mid", color="#285A89")
    axes[1].plot(cycles, [row["attempts"] for row in rows], "o", color="#285A89")
    axes[1].axhline(3, color="#A95635", linestyle="--", label="Limit: 3 pokusy")
    axes[1].set_ylabel("Počet pokusů")
    axes[1].set_xlabel("Pořadí samostatného běhu")
    axes[1].set_ylim(0, 3.5)
    axes[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    axes[1].legend(loc="lower right", frameon=False)
    axes[1].set_xticks(cycles)
    for axis in axes:
        axis.grid(axis="y", alpha=.18)
        axis.spines[["top", "right"]].set_visible(False)
    chart = output / "cycles.png"
    fig.savefig(chart, dpi=160)
    plt.close(fig)
    image = base64.b64encode(chart.read_bytes()).decode("ascii")
    successful = report["status_counts"].get("review_ready", 0)
    table = "".join(
        f"<tr><td>{row['cycle']}</td><td>{html.escape(row['status'])}</td>"
        f"<td>{row['attempts']}</td><td>{row['repairs']}</td><td>{row['duration_s']:.3f}</td></tr>"
        for row in rows
    )
    caveat = (
        "Deterministický worker záměrně chybuje při prvním pokusu a opravuje se při druhém. "
        "Výsledky ověřují řízení smyčky a běh testů; neměří kvalitu Codexu, RAG ani integraci n8n. "
        "Model nebyl volán."
        if is_demo else
        "Živý backend Codex. Výsledky se týkají pouze pevné malé testovací úlohy; "
        "počty tokenů CLI jsou uvedené jen při úplné telemetrii, cenu report nevyhodnocuje."
    )
    isolation_note = (
        "Codex generuje zdrojový text v jednorázovém kontejneru se sítí bridge a vlastním "
        "přihlašovacím volume ChatGPT. Odchozí síť workeru není omezena na domény OpenAI "
        "a auth volume je zapisovatelné kvůli obnově tokenů. Repozitář ani osobní složky "
        "nejsou připojené. Kandidát běží až v jiném offline kontejneru bez credentials. "
        "Shell nástroje jsou vypnuté a sandbox je read-only; živé vynucení je nutné ověřit "
        "na daném Docker hostiteli. Kontejner není VM a JUnit neprokazuje odolnost proti "
        "úmyslnému podvržení výsledku."
        if container_codex else
        "Worker a pytest jsou spouštěny v oddělených jednorázových kontejnerech bez sítě, "
        "hostitelských mountů a předávání přihlašovacích údajů. Read-only root filesystem, "
        "UID 10001, odebrané capabilities, no-new-privileges a limity prostředků jsou součástí "
        "profilu. Smoke testy vynucení se spouštějí zvlášť na konkrétním Docker hostiteli. "
        "Kandidát stále může ovlivnit testovací proces uvnitř kontejneru; JUnit není důkaz "
        "odolnosti proti úmyslnému podvržení výsledku."
        if docker_isolated else
        "Spouštěný kandidátní Python má oprávnění lokálního uživatele; může číst hostitelský "
        "disk, využít síť nebo zasáhnout do testovacího procesu. Kontrola otisků a JUnit není "
        "ochrana proti úmyslnému podvržení výsledku. Sandbox příkazů Codexu neizoluje pytest "
        "spouštěný řídicím programem."
    )
    isolation_status = ("Docker profil; ověřit smoke testy na daném hostiteli" if docker_isolated
                        else "CHYBÍ OS izolace; nezpřístupňovat veřejné spouštění")
    environment_status = ("Hostitelské prostředí se nepředává. Jen Codex má vlastní auth volume; checker žádné credentials."
                          if container_codex else
                          "Hostitelské prostředí se do kontejneru nepředává; HOME je /tmp"
                          if docker_isolated else
                          "Implementováno; nebrání libovolnému čtení hostitelského disku")
    document = f"""<!doctype html><html lang="cs"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dev loop — report {len(rows)} běhů</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;color:#202834;background:#fff;max-width:1000px;margin:30px auto;padding:0 20px}}h1,h2{{font-weight:600}}img{{width:100%;height:auto}}table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}th,td{{padding:7px 12px;text-align:left;border-bottom:1px solid #dde2e8}}.note{{padding:14px;background:#f1f5f8}}a{{color:#285a89}}</style>
<h1>Report: {len(rows)} běhů opravné smyčky</h1>
<p>{html.escape(label)} · Python {html.escape(report['python'])} · {html.escape(report['created_at_utc'])}</p>
<p>Úloha: {html.escape(report.get('task_id', TASK_ID))}</p>
<p class="note">{html.escape(caveat)}</p>
<p>Dokončeno {len(rows)} z {report['requested_cycles']} požadovaných běhů.
Ke kontrole připraveno {successful}/{len(rows)}. Celkem {report['total_attempts']} pokusů,
{report['total_repairs']} oprav. Medián {report['median_duration_s']:.3f} s,
maximum {report['max_duration_s']:.3f} s. Celková doba běhů {report['total_duration_s']:.3f} s.
Úspěch na první pokus: {sum(row['status'] == 'review_ready' and row['attempts'] == 1 for row in rows)}/{len(rows)}.
Volání modelu: {report['model_calls'] if report['model_calls'] is not None else 'neměřeno'}.
Tokeny hlášené CLI (input / cached input / output): {html.escape(str(report.get('cli_reported_tokens') or 'neměřeno'))}.
Cena modelu: neměřena.</p>
<img alt="Doba jednotlivých běhů a počet pokusů s limitem tři" src="data:image/png;base64,{image}">
<h2>Bezpečnostní hranice</h2>
<table><tr><th>Ochrana</th><th>Stav</th></tr>
<tr><td>Pevné zadání, token HTTP API, loopback jako výchozí adresa</td><td>Implementováno; lokální laboratoř</td></tr>
<tr><td>Nejvýše 3 pokusy na úlohu, nejvýše 20 úloh na dávku</td><td>Implementováno; kritická chyba dávku zastaví</td></tr>
<tr><td>Kontrolní testy mimo pracovní složku, úplný JUnit výsledek, audit souborů</td><td>Implementováno; audit není sandbox</td></tr>
<tr><td>Omezené dědění proměnných prostředí, oddělený testovací HOME</td><td>{html.escape(environment_status)}</td></tr>
<tr><td>Oprávnění Codex workeru</td><td>{'Docker, read-only sandbox, shell nástroje vypnuté; model potřebuje síť' if container_codex else 'Host adaptér: workspace-write, vypnutá síť příkazů; živé vynucení zde neověřeno'}</td></tr>
<tr><td>Izolace spuštěného testovacího Pythonu od hostitele</td><td>{html.escape(isolation_status)}</td></tr>
<tr><td>GitHub oprávnění a ochrana větví</td><td>Tento report je nenastavuje ani jejich vynucení nepotvrzuje</td></tr></table>
<h2>Co znamená veřejná větev</h2>
<p>Větev sdílí viditelnost repozitáře. Veřejnost může číst a kopírovat kód;
právo zápisu se řídí oprávněními repozitáře. Samostatná větev ani worktree nejsou
bezpečnostní izolace. Neveřejná data a přihlašovací údaje nepatří do žádné větve
veřejného repozitáře.</p>
<p class="note"><strong>Závěr kontroly: zatím pouze lokální laboratoř pro důvěryhodné úlohy.</strong>
{html.escape(isolation_note)}</p>
<table><tr><th>Před širším automatickým provozem</th><th>Co ještě vyřešit</th></tr>
<tr><td>Oddělený jednorázový runner</td><td>Izolovat worker i testy; žádný přístup k osobním složkám,
Docker socketu ani hostitelským přihlašovacím údajům; testy jen pro čtení, omezená síť,
CPU, paměť, disk a čas. Přístup k modelu oddělit od přístupu testovaného kódu.</td></tr>
<tr><td>Spouštění z GitHubu / n8n</td><td>Nyní pouze ruční důvěryhodný vstup.
Nespouštět veřejné issues, komentáře ani cizí PR jako agentní zadání s přístupem k secrets.
Nespouštět nedůvěryhodný kód přes pull_request_target.</td></tr>
<tr><td>Ochrana repozitáře</td><td>Ověřit rulesets, vyžadované kontroly a lidskou kontrolu změn;
minimální oprávnění tokenů. Stav vynucení není tímto reportem ověřen.</td></tr>
<tr><td>Spotřeba a kapacita</td><td>Chybí globální finanční limit,
rate limiting a limit velikosti HTTP vstupu. Tokeny lze převzít jen z úplné CLI telemetrie.
Host režim nemá limit zachyceného výstupu
subprocessu; Docker attach má limit 256 KiB.
Zámek běhů platí pouze pro jednu instanci procesu.
Dávka 20 úloh může u Codexu znamenat až 60 spuštění workeru.</td></tr>
<tr><td>Existující CI</td><td>Lokální kopie obsahuje Gitleaks, pip-audit a dependency review;
jejich aktuální zelený stav ani pravidla GitHubu zde nejsou potvrzeny.
Základní CI testuje RAG, nikoli tuto laboratoř; pip-audit míří na závislosti RAG.
Část workflow používá pohyblivé tagy akcí.</td></tr></table>
<p>Veřejně dostupný zdrojový kód není veřejně dostupný runner. Lokální logy, pracovní složky,
tokeny ani auth soubory nepublikovat. Tento report obsahuje pouze souhrnné metriky.
Nebylo provedeno commitnutí, push ani aplikování změn do RAG.</p>
<h2>Jednotlivé běhy</h2><table><tr><th>Běh</th><th>Stav</th><th>Pokusy</th><th>Opravy</th><th>Doba (s)</th></tr>{table}</table>
<h2>Zdroje bezpečnostních doporučení</h2>
<p><a href="https://developers.openai.com/codex/security/">Codex: sandbox a oprávnění</a> ·
<a href="https://docs.github.com/en/actions/reference/security/secure-use">GitHub: bezpečné workflow</a> ·
<a href="https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target">GitHub: rizika pull_request_target</a></p>
</html>"""
    destination = output / "report.html"
    destination.write_text(document, encoding="utf-8")
    return destination
