#! /usr/bin/env python3

##############################################################################
#
#   odt2anki - script that converts and odt file with questions in a table to
#   txt file that can be imported into Anki.
#
#   Author  : Eddy van den Aker
#   License : MIT
#
##############################################################################

import sys
import bs4
import odf.opendocument as odf
import argparse


# Create a parser and find all of the given element
def find_elements(data, to_find):
    parser = bs4.BeautifulSoup(str(data), 'lxml')
    return parser.find_all(to_find)


# Loads the data from the odt file and cleans it up
def get_odt_data(doc):
    doc = odf.load(doc)
    xml = str(doc.xml()).replace('table:table', 'table')
    xml = xml.replace('text:p', 'p')
    xml = xml.replace('text:h', 'h')
    return xml


# Converts the xml data into a 2D list, seperated per row
# and per cell
def get_table_data(xml):
    rows = find_elements(xml, 'table-row')
    table_cells = []
    for row in rows:
        cells = find_elements(row, 'p')
        row_values = [cell.get_text() for cell in cells]
        table_cells.append(row_values)
    del table_cells[0]
    return table_cells


# Cleans the data, by converting \\xe2\\x80\\x93 hex values to '-'.
# TODO: find better method for decoding hex values (not just '-')
def clean_data(tables):
    data = []
    for table in tables:
        for row in table:
            data.append(row[0] + "\t" + row[1] + " (" +
                        str(row[2]).replace("\\xe2\\x80\\x93", "-") + ")\n")
    return data


# Write data to file
def write_txt_file(data, output_file):
    with open(output_file, "w") as file:
        for row in data:
            file.writelines(row)


# Parse the command-line arguments given
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="set output file", type=str,
                        default='./output.txt')
    parser.add_argument("odtFile", help="odt input file", type=str)
    args = parser.parse_args()

    return args.odtFile, args.output


def main():
    doc, output = parse_arguments()
    xml = get_odt_data(doc)
    tables = find_elements(xml, 'table')
    table_collection = [get_table_data(table) for table in tables]
    table_data = clean_data(table_collection)
    write_txt_file(table_data, output)
    print("conversion complete...")


if __name__ == '__main__':
    sys.exit(main())
