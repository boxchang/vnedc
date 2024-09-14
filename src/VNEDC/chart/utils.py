def chart_config():
    config = {
        "ACID": {
            "TEMPERATURE": {
                "variables": ["T1_TEMPERATURE", "T2_TEMPERATURE"],
                "high": 66,
                "low": 60,
                "xlim": (0, 62),
                "ylim": (0, 75)
            },
            "CONCENTRATION": {
                "variables": ["T1_CONCENTRATION", "T2_CONCENTRATION"],
                "high": 1.7,
                "low": 1.0,
                "xlim": (0, 124),
                "ylim": (0, 2.0)
            }
        },
        "ALKALINE": {
            "TEMPERATURE": {
                "variables": ["T1_TEMPERATURE", "T2_TEMPERATURE"],
                "high": 66,
                "low": 60,
                "xlim": (0, 62),
                "ylim": (0, 75)
            },
            "CONCENTRATION": {
                "variables": ["T1_CONCENTRATION", "T2_CONCENTRATION"],
                "high": 1.3,
                "low": 0.7,
                "xlim": (0, 124),
                "ylim": (0, 2.0)
            }
        },
        "RINSING": {
            "CONCENTRATION": {
                "variables": ["T1_CONCENTRATION"],
                "high": 0.2,
                "low": 0.1,
                "xlim": (0, 62),
                "ylim": (0, 0.5)
            },
            "TEMPERATURE": {
                "variables": ["T3_TEMPERATURE"],
                "high": 66,
                "low": 60,
                "xlim": (0, 124),
                "ylim": (0, 80)
            },
            "OV1_TEMPERATURE": {
                "variables": ["OV1_1_TEMPERATURE", "OV1_2_TEMPERATURE"],
                "high": 86,
                "low": 80,
                "xlim": (0, 124),
                "ylim": (0, 120)
            }
        },
        "COAGULANT": {
            "CPF": {
                "variables": ["A_CPF", "B_CPF"],
                "high": 1.8,
                "low": 1.4,
                "xlim": (0, 124),
                "ylim": (0, 3.0)
            },
            "PH": {
                "variables": ["A_PH", "B_PH"],
                "high": 9,
                "low": 8,
                "xlim": (0, 124),
                "ylim": (0, 12)
            },
            "TEMPERATURE": {
                "variables": ["A_TEMPERATURE", "B_TEMPERATURE"],
                "high": 53,
                "low": 47,
                "xlim": (0, 124),
                "ylim": (0, 80)
            },
            "OV2_TEMPERATURE": {
                "variables": ["OV2_1_TEMPERATURE", "OV2_2_TEMPERATURE"],
                "high": 120,
                "low": 114,
                "xlim": (0, 124),
                "ylim": (0, 130)
            }
        },
        "LATEX": {
            "TSC": {
                "variables": ["A_T1_TSC", "A_T2_TSC", "B_T1_TSC", "B_T2_TSC"],
                "high": 13.5,
                "low": 12,
                "xlim": (0, 124),
                "ylim": (0, 20)
            },
            "PH": {
                "variables": ["A_T1_PH", "A_T2_PH", "B_T1_PH", "B_T2_PH"],
                "high": 10.2,
                "low": 9.8,
                "xlim": (0, 124),
                "ylim": (0, 12)
            },
            "TEMPERATURE": {
                "variables": ["A_T1_TEMPERATURE", "A_T2_TEMPERATURE", "B_T1_TEMPERATURE", "B_T2_TEMPERATURE"],
                "high": 35,
                "low": 29,
                "xlim": (0, 124),
                "ylim": (0, 50)
            },
            "OV3_TEMPERATURE": {
                "variables": ["OV3_1_TEMPERATURE", "OV3_2_TEMPERATURE"],
                "high": 100,
                "low": 90,
                "xlim": (0, 124),
                "ylim": (0, 110)
            },
            "OV4_TEMPERATURE": {
                "variables": ["OV4_TEMPERATURE"],
                "high": 60,
                "low": 50,
                "xlim": (0, 124),
                "ylim": (0, 70)
            }
        },
        "PRELEACH": {
            "TDS": {
                "variables": ["T5_TDS"],
                "high": 1500,
                "low": 1000,
                "xlim": (0, 62),
                "ylim": (0, 2000)
            },
            "TEMPERATURE": {
                "variables": ["T5_TEMPERATURE"],
                "high": 63,
                "low": 57,
                "xlim": (0, 124),
                "ylim": (0, 80)
            },
            "OV5_TEMPERATURE": {
                "variables": ["OV5_TEMPERATURE"],
                "high": 60,
                "low": 50,
                "xlim": (0, 124),
                "ylim": (0, 80)
            },
            "LIQUID_LEVEL": {
                "variables": ["T5_LIQUID_LEVEL"],
                "high": 230,
                "low": 230,
                "xlim": (0, 124),
                "ylim": (0, 250)
            }
        },
        "OVEN": {
            "TEMPERATURE": {
                "variables": ["A06B06_TEMPERATURE", "A07B07_TEMPERATURE", "A08B08_TEMPERATURE", "A09B09_TEMPERATURE",
                              "A10B10_TEMPERATURE", "A11B11_TEMPERATURE", "A12B12_TEMPERATURE", "A13B13_TEMPERATURE",
                              "A14B14_TEMPERATURE"],
                "high": 115,
                "low": 109,
                "xlim": (0, 124),
                "ylim": (0, 150)
            }
        },
        "COOLING": {
            "TEMPERATURE": {
                "variables": ["T4_TEMPERATURE"],
                "high": 38,
                "low": 32,
                "xlim": (0, 124),
                "ylim": (0, 50)
            },
            "LIQUID_LEVEL": {
                "variables": ["T4_LIQUID_LEVEL"],
                "high": 250,
                "low": 250,
                "xlim": (0, 62),
                "ylim": (0, 300)
            }
        },
        "CHLORINE": {
            "CONCENTRATION": {
                "variables": ["CONCENTRATION"],
                "high": 600,
                "low": 400,
                "xlim": (0, 124),
                "ylim": (0, 1000)
            },
            "LIQUID_LEVEL": {
                "variables": ["LIQUID_LEVEL"],
                "high": 280,
                "low": 280,
                "xlim": (0, 62),
                "ylim": (0, 300)
            }
        },
        "POSTLEACH": {
            "TDS": {
                "variables": ["T3_TDS"],
                "high": 250,
                "low": 150,
                "xlim": (0, 124),
                "ylim": (0, 400)
            },
            "TEMPERATURE": {
                "variables": ["T3_TEMPERATURE"],
                "high": 68,
                "low": 62,
                "xlim": (0, 124),
                "ylim": (0, 80)
            },
            "OV15_TEMPERATURE": {
                "variables": ["OV15_TEMPERATURE"],
                "high": 90,
                "low": 80,
                "xlim": (0, 124),
                "ylim": (0, 100)
            }
        },
        "FINAL_OVEN": {
            "OV16_TEMPERATURE": {
                "variables": ["OV16_1_TEMPERATURE", "OV16_2_TEMPERATURE"],
                "high": 121,
                "low": 115,
                "xlim": (0, 124),
                "ylim": (0, 150)
            }
        },
        "NBR_BOILER": {
            "TEMPERATURE": {
                "variables": ["BO1_TEMPERATURE", "BO2_TEMPERATURE", "BO3_TEMPERATURE"],
                "high": 0,
                "low": 0,
                "xlim": (0, 124),
                "ylim": (0, 300)
            }
        }
    }
    return config