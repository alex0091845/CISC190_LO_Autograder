from assignments import Assignments as A
from config import *
from levels import Levels

class LOs:
    LO1 = "LO1: Variables"
    LO2 = "LO2: Using Methods"
    LO3 = "LO3: Writing Methods"
    LO4 = "LO4: Arrays"
    LO5 = "LO5: Loops"
    LO6 = "LO6: User Input"
    LO7 = "LO7: Decisions"
    LO8 = "LO8: Custom Classes"
    LO9 = "LO9: Inheritance and Polymorphism"
    LO_NAMES = [LO1, LO2, LO3, LO4, LO5, LO6, LO7, LO8, LO9]

    # modules to LOs
    MODULE_NUM_TO_LO_NUM = {
        1: 2,
        2: 3,
        3: 4,
        4: 6,
        5: 7,
        6: 8,
        7: 9,
    }
    LO_TO_MODULE_NUM = {
        LO1: 1,
        LO2: 1,
        LO3: 2,
        LO4: 3,
        LO5: 4,
        LO6: 4,
        LO7: 5,
        LO8: 6,
        LO9: 7,
    }

    reqs: dict = {}
    results: dict = {}
    lo_name_to_id: dict = {}

    def __init__(self):
        self._init_reqs()
        self._init_lo_name_to_id()

    @staticmethod
    def _init_reqs():
        LOs.reqs = {
            LOs.LO1: {
                Levels.INTERN: lambda: A._and(["M1 Read and Try: Using Methods and Parameters"]),
                Levels.JUNIOR: lambda: A._and(["M1 Draw My Name", "M1 Share: Draw My Name"]),
                Levels.MIDDLE: lambda: A._and(["M1 Explain: Using Methods and Parameters"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO1"]),
            },
            LOs.LO2: {
                Levels.INTERN: lambda: A._and(["M1 Read and Try: Using Methods and Parameters"]),
                Levels.JUNIOR: lambda: A._and(["M1 Draw My Name", "M1 Share: Draw My Name"]),
                Levels.MIDDLE: lambda: A._and(["M1 Explain: Using Methods and Parameters"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO2"]),
            },
            LOs.LO3: {
                Levels.INTERN: lambda: A._and(["M2 Read and Try: Writing Methods"]),
                Levels.JUNIOR: lambda: A._and(["M2 Draw Shape", "M2 Share: Draw Shape"]),
                Levels.MIDDLE: lambda: A._and(["M2 Explain: Writing Methods"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO3"]),
            },
            LOs.LO4: {
                Levels.INTERN: lambda: A._and(["M3 Read and Try: Loops and Arrays"]),
                Levels.JUNIOR: lambda: A._and([A._or(["M3 Paint a Picture", "M3 Color Subtraction"]), "M3 Tri-effect", "M3 Share: Loops and Arrays"]),
                Levels.MIDDLE: lambda: A._and(["M3 Explain: Arrays and Tracing Code"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO4"]),
            },
            LOs.LO5: {
                Levels.INTERN: lambda: A._and(["M4 Read and Try: Nested Loops"]),
                Levels.JUNIOR: lambda: A._and(["M4 Simple Collage", "M4 Share: Simple Collage"]),
                Levels.MIDDLE: lambda: A._and(["M4 Explain: Loops"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO5"]),
            },
            LOs.LO6: {
                Levels.INTERN: lambda: A._and(["M4 Read and Try: User Input"]),
                Levels.JUNIOR: lambda: A._and(["M4 Create Multiple Shapes"]),
                Levels.MIDDLE: lambda: A._and(["M4 Explain: User Input"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO6"]),
            },
            LOs.LO7: {
                Levels.INTERN: lambda: A._and(["M5 Read and Try: Conditional Execution"]),
                Levels.JUNIOR: lambda: A._and(["M5 Chromakey", "M5 Share: Chromakey"]),
                Levels.MIDDLE: lambda: A._and(["M5 Explain: Conditional Execution"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO7"]),
            },
            LOs.LO8: {
                Levels.INTERN: lambda: A._and(["M6 Read and Try: Creating Your Own Custom Class"]),
                Levels.JUNIOR: lambda: A._and(["M6 Sales Funnel"]),
                Levels.MIDDLE: lambda: A._and(["M6 Explain: User-Defined Classes"]),
                Levels.SENIOR: lambda: A._and(["Final Project - LO8"]),
            },
            LOs.LO9: {
                Levels.INTERN: lambda: A._and(["M7 Read and Try: Inheritance and Polymorphism - LO9"]),
                Levels.JUNIOR: lambda: A._or(["M7 Perusall Discussion: Inheritance and Polymorphism", "M7 TIP: Advanced Topics - Inheritance"]),
                Levels.MIDDLE: lambda: A._and(["M7 Critters (Inheritance and Polymorphism - LO9)"]),
                Levels.SENIOR: lambda: A._and(["M7 Explain: Inheritance and Polymorphism - LO9"]),
            }
        }
    
    @staticmethod
    def _init_lo_name_to_id():
        LOs.lo_name_to_id = {
            LOs.LO1: 21686599,
            LOs.LO2: 21686600,
            LOs.LO3: 21686601,
            LOs.LO4: 21686602,
            LOs.LO5: 21686603,
            LOs.LO6: 21686604,
            LOs.LO7: 21686605,
            LOs.LO8: 21686606,
            LOs.LO9: 21686607,
        }