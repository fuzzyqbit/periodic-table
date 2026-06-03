from periodic_table.model import Category

CATEGORY_COLORS: dict[Category, str] = {
    Category.ALKALI_METAL:      "#ff6666",
    Category.ALKALINE_EARTH:    "#ffdead",
    Category.TRANSITION_METAL:  "#ffc0c0",
    Category.POST_TRANSITION:   "#bfbfbf",
    Category.METALLOID:         "#cccc99",
    Category.NONMETAL:          "#a0ffa0",
    Category.HALOGEN:           "#ffff99",
    Category.NOBLE_GAS:         "#c0ffff",
    Category.LANTHANIDE:        "#ffbfff",
    Category.ACTINIDE:          "#ff99cc",
    Category.UNKNOWN:           "#e0e0e0",
}

DIM_COLOR = "#dddddd"
