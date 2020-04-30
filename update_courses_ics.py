# Written by A Wan on 08.04.2019
# Create a modified ics file from a formatted input ics courses file

import os
import sys
from argparse import ArgumentParser

DESIRED_COURSE_TITLES = {
    'BME595H1': 'BME595: Biomedical Imaging',
    'ECE497Y1': 'ECE497: Capstone Design Project',
    'ECE568H1': 'ECE568: Computer Security',
}


# Modify the existing course calendar event title according to the DESIRED_COURSE_TITLES dictionary
def modify_course_event_title(event_title: str) -> str:
    et = event_title.split(' ')  # et[0] is course code (e.g. ECE421H1), et[1] is type and section (e.g. LEC0101)
    course_code = DESIRED_COURSE_TITLES[et[0]] if et[0] in DESIRED_COURSE_TITLES else et[0]
    course_type = et[1][:3]
    return course_code + ' (' + course_type + ')'


if __name__ == "__main__":
    parser = ArgumentParser(description='Read UofT Courses ICS file and modify it')
    parser.add_argument('--input_file', type=str, default='courseCalendar.ics', help='filepath to read from')
    parser.add_argument('--output_file', type=str, default='output.ics', help='output file name')
    args = parser.parse_args()

    input_filename = args.input_file
    if not os.path.exists(input_filename):
        print('Provided file', input_filename, 'was not found.')
        sys.exit(1)
    output_filename = os.path.join(os.path.dirname(input_filename), args.output_file)

    with open(input_filename) as icsfile, open(output_filename, 'w') as outfile:
        stopOutput = False
        for line in icsfile:
            if line == 'BEGIN:VALARM\n':
                stopOutput = True
            elif line == 'END:VALARM\n':
                stopOutput = False
            elif not stopOutput:
                cIndex = line.find(':')
                tag = line[:cIndex]
                if tag == 'SUMMARY':
                    summary = modify_course_event_title(line[cIndex + 1:])
                    outfile.write(line[:cIndex + 1] + summary + '\n')
                elif tag != 'DESCRIPTION':
                    outfile.write(line)
    sys.exit(0)
