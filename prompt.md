You are a top-tier Software Architect and an Expert Data Scientist. Your task is to write a Python script that programmatically generates a highly educational Jupyter Notebook (.ipynb) covering the plans (read plan.md). 

CRITICAL TECHNICAL CONSTRAINTS: 
1. DO NOT construct the Jupyter Notebook JSON schema manually. It is fragile and unprofessional. 
2. You MUST use the standard nbformat library (e.g., import nbformat as nbf) to construct the notebook, add cells ([nbf.v4.new](http://nbf.v4.new)_markdown_cell, [nbf.v4.new](http://nbf.v4.new)_code_cell), and write the file. 
3. The generated script must be production-ready, clean, and scalable. 

CONTENT AND PEDAGOGY GUIDELINES: 
1. Target Audience: AI Engineers and Data Science students who need deep, practical understanding. Do not dumb it down. 
2. Structure: Break the chapter into logical sections. Use Markdown for theory and Code cells for execution. 
3. Mathematical Rigor: Use proper LaTeX for all equations. Connect the math directly to real-world ML/AI applications (e.g., how transformations relate to neural network weights). 
4. Visualizations: Provide robust, bug-free code using matplotlib or plotly to visualize the concepts geometrically. 
5. Pragmatism: Skip fluff. Be direct, clear, and challenging. 

Output generate_nb.py for each modules, and then execute them to generate the educational ipynb files in the modules.