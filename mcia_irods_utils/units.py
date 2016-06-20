import math

_units = {
    0 : 'B',
    1 : 'K',
    2 : 'M',
    3 : 'G',
    4 : 'T',
# be far-sighted ;)
    5 : 'P',
    6 : 'E',
}

_si_units = {
    0 : 'b',
    1 : 'k',
    2 : 'm',
    3 : 'g',
    4 : 't',
# be far-sighted ;)
    5 : 'p',
    6 : 'e',
}

class UnitConverter:
    def __init__( self, factor, symbol = "" ):
        self.factor = factor
        self.symbol = symbol

    def __call__( self, value ):
        value = value / ( self.factor )
        fmt = "{0:1f}{1}"
        if "{0:.1f}".format( value ).endswith( ".0" ): fmt = "{0:.0f}{1}"
        return fmt.format( value, self.symbol )

class DictUnitConverter( UnitConverter ):
    def __init__( self, dict_, base ):
        self.dict = dict_
        self.base = float( base )
        self.maxkey = max( self.dict )

    def __call__( self, value ):
        if value == 0:
            return "0" + self.dict[0]

        logvalue = min( int( math.log( value ) / math.log( self.base ) ), self.maxkey )

        unit = self.dict[logvalue]

        value = value / ( self.base ** logvalue )

        fmt = "{0:.1f}{1}"
        if "{0:.1f}".format( value ).endswith( ".0" ): fmt = "{0:.0f}{1}"

        return fmt.format( value, unit )

nounit = UnitConverter( 1 )

B = UnitConverter( 1024 ** 0, "B" )
K = UnitConverter( 1024 ** 1, "K" )
M = UnitConverter( 1024 ** 2, "M" )
G = UnitConverter( 1024 ** 3, "G" )
T = UnitConverter( 1024 ** 4, "T" )

h = DictUnitConverter( _units, 1024 )
si = DictUnitConverter( _si_units, 1000 )

def base_convert( base, converter ):
    for k, v in base.items():
        base[k] = converter( v )

def options_parser_add_size_units( parser, dest = "converter" ):
    parser.add_option( "-b", "--bytes", const = B,
                      action = "store_const", dest = dest, default = nounit,
                      help = "print sizes in bytes" )
    parser.add_option( "-k", const = K,
                      action = "store_const", dest = dest,
                      help = "print sizes in kilobytes" )
    parser.add_option( "-m", const = M,
                      action = "store_const", dest = dest,
                      help = "print sizes in megabytes" )
    parser.add_option( "-g", const = G,
                      action = "store_const", dest = dest,
                      help = "print sizes in gigabytes" )
    parser.add_option( "-t", const = T,
                      action = "store_const", dest = dest,
                      help = "print sizes in terabytes" )

    parser.add_option( "-H", "--human-readable", const = h,
                      action = "store_const", dest = dest,
                      help = "print sizes in human readable format (e.g., 1K 234M 2G)" )

    parser.add_option( "--si", const = si,
                      action = "store_const", dest = dest,
                      help = "like -H, but use powers of 1000 not 1024" )
