"""
For the Win students should pass the tests for this file.
"""
import pytest
import file_clerk.clerk as clerk
from webcode_tk import html_tools as html
from webcode_tk import css_tools as css

project_dir = "project/"

styles_by_files = css.get_styles_by_html_files(project_dir)
html_files = html.get_all_html_files(project_dir)


def get_google_font_report(styles, min=1, max=2) -> str:
    """determines if the page is using the min number of google fonts

    We're looking for three things in each web page: 
    1) a link in the head to the googlefonts API, 
    2) each of those fonts being applied, and 
    3) at least the minimum number of unique Google fonts and no more than the
       max #.

    Args:
        styles: a list of files with the stylesheets they use
        min: minimum number of Google font families in use
        max: maximum number of Google font families in use
    
    Returns:
        report: a pass/fail report with accompanying data
    """

    # Loop through all HTML docs and their styles
    report = []

    for data in styles:
        
        # Step 1: get all linked Google fonts
        file = data.get("file")
        filename = clerk.get_file_name(file)
        links = html.get_elements("link", file)
        google_fonts_linked = []

        for link in links:
            href = link.attrs.get("href")
            if "fonts.googleapis.com" in href and href != 'https://fonts.googleapis.com':
                google_fonts_linked = get_google_font_data(href)

        # Check to see the linked fonts match required number.
        num_fonts = len(google_fonts_linked)
        if num_fonts < min:
            data = f"fail: {filename} does not link to min number of Google "
            data += "fonts."
            report.append(data)
            continue

        # if we have any google fonts, are they being used?
        stylesheets = data.get("stylesheets")
        fonts_used = []
        for sheet in stylesheets:
            font_data = css.get_font_families(sheet)
            if font_data:
                families = extract_families(font_data)
        if families:
            for family in google_fonts_linked:
                if family in families:
                    if family not in fonts_used:
                        fonts_used.append(family)
        num_used = len(fonts_used)
        if num_used >= min and num_used <= max:
            data = f"pass: {filename} uses the correct number of Google fonts"
            report.append(data)
    return report


def extract_families(family_data: list) -> list:
    families = []
    for datum in family_data:
        family_value = datum.get("family")
        family = family_value.split(",")[0]
        family = family.strip()
        family = family.replace('"', "")
        families.append(family)
    return families

def get_google_font_data(href: str) -> list:
    font_families = []
    font_data = href.split("family=")
    font_data.pop(0)
    for item in font_data:
        family = item.split(":")[0]
        family = family.replace("+", " ")
        font_families.append(family)
    return font_families

def get_elements_in_project(project_dir: str, min_required: list):
    element_results = []
    for element, expected_number in min_required:
        if "or" in element:
            elements = element.split("or")
            actual_number = 0
            for el in elements:
                actual_number += html.get_num_elements_in_folder(el.strip(),
                                                                 project_dir)
            element_results.append((element, expected_number, actual_number))
        else:
            actual_number = html.get_num_elements_in_folder(element,
                                                            project_dir)
            element_results.append((element, expected_number, actual_number))
    return element_results


min_required_elements = [
    ("h2", 3),
    ("p", 8),
    ("a", 5),
    ("br", 2),
    ("ul or ol", 3),
    ("li", 12),
    ("img", 4),
    ("figure", 4),
    ("figcaption", 4)]

min_number_of_elements = get_elements_in_project(project_dir,
                                                 min_required_elements)


@pytest.mark.parametrize("element,expected,actual", min_number_of_elements)
def test_files_for_exceeds_minimum_number_of_elements(element,
                                                      expected,
                                                      actual):
    expected_result = f"pass: there are at least {expected} <{element}> tags."
    if actual >= expected:
        actual_results = expected_result
    else:
        more = expected - actual
        actual_results = f"fail: your project needs {more} more <{element}>"
        actual_results += " tag/s to pass."
    assert actual_results == expected_result


def test_for_html_exceeds_number_of_image_files():
    image_files = []
    image_files += clerk.get_all_files_of_type(project_dir, "jpg")
    image_files += clerk.get_all_files_of_type(project_dir, "png")
    image_files += clerk.get_all_files_of_type(project_dir, "gif")
    image_files += clerk.get_all_files_of_type(project_dir, "webp")
    assert len(image_files) >= 3


if __name__ == '__main__':
    uses_gf = get_google_font_report(styles_by_files, 2)
    print(uses_gf)