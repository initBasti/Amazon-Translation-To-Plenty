import pytest
import pandas

from sample_data_attributes import attribute_sample
from packages.assignment import find_id_for_color

def test_find_id_for_color(attribute_sample):
    search = [
        'B0019 Lillypink', 'Uni pink', 'Legging N005 Braunton',
        'grauton LUG', 'Legging U003 blue', 'TD11 Braunton', 'Schwarz',
        'goldbraun', 'Hose Naturbaumwolle in M', 'weiß',
        'Braunton (Nr.9)', 'V2-violett', 'Mandala bordeauxrot',
        'Chakras-Bunt', 'Garuda in schwarz', 'B007 hellgruen',
        'Beige', 'V08 Oliveton', 'Ton Beige', 'Shirt in beige',
        'Hellblauton', 'fuchsrot', '001 Naturweiß', 'Batik blau',
        'Pfau. graublau', 'WOV32', 'Uni goldgelb', '004 in beige',
        'CS04 Olivengrünton', 'Rotton', 'brown', 'Arab Design',
        'WOV31', 'Ch2 in dunkel lila', '001 weiß', '002 Bordeauxrot',
        'lilaton', 'black', 'Dunkel Grau', 'bordeauxton',
        '002 Safrongelb', 'Olive-grün', 'Hand-grey', 'V02 schwarz',
        'Shirt buttonfree BLUE', 'violett', 'hellblau',
        'TH02. Schwarzton', 'Legging N007 Lila-line', 'Orange',
        'dunkel lila', 'V05 Dunkelblau', 'schwarz weiß',
        'Lebensblume. weiß', 'Bordeaux', 'Top N010 liquified',
        'mit 2er Knopfleiste', 'V 13', 'dunkel blau',
        'Legging N002 brownish', 'dunkel rot', 'hell blau',
        'V18 Braunton', 'marmor weiß', 'Asanoha violett', 'Om.2-grey',
        'Grün', 'dunkelblauton LUG', 'SD258 in schwarz', 'Hose in blau',
        'neon grün', 'bordeaux rot', 'Shirt buttonfree BLACK',
        '003 in schwarz', 'dunkelblau', 'WOV28', 'V11 violetteton',
        'Patchwork-bunt 002', 'Blau', 'Hose in beige', 'Shirt in blau',
        '005 in weiß', 'Batik Tiefrotton', 'Shirt 6button WHITE',
        'Ch2 in dunkel pink', '007 in schwarz', 'CS03 Blauton',
        '005 in beige', 'V2-bordeux rot', '08 schwarz',
        'CT04 Lilaton', 'SD301 in schwarz', '003 weiß', 'grünton LUG',
        'Patchwork Blauton', 'Legging N004 Brown Lagoon', 'Goldton',
        'schwarz mit grünem Muster', 'V07 Dunkelblau', 'pastelblau',
        'Hose im Aladdinstyle', 'langarm in schwarz', 'B010 orangeton',
        'Uni lila', 'bunt 1', 'Lila', 'türkis', 'Ch1 in turkis'
    ]

    expect = [81, 87, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101,
              102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113,
              114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 162, 163,
              164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175,
              176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 187, 188,
              189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200,
              201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212,
              213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 225,
              226, 227, 228, 229, 230, 231, 233, 234, 235, 236, 237, 238]

    for index, term in enumerate(search):
        result = find_id_for_color(attribute_sample, term)
        assert expect[index] == result, str(f"{term} => {result}")
