#!/usr/bin/env python3

"""
Purpose of this code: default linux mount doesn't checks if binded mount became broken.
It can happen when mounted dir was removed and created again: bind is based on inode numbers,
that will be changed for recreated dir, and bind will break silently.
We should find and remount all bind mounts because of this.
Task is reading content from /etc/mtab and for every mount with bind method checks that inodes
of mounted dir and mount point are the same.
If they're not, it does umount and mount dirs again.
"""

import os
import time
import stat
from subprocess import call

__version__ = '0.1.0'

# TODO:
# noop arg

def remount_func(mount_point, mounted_dir):
  umount = call(['umount', mount_point])
  if umount != 0:
    print("Error unmounting \'{}\'"
          .format(mount_point))
  else:
    print ('Successfully unmounted \'{}\''.format(mount_point))
    remount = call(['mount', '-B', mounted_dir, mount_point])
    if remount != 0:
      errno = get_errno()
      print("Error mounting \'{}\' on \'{}\'"
             .format(mount_point, mounted_dir))
      return False
    else:
      print ('Successfully remounted \'{}\' on \'{}\''.format(mount_point, mounted_dir))
      return True

def check_inode_numbers(mounted_dir, mount_point):
  mp_ino = os.stat(mount_point)[stat.ST_INO] # returns int
  md_ino = os.stat(mounted_dir)[stat.ST_INO]
  if mp_ino != md_ino:
    print ('Mountpoint inode number differs from mounted dir in: \n\
            mount point \'{}\' inode: {}\n\
            mount dir \'{}\' inode: {}\n'
            .format(mount_point, mp_ino, mounted_dir, md_ino))
    if remount_func (mount_point, mounted_dir):
      mp_ino = os.stat(mount_point)[stat.ST_INO] # re-read changed vars
      md_ino = os.stat(mounted_dir)[stat.ST_INO]
      print ('Inode numbers are equal:\n\
              mount point \'{}\' inode: {}\n\
              mount dir \'{}\' inode: {}\n'
              .format(mount_point, mp_ino, mounted_dir, md_ino))
      return True
    else:
      return False
      print ("Couldn't remount for unknown reasons.\n")
  else:
    print ('Inode numbers of {} and {} are equal: OK.\n'
            .format(mount_point, mounted_dir))
    return True

def main():
  retry = 10
  o = ''
  with open ('/etc/mtab', 'r') as mtab:
    for line in mtab:
      a = (mdev, mpo, fs, opts, dmp, fsck) = line.split()
      try:
        o = str(a[3]).split(',')[1] # split opts
      except Exception as e:
        pass
      # output is like:
      # ['/bin', '/var/chroot/jail/bin', 'none', 'rw,bind', '0', '0']
      if 'bind' in o: # we'll check for ever dirs mounted with bind method
        print ('Checking: {} on {}:'
                .format(a[0], a[1]))
        if check_inode_numbers(a[0], a[1]):
          pass
        else:
          while retry > 0:
            retry = retry - 1
            print ('Something went wrong. Retry, {} attempts left...\n'.format(retry))
            time.sleep(30)
            check_inode_numbers(a[0], a[1])

main()
