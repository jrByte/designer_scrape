#!/usr/bin/env python
# coding: utf-8

# ### Thesis Project
#
# Using Design Pattern: Facade
#
# Ideas:
# - Primary Color, Secondary, and Terrtiary Color Detection.
# - Color Blob detection using machine vision to see if there are larger or smaller patterns.

# In[1]:


import math
import time
import urllib

from PIL import Image
import os
import requests
from bs4 import BeautifulSoup
import matplotlib.image as mpimg
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from urllib.parse import urlparse


# In[2]:


class ImageFileManager:
    def __init__(self, image_directory):
        self.image_directory = image_directory

    def get_files_list(self, directory):
        print("Running get_files_list")
        # print("Directory:", directory)
        files = list()
        print(directory, os.listdir(directory))
        if not os.path.isdir(directory):
            os.makedirs(directory)

        for a in os.listdir(directory):
            files.append(a)
        return files


# In[3]:


class ImageWebScrapper:
    def __init__(self, image_directory, image_limit: int = 10):
        self.image_directory = image_directory
        self.website_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        self.image_limit = image_limit
        self.image_count = 1

    def download_images(self, url_images: list):
        """
        Iterates through a list of url images that it downloads and saves in the appropriate directory.
        It saves it within the image_limit directory under the hostname.

        :param url_images: a list of urls that are direct links to images.
        """

        #       Gets the domain from the URL and creates a directory for it.
        domain = url_images[0]
        print(domain)
        domain = '.'.join((urlparse(domain).netloc).split('.')[-2:])
        directory = os.path.join(self.image_directory, domain)
        if not os.path.exists(directory):
            os.makedirs(directory)

        os.chmod(directory, 0o755)

        #       Gets first file name to avoid overwritting other files.
        files = list()
        for a in os.listdir(directory):
            files.append(a)
        file_name_iteration = len(files)

        for url in url_images:
            print("Fetching Image:", self.image_count, domain)
            response = requests.get(url, headers=self.website_headers)
            if response.status_code == 200:
                file_location = os.path.join(directory, f"{file_name_iteration}.png")
                with open(file_location, 'wb') as f:
                    f.write(response.content)
                    file_name_iteration += 1
                    self.image_count += 1
                    f.close()

                os.chmod(file_location, 0o755)

                if self.image_count > self.image_limit:
                    print(f"(download_images): Image count reached: {self.image_limit}")
                    return True

    def fetch_louis_vuitton_pages(self, website):
        print("Running fetch_louis_vuitton_pages")
        page_dne = True
        count = 0
        louis_vuitton_images_pages = list()
        while count <= self.image_limit and page_dne:
            print("Page:", count)
            try:
                website += f"?page={count}"
                print(f"Fetching: {website}")

                req = requests.get(website, headers=self.website_headers)
                print(req.status_code)

                soup = BeautifulSoup(req.text, "html.parser", from_encoding="gzip")
                soup_images = soup.find_all('img', {"class": 'lv-smart-picture__object'})

                clean_url_images = list()
                for url in soup_images:
                    image_sources = url.get('data-srcset')
                    urls = (image_sources.split(','), '\n')
                    for url_records in urls:
                        for url in url_records:
                            url = url[:url.rfind(" ")]
                            url = url.replace(" ", "")
                            if url.rfind("wid=1180&hei=1180") != -1:
                                clean_url_images.append(url)
                louis_vuitton_images_pages.append(clean_url_images)
                count += 1
            except urllib.error.HTTPError as e:
                print(e)
                page_dne = False
            return louis_vuitton_images_pages


# In[18]:


