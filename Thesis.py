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
import colorsys

from PIL import Image
import os
import csv
import requests
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from sklearn.cluster import KMeans


class ImageFileManager:
    def __init__(self, directory):
        self.image_directory = os.path.join(directory, "images")
        self.csv_directory = os.path.join(directory, "csv")

    def get_files_list(self, directory):
        print("Running get_files_list")
        files = list()
        if not os.path.isdir(directory):
            os.makedirs(directory)
        for a in os.listdir(directory):
            files.append(a)
        return files

    def save_data_to_csv(self, data, csv_name, column_names):
        full_file_path = os.path.join(self.csv_directory, csv_name)
        with open(full_file_path, "w", newline="") as open_csv_file:
            wr = csv.DictWriter(open_csv_file, fieldnames=column_names)
            wr.writeheader()
            for rgb, count in data:
                red, green, blue = rgb
                wr.writerow({"Red": red, "Green": green, "Blue": blue, "Count": count})

            open_csv_file.close()
        print(f"CSV data saved to {full_file_path}")

    def read_csv_to_data(self, csv_name):
        # TODO: Correct the structure the csv is saved to a python data type.
        full_file_path = os.path.join(self.csv_directory, csv_name)
        with open(full_file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                print(row)
        # return data


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
        domain = domain + directory_special_name
        directory = os.path.join(self.image_directory, domain)
        if not os.path.exists(directory):
            os.makedirs(directory)

        os.chmod(directory, 0o755)

        files = list()
        for a in os.listdir(directory):
            files.append(a)
        file_name_iteration = len(files)

        for count, url in enumerate(url_images):
            delay = random.randint(1, 3)
            time.sleep(delay)
            response = requests.get(url, headers=self.website_headers)
            if response.status_code == 200:
                file_location = os.path.join(directory, f"{file_name_iteration}.png")
                with open(file_location, 'wb') as f:
                    f.write(response.content)
                    file_name_iteration += 1
                    self.image_count += 1
                    f.close()

                os.chmod(file_location, 0o755)

    def fetch_chanel_pages(self, website):
        count = 1

        all_website_images = list()
        page_exists = True
        image_duplicate_check = list()

        while (count <= self.website_category_limit) and page_exists:
            website_images = list()
            try:
                website_with_endpoint = website + f"page-{count}/"
                req = requests.get(website_with_endpoint, headers=self.website_headers)

                soup = BeautifulSoup(req.text, "html.parser", from_encoding="gzip")
                website_items = soup.find_all('div', {"class": 'product-grid__item js-product-edito fs-gridelement'})

                if len(website_items) == 0:
                    page_exists = False

                image_sizes_count = {}
                for website_image_count, images_in_website_items in enumerate(website_items):
                    images = images_in_website_items.find_all('picture', {"class": 'fs-element--inline'})
                    for image_count, image in enumerate(images):
                        source_tag = image.find('source')
                        if source_tag and 'srcset' in source_tag.attrs:
                            product_image_sizes = source_tag["srcset"]
                            urls = re.findall(r'(//www\.chanel\.com/[^ ]+\.jpg)', product_image_sizes)

                            url_size = []

                            for url in urls:
                                url_split = url.split("/")
                                size = (url_split[5][2:])
                                id = url_split[6][:url_split[6].rfind("-")]

                                url_size.append(size)

                                if size in image_sizes_count:
                                    image_sizes_count[size] += 1
                                else:
                                    image_sizes_count[size] = 1

                                if int(size) >= 1000 and not (id in image_duplicate_check):
                                    image_duplicate_check.append(id)
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
            except urllib.error.HTTPError as e:
                print(e)
                page_dne = False
        return louis_vuitton_images_pages


class ImageAnalysis:
    def __init__(self, directory, minimum_percentage_similarity):
        self.directory = directory
        self.image_directory = os.path.join(directory, "images")
        self.readme_images = os.path.join(directory, 'readme_images')
        self.minimum_percentage_similarity = minimum_percentage_similarity

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
        return '#%02x%02x%02x' % (r, g, b)

    def color_distance(self, rgb_1, rgb_2):
        distance = 0
        for x, y in zip(rgb_1, rgb_2):
            distance += (x - y) ** 2
        return round(math.sqrt(distance), 2)

    def color_analysis(self, data):
        r, g, b = zip(*data)
        simplified_r, simplified_g, simplified_b = (r / 255.0, g / 255.0, b / 255.0)
        h, l, s = colorsys.rgb_to_hls(simplified_r, simplified_g, simplified_b)
        triadic_result = []
        tetradic_result = []
        monochro_result = []
        analogous_result = []
        s_complementary_result = []

        complementary_result = (255 - r), (255 - g), (255 - b)

        for percentage in [(1 / 4), (1 / 2), (3 / 4)]:
            monochro_result.append((int(r * percentage), int(g * percentage), int(b * percentage)))

        for degree in [-30, 30]:
            adjusted_hue_for_color = ((h + degree) / 360)
            r, g, b = colorsys.hls_to_rgb(adjusted_hue_for_color, l, s)
            analogous_result.append(((r * 255), (g * 255), (b * 255)))

        for degree in [-150, 150]:
            adjusted_hue_for_color = ((h + degree) / 360)
            r, g, b = colorsys.hls_to_rgb(adjusted_hue_for_color, l, s)
            s_complementary_result.append(((r * 255), (g * 255), (b * 255)))

        for degree in [-120, 120]:
            adjusted_hue_for_color = ((h + degree) / 360)
            r, g, b = colorsys.hls_to_rgb(adjusted_hue_for_color, l, s)
            triadic_result.append(((r * 255), (g * 255), (b * 255)))

        for degree in [90, 180, 270]:
            adjusted_hue_for_color = ((h + degree) / 360)
            r, g, b = colorsys.hls_to_rgb(adjusted_hue_for_color, l, s)
            tetradic_result.append(((r * 255), (g * 255), (b * 255)))

        results = {
            "Complementary": complementary_result,
            "Monochromatic": monochro_result,
            "Analogous": analogous_result,
            "Split Complementary": s_complementary_result,
            "Triadic": triadic_result,
            "Tetradic": tetradic_result
        }

        return results

    def pie_chart(self, rgb_with_frequency, file_name):
        rgb_colors, frequencies = zip(*sorted(rgb_with_frequency))

        # Convert RGB to hex and sort them
        sorted_hex = []
        sorted_hex_legend = []
        for count, (r, g, b) in enumerate(rgb_colors):
            sorted_hex.append(self.rgb_to_hex(r, g, b))
            if len(sorted_hex_legend) < 10:
                sorted_hex_legend.append(
                    f"{self.rgb_to_hex(r, g, b)} : {round(frequencies[count] / sum(frequencies), 2) * 100}%")

        # Create a new figure and axes (2D)
        fig, ax = plt.subplots()

        # Plotting using the ax object
        ax.pie(frequencies, startangle=90, colors=sorted_hex)
        ax.legend(sorted_hex_legend, loc='center left', fontsize=7, bbox_to_anchor=(1, 0.5))

        save_location = os.path.join(self.readme_images, f'{file_name}_pie_chart.png')
        plt.savefig(save_location, dpi=600)

    def graph_rgb_spectrogram(self, rgb_with_frequency, file_name):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        yticks = [2, 1, 0]

        bar_width = 0.5  # You can adjust this value as needed

        rgb_colors, frequencies = zip(*rgb_with_frequency)
        total_value = sum(frequencies)
        scaled_frequencies = [(value / total_value) * 100 for value in frequencies]

        for index, rgb_colors in enumerate(rgb_colors):
            r_value = rgb_colors[0]
            g_value = rgb_colors[1]
            b_value = rgb_colors[2]

            hex_color_r = self.rgb_to_hex(0, 0, b_value)
            hex_color_g = self.rgb_to_hex(0, g_value, 0)
            hex_color_b = self.rgb_to_hex(r_value, 0, 0)

            # Plotting bar graph red
            ax.bar3d(r_value, 2, 0, 0.5, 0.5, scaled_frequencies[index], shade=True,
                     color=hex_color_r)
            # Plotting bar graph green
            ax.bar3d(g_value, 1, 0, 0.5, 0.5, scaled_frequencies[index], shade=True,
                     color=hex_color_g)
            # Plotting bar graph blue
            ax.bar3d(b_value, 0, 0, 0.5, 0.5, scaled_frequencies[index], shade=True,
                     color=hex_color_b)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # On the y-axis let's only label the discrete values that we have data for.
        ax.set_yticks(yticks)

        ax.view_init(elev=25, azim=108)
        save_location = os.path.join(self.readme_images, f'{file_name}_rgb_3d_bar_graph.png')
        plt.savefig(save_location, dpi=600)

    def graph_3d_rgb_frequency(self, rgb_with_frequency, file_name):
        rgb_colors, frequencies = zip(*rgb_with_frequency)
        r_values = [color[0] for color in rgb_colors]
        g_values = [color[1] for color in rgb_colors]
        b_values = [color[2] for color in rgb_colors]

        max_value = max(frequencies)
        scaled_numbers = [(value / max_value) * 200 for value in frequencies]

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        hex_colors = []
        for c in rgb_colors:
            hex_colors.append(self.rgb_to_hex(c))

        ax.scatter(r_values, g_values, b_values, c=hex_colors, marker='o',
                   s=[color_size for color_size in scaled_numbers],
                   alpha=0.7)

        ax.set_xlabel('(x-axis) Red')
        ax.set_ylabel('(y-axis) Green')
        ax.set_zlabel('(z-axis) Blue')

        ax = plt.gca()
        ax.set_ylim(ax.get_ylim()[::-1])

        ax.view_init(elev=70, azim=-45)
        save_location = os.path.join(self.readme_images, f'{file_name}_rgb_scatter_plot_1.png')
        plt.savefig(save_location, dpi=600)

        ax.view_init(elev=5, azim=45)
        save_location = os.path.join(self.readme_images, f'{file_name}_rgb_scatter_plot_2.png')
        plt.savefig(save_location, dpi=600)

        ax.view_init(elev=90, azim=45)
        save_location = os.path.join(self.readme_images, f'{file_name}_rgb_scatter_plot_3.png')
        plt.savefig(save_location, dpi=600)

        name = (os.path.dirname(self.directory))
        plt.title((name + ": RGB Scatter Plot"))
        # plt.show()

    def file_to_image(self, file_path):
        with Image.open(file_path).convert('RGB') as image:
            return image
        # return cv2.imread(file_path)

    def image_main_colors(self, image):
        by_color = defaultdict(int)

        for pixel in image.getdata():
            if pixel not in [(0, 0, 0), (255, 255, 255), (76, 105, 113)]:
                by_color[pixel] += 1

        return by_color

    def find_common_colors(self, color, k_sensitivity):
        np_points = np.array([list(k) + [v] for k, v in color.items()])
        colors = np_points[:, :3]
        frequencies = np_points[:, 3]

        # Applying KMeans clustering
        kmeans = KMeans(n_clusters=k_sensitivity, random_state=0).fit(colors, sample_weight=frequencies)

        # Initializing a counter to store the summed frequencies of colors per cluster
        cluster = Counter()

        # Assign each original color to the closest representative color
        for idx, label in enumerate(kmeans.labels_):
            rgb_tuple = tuple(kmeans.cluster_centers_[label].astype(int))
            r, g, b = int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2])

            cluster[r, g, b] += int(frequencies[idx])

        return cluster


