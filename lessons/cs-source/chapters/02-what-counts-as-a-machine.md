---
title: "¿Qué cuenta como máquina?"
---
Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre el estado y el control más allá de las variables](../guias-de-estudio/conceptos/estado-y-control-mas-alla-de-las-variables.md).

Antes de decir que un motor de expresiones regulares, una herramienta de compilación o un archivo de marcado "computa", tienes que decir qué es una máquina. La respuesta es más sencilla de lo que quizá imaginas. Una máquina tiene un **estado**, un conjunto de **pasos** permitidos y una forma de **representar** sus valores. También tiene hechos que se mantienen durante la ejecución (**invariantes**). Si puedes nombrar esos cuatro elementos, ya identificaste la máquina.

```mermaid
flowchart TB
    accTitle: Una máquina combina un estado y una regla para el siguiente estado. Puede prescindir de un procesador
    accDescr: Diagrama de un sistema de transición. El estado s se representa con bits, una pila, texto, rutas u otros valores. Pasa al estado s prima mediante un paso permitido: la regla de transición. Si hay una entrada de datos o un evento, alimenta el paso. El paso puede producir un efecto o un resultado observable. Un marco alrededor de ambos estados indica que el invariante se cumple tanto en s como en s prima.
    subgraph INV["El invariante I se cumple en s y en s′"]
        S["Estado s: bits, pila, texto, rutas, ..."] --> T(["Paso permitido: regla de transición"]) --> S2["Estado s′"]
    end
    IN["Entrada de datos o evento (si hay)"] -.-> T
    T -.-> OUT["Efecto o resultado observable (si hay)"]
```

La imagen muestra las cuatro partes sin nombrar ningún componente físico: el estado y su representación, un paso permitido y el invariante que se cumple antes y después del paso. La pila de capturas de un motor de expresiones regulares, un grafo de dependencias de Make y un búfer de editor encajan en esta plantilla. La plantilla no exige un número finito de estados, una entrada de datos y una salida explícitas ni instrucciones de máquina.

El primer objetivo de este libro es precisamente que adquieras ese hábito: *identifica la máquina que se esconde en el lenguaje*. Una máquina de pila, una máquina de registros y un sistema de reescritura pueden computar lo mismo, pero guardan su memoria en lugares distintos. Los conceptos de este capítulo te dan el vocabulario: sistemas de transición, semántica operacional (estado, un paso a la vez), máquinas de Turing, algoritmos de Márkov y completitud de Turing. Hay otra pregunta: ¿qué parte de un diseño *computa* y qué parte solo decide qué se ejecuta después ([[computation-versus-orchestration]])? El capítulo "Estado más allá de las variables" retoma la pregunta que más importa en este repositorio: ¿dónde vive el estado?
