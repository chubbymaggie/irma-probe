import logging, binascii, json, encodings, pprint

from lib.common.oopatterns import Singleton
from lib.leveldict.leveldict import LevelDictSerialized

log = logging.getLogger(__name__)

##############################################################################
# serializers
##############################################################################

class NSRLSerializer(object):

    fields = None

    @classmethod
    def loads(cls, value):
        value = json.loads(value)
        if isinstance(value[0], list):
            result = map(lambda col: dict((field, col[index]) for index, field in enumerate(cls.fields)), value)
        else:
            result = dict((field, value[index]) for index, field in enumerate(cls.fields))
        return result

    @classmethod
    def dumps(cls, value):

        def detect_charset(string):
            import chardet
            return chardet.detect(string)['encoding']

        try:
            if isinstance(value, list):
                result = json.dumps(map(lambda row: map(lambda key: row.get(key), cls.fields), value))
            else:
                result = json.dumps(map(lambda col: value.get(col), cls.fields))
        except Exception as e:
            if isinstance(value, list):
                for index, row in enumerate(value):
                    for colkey, colval in row.items():
                        if not isinstance(colval, unicode):
                            charset = detect_charset(colval)
                            charset = 'unicode-escape' if not charset else charset
                            try:
                                row[colkey] = colval.decode(charset)
                            except:
                                row[colkey] = colval.decode('unicode-escape')
                result = json.dumps(map(lambda row: map(lambda key: row.get(key), cls.fields), value))
            else:
                for colkey, colval in value.items():
                    if not isinstance(colval, unicode):
                        # try to use chardet to find encoding
                        charset = detect_charset(colval)
                        charset = 'unicode-escape' if not charset else charset
                        try:
                            value[colkey] = value[colkey].decode(charset)
                        except:
                            # treat false positive from chardet
                            value[colkey] = value[colkey].decode('unicode-escape')
                result = json.dumps(map(lambda col: value.get(col), cls.fields))
        return result

class NSRLOsSerializer(NSRLSerializer):

    fields = ['OpSystemVersion', 'OpSystemName', 'MfgCode' ]

class NSRLFileSerializer(NSRLSerializer):

    fields = ["MD5", "CRC32", "FileName", "FileSize", "ProductCode", "OpSystemCode", "SpecialCode"]

    @classmethod
    def dumps(cls, value):
        
        def detect_charset(string):
            import chardet
            return chardet.detect(string)['encoding']

        try:
            if isinstance(value, list):
                result = json.dumps(map(lambda row: map(lambda key: row.get(key), cls.fields), value))
            else:
                result = json.dumps(map(lambda col: value.get(col), cls.fields))
        except Exception as e:
            # failed to json it, bruteforce encoding
            if isinstance(value, list):
                for index, row in enumerate(value):
                    if not isinstance(row['FileName'], unicode):
                        charset = detect_charset(row['FileName']) 
                        charset = 'unicode-escape' if not charset else charset
                        try: 
                            row['FileName'] = row['FileName'].decode(charset)
                        except:
                            # treat false positive from chardet
                            row['FileName'] = row['FileName'].decode('unicode-escape')
                result = json.dumps(map(lambda col: map(lambda key: col.get(key), cls.fields), value))
            else:
                if not isinstance(value['FileName'], unicode):
                    # try to use chardet to find encoding
                    charset = detect_charset(value['FileName'])
                    charset = 'unicode-escape' if not charset else charset
                    try:
                        value['FileName'] = value['FileName'].decode(charset)
                    except:
                        # treat false positive from chardet
                         value['FileName'] = value['FileName'].decode('unicode-escape')
                result = json.dumps(map(lambda col: value.get(col), cls.fields))
        return result


class NSRLManufacturerSerializer(NSRLSerializer):

    fields = [ "MfgName" ]

class NSRLProductSerializer(NSRLSerializer):

    fields = ["ProductName", "ProductVersion", "OpSystemCode", "MfgCode", "Language", "ApplicationType"]

