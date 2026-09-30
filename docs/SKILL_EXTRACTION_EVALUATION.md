# Skill Extraction Evaluation

Handoff priority: *"Skill extraction from uploaded resumes has been a major known problem … audit it carefully."*

- **Evaluation set:** `tests/skill_extraction_cases.py` — 4 synthetic resumes (with deliberate traps: name initials, company names, English words that are technology names) + `sample_resume/sample.pdf` + `temp_resume.pdf` (local only, git-ignored).
- **Script:** `python tests/evaluate_skill_extraction.py --markdown`
- **Scoring:** exact canonical names, because matched/missing skills downstream are computed by exact string comparison. Skills in a case's `acceptable` set count neither way.
- **Inputs:** `raw` = text from the PDF pipeline; `cleaned` = `advanced_clean_text(raw)`. **Before the fix the React app and the backend used `cleaned`.**

## End-to-end stage trace (where information was lost)

| Stage | Observation on `temp_resume.pdf` (.NET developer) |
|---|---|
| Raw PDF → extracted text | Text extracted correctly (PyMuPDF). Two-column layout interleaves headings, but all skill words survive. |
| Extracted → cleaned text | `C#(ASP.Net)` → `c asp net`, `.NET` → `net`, casing removed. **C#, .NET, ASP.NET lost here.** |
| Cleaned → candidate skills | Alias matching finds `c`, `r` (name initial), `javascript`; capitalised-word patterns find nothing (text is lowercase). |
| Candidates → normalized | Normalizer returned lowercase keys (`angularjs`, `javascript`) and mapped canonical `REST API` → `R` via substring match. |
| Final skills shown | `R, angularjs, c, communication, innovation, javascript, problem solving, r, sql, time management` |

On raw text the same pipeline also produced names and places as skills (address/college name fragments, plus `Developed`, `SKILLS`, `Utilized` — exact tokens omitted because this resume contains personal data).

## Baseline (before)

| Case | Input | Recall % | Precision % | Extracted | Missed | False positives |
|---|---|---|---|---|---|---|
| synthetic_python_backend | raw | 11.1 | 5.7 | 35 | AWS, C++, CI/CD, Django, Docker, FastAPI, Flask, Git, GitHub Actions, MongoDB, NumPy, PostgreSQL, REST API, Redis, SQL, scikit-learn | APIs, Built, C, Databases, Implemented, Languages, Laravel, Mehta, Pune, R, SKILLS, Tools, TypeScript, aws, c, c++, django, docker, fastapi, flask, git, github, github actions, mongodb, numpy, postgres, postgresql, python, redis, rest, restful, sql, with |
| synthetic_python_backend | cleaned | 0.0 | 0.0 | 17 | AWS, C++, CI/CD, Django, Docker, FastAPI, Flask, Git, GitHub Actions, Linux, MongoDB, NumPy, PostgreSQL, Python, REST API, Redis, SQL, scikit-learn | R, TypeScript, aws, c, django, docker, fastapi, flask, git, github, github actions, mongodb, numpy, postgresql, python, redis, sql |
| synthetic_dotnet_fullstack | raw | 35.7 | 17.2 | 29 | .NET, CSS, HTML, Microsoft SQL Server, Node.js, React, Scrum, TypeScript, Web API | AWS, Built, C, Developed, DigitalOcean, FastAPI, Full, Machine Learning, R, SKILLS, Solutions, agile, asp.net, c, go, javascript, node.js, r, react, react.js, reactjs, scrum, sql, typescript |
| synthetic_dotnet_fullstack | cleaned | 14.3 | 16.7 | 12 | .NET, ASP.NET, C#, CSS, HTML, Jest, Microsoft SQL Server, Node.js, React, Scrum, TypeScript, Web API | C, c, go, javascript, node.js, r, react, scrum, sql, typescript |
| synthetic_data_scientist | raw | 20.0 | 10.3 | 29 | Apache Spark, Communication, Machine Learning, Matplotlib, Microsoft Excel, Natural Language Processing, NumPy, Pandas, Power BI, PyTorch, TensorFlow, XGBoost | Aman, Analyst, Built, C, Datadog, Delhi, Foods, R, Skills, Valley, communication, deep learning, leadership, machine learning, matplotlib, natural language processing, nlp, numpy, pandas, pytorch, sklearn, spark, spring, spring boot, tensorflow, xgboost |
| synthetic_data_scientist | cleaned | 6.7 | 6.7 | 15 | Apache Spark, Communication, Deep Learning, Machine Learning, Matplotlib, Microsoft Excel, Natural Language Processing, NumPy, Pandas, Power BI, PyTorch, Tableau, TensorFlow, XGBoost | C, Python, communication, deep learning, leadership, machine learning, matplotlib, natural language processing, numpy, pandas, pytorch, spring boot, tensorflow, xgboost |
| synthetic_non_technical_traps | raw | 25.0 | 7.1 | 14 | Communication, Microsoft Excel, Negotiation | C, Managed, Neha, R, Sales, Skills, TypeScript, communication, go, negotiation, oracle, swift, time management |
| synthetic_non_technical_traps | cleaned | 0.0 | 0.0 | 7 | Communication, Microsoft Excel, Negotiation, Time Management | C, R, communication, go, negotiation, swift, time management |
| sample_resume/sample.pdf | raw | 11.1 | 1.9 | 54 | Active Directory, Communication, Microsoft Exchange, Microsoft Office, PowerShell, SQL, Scrum, VMware | Adobe XD, Build, Built, Business, C, Cassandra, DEXIS, DePaul, Defined, Dental, Deploy, Deployed, Designed, Ghost, Go, Houston, Installed, JavaScript, KPIs, Maintained, Managed, Milestone, Name, Novell, Obtained, PBX, Paine, Pandas, R, SaaS, Skills, Slack, Snap, Staff, State, Sydney, Tested, Time Management, TypeScript, Video, Vista, Weights & Biases, Wetzel, Windows 7, Windows XP, budget, communication, database, laptops, phones, powershell, scrum, sql |
| sample_resume/sample.pdf | cleaned | 0.0 | 0.0 | 5 | Active Directory, Communication, Microsoft Exchange, Microsoft Office, PowerShell, SQL, Scrum, VMware, Windows | TypeScript, communication, powershell, scrum, sql |
| temp_resume.pdf (local only) | raw | 28.6 | 11.1 | 36 | .NET, AngularJS, CSS, Communication, HTML, Problem Solving, REST API, SQL, Time Management, Web API | APIs, AWS, Adaptability, [5 address/name tokens], C, Detail, Developed, FastAPI, Full, Implemented, LANGUAGES, Machine Learning, R, SKILLS, Sale, TypeScript, Utilized, angularjs, asp.net, c, communication, developing, innovation, javascript, management skills, r, restful, sql |
| temp_resume.pdf (local only) | cleaned | 7.1 | 9.1 | 11 | .NET, ASP.NET, AngularJS, C#, CSS, Communication, HTML, Problem Solving, QlikView, REST API, SQL, Time Management, Web API | R, angularjs, c, communication, innovation, javascript, problem solving, r, sql, time management |