class Facade:
    def __init__(self):
        self.directory = os.getcwd()
        self.image_directory = os.path.join(self.directory, "images")
        self.image_web_scrapper = ImageWebScrapper(self.directory, image_limit=1000, website_category_limit=30)
        self.image_file_manager = ImageFileManager(self.directory)
        self.image_analysis = ImageAnalysis(self.directory, 0)

    def download_website(self, url, directory_special_name):
        """
        Downloads product images from a desired website endpoint.

        Parameters
        ----------
        url : string
            full url path to the desired webpages to be scraped.
        directory_special_name: string
            directory name for which the files should be saved to.

        Returns
        -------
        bool
            indicates if the operation was successful.
        """
        domain = ('.'.join(urlparse(url).netloc.split('.')[-2:]))
        print(f"Scrapping {domain} for images.")
        if domain == "louisvuitton.com":
            pages = self.image_web_scrapper.fetch_louis_vuitton_pages(url)
        elif domain == "chanel.com":
            pages = self.image_web_scrapper.fetch_chanel_pages(url)
        else:
            print("Program has not been designed yet for this website.")
            return False

        # 2. Downloads all the collected URLS and saves them in the
        # images directories under the domain-name + special name.
        for page_count, page in enumerate(pages):
            print(f"[...]: Website [{domain}] :{page_count + 1} / {len(pages)}")
            self.image_web_scrapper.download_images(domain, page, directory_special_name, amount_of_pages=len(pages))

        return True

    def analyze_from_csv(self, csv_name):
        # TODO: read_csv_to_data function needs to return the array in the same format as when its saved.
        all_images_rgb_count = None
        # all_images_rgb_count = self.image_file_manager.read_csv_to_data(csv_name)
        self.image_analysis.graph_rgb_spectrogram(all_images_rgb_count, csv_name)

    def singular_image_analysis(self, file_path, k_image_sensitivity=10):
        """
        Analysis of a singular image.

        Parameters
        ----------
        file_path : string
            (required) the full path of the file.
        k_image_sensitivity: int
            (not required) defines the amount of neighbors for the k-nearest alg.
        Returns
        -------
        result : formatted string
            Describes the color pallets discovered.
        """

        image = self.image_analysis.file_to_image(file_path)
        colors = self.image_analysis.image_main_colors(image)

        # uses k-nearest neighbor machine learning algorithm to get the top colors.
        most_common_colors = self.image_analysis.find_common_colors(colors, k_image_sensitivity)
        results = self.image_analysis.color_analysis(most_common_colors[0][0])
        return f"Calculated Color Scheme from {most_common_colors[0][0]}: {results}"

    def analyze_all_images(self, analyze_directory, k_image_sensitivity=10):
        """

        Parameters
        ----------
        analyze_directory : string
            (required) the full path to the directory for the images that are desired to be analyzed.
        k_image_sensitivity : int
            (not required) defines the amount of neighbors for the k-nearest alg.

        Returns
        -------
        result : formatted string
            Describes the color pallets discovered.
        """

        # 1. initialization of variables.
        global top_main_color
        all_images_rgb_count = list()

        # 2. gets the files list. Preparing for analysis...
        designer_dir = os.path.join(self.image_directory, analyze_directory)
        files = self.image_file_manager.get_files_list(designer_dir)

        # 3. Iterating through each file and analysing its properties.
        for count, file in enumerate(files):
            print(f"\nAnalyzing file [{file}] {(count + 1)} out of {len(files)}")
            file_path = os.path.join(designer_dir, file)

            image = self.image_analysis.file_to_image(file_path)
            colors = self.image_analysis.image_main_colors(image)

            # 4. Uses k-nearest neighbor machine learning algorithm to get the top colors.
            most_common_colors = self.image_analysis.find_common_colors(colors, k_image_sensitivity)
            all_images_rgb_count += most_common_colors

            results = self.image_analysis.color_analysis(most_common_colors[0][0])

        file_name = analyze_directory
        self.image_file_manager.save_data_to_csv(all_images_rgb_count, file_name,
                                                 ["Red", "Green", "Blue", "Count"])

        self.image_analysis.graph_3d_rgb_frequency(all_images_rgb_count, file_name)
        self.image_analysis.graph_rgb_spectrogram(all_images_rgb_count, file_name)
        self.image_analysis.pie_chart(all_images_rgb_count, file_name)

        return f"Calculated Color Scheme from {most_common_colors[0][0]}: {results}"


if __name__ == "__main__":
    facade = Facade()

    website_url = "https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/_/N-tfr7qdp"
    facade.download_website(website_url, directory_special_name="-handbags")
    # facade.analyze_all_images("louisvuitton.com-handbags")

    # website_url = "https://www.chanel.com/gb/fashion/handbags/c/1x1x1x4/hobo-bags/"
    # facade.download_website(website_url, directory_special_name="-handbags")
    # facade.analyze_all_images("chanel.com-handbags", image_sensitivity=3, max=25)
    # facade.analyze_all_images("louisvuitton.com-handbags", image_sensitivity=3, max=25)