##############################################################################
# NSRL records
##############################################################################

class NSRLLevelDict(LevelDictSerialized):

    key = None

    def __init__(self, db, serializer=json, **kwargs):
        super(NSRLLevelDict, self).__init__(db, serializer, **kwargs)

    @classmethod
    def create_database(cls, dbfile, records, **kwargs):
        # import specific modules
        from csv import DictReader

        log_threshold = 50000
        
        # create database
        db = cls(dbfile, **kwargs)
        # open csv files
        csv_file = open(records, 'r')
        csv_entries = DictReader(csv_file)

        for index, row in enumerate(csv_entries):
            key = row.pop(cls.key)
            value = db.get(key, None)
            if not value:
                db[key] = row
            else:
                if isinstance(value, dict):
                    db[key] = [value, row]
                else:
                    # db[key].append([row]) is not possible as changes are only
                    # made in memory and __setitem__ is never called
                    db[key] = value + [row]
            if (index % log_threshold) == 0:
                print("Current progress: {0}".format(index))

        return db

##############################################################################
# NSRL File Record
##############################################################################

class NSRLFile(NSRLLevelDict):

    key = "SHA-1"

    def __init__(self, db, **kwargs):
        super(NSRLFile, self).__init__(db, NSRLFileSerializer, **kwargs)

##############################################################################
# NSRL OS Record
##############################################################################

class NSRLOs(NSRLLevelDict):

    key = "OpSystemCode"

    def __init__(self, db, **kwargs):
        super(NSRLOs, self).__init__(db, NSRLOsSerializer, **kwargs)

##############################################################################
# NSRL OS Record
##############################################################################

class NSRLManufacturer(NSRLLevelDict):

    key = "MfgCode"

    def __init__(self, db, **kwargs):
        super(NSRLManufacturer, self).__init__(db, NSRLManufacturerSerializer, **kwargs)

##############################################################################
# NSRL Product Record
##############################################################################

class NSRLProduct(NSRLLevelDict):

    key = "ProductCode"

    def __init__(self, db, **kwargs):
        super(NSRLProduct, self).__init__(db, NSRLProductSerializer, **kwargs)

##############################################################################
# NSRL module
##############################################################################

class NSRL(object):

    def __init__(self, *args, **kwargs):
        # TODO: need to specify paths in constructor, temporary pass via kwargs
        self.nsrl_file = None
        self.nsrl_product = None
        self.nsrl_os = None
        self.nsrl_manufacturer = None
        # temporary hack to prevent error when nsrl db is not provided
        if reduce(lambda x, y: x and y, (kwargs[key] 
            for key in ['nsrl_file_db', 'nsrl_prod_db', 'nsrl_os_db', 'nsrl_mfg_db'])):
            self.nsrl_file = NSRLFile(kwargs['nsrl_file_db'])
            self.nsrl_product = NSRLProduct(kwargs['nsrl_prod_db'])
            self.nsrl_os = NSRLOs(kwargs['nsrl_os_db'])
            self.nsrl_manufacturer = NSRLManufacturer(kwargs['nsrl_mfg_db'])

    def _lookup_file(self, sha1sum):
        return self.nsrl_file[sha1sum]

    def _lookup_product(self, product_code):
        return self.nsrl_product[product_code]

    def _lookup_os(self, op_system_code):
        return self.nsrl_os[op_system_code]

    def _lookup_manufacturer(self, manufacturer_code):
        return self.nsrl_manufacturer[manufacturer_code]

    def lookup_by_sha1(self, sha1sum):
        operations = [
            ( sha1sum, 'SHA-1',        self.nsrl_file, None),
            ( None,    'ProductCode',  self.nsrl_product, 'SHA-1'), 
            ( None,    'OpSystemCode', self.nsrl_os, 'SHA-1'),
            ( None,    'MfgCode',      self.nsrl_manufacturer, 'ProductCode')
        ]
        entries = dict((name, {}) for (_, name, _, _) in operations)
        try:
            for value, key, database, where in operations:
                if value:
                    entries[key][value] = database[value]
                else:
                    subkeys = set()
                    for subkey, subitem in entries[where].items():
                        if not isinstance(subitem, list):
                            subitem = [subitem]
                        subkeys.update(map(lambda x: x[key], subitem))
                    for subkey in subkeys:
                        entries[key][subkey] = database[subkey]
        except:
            pass
        return entries

    # TODO: need to be moved into probe
    def ready(self):
        return reduce(lambda x, y: (x is not None) and (y is not None),
            [self.nsrl_file, self.nsrl_product, self.nsrl_os, self.nsrl_manufacturer])
 

