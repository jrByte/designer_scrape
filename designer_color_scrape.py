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
        hex_list = list()
        for rgb in rgb_list:
            rgb = eval(rgb)
            hex_value = ('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2]))
            hex_list.append(hex_value)
        return hex_list

    def pie_chart(self, individual_images=True):
        colors = self.sorted_colors
        if not individual_images:
            colors = self.all_sorted_colors

        if self.sorted_colors:
            labels = list()
            sizes = list()
            for color in colors:
                labels.append(str(color[0]))
                sizes.append(color[1])
            # labels=labels, labeldistance=2
            plt.pie(sizes, colors=sorted(self.rgb_to_hex(labels)))
            plt.savefig('readme_images/Louis_Vuitton_colors.PNG', bbox_inches='tight', dpi=500)
            plt.show()
        else:
            raise "Must call get_image_main_colors() first before calling pie_chart()"

    def most_common_colors(self, most_common=300):
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

    def compile_all_main_colors(self):
        for colors in self.sorted_colors:
            self.all_sorted_colors.append(colors)

    def image_main_colors(self, image):
        image = image.convert("RGB")
        self.by_color = defaultdict(int)
        for pixel in image.getdata():
            if pixel != (0, 0, 0) and pixel != (255, 255, 255):
                self.by_color[pixel] += 1
        self.sorted_colors = self.most_common_colors()
        self.compile_all_main_colors()
        return self.sorted_colors


class file_manager(image_identifier):
    def __init__(self, designer_directory, minimum_percentage_similarity):
        super().__init__(minimum_percentage_similarity)
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
                print(f"Analysing: {file_name}")
                self.image_main_colors(image)

    def get_designer_images(self):
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
        file_name = len(self.get_files_list(directory=self.designer_directory)) + 1
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
    image_s = image_scrape(designer_directory="/Users/Jonas/Desktop/GitHub/Python/designer_scrape/designer_images",
                           designer_website='https://eu.louisvuitton.com/eng-e1/women/handbags/all-handbags/_/N-1ifgts8',
                           minimum_percentage_similarity=20, image_limit=30)

    # image_s.fetch_louis_vuitton_pages()
    image_s.get_designer_images()
    image_s.pie_chart(individual_images=False)