class ImageAnalysis:
    def __init__(self, image_directory):
        self.image_directory = image_directory
        self.minimum_percentage_similarity = 20

    def get_top_values(self, top_colors_in_all_images):
        minimum_top_colors = 10
        top_values = []
        for image in top_colors_in_all_images:
            cleaned_image = sorted(image)
            top_image_colors = sorted(cleaned_image)[:minimum_top_colors]
            for image_color in top_image_colors:
                top_values.append(image_color)
        return top_values

    def plot_3d_rgb_graph(self, rgb_with_frequency):
        print(rgb_with_frequency[:1])

    #     TODO: Rewrite
    def plot_rgb_scatter_with_frequency(self, rgb_with_frequency, image_path=None):
        plt.figure(1)
        rgb_colors, frequencies = zip(*rgb_with_frequency)
        r_values = [color[0] for color in rgb_colors]
        g_values = [color[1] for color in rgb_colors]
        b_values = [color[2] for color in rgb_colors]

        # Convert RGB colors to hexadecimal notation
        hex_colors = ['#%02x%02x%02x' % color for color in rgb_colors]

        plt.scatter(r_values, g_values, c=hex_colors, marker='o', s=[f * 10 for f in frequencies], alpha=0.7)
        plt.xlabel('Red')
        plt.ylabel('Green')
        plt.title('Scatter Plot of RGB Colors with Frequency')
        plt.colorbar(label='Blue')
        plt.grid(True)
        plt.show()

        #       plot 2
        colors2 = [color[0] for color in rgb_with_frequency]
        frequencies2 = [color[1] for color in rgb_with_frequency]
        r_values2 = [color[0] for color in colors2]
        g_values2 = [color[1] for color in colors2]
        b_values2 = [color[2] for color in colors2]

        # Plot the bar graph
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(colors2)), frequencies, color=[(r / 255, g / 255, b / 255) for r, g, b in colors2])
        plt.xticks(range(len(colors2)), colors2)
        plt.xlabel('RGB Colors')
        plt.ylabel('Frequency')
        plt.title('Top 10 Colors with Frequencies')
        plt.show()

        if image_path:
            plt.figure(3)
            # Assuming you have the path to the image file

            # Read the image using `mpimg.imread()`
            image = mpimg.imread(image_path)

            # Display the image using `imshow()`
            plt.imshow(image)

            # Show the plot
            plt.show()

    def image_most_common_colors(self, by_color, most_common=300):
        """
        Called by image_main_colors. Gets all the most common colors in the image. That counts the rgb values of each
        pixel in the image. While making sure that shades of colors are not included based on a certain
        amount of similarity.

        :param most_common:
        :return: most_common_rgb: returns a Counter datatype. Of the counted rbg values in the image.
        """
        most_common_rgb = Counter(by_color).most_common(most_common)
        common_rgb_clone = most_common_rgb.copy()
        for rgb_index in range(len(common_rgb_clone)):
            for rgb_index2 in range(rgb_index + 1, len(common_rgb_clone)):
                r1 = common_rgb_clone[rgb_index][0][0]
                g1 = common_rgb_clone[rgb_index][0][1]
                b1 = common_rgb_clone[rgb_index][0][2]

                r2 = common_rgb_clone[rgb_index2][0][0]
                g2 = common_rgb_clone[rgb_index2][0][1]
                b2 = common_rgb_clone[rgb_index2][0][2]

                distance = math.sqrt(math.pow((r2 - r1), 2) + math.pow((g2 - g1), 2) + math.pow((b2 - b1), 2))
                percentage = (distance / (math.sqrt(math.pow(255, 2) + math.pow(255, 2) + math.pow(255, 2)))) * 100

                if len(most_common_rgb) <= 10:
                    break
                else:
                    if percentage <= self.minimum_percentage_similarity:
                        if common_rgb_clone[rgb_index2] in most_common_rgb:
                            most_common_rgb.remove(common_rgb_clone[rgb_index2])

        return most_common_rgb

    def file_to_image(self, file_path):
        with Image.open(file_path).convert('RGB') as image:
            return image

    def image_main_colors(self, image):
        by_color = defaultdict(int)

        for pixel in image.getdata():
            if pixel != (0, 0, 0) and pixel != (255, 255, 255):
                by_color[pixel] += 1

        return by_color

    def single_pie_chart(self, image):
        """
        Creates a pie chart of the list of colors found.
        :param individual_images:
        :return:
        """
        print("Running single_pie_chart")

        labels = list()
        sizes = list()

        for color in colors:
            labels.append(str(color[0]))
            sizes.append(color[1])

        sorted_hex = sorted(self.rgb_to_hex(labels))
        plt.pie(sizes, startangle=90, colors=sorted_hex)
        plt.legend(sorted_hex, loc='center left', fontsize=7, bbox_to_anchor=(1, 0.5))
        plt.savefig('readme_images/Louis_Vuitton_colors.PNG', bbox_inches='tight', dpi=500)
        plt.show()

    def pie_chart(self, path):
        """
        Creates a pie chart of the list of colors found.
        :param individual_images:
        :return:
        """

        print("Running pie_chart")
        colors = self.sorted_colors
        if not individual_images:
            colors = self.all_sorted_colors

        if self.all_sorted_colors:
            labels = list()
            sizes = list()

            for color in colors:
                labels.append(str(color[0]))
                sizes.append(color[1])

            sorted_hex = sorted(self.rgb_to_hex(labels))

            plt.pie(sizes, startangle=90, colors=sorted_hex)
            plt.legend(sorted_hex, loc='center left', fontsize=7, bbox_to_anchor=(1, 0.5))
            plt.savefig('readme_images/Louis_Vuitton_colors.PNG', bbox_inches='tight', dpi=500)

            plt.show()

        else:
            raise "Must call get_image_main_colors() first before calling pie_chart()"