##############################################################################
# CLI for debug purposes
##############################################################################

if __name__ == '__main__':

    ##########################################################################
    # local import 
    ##########################################################################

    import argparse

    ##########################################################################
    # defined functions
    ##########################################################################

    nsrl_databases = {
        'file'        : NSRLFile,
        'os'          : NSRLOs,
        'manufacturer': NSRLManufacturer,
        'product'     : NSRLProduct,
    }

    def nsrl_create_database(**kwargs):
        database_type = kwargs['type']
        nsrl_databases[database_type].create_database(kwargs['database'], kwargs['filename'])

    def nsrl_get(**kwargs):
        database_type = kwargs['type']
        database = nsrl_databases[database_type](kwargs['database'], block_cache_size=1<<30, max_open_files=3000)
        value = database.get(kwargs['key'])
        print("key {0}: value {1}".format(kwargs['key'], value))

    def nsrl_resolve(**kwargs):
        # TODO: handle in a better way NRSL object
        kwargs['nsrl_file_db'] = kwargs['file']
        kwargs['nsrl_prod_db'] = kwargs['product']
        kwargs['nsrl_os_db'] = kwargs['os']
        kwargs['nsrl_mfg_db'] = kwargs['manufacturer']
        handle = NSRL(**kwargs)
        print(pprint.pformat(handle.lookup_by_sha1(kwargs['sha1'])))

    ##########################################################################
    # arguments
    ##########################################################################

    # define command line arguments
    parser = argparse.ArgumentParser(description='NSRL database module CLI mode')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the create parser
    create_parser = subparsers.add_parser('create', help='create NSRL records into a database')
    create_parser.add_argument('-t' , '--type', type=str, choices=['file', 'os', 'manufacturer', 'product'], help='type of the record')
    create_parser.add_argument('filename', type=str, help='filename of the NSRL record')
    create_parser.add_argument('database', type=str, help='database to store NSRL records')
    create_parser.set_defaults(func=nsrl_create_database)

    # create the scan parser
    get_parser = subparsers.add_parser('get', help='get the entry from database')
    get_parser.add_argument('-t' , '--type', type=str, choices=['file', 'os', 'manufacturer', 'product'], help='type of the record')
    get_parser.add_argument('database', type=str, help='database to read NSRL records')
    get_parser.add_argument('key', type=str, help='key to retreive')
    get_parser.set_defaults(func=nsrl_get)

    # create the scan parser
    get_parser = subparsers.add_parser('resolve', help='resolve from sha1')
    get_parser.add_argument('file', type=str, help='filename for file records')
    get_parser.add_argument('product', type=str, help='filename for product records')
    get_parser.add_argument('os', type=str, help='filename for os records')
    get_parser.add_argument('manufacturer', type=str, help='filename for manufacturer records')
    get_parser.add_argument('sha1', type=str, help='sha1 to lookup')
    get_parser.set_defaults(func=nsrl_resolve)

    args = parser.parse_args()

    # set verbosity
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    args = vars(parser.parse_args())
    func = args.pop('func')
    # with 'func' removed, args is now a kwargs with only the specific arguments
    # for each subfunction useful for interactive mode.
    func(**args)