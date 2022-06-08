import csv
import os
import re
import matplotlib.pyplot as plt
from pathlib import Path
import PIL
from exif import Image
from PIL.ExifTags import TAGS, GPSTAGS


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
    Useful function in order to know if a point is in the list
    :param test_list: the list we are looking in
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
    helpful function who get and return the file name
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


def eloignement(list_x, point, i, ancre):
    """
    define if a point is too far from another one
    :param ancre: indice where we are in the tested points
    :param list_x: x coordinates list of points already add to the result
    :param point: list of points to be tested
    :param i: indice where we want to test the point
    :return: True if the tested point is too far from the other one, False otherwise
    """
    if abs(list_x[i] - point[ancre - 1].x) < 100000000 * abs(point[ancre - 1].x - point[ancre - 2].x):
        return True
    return False


def search_for_files():
    """
    search recursively for all the files in the current directory
    :return: a list of paths of all the csv files
    """
    list_fichiers = []
    for repertory, sous_repertory, files in os.walk('.'):
        for name in files:
            if re.match(".+\\.([cC][sS][vV])", name):
                list_fichiers.append(os.path.join(repertory, name))
    return list_fichiers


def rename(input_path):
    """
    Rename a file, in order to track the files who already have been processed with the jarvis march
    :param input_path: path to the file
    :return: new path to the file, the original one with '[CONTOURED]_' before the file name
    """
    tail, head = os.path.split(input_path)
    ret = tail + '/[CONTOURED]_' + head
    return ret


def rename_old(input_path):
    """
    rename a file with [OLD] before
    :param input_path: path to the file
    :return: new path to the file, the original one with '[OLD]_' before the file name
    """
    tail, head = os.path.split(input_path)
    ret = tail + '/[OLD]_' + head
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
        try:
            for row in pointreader:
                list_pts_x.append(row[1])
                list_pts_y.append(row[2])
            list_pts_x = list(map(float, list_pts_x))
            list_pts_y = list(map(float, list_pts_y))
        except IndexError:
            print("not a csv file")
            return list_pts_x, list_pts_y
        except ValueError:
            print("smt wrong with the csv...")
            list_pts_x = ([])
            list_pts_y = ([])
            return list_pts_x, list_pts_y
    # rename the file who is going to be processed
    # dest = rename(fichier)
    # shutil.move(fichier, dest)

    return list_pts_x, list_pts_y


# Press the green button in the gutter to run the script.
def clean_cloud(list_pts_x, list_pts_y):
    """
    this function will remove some useless points of the cloud. The less point we have to process, the faster
    the run will be
    :param list_pts_x: list of the x coordinates
    :param list_pts_y: list of the y coordinates
    :return: point the list of the remaining x and y coordinates, ancre the length of the cleaned list,
    the lists of the remaining coordinates
    """
    n = len(list_pts_x)
    point = []
    ancre = 0
    list_exclusion = ([])
    #  clean the coordinates by removing the too far points
    for i in range(0, n):
        if i > 1:
            if eloignement(list_pts_x, point, i, ancre):
                point.append(Point(list_pts_x[i], list_pts_y[i]))
                print("point: ", point)
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

    return point, ancre, list_pts_x, list_pts_y


def add_in_csv(x, y, resultats, code):
    """
    add the x and y coordinates at the end of the results file, with the name of the directory as code
    :param x: x coordinates
    :param y: y coordinates
    :param resultats: results file
    :param code: code of the file
    :return: nothing
    """
    # Isolate the filename
    # name = get_name(code)
    ecrivain = csv.writer(resultats)
    for element in range(len(x)):
        elt = [x[element], y[element], code]
        ecrivain.writerow(elt)


def get_code(chemin):
    """
    get the code, with the highest directory name
    :param chemin: path to the file
    :return: the code number
    """
    chem = os.path.normpath(chemin).split(os.path.sep)
    return chem[0]


def get_coordinates_photo(photo):
    lat = 0
    long = 0
    with open(photo, 'rb') as im_file:
        my_im = Image(im_file)
        if my_im.has_exif:
            lat = my_im.gps_latitude
            lat_ref = my_im.gps_latitude_ref
            long = my_im.gps_longitude
            long_ref = my_im.gps_longitude_ref
    return lat, lat_ref, long, long_ref


def convert_gps(lat, lat_ref, long, long_ref):
    """
    convert DMS format GPS coordinates by decimal GPS format
    :param lat: latitude in DMS
    :param lat_ref: N/W/S/E
    :param long: longitude in DMS
    :param long_ref: N/W/S/E
    :return:
    """
    x = lat[0] + (lat[1] / 60) + (lat[2] / 3600)
    y = long[0] + (long[1] / 60) + (long[2] / 60)
    if lat_ref == 'S' or lat_ref == 'W':
        if long_ref == 'S' or long_ref == 'W':
            return -x, -y
        return -x, y
    elif long_ref == 'S' or long_ref == 'W':
        return x, -y
    else:
        return x, y


