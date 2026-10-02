
# Unemployment Analysis with Python

## Project objective
This project analyzes unemployment-rate data using Python. It covers:

- Data cleaning and preprocessing
- Exploratory data analysis
- Unemployment trends over time
- Regional comparisons
- Calendar-month patterns / seasonality
- A descriptive COVID-19 shock analysis
- Interactive visualization with Streamlit
- Exportable analysis summaries

## Dataset
The supplied dataset is stored at:

`data/Unemployment in India.csv`

The project uses the following fields:
- Region
- Date
- Frequency
- Estimated Unemployment Rate (%)
- Estimated Employed
- Estimated Labour Participation Rate (%)
- Area

## Project structure

```text
Unemployment_Analysis_Project/
│
├── app.py
├── analysis.py
├── requirements.txt
├── README.md
│
├── data/
│   └── Unemployment in India.csv
│
├── outputs/
│   └── generated after running analysis.py
│
└── src/
```

## How to run on Windows

### 1. Open Command Prompt / PowerShell
Go to the project folder:

```powershell
cd path\to\Unemployment_Analysis_Project
```

### 2. Create a virtual environment (recommended)

```powershell
py -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

If PowerShell blocks activation, you can skip activation and use `py -m pip` commands below.

### 3. Install libraries

```powershell
py -m pip install -r requirements.txt
```

### 4. Run the analysis

```powershell
py analysis.py
```

This creates CSV summaries, PNG charts, and `outputs/key_findings.txt`.

### 5. Launch the interactive dashboard

```powershell
py -m streamlit run app.py
```

The browser will open the Streamlit dashboard. If it does not, copy the local URL shown in the terminal.

## One-command dashboard after installation

```powershell
py -m streamlit run app.py
```

## Main analysis decisions

### COVID-19 period
For this academic project, March 2020 to June 2020 is grouped as the **COVID shock** period. The earlier available period is grouped as **Pre-COVID**, and the remaining observations as **Post-shock**.

This is a descriptive comparison. It does **not** prove that COVID-19 alone caused the observed change because other economic and social factors may also affect unemployment.

### Seasonality
Calendar-month averages are used to inspect recurring patterns. Because the available dataset covers a limited period, the result should be treated as exploratory rather than a definitive long-term seasonal model.

## Expected viva questions

1. What is unemployment rate?
2. Which Python libraries are used?
3. Why is data cleaning required?
4. How did you handle the Date column?
5. What is the difference between mean and median unemployment?
6. How did you analyze COVID-19?
7. What is seasonality?
8. Why should correlation not automatically be called causation?
9. Why is Streamlit used?
10. What are the limitations of the dataset?

## Important note
The project does not claim that COVID-19 was the only cause of changes in unemployment. The COVID section is a descriptive before/during/after comparison.
