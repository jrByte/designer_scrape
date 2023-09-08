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

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import re
import math
import random
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
    def __init__(self, directory):
        self.image_directory = os.path.join(directory, "images")

    def get_files_list(self, directory):
        print("Running get_files_list")
        # print("Directory:", directory)
        files = list()
        if not os.path.isdir(directory):
            os.makedirs(directory)

        print(directory, os.listdir(directory))

        for a in os.listdir(directory):
            files.append(a)
        return files


# In[3]:


class ImageWebScrapper:
    def __init__(self, directory, image_limit: int = 10, website_category_limit: int = 5):
        self.directory = directory
        self.image_directory = os.path.join(directory, "images")
        self.website_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        self.image_limit = image_limit
        self.image_count = 1
        self.website_category_limit = website_category_limit

    def download_images(self, domain, url_images: list, directory_special_name: str, amount_of_pages: int):
        """
        Iterates through a list of url images that it downloads and saves in the appropriate directory.
        It saves it within the image_limit directory under the hostname.

        :param url_images: a list of urls that are direct links to images.
        """

        #       Gets the domain from the URL and creates a directory for it.
        domain = domain + directory_special_name
        print("DOMAIN: ", domain)
        directory = os.path.join(self.image_directory, domain)
        if not os.path.exists(directory):
            os.makedirs(directory)

        os.chmod(directory, 0o755)

        #       Gets first file name to avoid overwritting other files.
        files = list()
        for a in os.listdir(directory):
            files.append(a)
        file_name_iteration = len(files)

        for count, url in enumerate(url_images):
            print(f"{count}/{len(url_images)}")
            # print("Fetching Image:", self.image_count, domain)
            delay = random.randint(0, 2)
            time.sleep(delay)
            # print(f"Delaying Fetch by {delay} seconds.")
            print("URL: ", url)
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
                    print(f"Image count reached: {self.image_limit}")
                    return True

    def fetch_chanel_pages(self, website):
        count = 1
        
        all_website_images = list()
        page_exists = True
        
        while (count <= self.website_category_limit) and page_exists:
            website_images = list()
            try:
                website_with_endpoint = website + f"page-{count}/"
                print(website_with_endpoint)
                req = requests.get(website_with_endpoint, headers=self.website_headers)

                soup = BeautifulSoup(req.text, "html.parser", from_encoding="gzip")
                website_items = soup.find_all('div', {"class": 'product-grid__item js-product-edito fs-gridelement'})

                if len(website_items) == 0:
                    page_exists = False

                for images_in_website_items in website_items:
                    images = images_in_website_items.find_all('picture', {"class": 'fs-element--inline'})
                    for image in images:
                        source_tag = image.find('source')
                        if source_tag and 'srcset' in source_tag.attrs:
                            product_image_sizes = source_tag["srcset"]
                            urls = re.findall(r'(//www\.chanel\.com/[^ ]+\.jpg)', product_image_sizes)
                            for url in urls:
                                if url.rfind("/w_1092/") != -1:
                                    website_images.append("http://" + url[2:])
                all_website_images.append(website_images)
                count += 1
            except urllib.error.HTTPError as e:
                print(e)
                page_exists = False
        return all_website_images

    def fetch_louis_vuitton_pages(self, website):
        count = 0
        louis_vuitton_images_pages = list()
        page_dne = True

        while (count <= self.website_category_limit) and page_dne:
            print("Page:", count)
            original_website = website
            try:
                original_website += f"?page={count}"
                print(f"Fetching: {original_website}")

                req = requests.get(original_website, headers=self.website_headers)
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
                # TODO: Remove
                if count == 2:
                    break
            #     ------
            except urllib.error.HTTPError as e:
                print(e)
                page_dne = False
        return louis_vuitton_images_pages


# In[18]:


