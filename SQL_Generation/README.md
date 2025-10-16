# Multi-Modal Agentic Workflow of Text-to-SQL Generation using Reflection Pattern

## Project Overview

This project demonstrates a multi-modal agentic workflow for Text-to-SQL generation, where a large language model (LLM) autonomously converts natural-language analytical questions into executable SQL queries, evaluates their correctness, and refines them through a reflection loop.

The system applies an agentic AI architecture that simulates how human analysts reason — by thinking, testing, and improving iteratively.
Through the Reflection Pattern, the agent reviews query outputs, compares them to the original question’s intent, and automatically self-corrects SQL errors or logic mismatches.

The notebook replicates an exercise from Deeplearning.AI’s “Agentic AI” course, adapted to use a different dataset. Majority of the code in this notebook is from the “Agentic AI” course.

## ⚙️ Core Workflow

🗣️ Natural-Language Understanding – The model interprets user questions and database schema.

🧩 SQL Generation – Converts intent into an executable SQL query tailored for SQLite.

🔍 Execution & Evaluation – Runs the query, inspects results, and detects inconsistencies.

🔁 Reflection Cycle – Provides feedback and refines SQL until it accurately answers the question.
The final execution of the agentic workflow looks as follows:

![Final Execution](https://github.com/hasongc01/Agentic-AI-Reflection-Design-Pattern-2/blob/main/FinalExecution.png)

## Data Overview
A product db was simulated (by GPT) to emulate the file from "Agentic AI" Course.
![product db](https://github.com/hasongc01/Agentic-AI-Reflection-Design-Pattern-2/blob/main/product%20db.png)


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

## 💡 Use Cases

🧾 Natural-Language Data Querying in BI Tools

Users can ask questions like “Show me total revenue by category in 2024” and instantly receive a valid SQL query with results.

The reflection loop ensures the query matches intent (correct filters, aggregations, and joins).

🤖 Autonomous Analytics Agents

Integrate the agent into dashboards (e.g., Streamlit, Power BI, or Looker) to enable self-updating analyses without manual SQL writing.

The model continually improves queries through feedback when schema or data change.
