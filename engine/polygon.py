"""Polygon, line and point algorithms

The main public functions are:
    separate_points_by_polygon: Fundamental clipper
    intersection: Determine intersections of lines

Some more specific or helper functions include:
    inside_polygon
    is_inside_polygon
    outside_polygon
    is_outside_polygon
    point_on_line
"""

import numpy
from math import sqrt
from random import uniform, seed as seed_function

from numerics import ensure_numeric


def separate_points_by_polygon(points, polygon,
                               closed=True,
                               check_input=True):
    """Determine whether points are inside or outside a polygon

    Input:
       points - Tuple of (x, y) coordinates, or list of tuples
       polygon - list of vertices of polygon
       closed - (optional) determine whether points on boundary should be
       regarded as belonging to the polygon (closed = True)
       or not (closed = False)
       check_input: Allows faster execution if set to False

    Outputs:
       indices: array of same length as points with indices of points falling
       inside the polygon listed from the beginning and indices of points
       falling outside listed from the end.

       count: count of points falling inside the polygon

       The indices of points inside are obtained as indices[:count]
       The indices of points outside are obtained as indices[count:]

    Examples:
       U = [[0,0], [1,0], [1,1], [0,1]]  # Unit square

       separate_points_by_polygon( [[0.5, 0.5], [1, -0.5], [0.3, 0.2]], U)
       will return the indices [0, 2, 1] and count == 2 as only the first
       and the last point are inside the unit square

    Remarks:
       The vertices may be listed clockwise or counterclockwise and
       the first point may optionally be repeated.
       Polygons do not need to be convex.
       Polygons can have holes in them and points inside a hole is
       regarded as being outside the polygon.

    Algorithm is based on work by Darel Finley,
    http://www.alienryderflex.com/polygon/

    """

    if check_input:
        # Input checks
        msg = 'Keyword argument "closed" must be boolean'
        assert isinstance(closed, bool), msg

        try:
            points = ensure_numeric(points, numpy.float)
        except Exception, e:
            msg = ('Points could not be converted to numeric array: %s'
                   % str(e))
            raise Exception(msg)

        try:
            polygon = ensure_numeric(polygon, numpy.float)
        except Exception, e:
            msg = ('Polygon could not be converted to numeric array: %s'
                   % str(e))
            raise Exception(msg)

        msg = 'Polygon array must be a 2d array of vertices'
        assert len(polygon.shape) == 2, msg

        msg = 'Polygon array must have two columns'
        assert polygon.shape[1] == 2, msg

        msg = ('Points array must be 1 or 2 dimensional. '
               'I got %d dimensions' % len(points.shape))
        assert 0 < len(points.shape) < 3, msg

        if len(points.shape) == 1:
            # Only one point was passed in. Convert to array of points.
            points = numpy.reshape(points, (1, 2))

            msg = ('Point array must have two columns (x,y), '
                   'I got points.shape[1]=%d' % points.shape[0])
            assert points.shape[1] == 2, msg

            msg = ('Points array must be a 2d array. I got %s...'
                   % str(points[:30]))
            assert len(points.shape) == 2, msg

            msg = 'Points array must have two columns'
            assert points.shape[1] == 2, msg

    N = polygon.shape[0]  # Number of vertices in polygon
    M = points.shape[0]  # Number of points

    indices = numpy.zeros(M, numpy.int)

    count = _separate_points_by_polygon(points, polygon, indices,
                                        closed=closed)

    # log.critical('Found %d points (out of %d) inside polygon' % (count, M))

    return indices, count


