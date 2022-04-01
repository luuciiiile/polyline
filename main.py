import csv
import os
import re
import shutil
import folium
import matplotlib.pyplot as plt
from pathlib import Path


# class Point, with x and y as the 2 coordinates
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def Left_index(points):
    """
    The algorithm start at the left most point, left_index find this point
    :param points: list of Points, each point have x and y coordinates
    :return: the most left point found in the list of Points
    """
    minn = 0
    for i in range(1, len(points)):
        if points[i].x < points[minn].x:
            minn = i
        elif points[i].x == points[minn].x:
            if points[i].y > points[minn].y:
                minn = i
    return minn


def is_in_list(test_list, x, y):
    """
    Usefull function in order to know if a point is in the list
    :param test_list: the loste we are looking in
    :param x: x coordinate of the point
    :param y: y coordinate of the point
    :return: True if the point(x, y) is in test_list, False otherwise
    """
    for a in range(len(test_list)):
        if test_list[a][0] == x and test_list[a][1] == y:
            return True
    return False


def orientation(p, q, r):
    """
    find the orientation of a p, q, r triplet
    :param p: Point with x and y coordinates
    :param q: Point with x and y coordinates
    :param r: Point with x and y coordinates
    :return: 0 if p, q, r are collinear, 1 if the orientation is clockwise, 2 if it's counterclockwise
    """
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2


def convexHull(points, n):
    """
    the actual algorithm who compute the jarvis march
    :param points: list of Points, from the CSV found
    :param n: number of points : length of the list points
    :return: 2 lists : the x and y coordinates of the points who constitute the wrapping
    """

    # this algorithm need at least 3 points...
    if n < 3:
        return

    left = Left_index(points)

    '''
    hull is the list of points who will be return
    p is the last point added to hull, start at the most left point of the list
    q is the next point who will be add to hull
    '''
    hull = []
    p = left
    q = 0
    '''
    start from the most left point
    moving counter clockwise until returning to the start
    complexity : O(h), with h the number of points in output
    '''
    while True:
        hull.append(p)
        '''
        find q, for each point, orientation(p, q, point) must be counter clockwise
        if a more counter clokwise point i is found, update q with this i
        '''
        q = (p + 1) % n
        for i in range(n):
            if orientation(points[p], points[i], points[q]) == 2:
                # update q if needed
                q = i
        # q is the most counter clockwise, update p for the next iteration
        p = q
        # in case we come to the first point
        if p == left:
            break
    # set the 2 lists who going to contain the coordinates
    x = []
    y = []
    for each in hull:
        x.append(points[each].x)
        y.append(points[each].y)
    return x, y


def get_name(input_path):
    """
    helpfull function who get and return the file name
    :param input_path: path of the file
    :return: the name of the file, without the extension
    ex :
    input_path = 'foo/bar.txt'
    return: 'bar'
    """
    ret = Path(input_path).stem
    return ret


def write_in_csv(x, y, input_file):
    """
    function who will create and write the coordinates in the result csv
    :param x: list of the x coordinates
    :param y: list of the y coordinates
    :param input_file: name of the file from which the jarvis march took the coordinates
    :return: nothing
    """

    '''
    create destination file and result directory if not exist
    if the file already exists, create a new file with '_v2' before the extension
    '''
    ret = get_name(input_file)
    dest = 'results/' + ret + '_hull.CSV'
    if os.path.exists(dest):
        dest = 'results/' + ret + '_v2' + '_hull.CSV'
    # open and write the coordinates in the new file
    with open(dest, 'w', newline='') as fichier:
        ecrivain = csv.writer(fichier)
        ecrivain.writerow(['X', 'Y'])

        for element in range(len(x)):
            elt = [x[element], y[element]]
            ecrivain.writerow(elt)


def eloignement(list_x, point, i):
    """
    define if a point is to far from another one
    :param list_x: x coordinates list of points already add to the result
    :param point: list of points to be tested
    :param i: indice where we want to test the point
    :return: True if the tested point is to far from the other one, False otherwise
    """
    if abs(list_x[i] - point[ancre - 1].x) < 100000000 * abs(point[ancre - 1].x - point[ancre - 2].x):
        return True
    return False


def search_for_files():
    """
    search recursively for all the files in the current directory
    :return: a list of paths of all the files who match the syntax [00000000-99999999]
    """
    list_fichiers = []
    for repertory, sous_repertory, files in os.walk('./test'):
        for name in files:
            if re.match('[00000000-99999999]', name):
                list_fichiers.append(os.path.join(repertory, name))
    return list_fichiers


def rename(input_path):
    """
    Rename a file, in order to track the files who already have been trated with the jarivs march
    :param input_path: path to the file
    :return: new path to the file, the original one with '[CONTOURED]_' before the file name
    """
    tail, head = os.path.split(input_path)
    ret = tail + '/[CONTOURED]_' + head
    return ret


def process_files(fichier):
    """
    read the input file, extract the x and y coordinates
    :param fichier:
    :return: two lists filled with the x and y coordinates
    """
    list_pts_x = ([])
    list_pts_y = ([])
    with open(fichier, newline='') as csvfile:
        pointreader = csv.reader(csvfile, delimiter=',')
        for row in pointreader:
            list_pts_x.append(row[1])
            list_pts_y.append(row[2])
        list_pts_x = list(map(float, list_pts_x))
        list_pts_y = list(map(float, list_pts_y))
    # rename the file who is going to be processed
    dest = rename(fichier)
    shutil.move(fichier, dest)

    return list_pts_x, list_pts_y


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # if the results directory does not exist, create it
    if not os.path.exists('results'):
        os.mkdir('results')
    # list of all the files who going to be processed
    list_files = search_for_files()

    # iterate on all the list_file list
    for fichier in list_files:
        #  take the coordinates
        list_pts_x, list_pts_y = process_files(fichier)

        n = len(list_pts_x)
        point = []
        ancre = 0
        list_exclusion = ([])

        #  clean the coordinates by removing the too far points
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
        list_exclusion.sort(reverse=True)
        # popping out the unwanted points
        for i in list_exclusion:
            list_pts_x.pop(i)
            list_pts_y.pop(i)

        # update the length of the list
        n = ancre

        # applies the algorithm on the cleaned list
        x, y = convexHull(point, n)

        # add the first points at the end, so we have a complete polygon when plot it
        x.append(x[0])
        y.append(y[0])

        # add the result coordinates to a new csv file in the result directory
        write_in_csv(x, y, fichier)

        # plot the points in a map
        # /!\ WIP - Doesn't work yet T-T
        m = folium.Map(location=[49.8153, 6.1296], zoom_start=9.5)
        folium.Marker([49.8153, 6.1296], popup='point').add_to(m)
        folium.Marker([49.8153, 5.1296], popup='point2').add_to(m)
        folium.Marker([49.8153, 7.1296], popup='point2').add_to(m)
        m.save('carte.html')

        # plot the points and their result with matplotlib
        plt.scatter(list_pts_x, list_pts_y, color='blue')
        plt.plot(x, y, color='pink')
        plt.show()
