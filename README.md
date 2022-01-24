# Dengue Season Predictor

### Overview
Dengue Season Predictor written in Python which takes in historical rain and dengue data (in csv format) and outputs upcoming peak dengue seasons with statistical information.

Inputs are received via command line arugment, which also starts the Python application with GUI. 

Users may view current input datas by clicking on the 'View Rainfall Datasets' and 'View Dengue Datasets' in the GUI.

All inputs and outputs are also presented in graph format in the GUI. Statistical calculations are shown as labelled text in the sidebar.

Users may click on the 'Export Prediction+Analysis' button to export both graph (as .png) and prediction with statistical information (as .txt). 

### Scope of Personal Contribution to Team Project:
- Python Tkinter GUI (graph and sidebar) -- Implementation
- Data Curve Smoothing via SciPy Savgol Filter -- Implementation
- 'Export Prediction+Analysis' functionality -- Implementation
- Input Validation via Tkinter GUI -- Implementation

### Screenshot of Single-Page Desktop Application
<img width="793" alt="Screenshot 2022-01-03 074338" src="https://user-images.githubusercontent.com/74390368/147892442-4a0180a2-f384-4a31-ae16-ddb909cae6b4.png">

### Features

#### View Datasets Button 
<img width="571" alt="image" src="https://user-images.githubusercontent.com/74390368/147892639-20d47f9c-2955-47a2-b3eb-a6e8bd66145d.png">
<img width="247" alt="image" src="https://user-images.githubusercontent.com/74390368/147892646-560a819b-81b3-4ca2-b791-4562b4b054dc.png">
<img width="503" alt="image" src="https://user-images.githubusercontent.com/74390368/147892650-622e108d-bb1e-43ef-b998-69314b312607.png">

#### Graph Curve Smoothing via SciPy Savgol Filter
<img width="281" alt="image" src="https://user-images.githubusercontent.com/74390368/147892692-f3123993-6ec2-4aaa-8538-dfa7e7522338.png">
<img width="334" alt="image" src="https://user-images.githubusercontent.com/74390368/147892761-b6111207-c753-435b-ab92-fa497d5f80a4.png">
<img width="484" alt="image" src="https://user-images.githubusercontent.com/74390368/147892765-bfea8c66-d200-4fbc-89f2-8465dd4d295a.png">
<img width="709" alt="image" src="https://user-images.githubusercontent.com/74390368/147892748-36a90030-2147-48bb-9b3c-214227a3d658.png">

#### Search Corresponding Data for Given Week 
<img width="400" alt="image" src="https://user-images.githubusercontent.com/74390368/147892800-39b25a92-7a09-4bc4-9820-2e6f9fc994c2.png">

#### Input Validation for Search Input Field
<img width="399" alt="image" src="https://user-images.githubusercontent.com/74390368/147892842-d920f2b5-a3b7-42ea-a7fa-357571c68fb9.png">
<img width="400" alt="image" src="https://user-images.githubusercontent.com/74390368/147892852-e7125d87-1248-4149-81fb-0a5e41b7c8ee.png">

#### Export Graph, Prediction, and Statistical Information
<img width="173" alt="image" src="https://user-images.githubusercontent.com/74390368/147892914-c1d0cda1-0300-43eb-ad84-6ec9f812aca6.png">
<img width="656" alt="image" src="https://user-images.githubusercontent.com/74390368/147892935-483dc3c2-f584-4e76-b596-4409541ace20.png">


