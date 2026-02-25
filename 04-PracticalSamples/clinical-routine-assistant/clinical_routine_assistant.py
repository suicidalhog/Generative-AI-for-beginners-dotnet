#!/usr/bin/env python3
"""Clinical-Personal Adaptive Routine Assistant (CLI).

A neuroprotective executive-function scaffold that adapts task load,
habits, and feedback from daily clinical state.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional

STATE_FILE = "clinical_state.json"


@dataclass
class Profile:
    sophistication: str = "A"  # A/B/C/D
    intervention_style: str = "misto_firme"
    demand_tolerance: str = "neutra"
    professional_modules: List[str] = None
    monitoring: List[str] = None
    philosophy: str = "hibrido_adaptativo"

    def __post_init__(self):
        if self.professional_modules is None:
            self.professional_modules = ["recondicionamento_cognitivo_clinico"]
        if self.monitoring is None:
            self.monitoring = ["alertas_humor", "relatorio_clinico"]


@dataclass
class DailyCheckIn:
    date: str
    energy: int
    mood: int
    anxiety: int
    sleep_hours: float
    sleep_quality: int
    cognition: int
    side_effects: str


@dataclass
class Task:
    title: str
    due_date: str
    domain: str
    exec_demand: str
    essential: bool = False
    completed: bool = False


class ClinicalRoutineAssistant:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.data = self._load()

    def _default_data(self) -> Dict:
        return {
            "profile": asdict(Profile()),
            "checkins": [],
            "tasks": [],
            "habits": {
                "agua_ml": {"target": 800, "streak": 0},
                "movimento_min": {"target": 5, "streak": 0},
                "luz_solar_min": {"target": 5, "streak": 0},
                "organizacao_min": {"target": 3, "streak": 0},
                "diario_clinico_min": {"target": 3, "streak": 0},
            },
            "habit_logs": [],
        }

    def _load(self) -> Dict:
        if not self.db_path.exists():
            return self._default_data()
        raw = self.db_path.read_text(encoding="utf-8").strip()
        if not raw:
            return self._default_data()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return self._default_data()

    def save(self) -> None:
        self.db_path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def set_profile(self, args: argparse.Namespace) -> None:
        profile = self.data["profile"]
        for key in [
            "sophistication",
            "intervention_style",
            "demand_tolerance",
            "philosophy",
        ]:
            value = getattr(args, key)
            if value:
                profile[key] = value
        if args.professional_modules:
            profile["professional_modules"] = [x.strip() for x in args.professional_modules.split(",") if x.strip()]
        if args.monitoring:
            profile["monitoring"] = [x.strip() for x in args.monitoring.split(",") if x.strip()]

    def add_checkin(self, checkin: DailyCheckIn) -> None:
        self.data["checkins"] = [c for c in self.data["checkins"] if c["date"] != checkin.date]
        self.data["checkins"].append(asdict(checkin))
        self.data["checkins"].sort(key=lambda c: c["date"])

    def add_task(self, task: Task) -> None:
        self.data["tasks"].append(asdict(task))

    def current_state(self) -> Dict:
        if not self.data["checkins"]:
            return {
                "load_factor": 0.5,
                "functional_mode": "baseline_sem_checkin",
                "risk_alerts": ["sem_dados_diarios"],
                "score": 50,
            }

        c = self.data["checkins"][-1]
        energy = c["energy"]
        mood = c["mood"]
        anxiety = c["anxiety"]
        cognition = c["cognition"]
        sleep_hours = c["sleep_hours"]
        sleep_quality = c["sleep_quality"]

        score = (
            0.22 * energy
            + 0.18 * mood
            + 0.18 * cognition
            + 0.14 * sleep_quality
            + 0.1 * min(sleep_hours, 9)
            + 0.18 * (10 - anxiety)
        ) * 10
        score = round(max(0, min(100, score)), 1)

        load_factor = max(0.2, min(1.2, score / 80))

        alerts = []
        if mood <= 3 and energy <= 4:
            alerts.append("risco_depressivo")
        if mood >= 8 and sleep_hours <= 5 and energy >= 8:
            alerts.append("risco_hipomania")
        if anxiety >= 8:
            alerts.append("ansiedade_alta")
        if cognition <= 3:
            alerts.append("regressao_executiva")

        mode = "funcional"
        if score < 45:
            mode = "crise_minima_funcional"
        elif score < 65:
            mode = "protecionista"

        return {
            "load_factor": load_factor,
            "functional_mode": mode,
            "risk_alerts": alerts,
            "score": score,
        }

    def classify_task(self, title: str) -> str:
        low = ["lavar", "arrumar", "organizar", "pagar", "email simples", "comprar"]
        high = ["artigo", "estudo profundo", "desenvolver", "projeto", "escrever", "analisar"]

        t = title.lower()
        if any(k in t for k in high):
            return "alta"
        if any(k in t for k in low):
            return "baixa"
        return "média"

    def prioritized_tasks(self, day: str) -> List[Dict]:
        state = self.current_state()
        mode = state["functional_mode"]
        weights = {"baixa": 3, "média": 2, "alta": 1}
        if mode == "funcional":
            weights = {"baixa": 1, "média": 2, "alta": 3}
        elif mode == "protecionista":
            weights = {"baixa": 3, "média": 2, "alta": 1}
        elif mode == "crise_minima_funcional":
            weights = {"baixa": 5, "média": 1, "alta": 0}

        tasks = [t for t in self.data["tasks"] if not t["completed"] and t["due_date"] <= day]
        for t in tasks:
            t["priority"] = weights.get(t["exec_demand"], 1) + (2 if t.get("essential") else 0)

        tasks.sort(key=lambda x: (-x["priority"], x["due_date"]))

        if mode == "crise_minima_funcional":
            tasks = [t for t in tasks if t["exec_demand"] == "baixa" or t.get("essential")]
        return tasks

    def routine_blocks(self) -> Dict[str, List[str]]:
        state = self.current_state()
        mode = state["functional_mode"]

        base = {
            "essenciais_biologicos": [
                "medicação no horário",
                "hidratação mínima",
                "2 refeições estruturadas",
                "higiene do sono",
                "movimento leve",
            ],
            "essenciais_psiquiatricos": [
                "exposição comportamental curta",
                "contato social mínimo",
                "higiene ambiental (5-10 min)",
                "psicoeducação breve",
            ],
            "produtividade_leve": ["leitura leve", "estudo clínico leve", "projeto pessoal micro-passo"],
            "recuperacao": ["lazer sem culpa", "estímulo sensorial positivo", "descompressão cognitiva"],
        }

        if mode == "crise_minima_funcional":
            base["produtividade_leve"] = ["apenas 1 micro-tarefa (<=10 min)"]
            base["recuperacao"].append("pausas protetivas programadas")
        return base

    def log_habits(self, done: Dict[str, bool]) -> None:
        today = date.today().isoformat()
        self.data["habit_logs"].append({"date": today, "done": done})

        adherence = mean([1 if v else 0 for v in done.values()]) if done else 0
        for name, item in self.data["habits"].items():
            if done.get(name):
                item["streak"] += 1
            else:
                item["streak"] = 0

            if adherence >= 0.8:
                if name.endswith("_ml"):
                    item["target"] = min(2500, item["target"] + 200)
                else:
                    item["target"] = min(45, item["target"] + 2)
            elif adherence <= 0.3:
                if name.endswith("_ml"):
                    item["target"] = max(500, item["target"] - 100)
                else:
                    item["target"] = max(3, item["target"] - 1)

    def antiburnout_flags(self) -> List[str]:
        flags = []
        recent = self.data["checkins"][-5:]
        if len(self.data["tasks"]) > 40:
            flags.append("overplanning")
        if recent:
            avg_anxiety = mean([d["anxiety"] for d in recent])
            avg_energy = mean([d["energy"] for d in recent])
            if avg_anxiety > 7 and avg_energy < 5:
                flags.append("evitacao_por_sobrecarga")
            if avg_energy > 8 and mean([d["sleep_hours"] for d in recent]) < 5.5:
                flags.append("hiperfoco_sem_recuperacao")

        return flags

    def weekly_report(self) -> str:
        end = date.today()
        start = end - timedelta(days=6)
        checkins = [
            c for c in self.data["checkins"] if start.isoformat() <= c["date"] <= end.isoformat()
        ]
        if not checkins:
            return "Sem dados da semana para gerar relatório."

        avg = {
            "energia": mean([c["energy"] for c in checkins]),
            "humor": mean([c["mood"] for c in checkins]),
            "ansiedade": mean([c["anxiety"] for c in checkins]),
            "cognição": mean([c["cognition"] for c in checkins]),
            "sono_h": mean([c["sleep_hours"] for c in checkins]),
        }

        state = self.current_state()
        flags = self.antiburnout_flags()
        return (
            "RELATÓRIO SEMANAL TÉCNICO\n"
            f"Período: {start.isoformat()} a {end.isoformat()}\n"
            f"Médias: energia={avg['energia']:.1f}, humor={avg['humor']:.1f}, ansiedade={avg['ansiedade']:.1f}, "
            f"cognição={avg['cognição']:.1f}, sono={avg['sono_h']:.1f}h\n"
            f"Score funcional atual: {state['score']}/100 | Modo: {state['functional_mode']}\n"
            f"Alertas de risco: {', '.join(state['risk_alerts']) if state['risk_alerts'] else 'nenhum'}\n"
            f"Sinais antiburnout: {', '.join(flags) if flags else 'nenhum'}\n"
            "Conduta sugerida: priorizar ativação comportamental graduada, blocos biológicos essenciais e revisão "
            "de carga executiva com tolerância à falha."
        )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Assistente clínico-pessoal adaptativo (CLI)")
    p.add_argument("--db", default=STATE_FILE, help="Arquivo JSON de persistência")
    sub = p.add_subparsers(dest="cmd", required=True)

    profile = sub.add_parser("profile", help="Configura preferências clínicas do sistema")
    profile.add_argument("--sophistication", choices=["A", "B", "C", "D"])
    profile.add_argument("--intervention-style")
    profile.add_argument("--demand-tolerance")
    profile.add_argument("--professional-modules")
    profile.add_argument("--monitoring")
    profile.add_argument("--philosophy")

    c = sub.add_parser("checkin", help="Registra estado clínico diário")
    c.add_argument("--energy", type=int, required=True)
    c.add_argument("--mood", type=int, required=True)
    c.add_argument("--anxiety", type=int, required=True)
    c.add_argument("--sleep-hours", type=float, required=True)
    c.add_argument("--sleep-quality", type=int, required=True)
    c.add_argument("--cognition", type=int, required=True)
    c.add_argument("--side-effects", default="nenhum")

    t = sub.add_parser("add-task", help="Adiciona tarefa com classificação executiva")
    t.add_argument("title")
    t.add_argument("--due-date", default=date.today().isoformat())
    t.add_argument("--domain", default="pessoal")
    t.add_argument("--exec-demand", choices=["baixa", "média", "alta"])
    t.add_argument("--essential", action="store_true")

    sub.add_parser("plan", help="Mostra plano diário adaptativo")
    sub.add_parser("dashboard", help="Mostra dashboard e alertas")
    h = sub.add_parser("habits", help="Registra adesão de hábitos")
    h.add_argument("--done", required=True, help="CSV com hábitos concluídos")

    sub.add_parser("weekly-report", help="Gera relatório semanal técnico")

    e = sub.add_parser("export", help="Exporta estado para JSON em outro caminho")
    e.add_argument("--output", required=True)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    app = ClinicalRoutineAssistant(Path(args.db))

    if args.cmd == "profile":
        app.set_profile(args)
        app.save()
        print("Perfil atualizado.")
        return

    if args.cmd == "checkin":
        c = DailyCheckIn(
            date=date.today().isoformat(),
            energy=args.energy,
            mood=args.mood,
            anxiety=args.anxiety,
            sleep_hours=args.sleep_hours,
            sleep_quality=args.sleep_quality,
            cognition=args.cognition,
            side_effects=args.side_effects,
        )
        app.add_checkin(c)
        app.save()
        print("Check-in diário registrado.")
        return

    if args.cmd == "add-task":
        demand = args.exec_demand or app.classify_task(args.title)
        app.add_task(
            Task(
                title=args.title,
                due_date=args.due_date,
                domain=args.domain,
                exec_demand=demand,
                essential=args.essential,
            )
        )
        app.save()
        print(f"Tarefa adicionada ({demand}).")
        return

    if args.cmd == "plan":
        today = date.today().isoformat()
        state = app.current_state()
        print(f"Modo funcional: {state['functional_mode']} | Score: {state['score']}")
        print("\nBlocos de rotina:")
        for k, vals in app.routine_blocks().items():
            print(f"- {k}:")
            for v in vals:
                print(f"  • {v}")
        print("\nTarefas priorizadas:")
        tasks = app.prioritized_tasks(today)
        for i, t in enumerate(tasks[:8], start=1):
            print(f"{i}. [{t['exec_demand']}] {t['title']} (essencial={t['essential']})")
        return

    if args.cmd == "dashboard":
        state = app.current_state()
        print("DASHBOARD DIÁRIO")
        print(f"Score funcional: {state['score']}/100")
        print(f"Modo: {state['functional_mode']}")
        print(f"Alertas: {', '.join(state['risk_alerts']) if state['risk_alerts'] else 'nenhum'}")
        print(f"Antiburnout: {', '.join(app.antiburnout_flags()) or 'nenhum'}")
        print("Hábitos-alvo:")
        for name, item in app.data["habits"].items():
            print(f"- {name}: meta={item['target']} (streak={item['streak']})")
        return

    if args.cmd == "habits":
        selected = {x.strip() for x in args.done.split(",") if x.strip()}
        done_map = {name: (name in selected) for name in app.data["habits"].keys()}
        app.log_habits(done_map)
        app.save()
        print("Hábitos registrados e metas ajustadas automaticamente.")
        return

    if args.cmd == "weekly-report":
        print(app.weekly_report())
        return

    if args.cmd == "export":
        Path(args.output).write_text(json.dumps(app.data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Exportado para {args.output}")
        return


if __name__ == "__main__":
    main()