def _separate_points_by_polygon(points, polygon, indices,
                                closed):
    """Underlying algorithm to partition point according to polygon

    Old C-code converted to Python
    FIXME(Ole): Refactor into numpy code
    """

    # Suppress numpy warnings (as we'll be dividing by zero)
    original_numpy_settings = numpy.seterr(invalid='ignore', divide='ignore')

    # FIXME: Pass these in
    rtol = 0.0
    atol = 0.0

    # Get polygon extents to quickly rule out points that
    # are outside its bounding box
    minpx = min(polygon[:, 0])
    maxpx = max(polygon[:, 0])
    minpy = min(polygon[:, 1])
    maxpy = max(polygon[:, 1])

    M = points.shape[0]
    N = polygon.shape[0]

    x = points[:, 0]
    y = points[:, 1]

    # Vector keeping track of which points are inside
    inside = numpy.zeros(M, dtype=numpy.int)  # All assumed outside initially

    # Mask for points can be considered for inclusion
    candidates = numpy.ones(M, dtype=numpy.bool)  # All True initially

    # Only work on those that are inside polygon bounding box
    # FIXME (Ole): TODO this optimisation later
    #outside_box = (x > maxpx) + (x < minpx) + (y > maxpy) + (y < minpy)
    #inside_box = -outside_box
    #ipoints = points[inside_box]

    # Find points on polygon boundary
    for i in range(N):

        #if not numpy.sometrue(candidates):
        #    break

        # Loop through polygon vertices
        j = (i + 1) % N

        px_i = polygon[i, 0]
        py_i = polygon[i, 1]
        px_j = polygon[j, 0]
        py_j = polygon[j, 1]

        # Select those that are on the boundary FIXME: restrict to inside box
        boundary_points = point_on_line(points,
                                        [[px_i, py_i], [px_j, py_j]],
                                        rtol, atol)

        if closed:
            inside[boundary_points] = 1
        else:
            inside[boundary_points] = 0

        # Remove boundary point from further analysis
        candidates[boundary_points] = False

    #print 'masih ada', candidates, inside

    # Algorithm for finding points inside polygon
    for i in range(N):
        #print i, j

        #print 'inside', inside

        #if not numpy.sometrue(candidates):
        #    break

        # Loop through polygon vertices
        j = (i + 1) % N

        px_i = polygon[i, 0]
        py_i = polygon[i, 1]
        px_j = polygon[j, 0]
        py_j = polygon[j, 1]

        # Intersection formula
        sigma = (y - py_i) / (py_j - py_i) * (px_j - px_i)
        seg_i = (py_i < y) * (py_j >= y)
        seg_j = (py_j < y) * (py_i >= y)
        mask = (px_i + sigma < x) * (seg_i + seg_j) * candidates

        inside[mask] = 1 - inside[mask]

    # Restore numpy warnings
    numpy.seterr(**original_numpy_settings)

    # Record point as either inside or outside
    # FIXME (Ole): this is just for backwards compatibility
    inside_index = 0  # Keep track of points inside
    outside_index = M - 1  # Keep track of points outside (starting from end)

    for k in range(M):
        if inside[k] == 1:
            indices[inside_index] = k
            inside_index += 1
        else:
            indices[outside_index] = k
            outside_index -= 1

    return inside_index


def _separate_points_by_polygon_python(points, polygon, indices,
                                       closed):
    """Underlying algorithm to partition point according to polygon

    Old C-code converted to Python
    This is not using numpy code - available for testing only
    """

    # FIXME: Pass these in
    rtol = 0.0
    atol = 0.0

    # Get polygon extents to quickly rule out points that
    # are outside its bounding box
    minpx = min(polygon[:, 0])
    maxpx = max(polygon[:, 0])
    minpy = min(polygon[:, 1])
    maxpy = max(polygon[:, 1])

    M = points.shape[0]
    N = polygon.shape[0]

    inside_index = 0  # Keep track of points inside
    outside_index = M - 1  # Keep track of points outside (starting from end)

    # Begin main loop (for each point) - FIXME (write as vector ops)
    for k in range(M):
        x = points[k, 0]
        y = points[k, 1]
        inside = 0

        if x > maxpx or x < minpx or y > maxpy or y < minpy:
            #  Skip if point is outside polygon bounding box
            pass
        else:
            # Check if it is inside polygon
            for i in range(N):
                # Loop through polygon vertices
                j = (i + 1) % N

                px_i = polygon[i, 0]
                py_i = polygon[i, 1]
                px_j = polygon[j, 0]
                py_j = polygon[j, 1]

                if point_on_line(points[k, :],
                                 [[px_i, py_i], [px_j, py_j]],
                                 rtol, atol):
                    #  Point coincides with line segment
                    if closed:
                        inside = 1
                    else:
                        inside = 0
                    break
                else:
                    # Check if truly inside polygon
                    if (((py_i < y) and (py_j >= y)) or
                        ((py_j < y) and (py_i >= y))):
                        sigma = (y - py_i) / (py_j - py_i) * (px_j - px_i)
                        if (px_i + sigma < x):
                            inside = 1 - inside

        # Record point as either inside or outside
        if inside == 1:
            indices[inside_index] = k
            inside_index += 1
        else:
            indices[outside_index] = k
            outside_index -= 1

    return inside_index


