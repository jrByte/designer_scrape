import math
from PIL import Image
import os
import urllib
import urllib.error
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import matplotlib.pyplot as plt


class image_identifier:
    def __init__(self, minimum_percentage_similarity):
        self.by_color = defaultdict(int)
        self.sorted_colors = None
        self.all_sorted_colors = list()
        self.minimum_percentage_similarity = minimum_percentage_similarity

    @staticmethod
    def rgb_to_hex(rgb_list):
        print("Running rgb_to_hex")
        hex_list = list()
        for rgb in rgb_list:
            rgb = eval(rgb)
            hex_value = ('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2]))
            hex_list.append(hex_value)
        return hex_list

    def pie_chart(self, individual_images):
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

    def image_most_common_colors(self, most_common=300):
        """
        Called by image_main_colors. Gets all the most common colors in the image. That counts the rgb values of each
        pixel in the image. While making sure that shades of colors are not included based on a certain
        amount of similarity.

        :param most_common:
        :return: most_common_rgb: returns a Counter datatype. Of the counted rbg values in the image.
        """
        print("Running image_most_common_colors")
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

                if percentage <= self.minimum_percentage_similarity:
                    if common_rgb_clone[rgb_index2] in most_common_rgb:
                        most_common_rgb.remove(common_rgb_clone[rgb_index2])

        return most_common_rgb

    def compile_all_main_colors(self, sorted_colors):
        print("Running compile_all_main_colors")
        for colors in sorted_colors:
            self.all_sorted_colors.append(colors)

    def image_main_colors(self, image):
        """
        Called by get_image. This gets the main colors of the images besides white and black that
        come from borders of the image.

        :param image:
        :return:
        """
        print("Running image_main_colors")
        image = image.convert("RGB")
        self.by_color = defaultdict(int)

        for pixel in image.getdata():
            if pixel != (0, 0, 0) and pixel != (255, 255, 255):
                self.by_color[pixel] += 1

        sorted_colors = self.image_most_common_colors()
        self.compile_all_main_colors(sorted_colors)
        return self.sorted_colors


class file_manager(image_identifier):
    def __init__(self, designer_directory, minimum_percentage_similarity):
        super().__init__(minimum_percentage_similarity)
        self.designer_directory = designer_directory

    @staticmethod
    def get_files_list(directory):
        print("Running get_files_list")
        # print("Directory:", directory)
        files = list()
        for a in os.listdir(directory):
            files.append(a)
        return files

    def get_image(self, directory, files):
        """
        Iterates through the image files of the directory designer_images.

        :param directory:
        :param files:
        :return:
        """
        print("Running get_image")
        files = sorted(files)
        for file_name in files:
            print("\nNew File: ", file_name)
            with Image.open(f'{directory}/{file_name}') as image:
                # print(f"Analysing: {file_name}")
                self.image_main_colors(image)

    def get_designer_images(self):
        print("Running get_designer_images")
        self.get_image(self.designer_directory, self.get_files_list(self.designer_directory))


class image_scrape(file_manager):
    def __init__(self, designer_directory, designer_website, minimum_percentage_similarity, image_limit):
        super().__init__(designer_directory, minimum_percentage_similarity)
        self.website = designer_website
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        self.image_count = 0
        self.image_limit = image_limit

    # USE VPN.
    def fetch_louis_vuitton_pages(self):
        print("Running fetch_louis_vuitton_pages")
        website_copy = str(self.website)
        page_dne = True
        count = 0
        while count <= self.image_limit and page_dne:
            print("Page:", count)
            try:
                self.website += f"?page={count}"
                self.louis_vuitton_fetch_images()
                count += 1
            except urllib.error.HTTPError as e:
                print(e)
                page_dne = False

            self.website = website_copy
            if self.image_count >= self.image_limit:
                print(f"Image count reached: {self.image_limit}")
                break

    # USE VPN.
    def louis_vuitton_fetch_images(self):
        print("Running louis_vuitton_fetch_images")
        print(f"Fetching: {self.website}")
        req = Request(self.website, headers=self.headers)
        response = urlopen(req).read()
        soup = BeautifulSoup(response, "html.parser", from_encoding="gzip")
        soup_images = soup.find_all('img', {"class": 'lv-smart-picture__object'})

        clean_url_images = list()
        for url in soup_images:
            image_sources = url.get('data-srcset')
            urls = (image_sources.split(','), '\n')
            for url_records in urls:
                for url in url_records:
                    url = url[:url.rfind(" ")]
                    url = url.replace(" ", "")
                    if url.rfind("wid=1080&hei=1080") != -1:
                        clean_url_images.append(url)

        self.download_image(clean_url_images)

    def download_image(self, url_images):
        print("Running download_image")
        file_name = len(self.get_files_list(directory=self.designer_directory))
        for url in url_images:
            print("Fetching Image:", file_name)
            opener = urllib.request.build_opener()
            opener.addheaders = [
                ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, f"designer_images/{file_name}.png")
            file_name += 1
            self.image_count += 1
            if self.image_count >= self.image_limit:
                break


if __name__ == "__main__":
    image_s = image_scrape(designer_directory=str(os.path.join(os.getcwd(), "designer_images")),
                           designer_website='https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/_/N-1ifgts8',
                           minimum_percentage_similarity=20, image_limit=30)

    # image_s.fetch_louis_vuitton_pages()

    # Calls: get_files_list() -> get_image() ->
    # Loops(Running image_main_color -> Running image_most_common_colors -> Running compile_all_main_colors)
    image_s.get_designer_images()

    print("\nProgram Finished, displaying results...")

    # Calls: rgb_to_hex()
    image_s.pie_chart(individual_images=False)
