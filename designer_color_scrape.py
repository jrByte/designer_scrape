import math
from PIL import Image
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import matplotlib.pyplot as plt


class image_identifier:
    def __init__(self):
        pass

    @staticmethod
    def rgb_to_hex(rgb_list):
        hex_list = list()
        for rgb in rgb_list:
            rgb = eval(rgb)
            hex_value = ('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2]))
            hex_list.append(hex_value)
        return hex_list

    def pie_chart(self, sorted_colors):
        print()
        labels = list()
        sizes = list()
        for color in sorted_colors:
            print(color[0], color[1])
            labels.append(str(color[0]))
            sizes.append(color[1])

        print(labels)
        print(sizes)
        colors = self.rgb_to_hex(labels)

        plt.pie(sizes, labels=labels, labeldistance=1.15, colors=colors)

        plt.show()

    @staticmethod
    def sort_colors(by_color, most_common=200, max_keys=10):
        keys = Counter(by_color).most_common(most_common)
        minimum_percentage = 1
        # TODO: Shaders aren't removed correctly. This displays colors too similar to the others.
        while len(keys) >= max_keys:
            for index, key in enumerate(keys):
                if index + 1 < len(keys) and index - 1 >= 0:
                    r1 = keys[index][0][0]
                    g1 = keys[index][0][1]
                    b1 = keys[index][0][2]

                    r2 = keys[index + 1][0][0]
                    g2 = keys[index + 1][0][1]
                    b2 = keys[index + 1][0][2]

                    distance = math.sqrt(math.pow((r2 - r1), 2) + math.pow((g2 - g1), 2) + math.pow((b2 - b1), 2))
                    percentage = int(
                        (distance / (math.sqrt(math.pow(255, 2) + math.pow(255, 2) + math.pow(255, 2)))) * 100)

                    # print(f"{keys[index]}, {keys[index + 1]}, Difference: {percentage}%")
                    if percentage <= minimum_percentage:
                        # print(percentage, "<", minimum_percentage)
                        keys.remove(keys[index + 1])
            minimum_percentage += 1

        print(len(keys), keys)
        return keys

    def image_main_colors(self, image):
        by_color = defaultdict(int)
        for pixel in image.getdata():
            by_color[pixel] += 1

        sorted_colors = self.sort_colors(by_color)
        self.pie_chart(sorted_colors)
        return sorted_colors


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
                self.image_main_colors(image)

    def get_designer_images(self):
        print(self.get_files_list(self.designer_directory))
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
        soup_attempt2 = soup.find_all('img', {"class": 'lv-smart-picture__object'})

        for url in soup_attempt2:
            image_sources = url.get('data-srcset')
            # designer_images = (image_sources.split(','), '\n')


if __name__ == "__main__":
    fm = file_manager(designer_directory="C:/Users/Jonas Reynolds/Desktop/Github/pattern/designer_images")
    fm.get_designer_images()
    # fm.pie_chart()