def point_on_line(points, line, rtol=1.0e-5, atol=1.0e-8):
    """Determine if a point is on a line segment

    Input
        points: Coordinates of either
                * one point given by sequence [x, y]
                * multiple points given by list of points or Nx2 array
        line: Endpoint coordinates [[x0, y0], [x1, y1]] or
              the equivalent 2x2 numeric array with each row corresponding
              to a point.
        rtol: Relative error for how close a point must be to be accepted
        atol: Absolute error for how close a point must be to be accepted

    Output
        True or False

    Notes

    Line can be degenerate and function still works to discern coinciding
    points from non-coinciding.

    Tolerances rtol and atol are used with numpy.allclose()
    """

    # Prepare input data
    points = ensure_numeric(points)
    line = ensure_numeric(line)

    if len(points.shape) == 1:
        # One point only - make into 1 x 2 array
        points = points[numpy.newaxis, :]
        one_point = True
    else:
        one_point = False

    msg = 'Argument points must be either [x, y] or an Nx2 array of points'
    assert len(points.shape) == 2, msg
    assert points.shape[0] > 0, msg
    assert points.shape[1] == 2, msg
    N = points.shape[0]  # Number of points

    x = points[:, 0]
    y = points[:, 1]
    x0, y0 = line[0]
    x1, y1 = line[1]

    # Vector from beginning of line to point
    a0 = x - x0
    a1 = y - y0

    # It's normal vector
    a_normal0 = a1
    a_normal1 = -a0

    # Vector parallel to line
    b0 = x1 - x0
    b1 = y1 - y0

    # Dot product
    nominator = abs(a_normal0 * b0 + a_normal1 * b1)
    denominator = b0 * b0 + b1 * b1

    # Determine if point vector is parallel to line up to a tolerance
    is_parallel = numpy.zeros(N, dtype=numpy.bool)  # All False
    is_parallel[nominator <= atol + rtol * denominator] = True

    # Determine for points parallel to line if they are within end points
    a0p = a0[is_parallel]
    a1p = a1[is_parallel]

    len_a = numpy.sqrt(a0p * a0p + a1p * a1p)
    len_b = numpy.sqrt(b0 * b0 + b1 * b1)
    cross = a0p * b0 + a1p * b1

    # Initialise result to all False
    result = numpy.zeros(N, dtype=numpy.bool)

    # Result is True only if a0 * b0 + a1 * b1 >= 0 and len_a <= len_b
    result[is_parallel] = (cross >= 0) * (len_a <= len_b)

    # Return either boolean scalar or boolean vector
    if one_point:
        assert len(result) == 1
        return result[0]
    else:
        return result


def is_inside_polygon(point, polygon, closed=True):
    """Determine if one point is inside a polygon

    See inside_polygon for more details
    """

    indices = inside_polygon(point, polygon, closed)

    if indices.shape[0] == 1:
        return True
    else:
        return False


def inside_polygon(points, polygon, closed=True):
    """Determine points inside a polygon

       Functions inside_polygon and outside_polygon have been defined in
       terms of separate_by_polygon which will put all inside indices in
       the first part of the indices array and outside indices in the last

       See separate_points_by_polygon for documentation

       points and polygon can be a geospatial instance,
       a list or a numeric array
    """

    indices, count = separate_points_by_polygon(points, polygon,
                                                closed=closed,
                                                check_input=True)

    # Return indices of points inside polygon
    return indices[:count]


