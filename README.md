# Sistema fuzzy para manutenção baseada em condição de bomba hidráulica

Código do Trabalho de Conclusão de Curso **"Desenvolvimento de sistema baseado em lógica fuzzy para manutenção baseada em condição de bomba hidráulica"**, do curso de Engenharia de Controle e Automação da Universidade Tecnológica Federal do Paraná (UTFPR), Campus Curitiba.

- **Autor:** Lucas Havi Gomes Leite
- **Orientador:** Narco Afonso Ravazzoli Maciejewski
- **Aplicação on-line:** https://fuzzycriticidadebomba2026.streamlit.app/

> A versão **`v1.0-tcc1`** deste repositório é a que está descrita no texto entregue à banca do TCC 1 (2026). As referências de temperatura e de pressão ainda são **preliminares** e serão ajustadas com os ensaios em bancada previstos para o TCC 2 (2027).

## O que o sistema faz

O sistema avalia a condição de uma bomba de engrenagens externas (Bosch Rexroth AZPF) a partir de três leituras e devolve um **índice de criticidade de 0 a 100**, com a ação de manutenção recomendada.

| Entrada | Unidade | Faixa aceita |
|---|---|---|
| Temperatura do óleo | °C | 20 a 100 |
| Pressão de saída | bar | 0 a 300 |
| Contaminação (código ISO 4406, convertido em Δ em relação à classe 20/18/15) | — | três inteiros de 0 a 30 |

- **Inferência:** Mamdani (mínimo e máximo), com 3 termos linguísticos por variável e 27 regras.
- **Defuzzificação:** centroide, com o universo de saída discretizado em 1001 pontos.
- **Referências da bancada:**
  - temperatura de referência `T_ref` de 20 a 75 °C, valor preliminar 50 °C;
  - pressão de referência `p_ref` de 10 a 210 bar, valor preliminar 100 bar.
- **Limites do fabricante:** 80 °C (vedação NBR), 210 e 250 bar, e classe de limpeza 20/18/15.

| Índice | Criticidade | Ação recomendada |
|---|---|---|
| abaixo de 37,5 | baixa (tolerável) | Operação normal: manter o monitoramento. |
| de 37,5 a 62,5 | média (indesejável) | Programar manutenção: inspeção da bomba e da sucção, troca ou filtragem do óleo. |
| acima de 62,5 | alta (crítico) | Intervenção imediata: interromper a operação e investigar a causa. |

## Arquivos

| Arquivo | Função |
|---|---|
| `fuzzy_bomba.py` | Sistema fuzzy: verificação das entradas, funções de pertinência, base de regras, inferência, defuzzificação e classificação. Também tem um teste pelo terminal. |
| `graficos.py` | Gráficos de fuzzificação das entradas e do conjunto de saída com o centroide (usa o `fuzzy_bomba.py`). |
| `app.py` | Dashboard em Streamlit: entradas, resultado, gráficos, regras ativadas e histórico em CSV (usa os dois arquivos acima). |
| `requirements.txt` | Bibliotecas e versões usadas. |

## Como executar no computador

Versão usada no trabalho: Python 3.13.

```bash
pip install -r requirements.txt

streamlit run app.py      # abre o dashboard no navegador
python fuzzy_bomba.py     # teste pelo terminal: digita as leituras e mostra cada etapa
python graficos.py        # salva os quatro gráficos de um exemplo na pasta do projeto
```

Versões fixadas no `requirements.txt`: Streamlit 1.66.1, NumPy 2.5.4, Matplotlib 3.11.2 e pandas 3.1.0.

## Observações

- É uma ferramenta de apoio à decisão da equipe de manutenção. Os parâmetros são preliminares e não substituem a avaliação técnica do equipamento.
- No dashboard, o histórico de avaliações fica guardado só enquanto a página estiver aberta. Baixe o arquivo `.csv` antes de fechá-la.

## Como citar

LEITE, Lucas Havi Gomes. **Desenvolvimento de sistema baseado em lógica fuzzy para manutenção baseada em condição de bomba hidráulica**. 2026. Proposta de Trabalho de Conclusão de Curso (Graduação em Engenharia de Controle e Automação) – Universidade Tecnológica Federal do Paraná, Curitiba, 2026.
