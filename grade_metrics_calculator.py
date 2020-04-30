# Written by A Wan on 29.04.2020
# Imports
import re
from argparse import ArgumentParser

# Define Constants
COURSE_CODE = re.compile('([A-Z]{3})([0-9]{3})([HY])1')  # e.g. matches TMP100H1
GRADE_VALUES = {'A+': 9, 'A': 8, 'A-': 7, 'B+': 6, 'B': 5, 'B-': 4, 'C+': 3, 'C': 2, 'C-': 1}


class ZeroDict(dict):
    """
    A dictionary but return 0 when key is not there
    """

    def __missing__(self, key):
        return 0


def read_info(grades_file) -> list:
    """
    Return a list of the information from the grades
    :param grades_file: a file containing lines formatted: `Code<whitespace>TEMP PLACEHOLDER<w>0.50<w>90<w>A+<w>A`
    :return: A list of the form [(Course Code, Weight, Mark, Letter Grade, Avg Letter Grade)]
    """
    info = []
    with open(grades_file) as g:
        for line in g:
            if line.startswith('#'):
                continue
            s = line.split()
            info.append([s[0], float(s[-4]), int(s[-3]), s[-2], s[-1]])
    return info


# Unfortunately these small funcs have overhead that isn't removed by compiler optimization since Python is interpreted
def gpa_value(mark: int) -> float:
    """
    :param mark: numerical grade
    :return: GPA value corresponding to grade
    """
    if mark >= 85:
        return 4.0
    elif mark >= 80:
        return 3.7
    elif mark >= 77:
        return 3.3
    elif mark >= 73:
        return 3.0
    elif mark >= 70:
        return 2.7
    elif mark >= 67:
        return 2.3
    elif mark >= 63:
        return 2.0
    elif mark >= 60:
        return 1.7
    return 0.0


def letter_grade_distance(s1: str, s2: str) -> int:
    return GRADE_VALUES[s1] - GRADE_VALUES[s2]


if __name__ == "__main__":
    parser = ArgumentParser(description='Calculate some high level metrics ')
    parser.add_argument('--input_file', '-i', type=str, default='sample_grades.txt', help='File containing grades')
    parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Print additional information')
    args = parser.parse_args()

    # Read Data
    info = read_info(args.input_file)

    # Calculate Desired Quantities (all at once, in one iteration over the data)
    weights, gpa, avg, h_avg, h_weights = 0., 0., 0., 0., 0.
    done_first_year = False
    if args.verbose:
        letters = ZeroDict()
        avg_grade_distance, gd_weights = 0., 0.

    for x in info:
        # First year should be all 100-level courses, after it's over count everything towards Honours
        # Use the last initial 100-level course as the end of first year
        match_obj = re.match(COURSE_CODE, x[0])
        if not match_obj.group(2).startswith('1') or done_first_year:
            done_first_year = True
            h_weights += x[1]
            h_avg += x[1] * x[2]

        weights += x[1]
        gpa += x[1] * gpa_value(x[2])
        avg += x[1] * x[2]

        # This isn't great - there could easily be one verbose check outside the loop, but it's a small number of iters
        if args.verbose:
            lg = x[3]
            letters[lg] = letters[lg] + 1

            if not x[4] == '?':
                gd_weights += x[1]
                avg_grade_distance += x[1] * letter_grade_distance(lg, x[4])

    gpa /= weights
    avg /= weights
    h_avg /= h_weights

    # Print Desired Quantities
    if args.verbose:
        avg_grade_distance /= gd_weights
        letters_str = '{'
        for key, value in sorted(letters.items(), key=lambda x: x[0]):
            letters_str += "{} : {} | ".format(key, value)
        letters_str = letters_str[:-3] + '}'
        print('Letter Grade Distribution:', letters_str)

        print('Performance Relative to Average:',
              "+{:.3f}".format(avg_grade_distance) if avg_grade_distance > 0 else "{:.3f}".format(avg_grade_distance),
              '(1 => +/-, 3 => Letter Grade Difference)')

    print('cGPA:', "{:.3f}".format(gpa))
    print('Average:', "{:.3f}".format(avg))
    print('Average for Honours:', "{:.3f}".format(h_avg))
