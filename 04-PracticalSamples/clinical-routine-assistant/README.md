# Clinical Routine Assistant (CLI)

Script em Python para organização clínica-pessoal com rotina adaptativa, tolerância à falha e foco em recuperação funcional.

## O que o script faz

- Registra estado clínico diário (energia, humor, ansiedade, sono, cognição, efeitos colaterais).
- Calcula **score funcional (0-100)** e define modo de operação:
  - `funcional`
  - `protecionista`
  - `crise_minima_funcional`
- Classifica tarefas por demanda executiva (`baixa`, `média`, `alta`) e prioriza conforme estado.
- Gera blocos de rotina (biológico, psiquiátrico, produtividade leve e recuperação).
- Aplica hábitos progressivos em micro-dose com regressão sem punição.
- Detecta padrões antiburnout (overplanning, hiperfoco sem recuperação e evitação por sobrecarga).
- Gera relatório semanal em linguagem técnico-clínica.

## Requisitos

- Python 3.10+

## Uso rápido

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py --help
```

### 1) Configurar preferências críticas (responde suas 6 perguntas)

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py profile \
  --sophistication B \
  --intervention-style misto_firme \
  --demand-tolerance neutra \
  --professional-modules estudo_psiquiatrico,producao_cientifica,recondicionamento_cognitivo_clinico \
  --monitoring alertas_humor,relatorio_clinico,alerta_psiquiatra \
  --philosophy recuperacao_conservadora
```

### 2) Registrar check-in diário

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py checkin \
  --energy 4 --mood 5 --anxiety 7 --sleep-hours 6 --sleep-quality 4 --cognition 4 \
  --side-effects "sedação matinal"
```

### 3) Inserir tarefas

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py add-task "Organizar consultório" --essential
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py add-task "Escrever revisão de artigo" --domain profissional
```

### 4) Gerar plano diário adaptativo

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py plan
```

### 5) Dashboard diário

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py dashboard
```

### 6) Log de hábitos

`--done` recebe CSV de hábitos feitos no dia.

Hábitos disponíveis por padrão:
- `agua_ml`
- `movimento_min`
- `luz_solar_min`
- `organizacao_min`
- `diario_clinico_min`

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py habits --done agua_ml,movimento_min
```

### 7) Relatório semanal

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py weekly-report
```

### 8) Exportar JSON

```bash
python 04-PracticalSamples/clinical-routine-assistant/clinical_routine_assistant.py export --output ./backup_clinical_state.json
```

## Persistência

Por padrão, os dados ficam em `clinical_state.json` no diretório atual.
Para usar outro arquivo:

```bash
python .../clinical_routine_assistant.py --db /caminho/estado.json dashboard
```

## Próximos passos (roadmap)

- Modo GUI (Tkinter/PyQt)
- Visualização em calendário
- Exportação PDF
- Integração com Google Calendar/Notion
- Módulo LLM local para coaching cognitivo