def is_outside_polygon(point, polygon, closed=True):
    """Determine if one point is outside a polygon

    See outside_polygon for more details
    """

    indices = outside_polygon(point, polygon, closed=closed)

    if indices.shape[0] == 1:
        return True
    else:
        return False


def outside_polygon(points, polygon, closed=True):
    """Determine points outside a polygon

       Functions inside_polygon and outside_polygon have been defined in
       terms of separate_by_polygon which will put all inside indices in
       the first part of the indices array and outside indices in the last

       See separate_points_by_polygon for documentation
    """

    indices, count = separate_points_by_polygon(points, polygon,
                                                closed=closed,
                                                check_input=True)

    # Return indices of points outside polygon
    if count == len(indices):
        # No points are outside
        return numpy.array([])
    else:
        # Return indices for points outside (reversed)
        return indices[count:][::-1]


def in_and_outside_polygon(points, polygon, closed=True):
    """Separate a list of points into two sets inside and outside a polygon

    Input
        points: (tuple, list or array) of coordinates
        polygon: Set of points defining the polygon
        closed: Set to True if points on boundary are considered
                to be 'inside' polygon

    Output
        inside: Array of points inside the polygon
        outside: Array of points outside the polygon

    See separate_points_by_polygon for more documentation
    """

    indices, count = separate_points_by_polygon(points, polygon,
                                                closed=closed,
                                                check_input=True)

    if count == len(indices):
        # No points are outside
        return indices[:count], []
    else:
        # Return indices for points inside and outside (reversed)
        return  indices[:count], indices[count:][::-1]


#--------------------------------------------------
# Helper function to generate points inside polygon
#--------------------------------------------------
def populate_polygon(polygon, number_of_points, seed=None, exclude=None):
    """Populate given polygon with uniformly distributed points.

    Input:
       polygon - list of vertices of polygon
       number_of_points - (optional) number of points
       seed - seed for random number generator (default=None)
       exclude - list of polygons (inside main polygon) from where points
                 should be excluded

    Output:
       points - list of points inside polygon

    Examples:
       populate_polygon( [[0,0], [1,0], [1,1], [0,1]], 5 )
       will return five randomly selected points inside the unit square
    """

    # Find outer extent of polygon
    max_x = min_x = polygon[0][0]
    max_y = min_y = polygon[0][1]
    for point in polygon[1:]:
        x = point[0]
        if x > max_x:
            max_x = x
        if x < min_x:
            min_x = x

        y = point[1]
        if y > max_y:
            max_y = y
        if y < min_y:
            min_y = y

    # Generate random points until enough are in polygon
    seed_function(seed)
    points = []
    while len(points) < number_of_points:
        x = uniform(min_x, max_x)
        y = uniform(min_y, max_y)

        append = False
        if is_inside_polygon([x, y], polygon):
            append = True

            #Check exclusions
            if exclude is not None:
                for ex_poly in exclude:
                    if is_inside_polygon([x, y], ex_poly):
                        append = False

        if append is True:
            points.append([x, y])

    return points


#------------------------------------
# Functionality for line intersection
#------------------------------------

