'''
Some IO interfaces that do checksumming on-the-fly.
'''

from os.path import basename

from . import cksum_ffi
from .context_timer import ContextTimer

class CksumWriter:
    '''
    A simple writer class that works with asdf
    '''
    def __init__(self, fn, *open_args, do_checksum=True, checksum_fn=None, **open_kwargs):
        self.fn = fn
        self.open_args = open_args
        self.open_kwargs = open_kwargs
        self.bytes_written = 0
        self.do_checksum = do_checksum

        if checksum_fn is None:
            self.checksum_fn = fn + '.crc32'
            self.checksum_file_mode = 'a'
        else:
            self.checksum_fn = checksum_fn
            self.checksum_file_mode = 'w'
        
        self.io_timer = ContextTimer(cumulative=True)
        self.checksum_timer = ContextTimer(cumulative=True)
        
    def __enter__(self):
        self.fp = open(self.fn, *self.open_args, **self.open_kwargs, mode='wb')
        self.checksum = cksum_ffi.CRC32_FAST_SEED
        return self
    
    def __exit__(self, *excep):
        with self.io_timer:
            self.fp.close()
        self._finalize()
        
        if self.do_checksum:
            with open(self.checksum_fn, self.checksum_file_mode) as cfp, self.checksum_timer:
                cfp.write(f'{self.checksum} {self.bytes_written} {basename(self.fn)}\n')
    
    def write(self, data):  # asdf only seems to need one arg version
        data = memoryview(data)  # so we can use data.nbytes
        
        if self.do_checksum:
            self.running_checksum = self._ingest(data)
            
        with self.io_timer:
            size = self.fp.write(data)
        self.bytes_written += size        
            
        return size
    
    def tell(self, *args, **kwargs):
        with self.io_timer:  # might as well
            return self.fp.tell(*args, **kwargs)
    
    def flush(self, *args, **kwargs):
        with self.io_timer:
            return self.fp.flush(*args, **kwargs)
    
    def _ingest(self, data):
        with self.checksum_timer:
            self.checksum = cksum_ffi.crc32_fast_partial(cksum_ffi.ffi.from_buffer(data), data.nbytes, self.checksum)
        
    def _finalize(self):
        with self.checksum_timer:
            self.checksum = cksum_ffi.crc32_fast_finalize(self.bytes_written, self.checksum)


class CksumReader:
    '''
    An object that represents a repository of checksums.
    Files read with this class (by calling the object) will have their checksums verified.
    Reading returns a buffer that can be efficiently loaded by numpy with np.frombuffer().
    '''
    def __init__(self, checksum_fn, verify_checksums=True, verbose=False):
        self.verbose = verbose
        self.nverify = 0
        
        if verify_checksums:
            with open(checksum_fn, 'r') as fp:
                self.known_checksums = [line.split() for line in fp.readlines()]
        
        self.checksum_fn = checksum_fn
        self.known_checksums = {line[2]:dict(crc32=int(line[0]), size=int(line[1])) for line in self.known_checksums}
        self.verify_checksums = verify_checksums
        
        self.io_timer = ContextTimer(cumulative=True)
        self.checksum_timer = ContextTimer(cumulative=True)
        
        self.bytes_read = 0
    
    def __call__(self, fn, verify_checksum=None, verbose=False):
        if verify_checksum is None:
            verify_checksum = self.verify_checksums
        if verbose is None:
            verbose = self.verbose
            
        fnbase = basename(fn)
        if verify_checksum and fnbase not in self.known_checksums:
            raise ValueError(f'Filename "{fnbase}" not in checksum file {self.checksum_fn}!')
            
        # TODO: could read in blocks to trigger readahead
        with open(fn, 'rb') as fp, self.io_timer:
            data = fp.read()
        data = memoryview(data)  # ?
        self.bytes_read += data.nbytes
            
        if verify_checksum:
            with self.checksum_timer:
                checksum = self._checksum_partial(data)
                checksum = cksum_ffi.crc32_fast_finalize(data.nbytes, checksum)

            if data.nbytes != self.known_checksums[fnbase]['size']:
                raise ValueError(f"File size {data.nbytes} for file {fn} did not match "
                                 f"size {self.known_checksums[fnbase]['size']} from {self.checksum_fn}")
            elif checksum != self.known_checksums[fnbase]['crc32']:
                raise ValueError(f"Checksum {checksum} for file {fn} did not match "
                                 f"checksum {self.known_checksums[fnbase]['crc32']} from {self.checksum_fn}")
            else:
                self.nverify += 1
            
        return data
    
    def report(self):
        print(f'Verified {self.nverify} checksum(s)')
        
    def __del__(self):
        if self.verbose:
            self.report()
            
    @classmethod
    def _checksum_partial(cls, data, partial_checksum=cksum_ffi.CRC32_FAST_SEED):
        return cksum_ffi.crc32_fast_partial(cksum_ffi.ffi.from_buffer(data), data.nbytes, partial_checksum)
