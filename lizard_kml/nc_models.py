from django.conf import settings
import netCDF4
import datetime

# Copied from openearthtools/kmldap
from numpy import any, all, ma, apply_along_axis, nonzero, array, isnan
from scipy.interpolate import interp1d
from functools import partial


class Transect(object):
    """Transect that has coordinates and time"""
    def __init__(self, id):
        self.id = id
        # x and y can be lat,lon, we don't care here...
        self.x = array([])
        self.y = array([])
        self.z = array([])
        self.t = array([])
        # Cross shore is the local (engineering) coordinate system
        # or engineering datum, see for example:
        # http://en.wikipedia.org/wiki/Datum_(geodesy)#Engineering_datums
        self.cross_shore = array([])

    def begindates(self):
        return [date for date in self.t]

    def enddates(self):
        return [date.replace(year=date.year+1) for date in self.t]

    def interpolate_z(self):
        """interpolate over missing z values"""
        if not self.z.any():
            return self.z
        def fillmissing(x,y):
            """fill nans in y using linear interpolation"""
            f = interp1d(x[~isnan(y)], y[~isnan(y)], kind='linear',bounds_error=False, copy=True)
            new_y = f(list(x)) #some bug causes it not to work if x is passed directly
            return new_y
        # define an intorpolation for a row by partial function application
        rowinterp = partial(fillmissing, self.cross_shore)
        # apply to rows (along columns)
        z = apply_along_axis(rowinterp, 1, self.z)
        # mask missings
        z = ma.masked_array(z, mask=isnan(z))
        return z


class PointCollection(object):
    def __init__(self):
        self.id = array([])
        self.x = array([])
        self.y = array([])
        self.z = array([])


# Some factory functions, because the classes are dataset unaware (they were also used by other EU countries)
# @cache.beaker_cache('id', expire=60)
def makejarkustransect(kml_args_dict):
    """Make a transect object, given an id (1000000xareacode + alongshore distance)"""
    id = kml_args_dict['id']
    # TODO: Dataset does not support with ... as dataset, this can lead to too many open ports if datasets are not closed, for whatever reason
    dataset = netCDF4.Dataset(settings.NC_RESOURCE)
    tr = Transect(id)

    # Opendap is index based, so we have to do some numpy tricks to get the data over (and fast)
    # read indices for all years (only 50 or so), takes 0.17 seconds on my wireless
    years = dataset.variables['time'][:]
    # read all indices (this would be nice to cache)... takes 0.24 seconds on my wireless
    id = dataset.variables['id'][:] 
    alongshoreindex = nonzero(id == tr.id)
    alongshoreindex = alongshoreindex[0][0]
    lon = dataset.variables['lon'][alongshoreindex,:] 
    lat = dataset.variables['lat'][alongshoreindex,:] 
    #filter out the missing to make it a bit smaller
    z = dataset.variables['altitude'][:,alongshoreindex,:]
    filter = z == dataset.variables['altitude']._FillValue # why are missings not taken into account?
    z[filter] = None
    # convert to datetime objects. (netcdf only stores numbers, we use years here (ignoring the measurement date))
    t = array([datetime.datetime.fromtimestamp(days*3600*24) for days in years])
    cross_shore = dataset.variables['cross_shore'][:]
    # leave out empty crossections and empty dates
    tr.lon = lon[(~filter).any(0)]
    tr.lat = lat[(~filter).any(0)]
    # keep what is not filtered in 2 steps 
    #         [over x            ][over t            ]
    tr.z = z[:,(~filter).any(0)][(~filter).any(1),:] 
    tr.t = t[(~filter).any(1)]
    tr.cross_shore = cross_shore[(~filter).any(0)]

    # get the water level variables
    mhw = dataset.variables['mean_high_water'][alongshoreindex]
    mlw = dataset.variables['mean_low_water'][alongshoreindex]
    tr.mhw = mhw.squeeze()
    tr.mlw = mlw.squeeze()

    dataset.close()
    return tr


#TODO: @cache.beaker_cache(None, expire=600)
def makejarkusoverview(kml_args_dict):
    dataset = netCDF4.Dataset(settings.NC_RESOURCE, 'r')
    points = PointCollection()
    id = dataset.variables['id'][:] # ? why
    # Get the locations of the beach poles..
    lon = dataset.variables['rsp_lon'][:] #[:,rsp] #? can this be done simpler?
    lat = dataset.variables['rsp_lat'][:] #[:,rsp] #?
    points.id = id
    points.lon = lon
    points.lat = lat
    dataset.close()
    return points