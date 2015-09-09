import datetime
import calendar
from luna.common.exceptions import InputException, ConsistencyException
import pytz
from luna.datatypes.auxiliary import Interval


#--------------------------
#    Logger
#--------------------------

import logging
logger = logging.getLogger(__name__)


#--------------------------
#    Notation
#--------------------------

# varname_dt = datetime
# vartime_s = seconds
# vartime_ms = milliseconds


#--------------------------
#    Time now and init
#--------------------------


def now_t():
    '''Return the current time in epoch seconds'''
    return now_s()
    
def now_s():
    '''Return the current time in epoch seconds'''
    return calendar.timegm(now_dt().utctimetuple())

def now_dt(tzinfo='UTC'):
    '''Return the current time in datetime format'''
    if tzinfo != 'UTC':
        raise NotImplementedError()
    return datetime.datetime.utcnow().replace(tzinfo = pytz.utc)

def dt(*args, **kwargs):
    '''Initialize a datetime object in the proper way. Using the standard datetime leads to a lot of
     problems with the tz package. Also, it forces UTC timezone if no timezone is specified'''

    tzinfo  = kwargs.pop('tzinfo', None)
    trustme = kwargs.pop('trustme', None)

    if (tzinfo is None):
        # Force UTC if None
        timezone = timezonize('UTC')
        
    else:
        timezone = timezonize(tzinfo)
    
    time_dt = timezone.localize(datetime.datetime(*args))

    # Check consistency    
    if not trustme and timezone != pytz.UTC:
        if not check_dt_consistency(time_dt):
            raise InputException('Sorry, time {} does not exists on timezone {}'.format(time_dt, timezone))

    return  time_dt


#--------------------------
#    Timezone-related
#--------------------------

def check_dt_consistency(date_dt):
    '''Check that the timezone is consistent with the datetime (some conditions in Python lead to have summertime set in winter)'''

    # https://en.wikipedia.org/wiki/Tz_database
    # https://www.iana.org/time-zones
    
    if date_dt.tzinfo is None:
        return True
    else:
        
        # This check is quite heavy but there is apparently no other way to do it.
        if date_dt.utcoffset() != dt_from_s(s_from_dt(date_dt), tz=date_dt.tzinfo).utcoffset():
            return False
        else:
            return True


def correct_dt_dst(datetime_obj):
    '''Check that the dst is correct and if not change it'''

    # https://en.wikipedia.org/wiki/Tz_database
    # https://www.iana.org/time-zones

    if datetime_obj.tzinfo is None:
        return datetime_obj

    # Create and return a New datetime object. This corrects the DST if errors are present.
    return dt(datetime_obj.year,
              datetime_obj.month,
              datetime_obj.day,
              datetime_obj.hour,
              datetime_obj.minute,
              datetime_obj.second,
              datetime_obj.microsecond,
              tzinfo=datetime_obj.tzinfo)


def timezonize(timezone):
    '''Convert a string representation of a timezone to its pytz object or do nothing if the argument is already a pytz timezone'''
    
    # Check if timezone is a valid pytz object is hard as it seems that they are spread arount the pytz package.
    # Option 1): Try to convert if string or unicode, else try to
    # instantiate a datetiem object with the timezone to see if it is valid 
    # Option 2): Get all memebers of the pytz package and check for type, see
    # http://stackoverflow.com/questions/14570802/python-check-if-object-is-instance-of-any-class-from-a-certain-module
    # Option 3) perform a hand.made test. We go for this one, tests would fail if it gets broken
    
    if not 'pytz' in str(type(timezone)):
        timezone = pytz.timezone(timezone)
    return timezone


#--------------------------
#    Conversions
#--------------------------
 
def dt_from_t(timestamp_s, tz=None):
    '''Create a datetime object from an epoch timestamp in seconds. If no timezone is given, UTC is assumed'''
    # TODO: check if uniform everything on this one or not.
    return dt_from_s(timestamp_s=timestamp_s, tz=tz)
    

def dt_from_s(timestamp_s, tz=None):
    '''Create a datetime object from an epoch timestamp in seconds. If no timezone is given, UTC is assumed'''

    if not timestamp_s:
        raise InputException("timestamp not set")

    if not tz:
        tz = "UTC"
    try:
        timestamp_dt = datetime.datetime.utcfromtimestamp(float(timestamp_s))
    except TypeError:
        raise InputException('timestamp_s argument must be string or number, got {}'.format(type(timestamp_s)))

    pytz_tz = timezonize(tz)
    timestamp_dt = timestamp_dt.replace(tzinfo=pytz.utc).astimezone(pytz_tz)
    
    return timestamp_dt