class ImageAnalysis:
    def __init__(self, directory):
        self.directory = directory
        self.image_directory = os.path.join(directory, "images")
        self.readme_images = os.path.join(directory, 'readme_images')
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

    def rgb_to_hex(self, r, g, b):
        hex_value = ('#%02x%02x%02x' % (r, g, b))
        return hex_value

    # TODO: working on this currently.
    def graph_rgb_spectrogram(self, rgb_with_frequency):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        yticks = [2, 1, 0]

        bar_width = 0.5  # You can adjust this value as needed

        for rgb_colors, frequencies in rgb_with_frequency:
            r_value = rgb_colors[0]
            g_value = rgb_colors[1]
            b_value = rgb_colors[2]

            # Plotting bar graph red
            ax.bar3d(r_value, yticks[0], 0, bar_width, bar_width, frequencies, shade=True,
                     color=self.rgb_to_hex(r_value, 0, 0))

            # Plotting bar graph green
            ax.bar3d(g_value, yticks[1], 0, bar_width, bar_width, frequencies, shade=True,
                     color=self.rgb_to_hex(0, g_value, 0))

            # Plotting bar graph blue
            ax.bar3d(b_value, yticks[2], 0, bar_width, bar_width, frequencies, shade=True,
                     color=self.rgb_to_hex(0, 0, b_value))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # On the y-axis let's only label the discrete values that we have data for.
        ax.set_yticks(yticks)

        ax.view_init(elev=60, azim=-45)
        save_location = os.path.join(self.readme_images, 'rgb_3d_bar_graph.png')
        plt.savefig(save_location, dpi=600)

        plt.show()

    def graph_3d_rgb_frequency(self, rgb_with_frequency):
        rgb_colors, frequencies = zip(*rgb_with_frequency)
        r_values = [color[0] for color in rgb_colors]
        g_values = [color[1] for color in rgb_colors]
        b_values = [color[2] for color in rgb_colors]

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        # Convert RGB colors to hexadecimal notation
        hex_colors = ['#%02x%02x%02x' % color for color in rgb_colors]

        max_size = 199
        color_sizes = [(num - 1) / max_size for num in frequencies]

        ax.scatter(r_values, g_values, b_values, c=hex_colors, marker='o', s=[color_size for color_size in color_sizes],
                   alpha=0.7)

        ax.set_xlabel('(X) Red 0-255')
        ax.set_ylabel('(Y) Green 0-255')
        ax.set_zlabel('(Z) Blue 0-255')

        ax = plt.gca()
        ax.set_ylim(ax.get_ylim()[::-1])

        ax.view_init(elev=70, azim=-45)
        save_location = os.path.join(self.readme_images, 'rgb_scatter_plot_1.png')
        plt.savefig(save_location, dpi=600)

        ax.view_init(elev=5, azim=45)
        save_location = os.path.join(self.readme_images, 'rgb_scatter_plot_2.png')
        plt.savefig(save_location, dpi=600)

        ax.view_init(elev=90, azim=45)
        save_location = os.path.join(self.readme_images, 'rgb_scatter_plot_3.png')
        plt.savefig(save_location, dpi=600)

        name = (os.path.dirname(self.directory))
        plt.title((name + ": RGB Scatter Plot"))
        plt.show()

    def show_image(self, image_path):
        if image_path:
            plt.figure(3)
            # Assuming you have the path to the image file

            # Read the image using `mpimg.imread()`
            image = mpimg.imread(image_path)

            # Display the image using `imshow()`
            plt.imshow(image)

            # Show the plot
            plt.show()

    def get_rgb_distance(self, r1, g1, b1, r2, g2, b2):
        distance = math.sqrt(math.pow((r2 - r1), 2) + math.pow((g2 - g1), 2) + math.pow((b2 - b1), 2))
        percentage = (distance / (math.sqrt(math.pow(255, 2) + math.pow(255, 2) + math.pow(255, 2)))) * 100
        return {"distance": distance, "percentage": percentage}

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

                percentage_of_similarity = self.get_rgb_distance(r1, g1, b1, r2, g2, b2)["percentage"]

                if len(most_common_rgb) <= 10:
                    break
                else:
                    if percentage_of_similarity <= self.minimum_percentage_similarity:
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


# In[35]:


class Facade:
    def __init__(self):
        #       default variables
        self.directory = os.getcwd()
        self.image_directory = os.path.join(self.directory, "images")
        #       calling necessary classes
        self.image_web_scrapper = ImageWebScrapper(self.directory, image_limit=1000, website_category_limit=30)
        self.image_file_manager = ImageFileManager(self.directory)
        self.image_analysis = ImageAnalysis(self.directory)

    def download_website(self, url, directory_special_name=""):
        # Gets a list of image urls within the website.
        domain = ('.'.join((urlparse(url).netloc).split('.')[-2:]))

        print(f"Scrapping {domain} for images.")
        if domain == "louisvuitton.com":
            pages = self.image_web_scrapper.fetch_louis_vuitton_pages(url)
        elif domain == "chanel.com":
            pages = self.image_web_scrapper.fetch_chanel_pages(url)
        else:
            print("Program has not been designed yet for this website.")
            return None

        # print(pages)

        # Iterating through each page to download the image.
        for page in pages:
            self.image_web_scrapper.download_images(domain, page, directory_special_name, amount_of_pages=len(pages))

    def analyze_all_images(self, analyze_directory="louisvuitton.com"):
        # directory to analyze`
        louis_vuitton_dir = os.path.join(self.image_directory, analyze_directory)
        files = self.image_file_manager.get_files_list(louis_vuitton_dir)

        all_images_rgb_count = list()
        for count, file in enumerate(files):
            print(f"Analyzing file {(count + 1)} out of {len(files)}")
            file_path = os.path.join(louis_vuitton_dir, file)
            image = self.image_analysis.file_to_image(file_path)
            colors = self.image_analysis.image_main_colors(image)
            most_common_colors = self.image_analysis.image_most_common_colors(colors)
            all_images_rgb_count += most_common_colors

            # if count <= 20:
            #     break

        # self.image_analysis.plot_rgb_scatter_with_frequency(all_images_rgb_count)
        # self.image_analysis.graph_3d_rgb_frequency(all_images_rgb_count)
        self.image_analysis.graph_rgb_spectrogram(all_images_rgb_count)


# In[34]:


if __name__ == "__main__":
    facade = Facade()

    # website_url = "https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/_/N-tfr7qdp"
    # facade.download_website(website_url, directory_special_name="-handbags")
    # facade.analyze_all_images("louisvuitton.com-handbags")

    website_url = "https://www.chanel.com/gb/fashion/handbags/c/1x1x1x4/hobo-bags/"
    # facade.download_website(website_url, directory_special_name="-handbags")
    facade.analyze_all_images("chanel.com-handbags")