def intersection(line0, line1, rtol=1.0e-5, atol=1.0e-8):
    """Returns intersecting point between two line segments.

    However, if parallel lines coincide partly (i.e. share a common segment),
    the line segment where lines coincide is returned

    Inputs:
        line0, line1: Each defined by two end points as in:
                      [[x0, y0], [x1, y1]]
                      A line can also be a 2x2 numpy array with each row
                      corresponding to a point.

    Output:
        status, value - where status and value is interpreted as follows:
        status == 0: no intersection, value set to None.
        status == 1: intersection point found and returned in value as [x,y].
        status == 2: Collinear overlapping lines found.
                     Value takes the form [[x0,y0], [x1,y1]] which is the
                     segment common to both lines.
        status == 3: Collinear non-overlapping lines. Value set to None.
        status == 4: Lines are parallel. Value set to None.
    """

    line0 = ensure_numeric(line0, numpy.float)
    line1 = ensure_numeric(line1, numpy.float)

    x0, y0 = line0[0, :]
    x1, y1 = line0[1, :]

    x2, y2 = line1[0, :]
    x3, y3 = line1[1, :]

    denom = (y3 - y2) * (x1 - x0) - (x3 - x2) * (y1 - y0)
    u0 = (x3 - x2) * (y0 - y2) - (y3 - y2) * (x0 - x2)
    u1 = (x2 - x0) * (y1 - y0) - (y2 - y0) * (x1 - x0)

    if numpy.allclose(denom, 0.0, rtol=rtol, atol=atol):
        # Lines are parallel - check if they are collinear
        if numpy.allclose([u0, u1], 0.0, rtol=rtol, atol=atol):
            # We now know that the lines are collinear
            state = (point_on_line([x0, y0], line1, rtol=rtol, atol=atol),
                     point_on_line([x1, y1], line1, rtol=rtol, atol=atol),
                     point_on_line([x2, y2], line0, rtol=rtol, atol=atol),
                     point_on_line([x3, y3], line0, rtol=rtol, atol=atol))

            return collinearmap[state]([x0, y0], [x1, y1],
                                       [x2, y2], [x3, y3])
        else:
            # Lines are parallel but aren't collinear
            return 4, None  # FIXME (Ole): Add distance here instead of None
    else:
        # Lines are not parallel, check if they intersect
        u0 = u0 / denom
        u1 = u1 / denom

        x = x0 + u0 * (x1 - x0)
        y = y0 + u0 * (y1 - y0)

        # Sanity check - can be removed to speed up if needed
        assert numpy.allclose(x, x2 + u1 * (x3 - x2), rtol=rtol, atol=atol)
        assert numpy.allclose(y, y2 + u1 * (y3 - y2), rtol=rtol, atol=atol)

        # Check if point found lies within given line segments
        if 0.0 <= u0 <= 1.0 and 0.0 <= u1 <= 1.0:
            # We have intersection
            return 1, numpy.array([x, y])
        else:
            # No intersection
            return 0, None


# Result functions used in intersection() below for possible states
# of collinear lines
# (p0,p1) defines line 0, (p2,p3) defines line 1.

def lines_dont_coincide(p0, p1, p2, p3):
    return 3, None


def lines_0_fully_included_in_1(p0, p1, p2, p3):
    return 2, numpy.array([p0, p1])


def lines_1_fully_included_in_0(p0, p1, p2, p3):
    return 2, numpy.array([p2, p3])


def lines_overlap_same_direction(p0, p1, p2, p3):
    return 2, numpy.array([p0, p3])


def lines_overlap_same_direction2(p0, p1, p2, p3):
    return 2, numpy.array([p2, p1])


def lines_overlap_opposite_direction(p0, p1, p2, p3):
    return 2, numpy.array([p0, p2])


def lines_overlap_opposite_direction2(p0, p1, p2, p3):
    return 2, numpy.array([p3, p1])


# This function called when an impossible state is found
def lines_error(p1, p2, p3, p4):
    msg = ('Impossible state: p1=%s, p2=%s, p3=%s, p4=%s'
           % (str(p1), str(p2), str(p3), str(p4)))
    raise RuntimeError(msg)

# Mapping to possible states for line intersection
#
#                 0s1    0e1    1s0    1e0   # line 0 starts on 1, 0 ends 1,
#                                                   1 starts 0, 1 ends 0
collinearmap = {(False, False, False, False): lines_dont_coincide,
                (False, False, False, True): lines_error,
                (False, False, True, False): lines_error,
                (False, False, True, True): lines_1_fully_included_in_0,
                (False, True, False, False): lines_error,
                (False, True, False, True): lines_overlap_opposite_direction2,
                (False, True, True, False): lines_overlap_same_direction2,
                (False, True, True, True): lines_1_fully_included_in_0,
                (True, False, False, False): lines_error,
                (True, False, False, True): lines_overlap_same_direction,
                (True, False, True, False): lines_overlap_opposite_direction,
                (True, False, True, True): lines_1_fully_included_in_0,
                (True, True, False, False): lines_0_fully_included_in_1,
                (True, True, False, True): lines_0_fully_included_in_1,
                (True, True, True, False): lines_0_fully_included_in_1,
                (True, True, True, True): lines_0_fully_included_in_1}
