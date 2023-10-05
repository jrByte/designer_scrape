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
import cv2
from bs4 import BeautifulSoup
import matplotlib.image as mpimg
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from urllib.parse import urlparse


class ImageFileManager:
    def __init__(self, directory):
        self.image_directory = os.path.join(directory, "images")
        self.csv_directory = os.path.join(directory, "csv")

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

    def save_data_to_csv(self, data, csv_name, column_names):
        file_path = os.path.join(self.csv_directory, csv_name)
        with open(file_path, "w", newline="") as open_csv_file:
            wr = csv.DictWriter(open_csv_file, fieldnames=column_names)
            wr.writeheader()

            # Write the data rows
            for rgb, count in data:
                red, green, blue = rgb
                wr.writerow({"Red": red, "Green": green, "Blue": blue, "Count": count})

            open_csv_file.close()
        print(f"CSV data saved to {file_path}")

    def image_transparency_test(self, directory):
        result = True
        for file in os.listdir(directory):
            with Image.open(os.path.join(directory, file)) as image:
                image_data = np.array(image)
                h, w, c = image_data.shape
                if c == 4:
                    print(f"Image Transparent [TRUE]: {file}")
                else:
                    print(f"Image Transparent [FALSE]: {file}")
                    result = False
        return result


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
            # print("Fetching Image:", self.image_count, domain)
            delay = random.randint(0, 2)
            time.sleep(delay)
            # print(f"Delaying Fetch by {delay} seconds.")
            # print("URL: ", url)
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
        image_sizes_count = dict()
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

                # print(f"Website: {website_with_endpoint}\nImage Count: [{len(website_items)}]")
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
                                # if url.rfind("/w_1092/") != -1:
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

                            # print(f"URL http://[{urls[0][2:]}]: {url_size}")

                all_website_images.append(website_images)
                # print(all_website_images)
                count += 1
            except urllib.error.HTTPError as e:
                print(e)
                page_exists = False

            # print(image_sizes_count)
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

            #     ------
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
        hex_value = ('#%02x%02x%02x' % (r, g, b))
        return hex_value

    def color_distance(self, rgb_1, rgb_2):
        return round(math.sqrt(sum((x - y) ** 2 for x, y in zip(rgb_1, rgb_2))), 1)

    def color_analysis(self, rgb_data):
        r,g,b = rgb_data[0], rgb_data[1], rgb_data[2]
        h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)

        complementary_result = 255-r, 255-g, 255-b

        monochromatic_result = [(int(r*i), int(g*i), int(b*i)) for i in [0.25, 0.5, 0.75]]

        analogous_result = [(int(r*255), int(g*255), int(b*255)) for r, g, b in [colorsys.hls_to_rgb((h + i/360.0) % 1, l, s) for i in [-30, 30]]]

        split_complementary_result = [(int(r*255), int(g*255), int(b*255)) for r, g, b in [colorsys.hls_to_rgb((h + i/360.0) % 1, l, s) for i in [-150, 150]]]

        triadic_result = [(int(r*255), int(g*255), int(b*255)) for r, g, b in [colorsys.hls_to_rgb((h + i/360.0) % 1, l, s) for i in [-120, 120]]]

        tetradic_result = [(int(r*255), int(g*255), int(b*255))for r, g, b in [colorsys.hls_to_rgb((h + i/360.0) % 1, l, s) for i in [90, 180, 270]]]

        results = {
            "Complementary": complementary_result,
            "Monochromatic": monochromatic_result,
            "Analogous": analogous_result,
            "Split Complementary": split_complementary_result,
            "Triadic": triadic_result,
            "Tetradic": tetradic_result
            }

        return results


    def graph_rgb_spectrogram(self, rgb_with_frequency, file_name):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        yticks = [2, 1, 0]

        bar_width = 0.5  # You can adjust this value as needed

        rgb_colors, frequencies = zip(*rgb_with_frequency)
        max_value = max(frequencies)
        scaled_frequencies = [(value / max_value) * 100 for value in frequencies]

        for index, rgb_colors in enumerate(rgb_colors):
            r_value = rgb_colors[0]
            g_value = rgb_colors[1]
            b_value = rgb_colors[2]

            # Plotting bar graph red
            ax.bar3d(r_value, yticks[0], 0, bar_width, bar_width, scaled_frequencies[index], shade=True,
                     color=self.rgb_to_hex(r_value, 0, 0))

            # Plotting bar graph green
            ax.bar3d(g_value, yticks[1], 0, bar_width, bar_width, scaled_frequencies[index], shade=True,
                     color=self.rgb_to_hex(0, g_value, 0))

            # Plotting bar graph blue
            ax.bar3d(b_value, yticks[2], 0, bar_width, bar_width, scaled_frequencies[index], shade=True,
                     color=self.rgb_to_hex(0, 0, b_value))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # On the y-axis let's only label the discrete values that we have data for.
        ax.set_yticks(yticks)

        ax.view_init(elev=25, azim=108)
        save_location = os.path.join(self.readme_images, f'{file_name}_rgb_3d_bar_graph.png')
        plt.savefig(save_location, dpi=600)

        # plt.show()

    def graph_3d_rgb_frequency(self, rgb_with_frequency, file_name):
        rgb_colors, frequencies = zip(*rgb_with_frequency)
        r_values = [color[0] for color in rgb_colors]
        g_values = [color[1] for color in rgb_colors]
        b_values = [color[2] for color in rgb_colors]

        max_value = max(frequencies)
        scaled_numbers = [(value / max_value) * 200 for value in frequencies]

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        # Convert RGB colors to hexadecimal notation
        hex_colors = ['#%02x%02x%02x' % color for color in rgb_colors]

        ax.scatter(r_values, g_values, b_values, c=hex_colors, marker='o',
                   s=[color_size for color_size in scaled_numbers],
                   alpha=0.7)

        ax.set_xlabel('(X) Red 0-255')
        ax.set_ylabel('(Y) Green 0-255')
        ax.set_zlabel('(Z) Blue 0-255')

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

    def file_to_image(self, file_path):
        with Image.open(file_path).convert('RGB') as image:
            return image
        # return cv2.imread(file_path)

    def image_main_colors(self, image):
        by_color = defaultdict(int)

        for pixel in image.getdata():
            if pixel != (0, 0, 0) and pixel != (255, 255, 255) and pixel != (76, 105, 113):
                by_color[pixel] += 1

        return by_color


