# by Targosz Seweryn
# tseweryn@amazon.com

# BACKUP LIBRARIES
#
# import openpyxl, os
# from selenium.webdriver import Firefox, Chrome
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait

site_dict = {
    'RECEIVE': 1,
    'STOW': 2,
    'SWEEPER': 3,
    'PICK': 4,
    'WAREHOUSE DEALS': 5,
    'PACK': 6,
    'ICQA': 7,
    'INDUCT': 8,
    'IB PROBLEM SOLVE': 9,
    'REBIN': 10,
    'SHIP': 11,
    'SORT': 12,
    'OB PROBLEM SOLVE': 13,
    'MOD': 14,
    'CUSTOMER RETURNS RECEIVE': 15,
    'MINESWEEPER': 16
}
type_dict = {
    'RECEIVE': {
        'Wrong ASIN': 2,
        'Stickered Wrong ASIN': 3,
        'Physical Overage': 4,
        'Similar ASIN': 5,
        'Switched ASINS': 6,
        'Datelot': 7,
        'Damaged Item': 8,
        'Virtual Overage': 9,
        'Item Required Cubiscan': 10,
        'Not Yet Received': 51,
        'Mastercase': 52,
        'Item Not Prepped': 134,
        'Standard Work Violation': 136,
        'Items Not Decanted': 137,
        'BOX on Demand Defect': 165
    },
    'STOW': {
        'Adjacent Bin': 12,
        'Other Bin Scanned': 13,
        'Scanned Not Stowed': 14,
        'Stowed Not Scanned': 15,
        'Stowed Similar Titles': 16,
        'Stowed Wrong ASIN': 17,
        'Like ASIN in Same Bin': 18,
        'Like/Same Asin in Adjacent Bin': 19,
        'Improper Bin Choice': 20,
        'Overstuffed/Unorganized': 21,
        'Overhang > Two Inches': 22,
        'Mastercase': 114,
        'Switcheroo': 127,
        'Standard Work Violation': 163
    },
    'SWEEPER': {

    },
    'PICK': {
        'Picked Not Scanned': 25,
        'Scanned Not Picked': 26,
        'Overstacked Cart': 53,
        'Picked to Wrong Tote': 54,
        'Trash in Location': 55,
        'Mastercase': 56,
        'Under Picked': 57,
        'Mispick': 58,
        'Switcheroo': 59,
        'Standard Work Violation': 135,
        'Multiple Logins': 144,
        'False Pick Reject': 145,
        'Broken Set': 146,
        'Failed to Convey': 147
    },
    'PACK': {
        'Not Pyramid Stacked': 28,
        'Spine to Spine': 29,
        'Improper Box Type': 30,
        'Contains Damaged Item': 33,
        'PSlip Missing From Box': 34,
        'Missing License Plate': 35,
        'Etiquette Violation': 115,
        'Processed Too Few': 116,
        'Processed Too Many': 117,
        'False Problem': 143,
        'Standard Work Violation': 172
    },
    'ICQA': {
        'Miscounted Asins': 60,
        'Miscounted Quantity - Too Few': 61,
        'Miscounted Quantity - Too Many': 62,
        'Mislabeled Product': 63,
        'Amnesty Error - Wrong Location': 64,
        'Amnesty Error - Too Many': 65,
        'Amnesty Error - Too Few': 66,
        'Damage Processing Error': 67,
        'Other': 68,
        'Standard Work Violation': 164
    },
    'INDUCT': {
        'Etiquette Violation': 69,
        'False Adhoc': 70,
        'Processed Too Few': 71,
        'Processed Too Many': 72,
        'Processed Wrong Condition': 73,
        'Processed Wrong Item': 74,
        'Processed Wrong Location': 75,
        'Standard Work Violation': 76,
        'Wrong Adjustment': 77
    },
    'IB PROBLEM SOLVE': {
        'Etiquette Violation': 78,
        'False Adhoc': 79,
        'Processed Too Few': 80,
        'Processed Too Many': 81,
        'Processed Wrong Condition': 82,
        'Processed Wrong Item': 83,
        'Processed Wrong Location': 84,
        'Standard Work Violation': 85,
        'Wrong Adjustment': 86,
        'Found on Open PO': 128,
        'Not Stickered': 129,
        'ASIN Virtually in csXP': 130,
        'ASIN Virtually in Shorts': 131,
        'Broken Set': 132,
        'PID Wrong ASIN': 133
    },
    'REBIN': {
        'Etiquette Violation': 87,
        'False Adhoc': 88,
        'Processed Too Few': 89,
        'Processed Too Many': 90,
        'Processed Wrong Condition': 91,
        'Processed Wrong Item': 92,
        'Processed Wrong Location': 93,
        'Standard Work Violation': 94,
        'Wrong Adjustment': 95
    },
    'SHIP': {
        'Etiquette Violation': 96,
        'False Adhoc': 97,
        'Processed Too Few': 98,
        'Processed Too Many': 99,
        'Processed Wrong Condition': 100,
        'Processed Wrong Item': 101,
        'Processed Wrong Location': 102,
        'Standard Work Violation': 103,
        'Wrong Adjustment': 104
    },
    'SORT': {
        'Etiquette Violation': 105,
        'False Adhoc': 106,
        'Processed Too Few': 107,
        'Processed Too Many': 108,
        'Processed Wrong Condition': 109,
        'Processed Wrong Item': 110,
        'Processed Wrong Location': 111,
        'Standard Work Violation': 112,
        'Wrong Adjustment': 113
    },
    'OB PROBLEM SOLVE': {
        'Etiquette Violation': 118,
        'False Adhoc': 119,
        'Processed Too Few': 120,
        'Processed Too Many': 121,
        'Processed Wrong Condition': 122,
        'Processed Wrong Item': 123,
        'Processed Wrong Location': 124,
        'Standard Work Violation': 125,
        'Wrong Adjustment': 126,
        'Stickered Wrong ASIN': 142
    },
    'MOD': {
        'Incorrectly Bound': 148,
        'Finalized Damaged Book': 149,
        'Finalized Onto Wrong Cart': 150,
        'Submitted Damaged Book': 151,
        'Wholesale Placed on Retail Cart': 152,
        'CS 2 in 1': 153
    },
    'CUSTOMER RETURNS RECEIVE': {
        'Virtual Overage': 154,
        'Physical Overage': 155,
        'Damaged Item': 156,
        'Wrong ASIN': 157,
        'Proccessed HRV': 158,
        'Customer Details': 159,
        'Etiquette Violation': 160,
        'False Escalation': 161,
        'Inadequate Research': 162,
        'BOX on Demand Defect': 166
    },
    'MINESWEEPER': {

    }
}