# In[35]:


class Facade:
    def __init__(self):
        #       default variables
        self.image_directory = os.path.join(os.getcwd(), "images")
        #       calling necessary classes
        self.image_web_scrapper = ImageWebScrapper(self.image_directory)
        self.image_file_manager = ImageFileManager(self.image_directory)
        self.image_analysis = ImageAnalysis(self.image_directory)

    def get_files(self):
        louis_vuitton_dir = os.path.join(self.image_directory, "louisvuitton.com")
        image_paths = list()
        print(self.image_file_manager.get_files_list(louis_vuitton_dir))
        for file_name in self.image_file_manager.get_files_list(louis_vuitton_dir):
            full_path_image = os.path.join(louis_vuitton_dir, file_name)
            image_paths.append(full_path_image)
        return image_paths

    def download_website(self, url):
        pages = self.image_web_scrapper.fetch_louis_vuitton_pages(url)
        for page in pages:
            self.image_web_scrapper.download_images(page)

    def analyze_image(self, file_path):
        image = self.image_analysis.file_to_image(file_path)
        colors = self.image_analysis.image_main_colors(image)
        most_common_colors = self.image_analysis.image_most_common_colors(colors)
        self.image_analysis.plot_rgb_scatter_with_frequency(most_common_colors, file_path)

    def analyze_all_images(self):
        louis_vuitton_dir = os.path.join(self.image_directory, "louisvuitton.com")
        files = self.image_file_manager.get_files_list(louis_vuitton_dir)
        all_images_rgb_count = list()
        for file in files:
            print("Analyzing file: ", file)
            file_path = os.path.join(louis_vuitton_dir, file)
            image = self.image_analysis.file_to_image(file_path)
            colors = self.image_analysis.image_main_colors(image)
            most_common_colors = self.image_analysis.image_most_common_colors(colors)
            all_images_rgb_count += most_common_colors

        # self.image_analysis.plot_rgb_scatter_with_frequency(all_images_rgb_count)
        self.image_analysis.plot_3d_rgb_graph(all_images_rgb_count)



# In[34]:


if __name__ == "__main__":
    facade = Facade()
    website_url = "https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/_/N-tfr7qdp"
    # facade.download_website(website_url)

    # facade.analyze_image(r'/Users/Jonas/Desktop/GitHub/Python/designer_scrape/images/louisvuitton.com/0.png')
    facade.analyze_all_images()

    #     for i in facade.get_files():
    #         facade.analyze_image(i)
    #         time.sleep(3)

    # facade.analyze_all_images()

# In[ ]:
