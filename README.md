# Designer Scrape
## About

Designer Scrape is a dynamic and user-friendly tool to analyze various luxury clothing brands. It was initially built 
for my bachelor thesis to analyze the correlation of color usage of various high profile brands to gain insight and 
better understanding of currently used color trends and combinations.The code is built to be dynamic and manageable in 
various ways using the design pattern Facade. To maintain accurate and consistent results, only the front part of a 
handbags have been analyzed.

## Key Features
- Unique 3d graph: to visualize the trends and areas of avoidance for color in the collection of images.
- Image Scrabble websites: Louis Vuitton and Chanel.
- Color pallet analysis, conducted by comparing the calculated values of 
- Utilization of K nearest neighbor machine learning algorithm to discover the most common colors in the image.

## Getting Started

Before you start, be sure to check the laws and regulations set in your region and the company you are scarping data from.
Companies offer a endpoint 'robot.txt' to define the terms of service for web scrapping. 

1. clone the repository to your local machine. (Both Windows or Mac operating system is fine)
2. Install the required dependencies using 'poetry install' ensuring that Python 3.8 is used for the best compatibility. 
3. Use the python environment created with the required dependencies to run the code.
4. The 'Facade' class offers various methods to easily execute the systems required to make the analyses. 

## Louis Vuitton Analysis
<img src="readme_images/louisvuitton.com-handbags_rgb_scatter_plot_1.png?raw=true" alt="1st View" width="600" height="500">
<img src="readme_images/louisvuitton.com-handbags_rgb_scatter_plot_2.png?raw=true" alt="2nd View" width="600" height="500">


## Agenda
- Build abnormality algorithms to detect ongoing changes and potential trend predictions.