| Input | Micro recall % | Micro precision % | TP | FP | Missed |
|---|---|---|---|---|---|
| raw | 21.6 | 8.1 | 16 | 181 | 58 |
| cleaned | 5.4 | 6.0 | 4 | 63 | 70 |

## After the fix

| Case | Input | Recall % | Precision % | Extracted | Missed | False positives |
|---|---|---|---|---|---|---|
| synthetic_python_backend | raw | 100.0 | 100.0 | 19 | - | - |
| synthetic_python_backend | cleaned | 88.9 | 100.0 | 17 | C++, CI/CD | - |
| synthetic_dotnet_fullstack | raw | 100.0 | 100.0 | 15 | - | - |
| synthetic_dotnet_fullstack | cleaned | 71.4 | 100.0 | 11 | .NET, ASP.NET, C#, Node.js | - |
| synthetic_data_scientist | raw | 100.0 | 100.0 | 16 | - | - |
| synthetic_data_scientist | cleaned | 93.3 | 100.0 | 15 | Microsoft Excel | - |
| synthetic_non_technical_traps | raw | 100.0 | 80.0 | 5 | - | Oracle Database |
| synthetic_non_technical_traps | cleaned | 100.0 | 80.0 | 5 | - | Oracle Database |
| sample_resume/sample.pdf | raw | 100.0 | 100.0 | 9 | - | - |
| sample_resume/sample.pdf | cleaned | 100.0 | 100.0 | 9 | - | - |
| temp_resume.pdf (local only) | raw | 100.0 | 100.0 | 15 | - | - |
| temp_resume.pdf (local only) | cleaned | 78.6 | 100.0 | 12 | .NET, ASP.NET, C# | - |

| Input | Micro recall % | Micro precision % | TP | FP | Missed |
|---|---|---|---|---|---|
| raw | 100.0 | 98.7 | 74 | 1 | 0 |
| cleaned | 86.5 | 98.5 | 64 | 1 | 10 |

## Summary

| Input used by the app | Recall | Precision |
|---|---|---|
| Before (cleaned text, old extractor) | 5.4 % | 6.0 % |
| After (raw text, fixed extractor) | 100 % | 98.7 % |

- The remaining false positive is `Oracle Database` from the company name *Oracle Towers Realty* — a genuine ambiguity that a vocabulary matcher cannot resolve (known limitation B19).
- The cleaned-text rows show why skills must be extracted from raw text: even with the fixed extractor, cleaning still destroys C++, C#, .NET, Node.js and CI/CD.
- The set is small and was used while fixing, so it is a regression gate, not an unbiased benchmark. A spot check on unlabelled dataset resumes (IT, Engineering, HR, Chef) and four `jobs.csv` descriptions showed no obvious false positives; non-technical domains get few skills because the vocabulary is technology-focused.