def s_from_dt(dt):
    '''Returns seconds with floating point for milliseconds/microseconds.'''
    
    assert(isinstance(dt, datetime.datetime))
    microseconds_part = (dt.microsecond/1000000.0) if dt.microsecond else 0
    return  ( calendar.timegm(dt.utctimetuple()) + microseconds_part)


class TimeInterval(Interval):
    ''' A time interval is much more complicated than a Inteval as we have also the logical intervals (months, for example)'''
    
    LOGICAL  = 'Logical'
    PHYSICAL = 'Phyisical'
    
    # NOT ref to https://docs.python.org/2/library/datetime.html  %d, %m, %w %y - %H, %M, %S
    # Instead: M, D, Y, W - h m s
    
    mapping_table = {  'Y': 'years',
                       'M': 'months',
                       'W': 'weeks',
                       'D': 'days',
                       'h': 'hours',
                       'm': 'minutes',
                       's': 'seconds',
                       'u': 'microseconds'
                      }

    
    
    def __init__(self, string=None, years=0, weeks=0, months=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0):

        if string and (years or months or days or hours or minutes or seconds or microseconds):
            raise InputException('Choose between string init and explicit setting of years,months, days, hours etc.')

        self.years        = years
        self.months       = months
        self.weeks        = weeks
        self.days         = days
        self.hours        = hours
        self.minutes      = minutes 
        self.seconds      = seconds
        self.microseconds = microseconds

        if string:  
            self.strings = string.split("_")
            #if len (self.strings) > 1:
            #    raise InputException('Complex time intervals are not yet supported')

            import re
            regex = re.compile('^([0-9]+)([YMDWhmsu]{1,2})$')
            
            for string in self.strings:
                try:
                    groups   =  regex.match(string).groups()
                except AttributeError:
                    raise InputException('Error, got unknow interval ({})'.format(string))

                setattr(self, self.mapping_table[groups[1]], int(groups[0]))


    def __repr__(self):
        return self.string


    def __add__(self, other):
        
        if isinstance(other, self.__class__):
            
            return TimeInterval( years        = self.years + other.years,
                                 months       = self.months + other.months,
                                 weeks        = self.weeks + other.weeks,
                                 days         = self.days + other.days,
                                 hours        = self.hours + other.hours,
                                 minutes      = self.minutes + other.minutes,
                                 seconds      = self.seconds + other.seconds,
                                 microseconds = self.microseconds + other.microseconds)

        elif isinstance(other, datetime.datetime):
            
            if not other.tzinfo:
                raise InputException('Timezone of the datetime to sum with is required')

            return self.shift_dt(other, times=1)

    
    def __radd__(self, other):
        return self.__add__(other)

    @property
    def string(self):

        string = ''
        if self.years: string += str(self.years)               + 'Y' + '_'
        if self.months: string += str(self.months)             + 'M' + '_'
        if self.weeks: string += str(self.weeks)               + 'W' + '_'
        if self.days: string += str(self.days)                 + 'D' + '_'
        if self.hours: string += str(self.hours)               + 'h' + '_'
        if self.minutes: string += str(self.minutes)           + 'm' + '_'
        if self.seconds: string += str(self.seconds)           + 's' + '_'
        if self.microseconds: string += str(self.microseconds) + 'u' + '_'

        string = string[:-1]
        return string

    def is_composite(self):
        
        types = 0
        for item in self.mapping_table:
            if getattr(self, self.mapping_table[item]): types +=1
        
        return True if types > 1 else False 

    @property
    def type(self):
        '''Returns the type of the TimeInterval.
         - Physical if hours, minutes, seconds, micorseconds
         - Logical if Years, Months, Days, Weeks
        The difference? Years, Months, Days, Weeks have different lenghts depending ont he starting date.
        '''

        if self.years or self.months or self.weeks or self.days:
            return self.LOGICAL
        elif self.hours or self.minutes or self.seconds or self.microseconds:
            return self.PHYSICAL
        else:
            raise ConsistencyException('Error, TimeSlot not initialized?!')
        

    def round_dt(self, time_dt, how = None):
        '''Round a datetime according to this TimeInterval. Only simple time intervals are supported in this operation'''

        if self.is_composite():
            raise InputException('Sorry, only simple time intervals are supported byt he rebase operation')

        if not time_dt.tzinfo:
            raise InputException('Timezone of the datetime is required')    
        
        # Convert input time to seconds
        time_s = s_from_dt(time_dt)
        
        #-------------------------
        # Physical time 
        #-------------------------
        if self.type == self.PHYSICAL:
            
            # Get TimeInterval duration in seconds
            timeInterval_s = self.duration_s(time_dt)

            # Apply modular math:
            time_floor_s = time_s - (time_s % timeInterval_s)
            time_ceil_s   = time_floor_s + timeInterval_s
            
            if how == 'floor':
                time_rounded_s = time_floor_s
             
            elif how == 'ceil':
                time_rounded_s = time_ceil_s
            
            else:
                raise NotImplementedError('Easy to implement but no time. Take vcare about pre-1970 times (negative sign)')
                # The following does not work
                #time_rounded_s = time_floor_s if ( time_s < ( time_s + abs(time_ceil_s - time_floor_s)/2) ) else time_ceil_s
                
        #-------------------------
        # Logical time 
        #-------------------------
        elif self.type == self.LOGICAL:
            raise NotImplementedError('Logical not yet implemented')

        #-------------------------
        # Other (Consistency error)
        #-------------------------
        else:
            raise ConsistencyException('Error, TimeSlot type not PHYSICAL nor LOGICAL?!')

        return dt_from_s(time_rounded_s, tz=time_dt.tzinfo)


    def floor_dt(self, time_dt):
        '''Floor a datetime according to this TimeInterval. Only simple time intervals are supported in this operation'''       
        return self.round_dt(time_dt, how='floor')
 
    
    def ceil_dt(self, time_dt):
        '''Ceil a datetime according to this TimeInterval. Only simple time intervals are supported in this operation'''        
        return self.round_dt(time_dt, how='ceil')

    def rebase_dt(self, time_dt):
        '''Rebase a given datetime to this TimeInterval. Only simple time intervals are supported in this operation'''
        return self.round_dt(time_dt, how='floor')
              
    def shift_dt(self, time_dt, times=0):
        '''Shift a given datetime of n times of this TimeInterval. Only simple time intervals are supported in this operation'''
        if self.is_composite():
            raise InputException('Sorry, only simple time intervals are supported byt he rebase operation')
 
        # Convert input time to seconds
        time_s = s_from_dt(time_dt)
         
        #-------------------------
        # Physical time TimeSlot
        #-------------------------
        if self.type == self.PHYSICAL:
            
            # Get TimeInterval duration in seconds
            timeInterval_s = self.duration_s(time_dt)

            time_shifted_s = time_s + ( timeInterval_s * times )
            time_shifted_dt = dt_from_s(time_shifted_s, tz=time_dt.tzinfo)

        #-------------------------
        # Logical time TimeSlot
        #-------------------------
        elif self.type == self.LOGICAL:
            raise NotImplementedError('Shifting of Logical intervals not yet implemented')

        #-------------------------
        # Other (Consistency error)
        #-------------------------
        else:
            raise ConsistencyException('Error, TimeSlot type not PHYSICAL nor LOGICAL?!')
 
        return time_shifted_dt      

    def duration_s(self, time_dt):
        '''Get the duration of the interval in seconds'''
        if self.is_composite():
            raise InputException('Sorry, only simple time intervals are supported by this operation')

        if self.type == 'Logical' and not time_dt:
            raise InputException('With a logical TimeInterval you can ask for duration only if you provide the starting point')
        
        if self.type == 'Logical':
            raise NotImplementedError()

        # Hours. Minutes, Seconds
        if self.hours:
            timeInterval_s = self.hours * 60 * 60
        if self.minutes:
            timeInterval_s = self.minutes * 60
        if self.seconds:
            timeInterval_s = self.seconds
        if self.microseconds:
            timeInterval_s = 1/1000000.0 * self.microseconds
               
        return timeInterval_s
        
    @property
    def duration(self):
        if self.type == 'Logical':
            raise InputException('Sorry, the duration of a logical time interval is not defined. use duration_s() providing the starting point.')
        return self.duration_s()












