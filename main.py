#!/usr/bin/env python3

import os
from datetime import datetime
from extended_dictionary import ExtendedDictionary


def main():
    ext_dict = ExtendedDictionary()

    now = datetime.utcnow()
    now_str = now.strftime("%d/%m/%Y %H:%M:%S")
    
    for x in range(100000000):
        hash_val_key = hash(now_str + str(x))
        hash_val =[ now_str ]
        if not ext_dict.is_basket_empty():
            if ext_dict.does_key_exist(hash_val_key):
                val = ext_dict.get_key_val(hash_val_key)
                print (val)
            else:
                ext_dict.add_key(hash_val_key, hash_val)
        else:
            ext_dict.add_key(hash_val_key, hash_val)

    print (ext_dict.size())


if __name__ == "__main__":
    main()
