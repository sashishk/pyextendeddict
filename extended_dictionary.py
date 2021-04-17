#!/usr/bin/env python3
"""
Motivation:
https://stackoverflow.com/questions/23532449/maximum-size-of-a-dictionary-in-python

Access times for a string key in a python dictionary is in the order of 
1 microsecond (1s / 1000 / 1000).

The time taken increases slightly dependent on the number of entries in 
the dictionary, possibly with something like a log(N) scaling.

Performance degrades significantly for dictionaries larger than 2^26 = 67,108,864. 
It takes 30x longer to read from a dictionary of size 2^27 = 134,217,728, and 9000x 
longer for a dictionary of size 2^28 = 268,435,456. 
My computer ran out of memory before reaching 2^29.

Therefore, the practical answer to your question of the maximum size of a dictionary 
in python is:
2^26 = 67,108,864

Approach:
---------
If the wish is to use dictionary as datastore to store huge number of records, then the ideal 
design can be to create dictionary of dictionary and limit size of internal dictionary to an 
allowed limit. A wrapper would be required with set of requried funcionalities.
"""

import sys
import copy

class ExtendedDictionary:
    """
    Class to manage huge sized key-value lookup
    """
    def __init__(self):
        # we need basket of buckets(dict)
        self.__basket = dict(dict())
        # temporary bucket is required to start filling-in
        self.__temp_bucket = dict() 
        # we should have a fixed size bucket
        self.__bucket_size = 75000 
        # maintain count of total buckets in the basket
        self.__bucket_count = -1 
        # let's start from scratch
        self.clear()

    def __validate_bucket_size(self) -> bool:
        # buckets should be within its limit
        return len(self.__temp_bucket) == self.__bucket_size

    def __add_to_basket(self):
        # the temp bucket has reached its limit, time to add to the basket
        self.__bucket_count = self.__bucket_count + 1
        self.__basket[self.__bucket_count] = copy.deepcopy(self.__temp_bucket)
        self.__temp_bucket.clear()

    def __is_key_in_basket(self, key) -> int:
        # check for existence of the key in backet
        bucket_key = -1 # invalid bucket
        if self.__bucket_count > -1:
            for item in self.__basket.items():
                if key in item[1]:
                    bucket_key = item[0]
                    break
        return bucket_key

    def __is_key_in_temp_bucket(self, key) -> bool:
        # check for existence of the key in temp bucket
        if bool(self.__temp_bucket) and key in self.__temp_bucket:
            return True
        return False

    def clear(self):
        self.__bucket_count = -1
        self.__temp_bucket.clear()
        for key, _ in self.__basket.items():
            self.__basket[key].clear()


    def is_basket_empty(self) -> bool:
        # is there any element in the basket
        return (self.__bucket_count < 0 and len(self.__temp_bucket)==0)

    def add_key(self, key, value):
        # add <key, value> to the backet
        self.__temp_bucket[key] = value
        if self.__validate_bucket_size():
            self.__add_to_basket()

    def size(self) -> int:
        # total elements in backet
        count = 0

        if self.__bucket_count > -1:
            count = (self.__bucket_count + 1) * self.__bucket_size

        if bool(self.__temp_bucket):
            count = count + len(self.__temp_bucket)
        return count

    def does_key_exist(self, key) -> bool:
        # check for existence of key
        status = False

        if self.__is_key_in_basket(key) != -1:
            status = True
        elif self.__is_key_in_temp_bucket(key):
            status = True

        return status

    def get_key_val(self, key) -> str:
        # get val from key
        # Returns: 
        # -1 - If no entries found
        # Else, value is returned
        
        val = "-1" #invalid key
        bucket_key = self.__is_key_in_basket(key)
        if bucket_key != -1:
            val = self.__basket[bucket_key][key]
        elif self.__is_key_in_temp_bucket(key):
            val = self.__temp_bucket[key]
        return val

    def add_bucket_to_basket(self, extended_dict: 'ExtendedDictionary'):
        # add a basket to this basket
        if extended_dict.bucket_count > -1:
            for item in extended_dict.basket.items():
                self.__bucket_count = self.__bucket_count + 1
                self.__basket[self.__bucket_count] = copy.deepcopy(item[1])

        # temp bucket of incoming extended_dict to be added as well
        self.__temp_bucket.update(extended_dict.temp_bucket)

        # if temp bucket results into overflow of bucket size
        if len(self.__temp_bucket) > self.__bucket_size:
            full_dict = [(k, v) for k, v in self.__temp_bucket.items()][:self.__bucket_size]
            rem_dict = [(k, v) for k, v in self.__temp_bucket.items()][self.__bucket_size:]
            self.__bucket_count = self.__bucket_count + 1
            self.__basket[self.__bucket_count] = copy.deepcopy(dict(full_dict))
            self.__temp_bucket.clear()
            self.__temp_bucket = copy.deepcopy(dict(rem_dict))

        # Clear off the extended_dict
        extended_dict.clear()
