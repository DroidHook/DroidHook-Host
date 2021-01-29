# Convert logs extracted from Xposed framework to samples' monitor reports
import json
import os
import re

LOG_DIR = './log/'
REPORT_DIR = './report/'

if __name__ == "__main__":
    log_list = os.listdir(LOG_DIR)
    report_list = os.listdir(REPORT_DIR)
    count = 0

    for log in log_list:
        count += 1
        if log in report_list:
            print('%d: %s has already been converted.' % (count, log))
            continue

        report_dic = {}
        with open(LOG_DIR + log) as log_file:
            for line in log_file:
                # Find logs provided by DroidHook
                if not re.match('\d\d-\d\d', line):
                    continue
                if not re.search('KotlinXposedMonitor', line):
                    continue

                line_report_dic = {}
                # Remove \n
                line = line[:-1]

                time = line[:18]
                line_log_start_position = re.search('KotlinXposedMonitor', line).end() + 1
                line_log_raw = line[line_log_start_position:].replace(' ','')
                line_class = line_log_raw[1 : re.search(':', line_log_raw).end()-1]
                line_log_raw = line_log_raw[re.search(':', line_log_raw).end() :]
                line_api = line_log_raw[: re.search('-', line_log_raw).end()-1]

                line_report_dic['class'] = line_class
                line_report_dic['api'] = line_api

                line_detail = line_log_raw[re.search('-', line_log_raw).end() :]
                if len(line_detail) != 0:
                    line_report_dic['details'] = line_detail

                report_dic[time] = line_report_dic

        with open(REPORT_DIR + log, mode='x', encoding='utf-8') as report_file:
            report_file.write(json.dumps(report_dic))
        print('%d: %s has been converted.' % (count, log))