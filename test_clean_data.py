"""
test_clean_data.py

Unit tests for parse_listing() in clean_data.py.

Run with:
    python -m unittest test_clean_data.py

These tests use small, hand-written examples of raw listing text (similar
to what scrape_listings.py captures from a Jiji listing card) rather than
real scraped data, so they keep working even if the live site changes.
"""
import unittest
from clean_data import parse_listing


class TestParseListing(unittest.TestCase):

    def test_price_extraction(self):
        raw = "Furnished 3bdrm Villa in Bole for rent\nETB 100,000\nBole"
        result = parse_listing(raw)
        self.assertEqual(result["price_etb"], 100000)

    def test_price_missing_returns_none(self):
        raw = "Furnished 3bdrm Villa in Bole for rent\nBole"
        result = parse_listing(raw)
        self.assertIsNone(result["price_etb"])

    def test_bedrooms_extraction(self):
        raw = "3bdrm Apartment in Kirkos for rent\nETB 75,000\nKirkos"
        result = parse_listing(raw)
        self.assertEqual(result["bedrooms"], 3)

    def test_studio_counts_as_zero_bedrooms(self):
        raw = "Studio Apartment in Bole for rent\nETB 45,000\nBole"
        result = parse_listing(raw)
        self.assertEqual(result["bedrooms"], 0)

    def test_property_type_detected_from_title_only(self):
        # "House" appears later in the text but should NOT override
        # "Villa" which appears in the title area
        raw = ("Furnished 4bdrm Villa in Yeka for rent\n"
               "Spacious compound, great for a family house gathering\n"
               "ETB 200,000\nYeka")
        result = parse_listing(raw)
        self.assertEqual(result["property_type"], "Villa")

    def test_size_m2_extraction_square_meter_format(self):
        raw = "3bdrm House in Bole for rent\n250 square meters\nETB 300,000\nBole"
        result = parse_listing(raw)
        self.assertEqual(result["size_m2"], 250)

    def test_size_m2_extraction_sqm_format(self):
        raw = "3bdrm House in Bole for rent\n250 sqm\nETB 300,000\nBole"
        result = parse_listing(raw)
        self.assertEqual(result["size_m2"], 250)

    def test_size_m2_missing_returns_none(self):
        raw = "3bdrm House in Bole for rent\nETB 300,000\nBole"
        result = parse_listing(raw)
        self.assertIsNone(result["size_m2"])

    def test_furnished_true(self):
        raw = "Fully furnished 2bdrm Apartment in Lideta for rent\nETB 90,000\nLideta"
        result = parse_listing(raw)
        self.assertTrue(result["furnished"])

    def test_furnished_false_when_explicitly_unfurnished(self):
        # Must NOT match "furnished" inside "unfurnished"
        raw = "Unfurnished 2bdrm Apartment in Lideta for rent\nETB 70,000\nLideta"
        result = parse_listing(raw)
        self.assertFalse(result["furnished"])

    def test_furnished_false_when_not_mentioned(self):
        raw = "2bdrm Apartment in Lideta for rent\nETB 70,000\nLideta"
        result = parse_listing(raw)
        self.assertFalse(result["furnished"])

    def test_sub_city_is_last_line(self):
        raw = "3bdrm Apartment in Bole for rent\nETB 100,000\nBole"
        result = parse_listing(raw)
        self.assertEqual(result["sub_city"], "Bole")


if __name__ == "__main__":
    unittest.main()