def list_gps_coordinates(list_files):
    coordinates_x = [()]
    coordinates_y = [()]
    for file in list_files:
        lat, lat_ref, long, long_ref = get_coordinates_photo(file)
        x, y = convert_gps(lat, lat_ref, long, long_ref)
        coordinates_x.append(x)
        coordinates_y.append(y)
    coordinates_x = list(map(float, coordinates_x))
    coordinates_y = list(map(float, coordinates_y))
    return coordinates_x, coordinates_y


def get_photo():
    list_fichiers = []
    for repertory, sous_repertory, files in os.walk('.'):
        for name in files:
            if re.match(".+\\.([jJ][pP][gG])", name):
                list_fichiers.append(os.path.join(repertory, name))
    return list_fichiers


def get_index(list_fichiers):
    index = 0
    list_index = []
    ref = get_code(list_fichiers[0])
    for fichier in list_fichiers:
        code = get_code(fichier)
        if code != ref:
            ref = code
            list_index.append(index)
        index += 1
    return list_index


def handle_photo(res):
    """

    :param res:
    :return:
    """
    photos = get_photo()
    list_index = get_index(photos)
    list_pts = []
    prev = 0
    if len(list_index) == 0:
        xs, ys = list_gps_coordinates(photos)
        list_pts = clean_cloud(xs, ys)
        x, y = convexHull(list_pts, len(list_pts))
        x.append(x[0])
        y.append(y[0])
        add_in_csv(x, y, res, get_code(photos))
        print("added in csv, withe the code : ", get_code(photos[prev]))
    else:
        for i in list_index:
            print("coucou")
            list_pts = list_gps_coordinates(photos[prev:i])
            x, y = convexHull(list_pts, len(list_pts))
            x.append(x[0])
            y.append(y[0])
            add_in_csv(x, y, res, get_code(photos[prev]))
            print("added in csv, withe the code : ", get_code(photos[prev]))
            prev = i
        list_pts.append(list_gps_coordinates(photos[prev:]))


def handle_csv(res):
    """

    :param res:
    :return:
    """
    non_traites = ([])
    # list of all the files who going to be processed
    list_files = search_for_files()
    # iterate on all the list_file list
    for fichier in list_files:
        #  take the coordinates
        # print("current file :", fichier)
        list_pts_xs, list_pts_ys = process_files(fichier)
        # clean the cloud, because we don't need all the points. The analysis will be faster with a smaller cloud
        points, n, list_pts_x, list_pts_y = clean_cloud(list_pts_xs, list_pts_ys)

        # applies the algorithm on the cleaned list
        if n < 3:
            non_traites.append(fichier)
            # print("not enough points, skipping...")
            continue
        x, y = convexHull(points, n)

        # add the first points at the end, so we have a complete polygon when plotting it
        x.append(x[0])
        y.append(y[0])
        # add the coordinates at the end of the results file, with the project code in the third column
        add_in_csv(x, y, resultats, get_code(fichier))
    if len(non_traites) == 0:
        print("tous les fichiers ont été traités !")
    else:
        print("ces fichiers n'ont pas été traités, par manque de points ou synthaxe incorrecte.")
        for fichier in non_traites:
            print(fichier)


if __name__ == '__main__':
    resultats = open('results.csv', 'w+', newline='')
    handle_photo(resultats)
    # get_coordinates_photo('photos/DJI_20220323125044_0001.JPG')
    # handle_csv(resultats)
    resultats.close()

    """non_traites = ([])
    resultats = open('results.csv', 'w+', newline='')
    # if the results directory does not exist, create it
    if not os.path.exists('results'):
        os.mkdir('results')
    # list of all the files who going to be processed
    list_files = search_for_files()

    to_plot_x = []
    to_plot_y = []
    # iterate on all the list_file list
    for fichier in list_files:
        #  take the coordinates
        # print("current file :", fichier)
        list_pts_xs, list_pts_ys = process_files(fichier)
        # clean the cloud, because we don't need all the points. The analysis will be faster with a smaller cloud
        points, n, list_pts_x, list_pts_y = clean_cloud(list_pts_xs, list_pts_ys)

        # applies the algorithm on the cleaned list
        if n < 3:
            non_traites.append(fichier)
            # print("not enough points, skipping...")
            continue
        x, y = convexHull(points, n)

        # add the first points at the end, so we have a complete polygon when plotting it
        x.append(x[0])
        y.append(y[0])


        to_plot_x.append(x)
        to_plot_y.append(y)

        # add the result coordinates to a new csv file in the result directory
        write_in_csv(x, y, fichier)
        # add the coordinates at the end of the results file, with the project code in the third column
        add_in_csv(x, y, resultats, get_code(fichier))

        # --- can be removed START ---
        # plot the points and their result with matplotlib
        # plt.scatter(list_pts_x, list_pts_y, color='blue')
        name = get_name(fichier)
        plt.plot(x, y, label="courbe " + name)
        # plt.legend()
        # plt.show()
        # --- END ---

    if len(non_traites) == 0:
        print("tous les fichiers ont été traités !")
    else:
        print("ces fichiers n'ont pas été traités, par manque de points ou synthaxe incorrecte.")
        for fichier in non_traites:
            print(fichier)

    resultats.close()
    # --- can be removed START ---
    axes = plt.gca()
    axes.set_xlim(45000, 100000)
    axes.set_ylim(55000, 110000)
    plt.show()
    # --- END ---"""
