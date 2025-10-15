# Agentic-AI

## Project Overview
This project demonstrates the reflection pattern within an agentic AI workflow that autonomously generates and improves data visualizations.

The notebook replicates an exercise from Deeplearning.AI’s “Agentic AI” course, adapted to use a different dataset. Majority of the code in this notebook is from the “Agentic AI” course.

All supporting functionality — such as prompt handling, visualization generation, and model interaction — is implemented through a custom utils.py module that emulates the original course utilities.

## Multimodal LLM
A multi-modal LLM is a system that can take and generate outputs beyond text (image, audio, video). The LLM will review the first draft chart, identify potential improvements—such as chart type, labels, or color choices—and then rewrite the chart generation code to produce a more effective visualization.

## Agentic Workflow
Generate an initial version (V1): Use a Large Language Model (LLM) to create the first version of the plotting code.

Execute code and create chart: Run the generated code and display the resulting chart.

Reflect on the output: Evaluate both the code and the chart using an LLM to detect areas for improvement (ex. clarity, accuracy, design).

Generate and execute improved version (V2): Produce a refined version of the plotting code based on reflection insights and render the enhanced chart.
