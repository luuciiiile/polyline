import csv
import os
import glob
import shutil
from pathlib import Path


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def Left_index(points):
    minn = 0
    for i in range(1, len(points)):
        if points[i].x < points[minn].x:
            minn = i
        elif points[i].x == points[minn].x:
            if points[i].y > points[minn].y:
                minn = i
    return minn


def is_in_list(test_list, x, y):
    for a in range(len(test_list)):
        if test_list[a][0] == x and test_list[a][1] == y:
            return True
    return False


def orientation(p, q, r):
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2


def convexHull(points, n):
    if n < 3:
        return
    l = Left_index(points)

    hull = []
    p = l
    q = 0
    while True:
        hull.append(p)
        q = (p + 1) % n
        for i in range(n):
            if orientation(points[p], points[i], points[q]) == 2:
                q = i
        p = q
        if p == l:
            break
    x = []
    y = []
    for each in hull:
        x.append(points[each].x)
        y.append(points[each].y)
    return x, y


def reformat_file(input_path):
    ret = Path(input_path).stem
    return ret


def write_in_csv(x, y, input_file):
    with open(input_file + '_hull.CSV', 'w', newline='') as fichier:
        ecrivain = csv.writer(fichier)
        ecrivain.writerow(['X', 'Y'])
        for element in range(len(x)):
            elt = [x[element], y[element]]
            ecrivain.writerow(elt)
        ret = reformat_file(input_file)
        src = input_file + '_hull.CSV'
        dest = 'results/' + ret + '_hull.CSV'
        shutil.move(src, dest)


def eloignement(list_x, point, i):
    if abs(list_x[i] - point[ancre - 1].x) < 1000 * abs(point[ancre - 1].x - point[ancre - 2].x):
        return True
    return False


def search_for_files():
    result = glob.glob('./*/*.CSV', recursive=True)
    return result


def process_files(fichier):
    list_pts_x = ([])
    list_pts_y = ([])
    with open(fichier, newline='') as csvfile:
        pointreader = csv.reader(csvfile, delimiter=',')
        for row in pointreader:
            list_pts_x.append(row[0])
            list_pts_y.append(row[1])
        list_pts_x = list(map(float, list_pts_x))
        list_pts_y = list(map(float, list_pts_y))
    return list_pts_x, list_pts_y


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    os.mkdir('results')
    list_files = search_for_files()

    for fichier in list_files:
        list_pts_x, list_pts_y = process_files(fichier)

        n = len(list_pts_x)
        point = []
        ancre = 0
        list_exclusion = ([])

        for i in range(0, n):
            if i > 1:
                if eloignement(list_pts_x, point, i):
                    point.append(Point(list_pts_x[i], list_pts_y[i]))
                    ancre += 1
                else:
                    list_exclusion.append(i)
            else:
                point.append(Point(list_pts_x[i], list_pts_y[i]))
                ancre += 1
        n = ancre
        x, y = convexHull(point, n)
        x.append(x[0])
        y.append(y[0])

        list_exclusion.sort(reverse=True)
        for i in list_exclusion:
            list_pts_x.pop(i)
            list_pts_y.pop(i)

        write_in_csv(x, y, fichier)
