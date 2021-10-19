# Designer Scrape

## Summary
Designer scrape is a simple algorithm that I am using to collect data from various designer websites. Currently only scraping of the louis vuitton website has been implemented, but I plan on adding more once I fine tune the color algorithm. It is highly advised to use a VPN to hide your IP address when scraping the images of the website to prevent your IP address from being blocked or restricted from other websites!!

## Installation
I use poetry a package manager to help install all my dependencies that I use for this project. Python 3.9 is used for this project and is ran on windows 10.

## Color Algorithm 
Currently the algorithm individually searches through every pixel and identifies the color of that pixel with RGB. This is then stored and counted for everytime there is an identical version of that RGB found. Anything that is similar to a certain percentage is remove because of them being considered shadows or shading of that color and are also very high in digits. The percentage of sensitivity of shades can be adjusted when calling the most_common_colors method, but is declared beforehand when creating an instance of the class image_scrape. This will be improved to be more OOP in the future.

## Results

![Alt text](readme_images/Louis_Vuitton_colors.PNG?raw=true "Louis Vuitton image collection of handbag colors")
https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/

## Agenda
- The pie chart will be sorted in the upcoming commits to be sorted in a rainbow. Starting with red.
- Color algorithm is planned on being improved with object recognition in the images to identifiy symbols that use particular colors for more accurate color identification.
- Expansion of other designer brands being scraped and including price points of each color. Note: Louis Vuitton doesn't display this, but other brands like Gucci do.
