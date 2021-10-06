import math
from PIL import Image
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import matplotlib.pyplot as plt


class image_identifier:
    def __init__(self):
        self.by_color = defaultdict(int)
        self.sorted_colors = None

    @staticmethod
    def rgb_to_hex(rgb_list):
        hex_list = list()
        for rgb in rgb_list:
            rgb = eval(rgb)
            hex_value = ('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2]))
            hex_list.append(hex_value)
        return hex_list

    def pie_chart(self):
        if self.sorted_colors:
            labels = list()
            sizes = list()
            for color in self.sorted_colors:
                labels.append(str(color[0]))
                sizes.append(color[1])
            plt.pie(sizes, labels=labels, labeldistance=1.15, colors=self.rgb_to_hex(labels))
            plt.show()
        else:
            raise "Must call get_image_main_colors() first before calling pie_chart()"

    def most_common_colors(self, most_common=300, minimum_percentage_similarity=2):
        most_common_rgb = Counter(self.by_color).most_common(most_common)
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

                if percentage <= minimum_percentage_similarity:
                    if common_rgb_clone[rgb_index2] in most_common_rgb:
                        most_common_rgb.remove(common_rgb_clone[rgb_index2])

        return most_common_rgb

    def get_image_main_colors(self, image):
        self.by_color = defaultdict(int)
        for pixel in image.getdata():
            self.by_color[pixel] += 1
        self.sorted_colors = self.most_common_colors()
        return self.sorted_colors


class file_manager(image_identifier):
    def __init__(self, designer_directory):
        super().__init__()
        self.designer_directory = designer_directory

    @staticmethod
    def get_files_list(directory):
        print("Directory:", directory)
        files = list()
        for a in os.listdir(directory):
            files.append(a)
        return files

    def get_image(self, directory, files):
        for file_name in files:
            with Image.open(f'{directory}/{file_name}') as image:
                self.get_image_main_colors(image)

    def get_designer_images(self):
        self.get_image(self.designer_directory, self.get_files_list(self.designer_directory))


class image_scrape(file_manager):
    def __init__(self, designer_directory):
        super().__init__(designer_directory)
        self.website = 'https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/_/N-1ifgts8'

    # TODO: USE VPN, create reliable method to fetch all images.
    def fetch_images(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        url = self.website
        req = Request(url, headers=headers)
        response = urlopen(req).read()
        soup = BeautifulSoup(response, "html.parser", from_encoding="gzip")
        soup_images = soup.find_all('img', {"class": 'lv-smart-picture__object'})

        for url in soup_images:
            image_sources = url.get('data-srcset')
            # designer_images = (image_sources.split(','), '\n')


if __name__ == "__main__":
    fm = file_manager(designer_directory="C:/Users/Jonas Reynolds/Desktop/Github/designer_scrape/designer_images")
    fm.get_designer_images()
    fm.pie_chart()