class Facade:
    def __init__(self):
        #       default variables
        self.directory = os.getcwd()
        self.image_directory = os.path.join(self.directory, "images")
        #       calling necessary classes
        self.image_web_scrapper = ImageWebScrapper(self.directory, image_limit=1000, website_category_limit=30)
        self.image_file_manager = ImageFileManager(self.directory)
        self.image_analysis = ImageAnalysis(self.directory, 0)

    def download_website(self, url, directory_special_name=""):
        # Gets a list of image urls within the website.
        domain = ('.'.join(urlparse(url).netloc.split('.')[-2:]))

        print(f"Scrapping {domain} for images.")
        if domain == "louisvuitton.com":
            pages = self.image_web_scrapper.fetch_louis_vuitton_pages(url)
        elif domain == "chanel.com":
            pages = self.image_web_scrapper.fetch_chanel_pages(url)
        else:
            print("Program has not been designed yet for this website.")
            return None

        # Iterating through each page to download the image.
        for page_count, page in enumerate(pages):
            print(f"[...]: Website [{domain}] :{page_count + 1} / {len(pages)}")
            self.image_web_scrapper.download_images(domain, page, directory_special_name, amount_of_pages=len(pages))

    def analyze_all_images(self, analyze_directory, image_sensitivity=25):
        # directory to analyze`
        designer_dir = os.path.join(self.image_directory, analyze_directory)
        files = self.image_file_manager.get_files_list(designer_dir)
        color_count_detection = Counter()
        all_images_rgb_count = list()

        for count, file in enumerate(files):
            print(f"\nAnalyzing file [{file}] {(count + 1)} out of {len(files)}")
            file_path = os.path.join(designer_dir, file)

            image = self.image_analysis.file_to_image(file_path)
            colors = self.image_analysis.image_main_colors(image)
            most_common_colors = Counter(colors).most_common(image_sensitivity)
            all_images_rgb_count += most_common_colors

            # analytics
            main_color = Counter(colors).most_common(1)
            results = self.image_analysis.color_analysis(main_color[0][0])

            print("\nSingle Image Data Analytics:")
            print(f"Most Common Color of the image: {main_color[0][0]}, count: {main_color[0][1]}")
            [print(f"{key}: {value}") for key, value in results.items()]

            noteable_values = []
            most_common_colors.remove(main_color[0])

            for image_top_colors in most_common_colors:
                # print("-----------------------------")
                # print("New top color compared: ", image_top_colors)

                closest_distance = 25
                max = closest_distance

                # if image_top_colors[0] == (255, 0, 0) or image_top_colors[0] == (0, 255, 0) or image_top_colors[0] == (0, 0, 255):


                for key, primary_analyzed_colors in results.items():
                    # print(f"Data Analytics: {key}", end=" ")
                    comparison = None
                    d = None

                    if len(primary_analyzed_colors) == 1 or type(primary_analyzed_colors) == tuple:
                        d = self.image_analysis.color_distance(image_top_colors[0], primary_analyzed_colors)
                        comparison = {"image_top_color": image_top_colors[0], "analyzed_color": primary_analyzed_colors, "distance": d}

                        # print(image_top_colors, " : ", primary_analyzed_colors, " distance: ", d, end=" ")

                    else:
                        for index, analyzed_color in enumerate(primary_analyzed_colors):
                            d = self.image_analysis.color_distance(image_top_colors[0], analyzed_color)
                            comparison = {"image_top_color": image_top_colors[0], "analyzed_color": analyzed_color, "distance": d}
                            # print(image_top_colors, " : ", analyzed_color, " distance: ", d, end=" ")

                    if 0 < d <= max and (closest_distance <= d ):
                        noteable_values.append({key: comparison})
                        closest_distance = d

            for i in noteable_values:
                for key in i.keys():
                    color_count_detection[str(key)] += 1

            if noteable_values:
                print("Detected color schema:", noteable_values)

            # if count <= 1:
            #     break

        print()
        self.image_file_manager.save_data_to_csv(all_images_rgb_count, analyze_directory,
                                                 ["Red", "Green", "Blue", "Count"])

        self.image_analysis.graph_3d_rgb_frequency(all_images_rgb_count, analyze_directory)
        self.image_analysis.graph_rgb_spectrogram(all_images_rgb_count, analyze_directory)

        print("\nTotal Image Collection Analysis:")
        total = len(files)
        for color_scheme, count in color_count_detection.items():
            print(f"{color_scheme}: {round((count / len(files)) * 100, 2)}% ({count} / {len(files)})")
            total -= count

        print(f"Remaining images with undetected color schemes: {round((total / len(files)) * 100, 2)}%")

        # TODO PIE PLOT
        # self.image_analysis.plot_rgb_scatter_with_frequency(all_images_rgb_count)


if __name__ == "__main__":
    facade = Facade()

    # website_url = "https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/_/N-tfr7qdp"
    # facade.download_website(website_url, directory_special_name="-handbags")
    # facade.analyze_all_images("louisvuitton.com-handbags")

    website_url = "https://www.chanel.com/gb/fashion/handbags/c/1x1x1x4/hobo-bags/"
    # facade.download_website(website_url, directory_special_name="-handbags")
    # facade.analyze_all_images("chanel.com-handbags", image_sensitivity=10)
    facade.analyze_all_images("louisvuitton.com-handbags", image_sensitivity=10)
