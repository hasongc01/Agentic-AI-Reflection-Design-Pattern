# Multi-Modal Agentic Workflow of Chart Generation using Reflection Pattern

## 🧠 Project Overview
This project explores a multi-modal agentic workflow for automated chart generation, integrating text, code, and visual reasoning. The workflow leverages an agentic AI architecture with a reflection pattern, enabling the model to iteratively critique and refine its own chart outputs based on data semantics and visual feedback.

Through this reflection loop, the agent autonomously:

- Interprets natural-language analytical queries.

- Generates data-driven Python code (e.g., using matplotlib or plotly) to visualize insights.

- Evaluates the fidelity, interpretability, and aesthetics of the resulting chart.

- Refines the visualization iteratively until alignment with the intended analytical goal is achieved.

The result is a closed-loop, self-improving chart generation system that mimics how human analysts explore, test, and polish visual insights — but in an automated, multi-modal way.

The notebook replicates an exercise from Deeplearning.AI’s “Agentic AI” course, adapted to use a different dataset. Majority of the code in this notebook is from the “Agentic AI” course.

All supporting functionality — such as prompt handling, visualization generation, and model interaction — is implemented through a custom utils.py module that emulates the original course utilities.

## Multimodal LLM
A multi-modal LLM is a system that can take and generate outputs beyond text (image, audio, video). The LLM will review the first draft chart, identify potential improvements—such as chart type, labels, or color choices—and then rewrite the chart generation code to produce a more effective visualization.

## Agentic Workflow
Generate an initial version (V1): Use a Large Language Model (LLM) to create the first version of the plotting code.

Execute code and create chart: Run the generated code and display the resulting chart.

Reflect on the output: Evaluate both the code and the chart using an LLM to detect areas for improvement (ex. clarity, accuracy, design).

Generate and execute improved version (V2): Produce a refined version of the plotting code based on reflection insights and render the enhanced chart.

## 🧩 LLM Model Used: gpt-4o-mini

This project uses OpenAI’s gpt-4o-mini, a lightweight variant of the GPT-4-Omni architecture designed for multi-modal reasoning across text, code, and visual inputs.

Despite its smaller footprint, gpt-4o-mini retains GPT-4-level reasoning quality while offering lower latency, faster inference, and cost efficiency, making it ideal for iterative agentic workflows such as reflection-based chart generation.

Key features:

💬 Multi-modal comprehension: Understands and generates text, code, and structured data simultaneously.

🎨 Visual reasoning: Interprets chart outputs and refines visual parameters based on feedback.

⚙️ Lightweight & responsive: Optimized for rapid reasoning loops in autonomous or self-reflective agents.

🧠 Reflection-friendly architecture: Suited for tasks requiring critique–revise–re-evaluate cycles.

In this workflow, gpt-4o-mini acts as both:

The reasoning engine — generating and explaining chart code from natural-language prompts.

The reflective evaluator — reviewing the generated visualization, diagnosing issues (ex. mislabeled axes, cluttered design), and iteratively improving the output.

## ⚙️ Core Components

- Agentic Orchestration: Modular LLM-based agents for planning, visualization, reflection, and improvement.

- Reflection Pattern: Structured feedback cycle comparing expected vs. generated visual output.

- Multi-Modal Reasoning: Joint understanding of textual intent, tabular data, and visual output.

- Evaluation Metrics: Considers chart accuracy, readability, and semantic alignment.

## 🚀 Use Cases

- Automated EDA (Exploratory Data Analysis) visualization.

- Generating publication-ready charts from natural language prompts.

- Teaching and evaluating visual reasoning in LLMs.

- Integrating self-correcting AI into business analytics workflows.
