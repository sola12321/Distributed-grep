import os
import sys
import subprocess
import random

#generate random log files
#./randomLogs/
def createRandomLog(num):
    for id in range(1,num+1):
        file = "./randomLogs/randomLogVM%d.log" % (id)
        rl = open(file, "w")
        size = 0
        while size < 60:
            line = html_log() + "\n"
            rl.write(line)
            size = os.path.getsize(file) / (1024 * 1024)
        rl.close()
        print(id)
        rl.close()

#00:34:23 GET /foo/bar.html
def html_log():
    return "{time} {method} {path}".format(
        time = random_time(),
        method = random_method(),
        path =random_path(),)


def random_time():
    h, m, sec = random.randint(0,24), random.randint(0,60), random.randint(0,60)
    return "%02d:%02d:%02d" % (h, m, sec)


def random_char():
    return ''.join(
        random.choice("qazwsxedcrfvtgbyhnujmikolp")
        for x in range(random.randint(3, 10)))


def random_path():
    return "/" + "/".join([random_char() for i in range(random.randint(0, 5))]) + ".html"


def random_method():
    return random.choice(["GET", "POST"])

createRandomLog(4)
